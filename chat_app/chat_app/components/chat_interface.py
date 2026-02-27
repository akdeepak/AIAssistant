import reflex as rx

from chat_app.components.input_area import input_area
from chat_app.components.message_bubble import message_bubble
from chat_app.states.chat_state import ChatState


def chat_interface() -> rx.Component:
    """The main chat interface component for the /chat page."""

    main_section = rx.cond(
        ChatState.messages,
        rx.fragment(
            rx.el.button(
                rx.icon("arrow-left"),
                rx.el.span("Back", class_name="ml-2"),
                on_click=ChatState.clear_messages,
                class_name=(
                    "flex items-center gap-2 px-4 py-2 mb-2 bg-white border "
                    "rounded-lg shadow-sm hover:bg-gray-100 w-fit mt-4 ml-4"
                ),
            ),
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
            ),
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
        # Scrollable chat area, constrained to the same width as the
        # input area so bubbles and text align cleanly.
        rx.el.div(
            main_section,
            class_name=(
                "flex-1 w-full max-w-3xl mx-auto px-6 "
                "flex flex-col"
            ),
        ),
        input_area(),
        class_name="h-screen flex flex-col bg-gray-50 w-full",
    )
