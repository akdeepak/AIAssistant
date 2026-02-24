import asyncio

import reflex as rx


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
