import flet as ft
from data.repository import get_all_donors, add_donation, get_all_donations
from models.donation import Donation
from ui.components import section, blood_badge

def build_donations_view(page: ft.Page):
    status_text = ft.Text("", color="green", size=12)
    list_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    donors = get_all_donors()
    donor_map = {d.id: d for d in donors}

    donor_dropdown = ft.Dropdown(
        label="Select Donor *", width=250,
        options=[ft.dropdown.Option(key=str(d.id), text=f"{d.name} ({d.blood_type})")
                 for d in donors]
    )
    units_field = ft.TextField(label="Units Donated *", width=150)

    def refresh_donors():
        nonlocal donors, donor_map
        donors = get_all_donors()
        donor_map = {d.id: d for d in donors}
        donor_dropdown.options = [
            ft.dropdown.Option(key=str(d.id), text=f"{d.name} ({d.blood_type})")
            for d in donors
        ]

    def render_list():
        rows = get_all_donations()
        list_col.controls.clear()
        list_col.controls.append(
            ft.Text(f"{len(rows)} donation(s) recorded", size=12, color="#888888"))
        for r in rows:
            list_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        blood_badge(r[3]),
                        ft.Column([
                            ft.Text(r[2], size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{r[4]} units donated  |  {r[5]}", size=12, color="#555555"),
                        ], spacing=2, expand=True)
                    ], spacing=10),
                    padding=12, bgcolor="#ffffff", border_radius=8,
                    border=ft.border.all(1, "#e0e0e0")
                )
            )
        page.update()

    def submit(e):
        if not donor_dropdown.value or not units_field.value:
            status_text.value = "Please select a donor and enter units."
            page.update()
            return
        try:
            units = int(units_field.value)
        except ValueError:
            status_text.value = "Units must be a number."
            page.update()
            return

        donor_id = int(donor_dropdown.value)
        donor = donor_map.get(donor_id)
        if not donor:
            status_text.value = "Donor not found."
            page.update()
            return

        add_donation(Donation(
            donor_id=donor_id,
            blood_type=donor.blood_type,
            units=units
        ))
        status_text.value = f"Donation recorded for {donor.name}. Stock updated."
        donor_dropdown.value = None
        units_field.value = ""
        refresh_donors()
        render_list()

    render_list()

    form = ft.Column([
        ft.Row([donor_dropdown, units_field], spacing=10),
        ft.ElevatedButton("Record Donation", on_click=submit),
        status_text
    ], spacing=10)

    return ft.Column([
        ft.Text("Donations", size=24, weight=ft.FontWeight.BOLD),
        section("Record New Donation", form),
        ft.Text("Donation History", size=16, weight=ft.FontWeight.BOLD),
        ft.Container(height=8),
        list_col,
    ], expand=True)