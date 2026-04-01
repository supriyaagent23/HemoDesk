import flet as ft
from data.repository import get_stats, get_all_stock
from ui.components import section, stat_card, BLOOD_COLORS

def build_dashboard_view(page: ft.Page):
    stats = get_stats()
    stock = get_all_stock()

    stat_cards = ft.Row([
        stat_card("Total Donors", stats["total_donors"], "#1565C0"),
        stat_card("Total Donations", stats["total_donations"], "#2E7D32"),
        stat_card("Pending Requests", stats["pending_requests"], "#F57C00", warning=True),
        stat_card("Low Stock Types", stats["low_stock"], "#C62828", warning=True),
    ], wrap=True, spacing=12)

    stock_row = ft.Row(wrap=True, spacing=10)
    for s in stock:
        color = BLOOD_COLORS.get(s.blood_type, "#888888")
        is_low = s.units < 5
        stock_row.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(s.blood_type, size=18, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Text(f"{s.units} units", size=13, color="#ffffff"),
                    ft.Text("LOW" if is_low else "OK", size=11,
                            color="#ffcccc" if is_low else "#ccffcc")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                width=90, padding=14,
                bgcolor=color,
                border_radius=10,
                border=ft.border.all(3, "#ffcccc") if is_low else None
            )
        )

    return ft.Column([
        ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(height=10, color="transparent"),
        section("Overview", stat_cards),
        section("Blood Stock Overview", stock_row),
    ], scroll=ft.ScrollMode.AUTO, expand=True)