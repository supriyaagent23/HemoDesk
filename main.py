import flet as ft
from data.db import init_db
from ui.home_view import build_home_view

def main(page: ft.Page):
    page.title = "HemoDesk - Blood Bank Management System"
    page.window_width = 1300
    page.window_height = 800
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#f5f5f5"

    # Initialize database
    init_db()
    
    # Build the home view
    home_view = build_home_view(page)
    
    # Clear page and add home view
    page.controls.clear()
    page.add(home_view)
    
    # Force update
    page.update()

ft.app(target=main)