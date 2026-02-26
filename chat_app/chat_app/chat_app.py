import reflex as rx
from chat_app.components.chat_interface import chat_interface
from chat_app.states.layout_state import LayoutState


def sidebar_item(text: str, icon: str, href: str) -> rx.Component:
    """Single item in the sidebar that navigates to a route."""

    return rx.link(
        rx.hstack(
            rx.icon(icon, color="#bfc9d1"),
            rx.text(text, size="4", color="#bfc9d1"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.75rem",
            align="center",
            style={
                "_hover": {
                    "background": "#353436",
                    "color": "#fff",
                },
                "border-radius": "0.5em",
            },
        ),
        href=href,
        underline="none",
        weight="medium",
        width="100%",
    )


def sidebar_items() -> rx.Component:
    return rx.vstack(
        sidebar_item("Dashboard", "layout-dashboard", "/"),
        sidebar_item("Assistant Studio", "square-library", "/assistant-studio"),
        sidebar_item("Knowledge Base", "bar-chart-4", "#"),
        sidebar_item("Analytics", "mail", "#"),
        spacing="1",
        width="100%",
    )


def sidebar() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.vstack(
                rx.hstack(
                    rx.image(
                        src="/logo.png",
                        width="50.25em",
                        height="auto",
                        border_radius="25%",
                    ),
                    # rx.heading("INSTANDA", size="7", weight="bold"),
                    align="center",
                    justify="start",
                    padding_x="0.5rem",
                    width="100%",
                ),
                sidebar_items(),
                spacing="5",
                padding_x="1em",
                padding_y="1.5em",
                bg="#2d2c2f",
                align="start",
                height="650px",
                width="16em",
            ),
        ),
        rx.mobile_and_tablet(
            rx.drawer.root(
                rx.drawer.trigger(rx.icon("align-justify", size=30)),
                rx.drawer.overlay(z_index="5"),
                rx.drawer.portal(
                    rx.drawer.content(
                        rx.vstack(
                            rx.box(
                                rx.drawer.close(rx.icon("x", size=30)),
                                width="100%",
                            ),
                            sidebar_items(),
                            spacing="5",
                            width="100%",
                        ),
                        top="auto",
                        right="auto",
                        height="100%",
                        width="20em",
                        padding="1.5em",
                        bg="#2d2c2f",
                    ),
                    width="100%",
                ),
                direction="left",
            ),
            padding="1em",
        ),
    )


