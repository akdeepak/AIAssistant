import json
from pathlib import Path

import reflex as rx

from chat_app.states.chat_state import ChatState


TEMPLATES_JSON_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "assistant_templates.json"
)


def load_templates() -> list[dict]:
    try:
        with TEMPLATES_JSON_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def template_card(
    image_src: str,
    title: str,
    description: str,
    tag_color: str = "purple-500",
) -> rx.Component:
    """Large template-style card with image, title, and tag.

    Clicking the card still sends the description as the message.
    """

    return rx.el.button(
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
        on_click=ChatState.send_message({"message": description}),
        type="button",
        class_name="w-full max-w-md focus:outline-none",
    )


def preset_cards() -> rx.Component:
    templates = load_templates()

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
            *[
                template_card(
                    card.get("image_src", ""),
                    card.get("title", ""),
                    card.get("description", ""),
                    card.get("tag_color", "purple-500"),
                )
                for card in templates
            ],
            class_name="gap-8 grid grid-cols-1 lg:grid-cols-2 w-full",
        ),
        class_name=(
            "flex flex-col justify-center items-start gap-8 w-full max-w-[72rem] "
            "mx-auto px-12 py-12"
        ),
    )
