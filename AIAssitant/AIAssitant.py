# """Welcome to Reflex! This file outlines the steps to create a basic app."""

# import reflex as rx

# from rxconfig import config


# class State(rx.State):
#     """The app state."""


# def index() -> rx.Component:
#     # Sidebar-like layout using Reflex
#     return rx.hstack(
#         # Sidebar (left stack)
#         rx.vstack(
#             rx.image(
#                 # src="/assets/instanda_logo.png",  # Update to your logo path if needed
#                 src=rx.asset("instanda_new.png"),  # Use Reflex's asset management
#                 width="150px",
#                 alt="Logo",
#                 style={"marginBottom": "2rem"},
#             ),
#             rx.box(
#                 rx.heading("📋 How to Use", size="6"),
#                 rx.ordered_list(
#                     rx.list_item("Upload a JSON policy document"),
#                     rx.list_item("Type your question about the policy"),
#                     rx.list_item("Click Submit to get AI-powered answers"),
#                 ),
#                 style={"padding": "1rem"},
#             ),
#             spacing="4",
#             align="start",
#             width="320px",
#             min_height="100vh",
#             style={"backgroundColor": "#f8f9fa", "borderRight": "1px solid #e0e0e0"},
#         ),
#         # Main content (right)
#         rx.container(
#             rx.color_mode.button(position="top-right"),
#             rx.vstack(
#                 rx.heading("Welcome to Reflex What is happening !", size="9"),
#                 rx.text(
#                     "Get started by editing ",
#                     rx.code(f"{config.app_name}/{config.app_name}.py"),
#                     size="5",
#                 ),
#                 rx.link(
#                     rx.button("Check out our docs!"),
#                     href="https://reflex.dev/docs/getting-started/introduction/",
#                     is_external=True,
#                 ),
#                 spacing="5",
#                 justify="center",
#                 min_height="85vh",
#             ),
#             width="100%",
#         ),
#         spacing="0",
#         align="start",
#         width="100vw",
#     )


# app = rx.App()
# app.add_page(index)


import reflex as rx
from components.chat_interface import chat_interface


def index() -> rx.Component:
    """The main page of the chat application."""
    return chat_interface()


app = rx.App(theme=rx.theme(appearance="light"))
app.add_page(index)
