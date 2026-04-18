import flet as ft

# Blood type lists
BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
BLOOD_TYPES_WITH_UNKNOWN = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
BLOOD_TYPES_NO_ALL = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
ALL_BLOOD_TYPES = ["All"] + BLOOD_TYPES

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
        content=ft.Text(blood_type, size=12, weight=ft.FontWeight.BOLD, color="#ffffff"),
        bgcolor=color,
        border_radius=6,
        padding=ft.Padding.symmetric(vertical=3, horizontal=8),
    )

def urgency_badge(urgency: str) -> ft.Container:
    colors = {
        "Critical": "#C62828",
        "High": "#E65100",
        "Normal": "#1565C0",
        "Low": "#2E7D32",
    }
    color = colors.get(urgency, "#888888")
    return ft.Container(
        content=ft.Text(urgency, size=11, color="#ffffff"),
        bgcolor=color,
        border_radius=6,
        padding=ft.Padding.symmetric(vertical=2, horizontal=7),
    )

def status_badge(status: str) -> ft.Container:
    colors = {
        "Pending": "#F57C00",
        "Fulfilled": "#2E7D32",
        "Rejected": "#C62828",
    }
    color = colors.get(status, "#888888")
    return ft.Container(
        content=ft.Text(status, size=11, color="#ffffff"),
        bgcolor=color,
        border_radius=6,
        padding=ft.Padding.symmetric(vertical=2, horizontal=7),
    )

def section(title: str, content: ft.Control) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(height=4),
            content,
        ], spacing=8),
        padding=14,
        bgcolor="#ffffff",
        border_radius=10,
        border=ft.Border.all(1, "#E0E0E0"),
        margin=ft.Margin.only(bottom=12),
    )

def stat_card(label: str, value, color: str, warning: bool = False) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Text(str(value), size=28, weight=ft.FontWeight.BOLD, color=color),
            ft.Text(label, size=12, color="#555555"),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        padding=16,
        bgcolor="#FFEBEE" if warning else "#ffffff",
        border_radius=10,
        border=ft.Border.all(2, color if warning else "#E0E0E0"),
        expand=True,
        alignment=ft.Alignment(0, 0),
    )