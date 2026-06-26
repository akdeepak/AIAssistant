import reflex as rx

from chat_app.states.chat_state import ChatState


def input_area() -> rx.Component:
    return rx.el.div(
        # Gradient fade above the input so messages don't hard-cut
        rx.el.div(
            class_name=(
                "absolute -top-8 left-0 right-0 h-8 "
                "bg-gradient-to-t from-[#f5f5f5] to-transparent pointer-events-none"
            ),
        ),
        rx.el.form(
            rx.el.textarea(
                name="message",
                placeholder="Type a message",
                enter_key_submit=True,
                class_name=(
                    "bg-transparent resize-none outline-none text-[14px] py-2.5 px-3 "
                    "min-h-10 text-gray-800 max-h-36 peer !overflow-y-auto w-full "
                    "placeholder:text-gray-400"
                ),
                auto_height=True,
                required=True,
            ),
            rx.box(
                rx.cond(
                    ChatState.messages,
                    rx.el.button(
                        rx.icon("square-pen", size=16),
                        title="New chat",
                        class_name=(
                            "rounded-full bg-gray-50 text-gray-500 p-2 size-9 "
                            "inline-flex items-center justify-center hover:bg-gray-100 "
                            "border border-gray-200 transition-colors"
                        ),
                        type="button",
                        on_click=ChatState.clear_messages,
                    ),
                ),
                rx.el.button(
                    rx.cond(
                        ChatState.typing,
                        rx.icon("loader-circle", size=18, class_name="animate-spin"),
                        rx.icon("send-horizontal", size=18),
                    ),
                    class_name=(
                        "self-end rounded-full bg-indigo-600 hover:bg-indigo-700 "
                        "text-white p-2 disabled:opacity-40 size-9 inline-flex "
                        "items-center justify-center transition-colors"
                    ),
                    disabled=ChatState.typing,
                ),
                class_name=(
                    "flex flex-row mb-2 peer-placeholder-shown:[&>*:last-child]:opacity-40 "
                    "peer-placeholder-shown:[&>*:last-child]:pointer-events-none w-full"
                ),
                justify_content=rx.cond(
                    ChatState.messages,
                    "space-between",
                    "end",
                ),
            ),
            reset_on_submit=True,
            on_submit=ChatState.send_message,
            class_name=(
                "flex flex-col gap-2 rounded-2xl bg-white w-full "
                "border border-gray-200 px-3 py-1 "
                "focus-within:border-indigo-300 focus-within:ring-indigo-100 "
                "focus-within:ring-2 transition-all"
            ),
        ),
        class_name=(
            "relative w-full max-w-[1000px] mx-auto px-4 pb-5 flex-shrink-0"
        ),
    )
