import asyncio
import json
from pathlib import Path

import reflex as rx
import requests


TEMPLATES_JSON_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "assistant_templates.json"
)

INGEST_URL = "http://localhost:9000/llama-faq/ingest"


def _load_templates_from_file() -> list[dict]:
    """Load assistant templates from the JSON file.

    Used to initialise in-memory state; tolerant of missing/invalid files.
    """

    try:
        if TEMPLATES_JSON_PATH.exists():
            with TEMPLATES_JSON_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        return []
    except (OSError, json.JSONDecodeError):
        return []


def _append_assistant_template(
    name: str,
    description: str,
    image_src: str | None = None,
    knowledge_base_id: str | None = None,
    source_file: str | None = None,
    kb_message: str | None = None,
    kb_documents: int | None = None,
) -> dict | None:
    """Append a new assistant definition to the templates JSON file.

    Returns the new entry dict on success so callers can also update
    in-memory state used by the UI. If persisting fails, returns None.
    """

    templates = _load_templates_from_file()

    # Determine image source for persistence:
    # - If an explicit image_src is provided, normalise values coming from
    #   the upload handler so that we do not persist the `/_upload` prefix
    #   into the templates JSON. Instead we store "/<filename>.png" which
    #   matches the convention used by the built-in templates.
    # - Otherwise, fall back to a slug-based filename.
    if image_src is not None and image_src != "":
        if image_src.startswith("/_upload/"):
            # Keep only the file name and point to the root path, e.g.
            # "/_upload/instanda_logo1.png" -> "/instanda_logo1.png".
            effective_image_src = f"/{Path(image_src).name}"
        else:
            effective_image_src = image_src
    else:
        # Simple slug for image name, e.g. "Fleet AI Assistant" -> "/fleetaiassistant.png"
        slug = "".join(ch.lower() for ch in name if ch.isalnum()) or "assistant"
        effective_image_src = f"/{slug}.png"

    new_entry: dict = {
        "image_src": effective_image_src,
        "title": name,
        "description": description,
        "tag_color": "purple-500",
    }

    # Include knowledge base metadata if available
    if knowledge_base_id is not None:
        new_entry["knowledge_base_id"] = knowledge_base_id
    if source_file is not None:
        new_entry["source_file"] = source_file
    if kb_message is not None:
        new_entry["kb_message"] = kb_message
    if kb_documents is not None:
        new_entry["kb_documents"] = kb_documents

    templates.append(new_entry)

    try:
        TEMPLATES_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with TEMPLATES_JSON_PATH.open("w", encoding="utf-8") as f:
            json.dump(templates, f, indent=2)
    except OSError:
        # If saving fails, we silently ignore for now.
        # The UI flow should still complete.
        return None

    return new_entry


INITIAL_TEMPLATES: list[dict] = _load_templates_from_file()


