import flet as ft
from data.repository import get_all_stock, update_stock
from ui.components import section, BLOOD_COLORS

def build_stock_view(page: ft.Page):
    status_text = ft.Text("", color="green", size=12)
    stock_col = ft.Column(spacing=8)

    blood_dropdown = ft.Dropdown(
        label="Blood Type *", width=150,
        options=[ft.dropdown.Option(b) for b in
                 ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]]
    )
    units_field = ft.TextField(label="Units *", width=120)
    action_dropdown = ft.Dropdown(
        label="Action *", width=150,
        options=[ft.dropdown.Option("Add"), ft.dropdown.Option("Remove")]
    )

    def render_stock():
        stock = get_all_stock()
        stock_col.controls.clear()
        for s in stock:
            color = BLOOD_COLORS.get(s.blood_type, "#888888")
            is_low = s.units < 5
            stock_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            ft.Text(s.blood_type, size=16, weight=ft.FontWeight.BOLD,
                                    color="#ffffff"),
                            bgcolor=color, border_radius=6,
                            padding=ft.padding.symmetric(8, 14),
                            width=70
                        ),
                        ft.Text(f"{s.units} units available",
                                size=14, expand=True),
                        ft.Container(
                            ft.Text("LOW STOCK", size=11, color="#ffffff"),
                            bgcolor="#C62828", border_radius=4,
                            padding=ft.padding.symmetric(3, 8),
                            visible=is_low
                        )
                    ], spacing=12),
                    padding=12, bgcolor="#ffffff", border_radius=8,
                    border=ft.border.all(2 if is_low else 1,
                                         "#C62828" if is_low else "#e0e0e0")
                )
            )
        page.update()

    def submit(e):
        if not blood_dropdown.value or not units_field.value or not action_dropdown.value:
            status_text.value = "Please fill all fields."
            page.update()
            return
        try:
            units = int(units_field.value)
        except ValueError:
            status_text.value = "Units must be a number."
            page.update()
            return

        change = units if action_dropdown.value == "Add" else -units
        update_stock(blood_dropdown.value, change)
        status_text.value = f"{action_dropdown.value}ed {units} units of {blood_dropdown.value}."
        units_field.value = ""
        blood_dropdown.value = None
        action_dropdown.value = None
        render_stock()

    render_stock()

    form = ft.Column([
        ft.Row([blood_dropdown, units_field, action_dropdown], spacing=10),
        ft.ElevatedButton("Update Stock", on_click=submit),
        status_text
    ], spacing=10)

    return ft.Column([
        ft.Text("Blood Stock", size=24, weight=ft.FontWeight.BOLD),
        section("Manually Update Stock", form),
        ft.Text("Current Stock Levels", size=16, weight=ft.FontWeight.BOLD),
        ft.Container(height=10),
        stock_col,
    ], scroll=ft.ScrollMode.AUTO, expand=True)