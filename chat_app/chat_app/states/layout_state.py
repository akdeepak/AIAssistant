import asyncio
import json
from pathlib import Path

import reflex as rx


TEMPLATES_JSON_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "assistant_templates.json"
)


def _append_assistant_template(name: str, description: str) -> None:
    """Append a new assistant definition to the templates JSON file.

    If the file does not exist or is invalid, it will be (re)created.
    """

    templates: list[dict]
    try:
        if TEMPLATES_JSON_PATH.exists():
            with TEMPLATES_JSON_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                templates = data if isinstance(data, list) else []
        else:
            templates = []
    except (OSError, json.JSONDecodeError):
        templates = []

    # Simple slug for image name, e.g. "Fleet AI Assistant" -> "/fleetaiassistant.png"
    slug = "".join(ch.lower() for ch in name if ch.isalnum()) or "assistant"
    image_src = f"/{slug}.png"

    new_entry = {
        "image_src": image_src,
        "title": name,
        "description": description,
        "tag_color": "purple-500",
    }

    templates.append(new_entry)

    try:
        TEMPLATES_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with TEMPLATES_JSON_PATH.open("w", encoding="utf-8") as f:
            json.dump(templates, f, indent=2)
    except OSError:
        # If saving fails, we silently ignore for now.
        # The UI flow should still complete.
        return


class LayoutState(rx.State):
    """Global layout/navigation state for the app."""

    current_page: str = "dashboard"

    # Controls whether the Assistant Builder form/upload is visible.
    show_assistant_upload: bool = False

    # Store latest Assistant configuration (optional, for future use).
    assistant_name: str = ""
    assistant_description: str = ""

    # Status flags for Assistant creation flow.
    creating_assistant: bool = False
    assistant_created: bool = False

    # Alert dialog state for assistant creation flow.
    assistant_dialog_open: bool = False
    assistant_dialog_message: str = ""

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

    @rx.event
    def submit_assistant(self, form_data: dict):
        """Handle Assistant Builder form submission."""

        self.assistant_name = form_data.get("assistant_name", "").strip()
        self.assistant_description = form_data.get("assistant_description", "").strip()
        self.creating_assistant = True
        self.assistant_created = False

        # Open alert dialog indicating that creation is in progress.
        self.assistant_dialog_open = True
        self.assistant_dialog_message = "Assistant creation in progress..."

        # Kick off background task to simulate creation flow.
        yield LayoutState.finish_assistant_creation

    @rx.event(background=True)
    async def finish_assistant_creation(self):
        """Simulate assistant creation, then mark as created."""

        await asyncio.sleep(2)

        # Capture current assistant details outside of the state lock
        async with self:
            name = self.assistant_name
            description = self.assistant_description

        # Persist the new assistant definition into the JSON file
        _append_assistant_template(name, description)

        # Now update UI state to reflect completion
        async with self:
            self.creating_assistant = False
            self.assistant_created = True
            # Update dialog message to indicate success.
            self.assistant_dialog_message = "Assistant created successfully!"
            # Hide the form once the assistant is successfully created
            self.show_assistant_upload = False

    @rx.event
    def close_assistant_dialog(self):
        """Close the assistant creation alert dialog."""

        self.assistant_dialog_open = False
