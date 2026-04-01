import reflex as rx


def chat_interface() -> rx.Component:
    """Placeholder chat interface for the root AIAssitant project.

    The full-featured chat UI lives in the assistant-chat/ project.
    This stub provides a minimal working page so the root Reflex app
    can start without errors.
    """
    return rx.el.div(
        rx.el.div(
            rx.heading("AI Assistant", size="7"),
            rx.text(
                "This is the root project shell. "
                "Run the assistant-chat/ project for the full chat experience.",
                size="3",
                color="gray",
            ),
            class_name="flex flex-col items-center justify-center gap-4 h-screen",
        ),
        class_name="h-screen flex flex-col bg-gray-50 w-full",
    )
