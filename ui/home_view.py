import flet as ft
from ui.dashboard_view import build_dashboard_view
from ui.donors_view import build_donors_view
from ui.stock_view import build_stock_view
from ui.requests_view import build_requests_view
from ui.lab_tests_view import build_lab_tests_view
# REMOVED: from ui.eligibility_view import build_eligibility_view


def build_home_view(page: ft.Page):
    # Main content area
    content_area = ft.Column(spacing=0, expand=True)
    
    # Store views cache
    views = {}
    
    nav_items = [
        {"icon": ft.Icons.DASHBOARD, "label": "Dashboard", "color": "#1565C0", "index": 0},
        {"icon": ft.Icons.PEOPLE, "label": "Donors", "color": "#2E7D32", "index": 1},
        {"icon": ft.Icons.OPACITY, "label": "Blood Stock", "color": "#C62828", "index": 2},
        {"icon": ft.Icons.ASSIGNMENT, "label": "Requests", "color": "#F57C00", "index": 3},
        {"icon": ft.Icons.SCIENCE, "label": "Test & Donate", "color": "#6A1B9A", "index": 4},
        
    ]
    

    current_index = [0]
    
    # Function to create navigation items
    def create_nav_item(item):
        def on_click(e):
            current_index[0] = item["index"]
            load_view(item["index"])
            page.update()
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(item["icon"], color=item["color"], size=20),
                ft.Text(item["label"], size=13, weight=ft.FontWeight.W_500),
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            border_radius=8,
            ink=True,
            on_click=on_click,
        )
    

    def load_view(index):
        # Clear content area
        content_area.controls.clear()
        
        if index == 0:
            if "dashboard" not in views:
                views["dashboard"] = build_dashboard_view(page, lambda idx: load_view(idx))
            content_area.controls.append(views["dashboard"])
        elif index == 1:
            if "donors" not in views:
                views["donors"] = build_donors_view(page)
            content_area.controls.append(views["donors"])
        elif index == 2:
            if "stock" not in views:
                views["stock"] = build_stock_view(page)
            content_area.controls.append(views["stock"])
        elif index == 3:
            if "requests" not in views:
                views["requests"] = build_requests_view(page)
            content_area.controls.append(views["requests"])
        elif index == 4:
            if "lab_tests" not in views:
                views["lab_tests"] = build_lab_tests_view(page)
            content_area.controls.append(views["lab_tests"])
        # REMOVED: Eligibility case (index 5)
        
        page.update()
    

    nav_sidebar = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.BLOODTYPE, size=35, color="#C62828"),
                    ft.Text("HemoDesk", size=18, weight=ft.FontWeight.BOLD, color="#C62828"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=15,
            ),
            ft.Divider(height=1),
            ft.Column([
                create_nav_item(item) for item in nav_items
            ], spacing=3),
        ], spacing=5),
        width=200,
        bgcolor="#ffffff",
        border_radius=ft.BorderRadius.only(top_right=10, bottom_right=10),
    )
    

    load_view(0)
    
    # Main layout
    main_layout = ft.Row(
        controls=[
            nav_sidebar,
            ft.VerticalDivider(width=1, color="#E0E0E0"),
            ft.Container(
                content=content_area,
                expand=True,
                padding=15,
                bgcolor="#F8F9FA",
            ),
        ],
        expand=True,
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
    
    return main_layout