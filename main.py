import flet as ft
from data.db import init_db
from ui.home_view import build_home_view

def main(page: ft.Page):
    page.title = "HemoDesk - Blood Bank Management System"
    page.window_width = 1400
    page.window_height = 900
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#f5f5f5"
    page.theme_mode = ft.ThemeMode.LIGHT

    init_db()
    
    home_view = build_home_view(page)
    page.add(home_view)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)