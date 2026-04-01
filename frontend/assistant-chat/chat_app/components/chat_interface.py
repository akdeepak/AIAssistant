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
            class_name="flex flex-col gap-5 pb-32 pt-6 px-2",
        ),
        rx.el.div(
            rx.icon("message-circle", size=40, class_name="text-gray-300 mb-3"),
            rx.el.p(
                "Start a conversation",
                class_name="text-gray-500 text-base font-medium",
            ),
            rx.el.p(
                "Type a message below to begin.",
                class_name="text-gray-400 text-sm",
            ),
            class_name="flex flex-col flex-1 items-center justify-center gap-1",
        ),
    )

    return rx.el.div(
        # Full-width scrollable wrapper — scrollbar hugs the right edge
        rx.el.div(
            # Centered content column inside the full-width scroller
            rx.el.div(
                main_section,
                class_name="max-w-[1000px] mx-auto px-4 w-full flex flex-col flex-1",
            ),
            class_name=(
                "flex flex-col flex-1 overflow-y-auto custom-scrollbar w-full"
            ),
        ),
        input_area(),
        class_name="h-screen flex flex-col bg-[#f5f5f5] w-full overflow-hidden",
    )
