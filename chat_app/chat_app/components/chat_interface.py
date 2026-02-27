import reflex as rx

from chat_app.components.input_area import input_area
from chat_app.components.message_bubble import message_bubble
from chat_app.states.chat_state import ChatState


def chat_interface() -> rx.Component:
    """The main chat interface component for the /chat page."""

    main_section = rx.cond(
        ChatState.messages,
        rx.auto_scroll(
            rx.foreach(
                ChatState.messages,
                lambda m, i: message_bubble(
                    m["text"],
                    m["is_ai"],
                    i == ChatState.messages.length() - 1,
                ),
            ),
            class_name="flex flex-col gap-4 pb-24 pt-6",
            # class_name="text-gray-500 text-sm mt-8 text-center"
        ),
        rx.el.div(
            rx.el.p(
                "Start a conversation by typing a message below.",
                class_name="text-gray-500 text-sm mt-8 text-center",
            ),
            class_name="flex flex-col gap-4 pb-24 pt-6",
        ),
    )

    return rx.el.div(
        # Centered chat column for messages.
        rx.el.div(
            main_section,
            class_name="flex flex-col flex-1 max-w-[720px] mx-auto px-4 w-full",
        ),
        # Input area uses the same max width and padding in its own
        # wrapper so the question bubble and text area align.
        input_area(),
        class_name="h-screen flex flex-col bg-gray-50 w-full",
    )
