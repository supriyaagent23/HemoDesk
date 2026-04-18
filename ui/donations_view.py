import flet as ft
from data.repository import get_all_donors, add_donation, get_all_donations, is_eligible_to_donate, get_settings
from models.donation import Donation
from ui.components import section, blood_badge

def build_donations_view(page: ft.Page):
    status_text = ft.Text("", size=12)
    list_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    eligibility_text = ft.Text("", size=12)

    donors = get_all_donors()
    donor_map = {d.id: d for d in donors}
    settings = get_settings()
    max_limit = settings.get("max_stock_limit", 100)

    donor_dropdown = ft.Dropdown(
        label="Select Donor *", width=250,
        options=[ft.dropdown.Option(key=str(d.id), text=f"{d.name} ({d.blood_type})")
                 for d in donors]
    )
    
    # UNITS FIELD - Fixed InputFilter
    units_field = ft.TextField(
        label="Units Donated *", 
        width=150,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(regex_string=r"[0-9]", allow=True),
        max_length=4,
        hint_text="Enter number"
    )
    
    def check_eligibility(e):
        if not donor_dropdown.value:
            eligibility_text.value = "Please select a donor first."
            eligibility_text.color = "#C62828"
            page.update()
            return
        
        donor_id = int(donor_dropdown.value)
        eligible, message = is_eligible_to_donate(donor_id)
        
        eligibility_text.value = message
        eligibility_text.color = "#2E7D32" if eligible else "#C62828"
        page.update()

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
                    border=ft.Border.all(1, "#e0e0e0")
                )
            )
        page.update()

    def submit(e):
        if not donor_dropdown.value or not units_field.value:
            status_text.value = "Please select a donor and enter units."
            status_text.color = "#C62828"
            page.update()
            return
        
        if not units_field.value.isdigit():
            status_text.value = "Units must be a number."
            status_text.color = "#C62828"
            page.update()
            return
            
        units = int(units_field.value)
        if units <= 0:
            status_text.value = "Units must be greater than 0."
            status_text.color = "#C62828"
            page.update()
            return

        donor_id = int(donor_dropdown.value)
        donor = donor_map.get(donor_id)
        if not donor:
            status_text.value = "Donor not found."
            status_text.color = "#C62828"
            page.update()
            return

        success, message = add_donation(Donation(
            donor_id=donor_id,
            blood_type=donor.blood_type,
            units=units
        ), max_limit=max_limit)
        
        if success:
            status_text.value = message
            status_text.color = "#2E7D32"
            donor_dropdown.value = None
            units_field.value = ""
            eligibility_text.value = ""
            refresh_donors()
            render_list()
        else:
            status_text.value = message
            status_text.color = "#C62828"
        page.update()

    render_list()

    form = ft.Column([
        ft.Row([donor_dropdown, units_field], spacing=10),
        ft.Row([
            ft.ElevatedButton("Check Eligibility", on_click=check_eligibility, bgcolor="#6A1B9A", color="#ffffff"),
            ft.ElevatedButton("Record Donation", on_click=submit, bgcolor="#2E7D32", color="#ffffff"),
        ], spacing=10),
        eligibility_text,
        status_text
    ], spacing=10)

    return ft.Column([
        ft.Text("Donations", size=24, weight=ft.FontWeight.BOLD),
        section("Record New Donation", form),
        ft.Text("Donation History", size=16, weight=ft.FontWeight.BOLD),
        ft.Container(height=8),
        list_col,
    ], expand=True)