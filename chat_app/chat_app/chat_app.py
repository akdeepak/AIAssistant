import reflex as rx
from chat_app.components.chat_interface import chat_interface
from chat_app.components.preset_cards import preset_cards
from chat_app.states.layout_state import LayoutState


def sidebar_item(text: str, icon: str, href: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon, color="#bfc9d1"),
            rx.text(text, size="4", color="#bfc9d1"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.75rem",
            align="center",
            style={
                "_hover": {"background": "#353436", "color": "#fff"},
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
                height="100vh",
                width="16em",
                position="sticky",
                top="0",
            ),
        ),
        rx.mobile_and_tablet(
            rx.drawer.root(
                rx.drawer.trigger(rx.icon("align-justify", size=30)),
                rx.drawer.overlay(z_index="5"),
                rx.drawer.portal(
                    rx.drawer.content(
                        rx.vstack(
                            rx.box(rx.drawer.close(rx.icon("x", size=30)), width="100%"),
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
    """Redesigned Assistant Studio page — two-column hero + centred form."""

    # ── Status banner ──────────────────────────────────────────────
    status_banner = rx.cond(
        LayoutState.creating_assistant,
        rx.el.div(
            rx.el.span("⏳", class_name="mr-2"),
            "Creating assistant based on your knowledge base…",
            class_name=(
                "mb-6 flex items-center rounded-xl border border-blue-200 "
                "bg-blue-50 px-4 py-3 text-sm text-blue-800"
            ),
        ),
        rx.cond(
            LayoutState.assistant_created,
            rx.el.div(
                rx.el.span("✅", class_name="mr-2"),
                "Assistant created successfully! Your bot is ready to use.",
                class_name=(
                    "mb-6 flex items-center rounded-xl border border-emerald-200 "
                    "bg-emerald-50 px-4 py-3 text-sm text-emerald-800"
                ),
            ),
            rx.el.div(),
        ),
    )

    # ── Left hero panel ────────────────────────────────────────────
    hero_panel = rx.el.div(
        # Decorative gradient blob
        rx.el.div(
            class_name=(
                "absolute -top-16 -left-16 w-64 h-64 rounded-full "
                "bg-sky-400 opacity-20 blur-3xl pointer-events-none"
            ),
        ),
        rx.el.div(
            class_name=(
                "absolute bottom-0 right-0 w-48 h-48 rounded-full "
                "bg-blue-600 opacity-10 blur-2xl pointer-events-none"
            ),
        ),
        # Icon badge
        rx.el.div(
            rx.el.span("🤖", class_name="text-3xl"),
            class_name=(
                "relative z-10 mb-5 flex h-14 w-14 items-center justify-center "
                "rounded-2xl bg-white/10 backdrop-blur-sm border border-white/20"
            ),
        ),
        # Headline
        rx.el.h2(
            "Build your AI Assistant",
            class_name="relative z-10 text-2xl font-bold text-white mb-3 leading-tight",
        ),
        rx.el.p(
            "Configure a smart assistant powered by your own knowledge base. "
            "Upload documents, set a persona, and deploy in minutes.",
            class_name="relative z-10 text-blue-100 text-sm leading-relaxed mb-6",
        ),
        # Feature bullets
        rx.el.ul(
            rx.el.li(
                rx.el.span("✦", class_name="mr-2 text-sky-300"),
                "Custom knowledge base",
                class_name="flex items-center text-sm text-white/80 mb-3",
            ),
            rx.el.li(
                rx.el.span("✦", class_name="mr-2 text-sky-300"),
                "Instant deployment",
                class_name="flex items-center text-sm text-white/80 mb-3",
            ),
            rx.el.li(
                rx.el.span("✦", class_name="mr-2 text-sky-300"),
                "No code required",
                class_name="flex items-center text-sm text-white/80",
            ),
            class_name="relative z-10 list-none",
        ),
        class_name=(
            "relative overflow-hidden rounded-2xl bg-gradient-to-br "
            "from-[#1B2A4A] to-[#2E5C8A] p-7 flex flex-col justify-center h-full"
        ),
    )

    # ── Form panel ─────────────────────────────────────────────────
    form_panel = rx.cond(
        LayoutState.show_assistant_upload,
        rx.el.form(
            # Assistant Name
            rx.el.div(
                rx.el.label(
                    "Assistant Name",
                    class_name="block text-sm font-semibold text-gray-700 mb-1.5",
                    html_for="assistant_name",
                ),
                rx.el.input(
                    name="assistant_name",
                    id="assistant_name",
                    placeholder="e.g. Support Bot, Sales Assistant…",
                    class_name=(
                        "w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm "
                        "text-gray-900 placeholder-gray-400 "
                        "focus:outline-none focus:ring-2 focus:ring-[#4A7AB5] "
                        "focus:border-[#4A7AB5] focus:bg-white transition"
                    ),
                    on_change=LayoutState.set_assistant_name,
                    required=True,
                ),
                class_name="mb-5",
            ),
            # Assistant Description
            rx.el.div(
                rx.el.label(
                    "Description",
                    class_name="block text-sm font-semibold text-gray-700 mb-1.5",
                    html_for="assistant_description",
                ),
                rx.el.textarea(
                    name="assistant_description",
                    id="assistant_description",
                    placeholder="Describe the assistant's role, tone, and scope…",
                    class_name=(
                        "w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm "
                        "text-gray-900 placeholder-gray-400 min-h-[96px] resize-none "
                        "focus:outline-none focus:ring-2 focus:ring-[#4A7AB5] "
                        "focus:border-[#4A7AB5] focus:bg-white transition"
                    ),
                    on_change=LayoutState.set_assistant_description,
                    required=True,
                ),
                class_name="mb-5",
            ),
            # Two-column row: Avatar + Knowledge Base
            rx.el.div(
                # Avatar upload
                rx.el.div(
                    rx.el.label(
                        "Avatar Image",
                        class_name="block text-sm font-semibold text-gray-700 mb-1.5",
                    ),
                    rx.upload(
                        rx.el.div(
                            rx.el.div(
                                rx.icon("image-plus", size=22, color="#3B6EA5"),
                                class_name="mb-2",
                            ),
                            rx.el.p(
                                rx.el.span(
                                    "Click to upload",
                                    class_name="font-semibold text-[#3B6EA5]",
                                ),
                                " or drag & drop",
                                class_name="text-xs text-gray-500",
                            ),
                            rx.el.div(
                                rx.el.span("PNG", class_name="px-1.5 py-0.5 bg-gray-100 rounded text-[10px] text-gray-500 font-medium"),
                                rx.el.span("JPG", class_name="px-1.5 py-0.5 bg-gray-100 rounded text-[10px] text-gray-500 font-medium"),
                                rx.el.span("GIF", class_name="px-1.5 py-0.5 bg-gray-100 rounded text-[10px] text-gray-500 font-medium"),
                                rx.el.span("WebP", class_name="px-1.5 py-0.5 bg-gray-100 rounded text-[10px] text-gray-500 font-medium"),
                                class_name="flex gap-1 flex-wrap justify-center mt-1.5",
                            ),
                            class_name="flex flex-col items-center justify-center h-full",
                        ),
                        id="assistant_image",
                        max_files=1,
                        accept={
                            "image/png": [".png"],
                            "image/jpeg": [".jpg", ".jpeg"],
                            "image/gif": [".gif"],
                            "image/webp": [".webp"],
                        },
                        on_drop=LayoutState.handle_image_upload(
                            rx.upload_files(upload_id="assistant_image")
                        ),
                        class_name=(
                            "w-full h-[90px] rounded-xl border-2 border-dashed "
                            "border-blue-200 bg-blue-50/40 hover:border-[#4A7AB5] "
                            "hover:bg-blue-50 cursor-pointer transition "
                            "flex items-center justify-center"
                        ),
                    ),
                    rx.el.ul(
                        rx.foreach(
                            rx.selected_files("assistant_image"),
                            lambda name: rx.el.li(
                                rx.el.span("📎 ", class_name="mr-1"),
                                name,
                                class_name="text-xs text-blue-700 truncate",
                            ),
                        ),
                        class_name="mt-1 list-none",
                    ),
                    class_name="flex-1",
                ),
                # Knowledge base upload
                rx.el.div(
                    rx.el.label(
                        "Knowledge Base",
                        class_name="block text-sm font-semibold text-gray-700 mb-1.5",
                    ),
                    rx.upload.root(
                        rx.el.div(
                            rx.el.div(
                                rx.icon("cloud-upload", size=22, color="#2563eb"),
                                class_name="mb-2",
                            ),
                            rx.el.p(
                                rx.el.span(
                                    "Click to upload",
                                    class_name="font-semibold text-[#3B6EA5]",
                                ),
                                " or drag & drop",
                                class_name="text-xs text-gray-500",
                            ),
                            rx.el.div(
                                rx.el.span("PDF", class_name="px-1.5 py-0.5 bg-gray-100 rounded text-[10px] text-gray-500 font-medium"),
                                rx.el.span("DOCX", class_name="px-1.5 py-0.5 bg-gray-100 rounded text-[10px] text-gray-500 font-medium"),
                                rx.el.span("TXT", class_name="px-1.5 py-0.5 bg-gray-100 rounded text-[10px] text-gray-500 font-medium"),
                                rx.el.span("CSV", class_name="px-1.5 py-0.5 bg-gray-100 rounded text-[10px] text-gray-500 font-medium"),
                                class_name="flex gap-1 flex-wrap justify-center mt-1.5",
                            ),
                            class_name="flex flex-col items-center justify-center h-full",
                        ),
                        id="assistant_upload",
                        class_name=(
                            "w-full h-[90px] rounded-xl border-2 border-dashed "
                            "border-blue-200 bg-blue-50/40 hover:border-blue-400 "
                            "hover:bg-blue-50 cursor-pointer transition "
                            "flex items-center justify-center"
                        ),
                    ),
                    rx.el.ul(
                        rx.foreach(
                            rx.selected_files("assistant_upload"),
                            lambda name: rx.el.li(
                                rx.el.span("📄 ", class_name="mr-1"),
                                name,
                                class_name="text-xs text-blue-700 truncate",
                            ),
                        ),
                        class_name="mt-1 list-none",
                    ),
                    class_name="flex-1",
                ),
                class_name="flex gap-4 mb-5",
            ),
            # Submit button + progress bar (pushed to bottom via mt-auto)
            rx.el.div(
                rx.cond(
                    LayoutState.creating_assistant,
                    # ── Progress bar overlay ──
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.icon("loader-circle", size=16, class_name="animate-spin text-[#2E5C8A]"),
                                rx.el.p(
                                    LayoutState.creation_step,
                                    class_name="text-sm font-medium text-gray-700",
                                ),
                                class_name="flex items-center gap-2",
                            ),
                            rx.el.p(
                                LayoutState.creation_progress.to(str) + "%",
                                class_name="text-sm font-semibold text-[#2E5C8A]",
                            ),
                            class_name="flex items-center justify-between mb-2",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="h-full bg-gradient-to-r from-[#2E5C8A] to-[#4A7AB5] rounded-full transition-all duration-500 ease-out",
                                style={"width": LayoutState.creation_progress.to(str) + "%"},
                            ),
                            class_name="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    class_name=rx.cond(
                                        LayoutState.creation_progress >= 15,
                                        "size-2.5 rounded-full bg-[#2E5C8A]",
                                        "size-2.5 rounded-full bg-gray-300",
                                    ),
                                ),
                                rx.el.span("Validate", class_name="text-[10px] text-gray-400 mt-1"),
                                class_name="flex flex-col items-center",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    class_name=rx.cond(
                                        LayoutState.creation_progress >= 35,
                                        "size-2.5 rounded-full bg-[#2E5C8A]",
                                        "size-2.5 rounded-full bg-gray-300",
                                    ),
                                ),
                                rx.el.span("Upload", class_name="text-[10px] text-gray-400 mt-1"),
                                class_name="flex flex-col items-center",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    class_name=rx.cond(
                                        LayoutState.creation_progress >= 70,
                                        "size-2.5 rounded-full bg-[#2E5C8A]",
                                        "size-2.5 rounded-full bg-gray-300",
                                    ),
                                ),
                                rx.el.span("Index", class_name="text-[10px] text-gray-400 mt-1"),
                                class_name="flex flex-col items-center",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    class_name=rx.cond(
                                        LayoutState.creation_progress >= 100,
                                        "size-2.5 rounded-full bg-[#2E5C8A]",
                                        "size-2.5 rounded-full bg-gray-300",
                                    ),
                                ),
                                rx.el.span("Done", class_name="text-[10px] text-gray-400 mt-1"),
                                class_name="flex flex-col items-center",
                            ),
                            class_name="flex justify-between mt-3 px-1",
                        ),
                        class_name="w-full py-2",
                    ),
                    # ── Normal submit button ──
                    rx.el.button(
                        rx.el.span("✦", class_name="mr-2 opacity-70"),
                        "Create Assistant",
                        type="button",
                        on_click=LayoutState.submit_assistant(
                            rx.upload_files(upload_id="assistant_upload")
                        ),
                        class_name=(
                            "w-full py-3 rounded-xl bg-[#2E5C8A] text-white font-semibold "
                            "text-sm hover:bg-[#1B2A4A] active:scale-[0.98] transition-all "
                            "shadow-sm shadow-blue-200 flex items-center justify-center"
                        ),
                    ),
                ),
                class_name="mt-auto",
            ),
            class_name="flex flex-col flex-1",
        ),
        # Placeholder when form is hidden
        rx.el.div(
            rx.el.p(
                'Click "AI Assistant Builder" to get started.',
                class_name="text-gray-400 text-sm",
            ),
            class_name="flex items-center justify-center h-full min-h-[200px]",
        ),
    )

    # ── Alert dialog ───────────────────────────────────────────────
    assistant_dialog = rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Assistant Creation"),
            rx.alert_dialog.description(LayoutState.assistant_dialog_message),
            rx.alert_dialog.action(
                rx.button("OK", on_click=LayoutState.close_assistant_dialog)
            ),
        ),
        open=LayoutState.assistant_dialog_open,
    )

    # ── Page layout ────────────────────────────────────────────────
    content = rx.el.div(
        # Page heading row
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Assistant Studio",
                    class_name="text-xl font-bold text-gray-900",
                ),
                rx.el.p(
                    "Create and manage your AI assistants",
                    class_name="text-sm text-gray-500 mt-0.5",
                ),
            ),
            rx.el.button(
                rx.icon("plus", size=16, class_name="mr-2"),
                "AI Assistant Builder",
                on_click=LayoutState.open_assistant_upload,
                class_name=(
                    "inline-flex items-center px-5 py-2.5 rounded-xl "
                    "bg-[#2E5C8A] text-white text-sm font-semibold "
                    "hover:bg-[#1B2A4A] transition-colors shadow-sm"
                ),
            ),
            class_name="flex items-center justify-between mb-8",
        ),
        status_banner,
        # Two-column card
        rx.cond(
            LayoutState.show_assistant_upload,
            rx.el.div(
                # Left: hero
                rx.el.div(
                    hero_panel,
                    class_name="w-full lg:w-[38%] flex-shrink-0",
                ),
                # Right: form card
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Configure your assistant",
                            class_name="text-base font-semibold text-gray-800 mb-1",
                        ),
                        rx.el.p(
                            "Fill in the details below to set up your new assistant.",
                            class_name="text-sm text-gray-400 mb-4",
                        ),
                        form_panel,
                        class_name="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 h-full flex flex-col",
                    ),
                    class_name="flex-1",
                ),
                assistant_dialog,
                class_name="flex flex-col lg:flex-row gap-6 items-stretch flex-1 min-h-0",
            ),
            rx.el.div(),
        ),
        class_name="w-full p-6 h-screen bg-gray-50 overflow-hidden flex flex-col",
    )

    return rx.hstack(sidebar(), rx.box(content, width="100%"))


def index() -> rx.Component:
    return rx.hstack(sidebar(), rx.box(preset_cards(), width="100%"))


app = rx.App(theme=rx.theme(appearance="light"))
app.add_page(index, route="/", title="Dashboard")


def chat_page() -> rx.Component:
    return rx.hstack(sidebar(), rx.box(chat_interface(), width="100%"))


app.add_page(chat_page, route="/chat", title="Chat")
app.add_page(
    assistant_page,
    route="/assistant-studio",
    title="Assistant Studio",
    on_load=LayoutState.reset_studio,
)