class LayoutState(rx.State):
    """Global layout/navigation state for the app."""

    current_page: str = "dashboard"

    # Controls whether the Assistant Builder form/upload is visible.
    show_assistant_upload: bool = False

    # Store latest Assistant configuration (optional, for future use).
    assistant_name: str = ""
    assistant_description: str = ""
    assistant_image_src: str = ""

    # Status flags for Assistant creation flow.
    creating_assistant: bool = False
    assistant_created: bool = False

    # Alert dialog state for assistant creation flow.
    assistant_dialog_open: bool = False
    assistant_dialog_message: str = ""

    # Files uploaded for the assistant's knowledge base (filenames only for UI).
    uploaded_files: list[str] = []

    # In-memory cache of assistant templates shown on the dashboard.
    # This is initialised from the JSON file on startup and updated when
    # new assistants are created so the UI reflects changes without
    # requiring a server restart.
    assistant_templates: list[dict] = INITIAL_TEMPLATES

    @rx.event
    def set_assistant_name(self, value: str):
        """Update assistant name as the user types."""

        self.assistant_name = value.strip()

    @rx.event
    def set_assistant_description(self, value: str):
        """Update assistant description as the user types."""

        self.assistant_description = value.strip()

    @rx.event
    async def handle_image_upload(self, files: list[rx.UploadFile]):
        """Handle upload of the assistant image and store its served URL."""

        if not files:
            return

        first = files[0]
        # Save the image file to the upload dir and record its URL.
        upload_dir = rx.get_upload_dir()
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_name = getattr(first, "name", None) or getattr(
            first, "filename", "assistant_image"
        )
        file_bytes = await first.read()

        file_path = upload_dir / file_name
        try:
            with file_path.open("wb") as f:
                f.write(file_bytes)
        except OSError:
            return

        # Store a plain string URL path for the uploaded image.
        # Uploaded files are served from the `/_upload` mount point.
        self.assistant_image_src = f"/_upload/{file_path.name}"

    @rx.event
    def set_page(self, page: str):
        self.current_page = page
        # Reset upload panel and status when navigating away
        if page != "projects":
            self.show_assistant_upload = False
            self.creating_assistant = False
            self.assistant_created = False

    @rx.event
    def open_assistant_upload(self):
        # Show the form panel and reset any previous status
        self.show_assistant_upload = True
        self.creating_assistant = False
        self.assistant_created = False
        self.assistant_dialog_open = False
        self.assistant_dialog_message = ""
        self.uploaded_files = []
        self.assistant_image_src = ""

    @rx.event
    def set_uploaded_files(self, files: list[rx.UploadFile] | None):
        """Store the list of uploaded files for display in the UI."""

        if not files:
            self.uploaded_files = []
            return

        names: list[str] = []
        for f in files:
            name = getattr(f, "name", None)
            if isinstance(name, str) and name:
                names.append(name)

        self.uploaded_files = names

    @rx.event
    async def submit_assistant(self, files: list[rx.UploadFile]):
        """Create an assistant and ingest the uploaded knowledge base file."""

        self.creating_assistant = True
        self.assistant_created = False

        # Open alert dialog indicating that creation is in progress.
        self.assistant_dialog_open = True
        self.assistant_dialog_message = "Assistant creation in progress..."

        knowledge_base_id: str | None = None
        kb_message: str | None = None
        kb_documents: int | None = None
        source_file: str | None = None

        # Call external ingest API with the uploaded file, if provided
        if files:
            first = files[0]
            try:
                file_name = getattr(first, "name", None) or getattr(
                    first, "filename", "uploaded_file"
                )
                file_bytes = await first.read()
                source_file = str(file_name)

                response = requests.post(
                    INGEST_URL,
                    headers={"accept": "application/json"},
                    files={"file": (source_file, file_bytes)},
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()

                knowledge_base_id = data.get("knowledge_base_id")
                kb_message = data.get("message")
                kb_documents = data.get("documents")
            except Exception:
                # If ingest fails, mark as failed and show a generic message.
                self.creating_assistant = False
                self.assistant_created = False
                self.assistant_dialog_message = (
                    "Assistant creation failed while ingesting knowledge base."
                )
                return

        # Persist the new assistant definition into the JSON file including KB metadata
        new_entry = _append_assistant_template(
            self.assistant_name,
            self.assistant_description,
            image_src=self.assistant_image_src or None,
            knowledge_base_id=knowledge_base_id,
            source_file=source_file,
            kb_message=kb_message,
            kb_documents=kb_documents,
        )

        # If persistence succeeded, also update the in-memory list so that
        # the dashboard sees the new assistant immediately without a
        # Reflex server restart.
        if new_entry is not None:
            self.assistant_templates.append(new_entry)

        # Mark as created and update dialog
        self.creating_assistant = False
        self.assistant_created = True
        self.assistant_dialog_message = "Assistant created successfully!"
        # Hide the form once the assistant is successfully created
        self.show_assistant_upload = False

    @rx.event
    def close_assistant_dialog(self):
        """Close the assistant creation alert dialog."""

        self.assistant_dialog_open = False
