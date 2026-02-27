import reflex as rx

from chat_app.components.typing_indicator import typing_indicator


def ai_bubble(message: str, is_last: bool = False) -> rx.Component:
    """Assistant (AI) message with avatar on the left."""

    return rx.el.div(
        # Avatar column
        rx.el.div(
            rx.icon("bot", size=16),
            class_name=(
                "rounded-full bg-white text-black p-2 size-8 inline-flex "
                "items-center justify-center border shadow-sm"
            ),
        ),
        # Message bubble column
        rx.el.div(
            rx.cond(
                message,
                rx.el.p(message, class_name="text-sm sm:text-base"),
                rx.cond(
                    is_last,
                    typing_indicator(),
                ),
            ),
            class_name=(
                "bg-white rounded-2xl px-3 py-2 text-black text-sm sm:text-base "
                "shadow-sm max-w-[90%]"
            ),
        ),
        class_name="flex flex-row items-start gap-3 text-black max-w-3xl",
    )


def user_bubble(message: str) -> rx.Component:
    """User message aligned to the right within the same column."""

    return rx.el.div(
        # Spacer to align with the assistant avatar column
        rx.el.div(class_name="size-8"),
        # User bubble aligned to the right
        rx.el.div(
            rx.el.p(message, class_name="text-sm sm:text-base"),
            class_name=(
                "text-white px-3 py-2 bg-blue-500 rounded-2xl w-fit max-w-[90%] "
                "ml-auto mr-12 shadow-sm"
            ),
        ),
        class_name="flex flex-row items-start gap-3 text-black max-w-3xl",
    )


def message_bubble(
    message: str, is_ai: bool = False, is_last: bool = False
) -> rx.Component:
    return rx.el.div(
        rx.cond(
            is_ai,
            ai_bubble(message, is_last),
            user_bubble(message),
        ),
        class_name="w-full flex flex-col gap-4 mx-auto max-w-3xl px-6",
    )
