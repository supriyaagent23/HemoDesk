import flet as ft
from ui.dashboard_view import build_dashboard_view
from ui.donors_view import build_donors_view
from ui.stock_view import build_stock_view
from ui.requests_view import build_requests_view
from ui.donations_view import build_donations_view
from ui.blood_check_view import build_blood_check_view
from ui.eligibility_view import build_eligibility_view


def build_home_view(page: ft.Page):
    # Create content area
    content_area = ft.Container(expand=True, padding=20, bgcolor="#f5f5f5")
    
    # Store views in dictionary
    views = {}
    
    # Create navigation rail
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=120,
        min_extended_width=150,
        bgcolor="#ffffff",
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD, label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PEOPLE, label="Donors"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.WATER_DROP, label="Stock"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ASSIGNMENT, label="Requests"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.FAVORITE, label="Donations"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.BLOODTYPE, label="Blood Check"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.HEALTH_AND_SAFETY, label="Eligibility"
            ),
        ],
    )
    
    def load_view(e):
        index = e.control.selected_index
        
        if index == 0:
            if "dashboard" not in views:
                views["dashboard"] = build_dashboard_view(page, lambda idx: navigate_to(idx))
            content_area.content = views["dashboard"]
        elif index == 1:
            if "donors" not in views:
                views["donors"] = build_donors_view(page)
            content_area.content = views["donors"]
        elif index == 2:
            if "stock" not in views:
                views["stock"] = build_stock_view(page)
            content_area.content = views["stock"]
        elif index == 3:
            if "requests" not in views:
                views["requests"] = build_requests_view(page)
            content_area.content = views["requests"]
        elif index == 4:
            if "donations" not in views:
                views["donations"] = build_donations_view(page)
            content_area.content = views["donations"]
        elif index == 5:
            if "blood_check" not in views:
                views["blood_check"] = build_blood_check_view(page)
            content_area.content = views["blood_check"]
        elif index == 6:
            if "eligibility" not in views:
                views["eligibility"] = build_eligibility_view(page)
            content_area.content = views["eligibility"]
        
        page.update()
    
    def navigate_to(index):
        nav_rail.selected_index = index
        # Manually trigger load_view
        class FakeEvent:
            def __init__(self, idx):
                self.control = type('obj', (object,), {'selected_index': idx})()
        load_view(FakeEvent(index))
    
    # Set the on_change handler
    nav_rail.on_change = load_view
    
    # Load dashboard initially
    views["dashboard"] = build_dashboard_view(page, lambda idx: navigate_to(idx))
    content_area.content = views["dashboard"]
    
    # Main layout
    return ft.Row(
        [
            nav_rail,
            ft.VerticalDivider(width=1, color="#E0E0E0"),
            content_area,
        ],
        expand=True,
        spacing=0,
    )