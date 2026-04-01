import flet as ft

BLOOD_TYPES = ["All", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
BLOOD_TYPES_NO_ALL = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
URGENCY_LEVELS = ["Normal", "Urgent", "Critical"]
STATUS_OPTIONS = ["Pending", "Fulfilled", "Rejected"]

BLOOD_COLORS = {
    "A+": "#C62828", "A-": "#E53935",
    "B+": "#1565C0", "B-": "#1E88E5",
    "AB+": "#6A1B9A", "AB-": "#8E24AA",
    "O+": "#2E7D32", "O-": "#43A047",
}

def section(title, content):
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(height=8, color="#eeeeee"),
            content
        ]),
        padding=16,
        margin=ft.margin.only(bottom=14),
        bgcolor="#f9f9f9",
        border_radius=10,
        border=ft.border.all(1, "#e0e0e0")
    )

def stat_card(label, value, color="#1565C0", warning=False):
    return ft.Container(
        content=ft.Column([
            ft.Text(str(value), size=30, weight=ft.FontWeight.BOLD,
                    color="#cc0000" if warning and int(value) > 0 else color),
            ft.Text(label, size=12, color="#666666")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        padding=20,
        width=150,
        bgcolor="#ffffff",
        border_radius=10,
        border=ft.border.all(2, "#cc0000" if warning and int(value) > 0 else "#e0e0e0"),
    )

def blood_badge(blood_type):
    color = BLOOD_COLORS.get(blood_type, "#888888")
    return ft.Container(
        content=ft.Text(blood_type, size=12, color="#ffffff", weight=ft.FontWeight.BOLD),
        bgcolor=color,
        border_radius=6,
        padding=ft.padding.symmetric(4, 10)
    )

def status_badge(status):
    colors = {"Pending": "#F57C00", "Fulfilled": "#2E7D32", "Rejected": "#C62828"}
    color = colors.get(status, "#888888")
    return ft.Container(
        content=ft.Text(status, size=11, color="#ffffff"),
        bgcolor=color,
        border_radius=6,
        padding=ft.padding.symmetric(3, 8)
    )

def urgency_badge(urgency):
    colors = {"Normal": "#1565C0", "Urgent": "#F57C00", "Critical": "#C62828"}
    color = colors.get(urgency, "#888888")
    return ft.Container(
        content=ft.Text(urgency, size=11, color="#ffffff"),
        bgcolor=color,
        border_radius=6,
        padding=ft.padding.symmetric(3, 8)
    )