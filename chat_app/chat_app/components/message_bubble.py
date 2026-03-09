import reflex as rx

from chat_app.components.typing_indicator import typing_indicator


def ai_bubble(message: str, is_last: bool = False) -> rx.Component:
    """Assistant (AI) message with avatar on the left — Teams style."""

    return rx.el.div(
        # Avatar
        rx.el.div(
            rx.icon("bot", size=16),
            class_name=(
                "rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 "
                "text-white p-2 size-9 flex-shrink-0 inline-flex "
                "items-center justify-center shadow-sm"
            ),
        ),
        # Name + bubble column
        rx.el.div(
            # Sender label
            rx.el.p(
                "AI Assistant",
                class_name="text-xs font-semibold text-gray-600 mb-1 ml-1",
            ),
            # Bubble
            rx.el.div(
                rx.cond(
                    message,
                    rx.markdown(
                        message,
                        class_name=(
                            "text-[14px] leading-relaxed text-gray-800 "
                            "[&>ol]:list-decimal [&>ol]:pl-5 [&>ol]:space-y-1 "
                            "[&>ul]:list-disc [&>ul]:pl-5 [&>ul]:space-y-1 "
                            "[&>p]:my-1 [&>h1]:text-lg [&>h2]:text-base [&>h3]:text-sm "
                            "[&>h1]:font-bold [&>h2]:font-semibold [&>h3]:font-medium "
                            "[&>pre]:bg-gray-50 [&>pre]:rounded-lg [&>pre]:p-3 [&>pre]:text-xs "
                            "[&>pre]:overflow-x-auto [&>pre]:border "
                            "[&_code]:bg-gray-50 [&_code]:px-1 "
                            "[&_code]:rounded [&_code]:text-xs "
                            "[&_a]:text-indigo-600 [&_a]:underline"
                        ),
                    ),
                    rx.cond(
                        is_last,
                        typing_indicator(),
                    ),
                ),
                class_name=(
                    "bg-white border border-gray-200 rounded-xl rounded-tl-sm "
                    "px-4 py-3 text-gray-800 max-w-full"
                ),
            ),
            class_name="flex flex-col max-w-[90%]",
        ),
        class_name="flex flex-row items-start gap-2.5",
    )


def user_bubble(message: str) -> rx.Component:
    """User message aligned to the right — Teams style."""

    return rx.el.div(
        # Name + bubble column
        rx.el.div(
            rx.el.p(
                "You",
                class_name="text-xs font-semibold text-gray-600 mb-1 mr-1 text-right",
            ),
            rx.el.div(
                rx.el.p(
                    message,
                    class_name="text-[14px] leading-relaxed",
                ),
                class_name=(
                    "bg-indigo-600 text-white px-4 py-3 rounded-xl rounded-tr-sm "
                    "w-fit ml-auto"
                ),
            ),
            class_name="flex flex-col max-w-[90%] ml-auto",
        ),
        class_name="flex flex-row justify-end",
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
        class_name="w-full",
    )
