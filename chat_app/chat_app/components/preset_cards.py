import reflex as rx

from chat_app.states.chat_state import ChatState
from chat_app.states.layout_state import LayoutState


def template_card(
    image_src: str,
    title: str,
    description: str,
    tag_color: str = "purple-500",
    knowledge_base_id: str | None = None,
) -> rx.Component:
    """Large template-style card with image, title, and tag.

    Clicking the card selects the assistant (knowledge base) and
    navigates to the dedicated chat page, where the user can then
    type their question.
    """

    button = rx.el.button(
        # Outer card container
        rx.el.div(
            # Top image area
            rx.el.img(
                src=image_src,
                class_name="w-full h-40 object-cover rounded-t-3xl",
            ),
            # Bottom text area
            rx.el.div(
                rx.el.p(
                    title,
                    class_name="text-lg md:text-xl font-medium text-gray-900",
                    # class_name="text-base md:text-lg font-medium text-gray-900",
                ),
                rx.el.div(
                    rx.el.span(
                        class_name=f"inline-flex h-3 w-3 rounded-full bg-{tag_color} mr-2",
                    ),
                    rx.el.span(
                        description,
                        class_name="text-xs font-medium text-gray-500",
                    ),
                    class_name="flex items-center gap-2 mt-2",
                ),
                class_name="px-4 py-3",
            ),
            class_name=(
                "bg-white rounded-2xl shadow-sm border flex flex-col text-left "
                "overflow-hidden hover:shadow-md transition-shadow"
            ),
        ),
        # Select the assistant / knowledge base for subsequent chat
        # requests. The actual question will be whatever the user
        # types into the input area on the /chat page.
        on_click=ChatState.select_assistant(knowledge_base_id),
        type="button",
        class_name="w-full max-w-md focus:outline-none",
    )

    # Wrap the button in a link so that clicking a preset both seeds
    # the conversation and navigates to the chat page where the user
    # can continue chatting.
    return rx.link(button, href="/chat", underline="none")


def preset_cards() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("bot", size=24),
                class_name=(
                    "rounded-full bg-white p-2 size-10 inline-flex items-center "
                    "justify-center border"
                ),
            ),
            rx.el.p(
                "Instanda AI Agentic Assistant",
                class_name="text-2xl md:text-3xl font-medium",
            ),
            class_name="text-black flex flex-row gap-4 items-center mb-6",
        ),
        rx.el.div(
            rx.foreach(
                LayoutState.assistant_templates,
                lambda card, i: template_card(
                    card["image_src"],
                    card["title"],
                    card["description"],
                    card.get("tag_color", "purple-500"),
                    card.get("knowledge_base_id"),
                ),
            ),
            class_name="gap-8 grid grid-cols-1 lg:grid-cols-2 w-full",
        ),
        class_name=(
            "flex flex-col justify-center items-start gap-8 w-full max-w-[72rem] "
            "mx-auto px-12 py-12"
        ),
    )
