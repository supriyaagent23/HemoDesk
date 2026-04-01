import flet as ft
from data.db import init_db
from ui.home_view import build_home_view

def main(page: ft.Page):
    page.title = "HemoDesk - Blood Bank Management"
    page.window_width = 1100
    page.window_height = 700
    page.padding = 0
    page.bgcolor = "#ffffff"

    init_db()
    page.add(build_home_view(page))

ft.app(target=main)