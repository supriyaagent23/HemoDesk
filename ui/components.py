import flet as ft

# Blood type lists
BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
BLOOD_TYPES_NO_ALL = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
BLOOD_TYPES_WITH_UNKNOWN = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
ALL_BLOOD_TYPES = ["All"] + BLOOD_TYPES_NO_ALL
URGENCY_LEVELS = ["Critical", "High", "Normal", "Low"]
STATUS_OPTIONS = ["Pending", "Fulfilled", "Rejected"]

BLOOD_COLORS = {
    "A+": "#D32F2F", "A-": "#C62828",
    "B+": "#1565C0", "B-": "#0D47A1",
    "AB+": "#6A1B9A", "AB-": "#4A148C",
    "O+": "#2E7D32", "O-": "#1B5E20",
    "Unknown": "#757575",
}


def blood_badge(blood_type: str) -> ft.Container:
    color = BLOOD_COLORS.get(blood_type, "#757575")
    return ft.Container(
        content=ft.Text(blood_type, size=12, weight=ft.FontWeight.BOLD, color="white"),
        bgcolor=color,
        border_radius=8,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
    )


def urgency_badge(urgency: str) -> ft.Container:
    colors = {"Critical": "#C62828", "High": "#E65100", "Normal": "#1565C0", "Low": "#2E7D32"}
    color = colors.get(urgency, "#888888")
    return ft.Container(
        content=ft.Text(urgency, size=11, color="white"),
        bgcolor=color,
        border_radius=6,
        padding=ft.padding.symmetric(horizontal=8, vertical=2),
    )


def status_badge(status: str) -> ft.Container:
    colors = {"Pending": "#F57C00", "Fulfilled": "#2E7D32", "Rejected": "#C62828"}
    color = colors.get(status, "#888888")
    return ft.Container(
        content=ft.Text(status, size=11, color="white"),
        bgcolor=color,
        border_radius=6,
        padding=ft.padding.symmetric(horizontal=8, vertical=2),
    )


def section(title: str, content: ft.Control) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(height=3),
            content,
        ], spacing=8),
        padding=12,
        bgcolor="white",
        border_radius=10,
        border=ft.border.all(1, "#E0E0E0"),
    )


def stat_card(label: str, value, color: str, warning: bool = False) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Text(str(value), size=20, weight=ft.FontWeight.BOLD, color=color),
            ft.Text(label, size=10, color="#666666", text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
        padding=10,
        bgcolor="#FFEBEE" if warning else "white",
        border_radius=8,
        border=ft.border.all(1.5, color if warning else "#E0E0E0"),
        expand=True,
    )


def show_thank_you_dialog(page: ft.Page, donor_name: str, message: str = None):
    """Show a thank you dialog to the donor"""
    dialog = ft.AlertDialog(
        title=ft.Text("🎉 Thank You!", size=20, color="#2E7D32"),
        content=ft.Column([
            ft.Icon(ft.Icons.FAVORITE, size=50, color="#E91E63"),
            ft.Text(f"Dear {donor_name},", size=14, weight=ft.FontWeight.BOLD),
            ft.Text(message or "Thank you for your generous blood donation! Your contribution will help save lives. You are a true hero! 🦸‍♂️🦸‍♀️", size=12),
            ft.Text("❤️ HemoDesk Team", size=11, italic=True),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        actions=[
            ft.TextButton("Close", on_click=lambda e: page.close_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    page.dialog = dialog
    dialog.open = True
    page.update()