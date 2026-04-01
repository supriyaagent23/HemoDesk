import flet as ft
from ui.dashboard_view import build_dashboard_view
from ui.donors_view import build_donors_view
from ui.stock_view import build_stock_view
from ui.requests_view import build_requests_view
from ui.donations_view import build_donations_view

def build_home_view(page: ft.Page):
    content_area = ft.Container(expand=True, padding=20)

    views = [None, None, None, None, None]

    def load_view(index):
        if index == 0:
            views[0] = build_dashboard_view(page)
        elif index == 1:
            views[1] = build_donors_view(page)
        elif index == 2:
            views[2] = build_stock_view(page)
        elif index == 3:
            views[3] = build_requests_view(page)
        elif index == 4:
            views[4] = build_donations_view(page)
        content_area.content = views[index]
        page.update()

    def on_nav_change(e):
        load_view(e.control.selected_index)

    nav = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=110,
        bgcolor="#f5f5f5",
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE, label="Donors"),
            ft.NavigationRailDestination(icon=ft.Icons.WATER_DROP, label="Stock"),
            ft.NavigationRailDestination(icon=ft.Icons.ASSIGNMENT, label="Requests"),
            ft.NavigationRailDestination(icon=ft.Icons.FAVORITE, label="Donations"),
        ],
        on_change=on_nav_change
    )

    load_view(0)

    return ft.Row([
        nav,
        ft.VerticalDivider(width=1),
        content_area
    ], expand=True)