def assistant_page() -> rx.Component:
    """Assistant Studio page with AI Assistant Builder button and upload."""

    # Status banner: show progress or success messages
    status_banner = rx.cond(
        LayoutState.creating_assistant,
        rx.el.div(
            "Creating assistant based on your knowledge base...",
            class_name=(
                "mb-4 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 "
                "text-sm text-blue-800"
            ),
        ),
        rx.cond(
            LayoutState.assistant_created,
            rx.el.div(
                "Assistant created successfully! Your bot is now ready to use.",
                class_name=(
                    "mb-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 "
                    "text-sm text-emerald-800"
                ),
            ),
            rx.el.div(),
        ),
    )

    builder_button = rx.el.button(
        "AI Assistant Builder",
        on_click=LayoutState.open_assistant_upload,
        class_name=(
            "w-full py-3 text-white text-lg font-semibold "
            "bg-emerald-600 rounded-full hover:bg-emerald-700 transition-colors"
        ),
    )

    # Form that appears after clicking the builder button
    form_section = rx.cond(
        LayoutState.show_assistant_upload,
        rx.el.form(
            rx.el.div(
                rx.el.label(
                    "Assistant Name",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                    html_for="assistant_name",
                ),
                rx.el.input(
                    name="assistant_name",
                    id="assistant_name",
                    placeholder="Enter assistant name",
                    class_name=(
                        "w-full rounded-xl border border-gray-300 px-3 py-2 "
                        "focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    ),
                    on_change=LayoutState.set_assistant_name,
                    required=True,
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Assistant Description",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                    html_for="assistant_description",
                ),
                rx.el.textarea(
                    name="assistant_description",
                    id="assistant_description",
                    placeholder="Describe what this assistant should do",
                    class_name=(
                        "w-full rounded-xl border border-gray-300 px-3 py-2 min-h-[6rem] "
                        "focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    ),
                    on_change=LayoutState.set_assistant_description,
                    required=True,
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Knowledge Base",
                    class_name="block text-sm font-medium text-gray-700 mb-2",
                ),
                rx.upload.root(
                    rx.box(
                        rx.icon(
                            tag="cloud_upload",
                            style={
                                "width": "3rem",
                                "height": "3rem",
                                "color": "#2563eb",
                                "marginBottom": "0.75rem",
                            },
                        ),
                        rx.hstack(
                            rx.text(
                                "Click to upload",
                                style={
                                    "fontWeight": "bold",
                                    "color": "#1d4ed8",
                                },
                            ),
                            " or drag and drop",
                            style={
                                "fontSize": "0.875rem",
                                "color": "#4b5563",
                            },
                        ),
                        rx.text(
                            "SVG, PNG, JPG or GIF (MAX. 5MB)",
                            style={
                                "fontSize": "0.75rem",
                                "color": "#6b7280",
                                "marginTop": "0.25rem",
                            },
                        ),
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "padding": "1.5rem",
                            "textAlign": "center",
                        },
                    ),
                    id="assistant_upload",
                    style={
                        "maxWidth": "100%",
                        "height": "16rem",
                        "borderWidth": "2px",
                        "borderStyle": "dashed",
                        "borderColor": "#60a5fa",
                        "borderRadius": "0.75rem",
                        "cursor": "pointer",
                        "transitionProperty": "background-color",
                        "transitionDuration": "0.2s",
                        "transitionTimingFunction": "ease-in-out",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "boxShadow": "0 1px 2px rgba(0, 0, 0, 0.05)",
                    },
                ),
                # Show selected file names below the drop area
                rx.el.ul(
                    rx.foreach(
                        rx.selected_files("assistant_upload"),
                        lambda name: rx.el.li(
                            name,
                            class_name="text-sm text-gray-700",
                        ),
                    ),
                    class_name="mt-2 list-disc list-inside",
                ),
                class_name="mb-6",
            ),
            rx.el.button(
                "Create Assistant",
                type="button",
                on_click=LayoutState.submit_assistant(
                    rx.upload_files(upload_id="assistant_upload")
                ),
                class_name=(
                    "inline-flex items-center justify-center px-4 py-2 rounded-full "
                    "bg-emerald-600 text-white font-semibold hover:bg-emerald-700 transition-colors"
                ),
            ),
            class_name="bg-white rounded-3xl shadow-sm border p-6 flex flex-col",
        ),
        rx.el.div(),
    )

    # Alert dialog for assistant creation progress and success messages
    assistant_dialog = rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Assistant Creation"),
            rx.alert_dialog.description(
                LayoutState.assistant_dialog_message,
            ),
            rx.alert_dialog.action(
                rx.button(
                    "OK",
                    on_click=LayoutState.close_assistant_dialog,
                )
            ),
        ),
        open=LayoutState.assistant_dialog_open,
    )

    # Main content: builder card left at top, form centered below, with status banner
    content = rx.el.div(
        status_banner,
        # Left-aligned builder button card
        rx.el.div(
            builder_button,
            class_name="bg-white rounded-3xl shadow-sm border max-w-xs w-full p-6 mb-10",
        ),
        # Centered form section
        rx.el.div(
            form_section,
            class_name="max-w-2xl w-full mx-auto",
        ),
        assistant_dialog,
        class_name="w-full mt-16 h-screen flex flex-col bg-gray-50 px-8",
    )

    # Wrap with the same sidebar layout as the dashboard
    return rx.hstack(sidebar(), rx.box(content, width="100%"))


def index() -> rx.Component:
    """Dashboard page with the main chat interface."""
    return rx.hstack(sidebar(), rx.box(chat_interface(), width="100%"))


app = rx.App(theme=rx.theme(appearance="light"))
app.add_page(index, route="/", title="Dashboard")
app.add_page(assistant_page, route="/assistant-studio", title="Assistant Studio")
