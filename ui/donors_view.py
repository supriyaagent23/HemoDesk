import flet as ft
from data.repository import get_all_donors, add_donor, update_donor, delete_donor, search_donors
from models.donor import Donor
from ui.components import section, blood_badge, BLOOD_TYPES, BLOOD_TYPES_NO_ALL

def build_donors_view(page: ft.Page):
    selected = {"donor": None}
    list_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    status_text = ft.Text("", color="green", size=12)

    name_field = ft.TextField(label="Full Name *", width=220)
    age_field = ft.TextField(label="Age *", width=100)
    phone_field = ft.TextField(label="Phone *", width=180)
    blood_dropdown = ft.Dropdown(
        label="Blood Type *", width=130,
        options=[ft.dropdown.Option(b) for b in BLOOD_TYPES_NO_ALL]
    )
    search_field = ft.TextField(label="Search by name or phone", width=250)
    filter_dropdown = ft.Dropdown(
        label="Blood Type", width=130, value="All",
        options=[ft.dropdown.Option(b) for b in BLOOD_TYPES]
    )

    def clear_form():
        name_field.value = age_field.value = phone_field.value = ""
        blood_dropdown.value = None
        selected["donor"] = None
        status_text.value = ""

    def render_list():
        donors = search_donors(
            query=search_field.value or "",
            blood_type=filter_dropdown.value
        )
        list_col.controls.clear()
        list_col.controls.append(
            ft.Text(f"{len(donors)} donor(s) found", size=12, color="#888888"))
        for d in donors:
            def make_edit(dd):
                return lambda e: load_donor(dd)
            def make_delete(did):
                return lambda e: do_delete(did)
            list_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        blood_badge(d.blood_type),
                        ft.Column([
                            ft.Text(d.name, size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Age: {d.age}  |  Phone: {d.phone}", size=12, color="#555555"),
                            ft.Text(f"Last donation: {d.last_donation or 'Never'}", size=11, color="#888888"),
                        ], spacing=2, expand=True),
                        ft.Row([
                            ft.IconButton(ft.Icons.EDIT, icon_color="#1565C0",
                                          icon_size=18, on_click=make_edit(d)),
                            ft.IconButton(ft.Icons.DELETE, icon_color="#cc0000",
                                          icon_size=18, on_click=make_delete(d.id)),
                        ])
                    ], spacing=10),
                    padding=12, bgcolor="#ffffff", border_radius=8,
                    border=ft.border.all(1, "#e0e0e0")
                )
            )
        page.update()

    def load_donor(d):
        selected["donor"] = d
        name_field.value = d.name
        age_field.value = str(d.age)
        phone_field.value = d.phone
        blood_dropdown.value = d.blood_type
        status_text.value = f"Editing: {d.name}"
        page.update()

    def do_delete(did):
        delete_donor(did)
        clear_form()
        render_list()

    def submit(e):
        if not name_field.value or not age_field.value or not phone_field.value or not blood_dropdown.value:
            status_text.value = "Please fill all required fields."
            page.update()
            return
        try:
            age = int(age_field.value)
        except ValueError:
            status_text.value = "Age must be a number."
            page.update()
            return

        if selected["donor"]:
            d = selected["donor"]
            d.name = name_field.value.strip()
            d.age = age
            d.phone = phone_field.value.strip()
            d.blood_type = blood_dropdown.value
            update_donor(d)
            status_text.value = "Donor updated successfully."
        else:
            add_donor(Donor(
                name=name_field.value.strip(),
                age=age,
                blood_type=blood_dropdown.value,
                phone=phone_field.value.strip()
            ))
            status_text.value = "Donor added successfully."

        clear_form()
        render_list()

    render_list()

    form = ft.Column([
        ft.Row([name_field, age_field, phone_field, blood_dropdown], wrap=True, spacing=10),
        ft.Row([
            ft.ElevatedButton("Save Donor", on_click=submit),
            ft.TextButton("Clear", on_click=lambda e: (clear_form(), page.update()))
        ]),
        status_text
    ], spacing=10)

    filter_row = ft.Row([
        search_field, filter_dropdown,
        ft.ElevatedButton("Search", on_click=lambda e: render_list()),
        ft.TextButton("Reset", on_click=lambda e: (
            setattr(search_field, 'value', ''),
            setattr(filter_dropdown, 'value', 'All'),
            render_list()
        ))
    ], spacing=8, wrap=True)

    return ft.Column([
        ft.Text("Donors", size=24, weight=ft.FontWeight.BOLD),
        section("Add / Edit Donor", form),
        section("Search & Filter", filter_row),
        ft.Text("Donor List", size=16, weight=ft.FontWeight.BOLD),
        list_col,
    ], expand=True)