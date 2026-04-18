import flet as ft
import re
from data.repository import get_all_donors, add_donor, update_donor, delete_donor
from models.donor import Donor
from ui.components import section, blood_badge, BLOOD_TYPES_WITH_UNKNOWN


def build_donors_view(page: ft.Page):
    status_text = ft.Text("", size=12)
    list_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    # Form fields with proper validation
    name_field = ft.TextField(
        label="Full Name *", width=200,
        hint_text="Letters and spaces only"
    )
    age_field = ft.TextField(
        label="Age *", width=80,
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=3,
        hint_text="18-80"
    )
    blood_dropdown = ft.Dropdown(
        label="Blood Type *", width=130,
        options=[ft.dropdown.Option(b) for b in BLOOD_TYPES_WITH_UNKNOWN]  # Includes Unknown
    )
    phone_field = ft.TextField(
        label="Phone *", width=160,
        keyboard_type=ft.KeyboardType.PHONE,
        max_length=10,
        hint_text="10 digits only"
    )
    gender_dropdown = ft.Dropdown(
        label="Gender", width=120,
        options=[
            ft.dropdown.Option("Male"),
            ft.dropdown.Option("Female"),
            ft.dropdown.Option("Other"),
        ]
    )

    editing_id = [None]

    def validate_name(name):
        """Allow only letters and spaces"""
        return bool(re.match(r"^[a-zA-Z\s]{2,50}$", name.strip()))

    def validate_phone(phone):
        """Allow only 10 digits"""
        return bool(re.match(r"^\d{10}$", phone.strip()))

    def render_list():
        donors = get_all_donors()
        list_col.controls.clear()
        list_col.controls.append(
            ft.Text(f"{len(donors)} donor(s)", size=12, color="#888888")
        )

        for d in donors:
            def make_edit(donor):
                return lambda e: start_edit(donor)
            def make_delete(did):
                return lambda e: do_delete(did)

            list_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        blood_badge(d.blood_type),
                        ft.Column([
                            ft.Text(d.name, size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"Age: {d.age}  |  Phone: {d.phone}"
                                + (f"  |  Gender: {d.gender}" if d.gender else "")
                                + (f"  |  Last: {d.last_donation}" if d.last_donation else ""),
                                size=12, color="#555555"
                            ),
                        ], spacing=2, expand=True),
                        ft.Row([
                            ft.IconButton(ft.Icons.EDIT, icon_color="#1565C0",
                                          icon_size=18, on_click=make_edit(d)),
                            ft.IconButton(ft.Icons.DELETE, icon_color="#cc0000",
                                          icon_size=18, on_click=make_delete(d.id)),
                        ], spacing=0)
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=12, bgcolor="#ffffff", border_radius=8,
                    border=ft.Border.all(1, "#e0e0e0")
                )
            )
        page.update()

    def start_edit(donor: Donor):
        editing_id[0] = donor.id
        name_field.value = donor.name
        age_field.value = str(donor.age)
        blood_dropdown.value = donor.blood_type
        phone_field.value = donor.phone
        gender_dropdown.value = donor.gender or None
        status_text.value = f"Editing donor: {donor.name}"
        status_text.color = "#1565C0"
        page.update()

    def clear_form():
        editing_id[0] = None
        name_field.value = ""
        age_field.value = ""
        blood_dropdown.value = None
        phone_field.value = ""
        gender_dropdown.value = None
        status_text.value = ""
        page.update()

    def on_name_change(e):
        """Filter out numbers and special characters as user types"""
        name_field.value = re.sub(r'[^a-zA-Z\s]', '', name_field.value)
        page.update()

    def on_phone_change(e):
        """Filter out non-digits as user types"""
        phone_field.value = re.sub(r'[^\d]', '', phone_field.value)[:10]
        page.update()

    def on_age_change(e):
        """Filter out non-digits as user types"""
        age_field.value = re.sub(r'[^\d]', '', age_field.value)[:3]
        page.update()

    # Attach real-time filters
    name_field.on_change = on_name_change
    phone_field.on_change = on_phone_change
    age_field.on_change = on_age_change

    def submit(e):
        # Name validation
        if not name_field.value or not name_field.value.strip():
            status_text.value = "❌ Please enter donor name"
            status_text.color = "#C62828"
            page.update()
            return
        
        if not validate_name(name_field.value):
            status_text.value = "❌ Name must contain only letters and spaces (2-50 characters)"
            status_text.color = "#C62828"
            page.update()
            return
        
        # Age validation
        if not age_field.value:
            status_text.value = "❌ Please enter age"
            status_text.color = "#C62828"
            page.update()
            return
        
        if not age_field.value.isdigit():
            status_text.value = "❌ Age must be a number"
            status_text.color = "#C62828"
            page.update()
            return
        
        age = int(age_field.value)
        if age < 18 or age > 80:
            status_text.value = "❌ Age must be between 18 and 80"
            status_text.color = "#C62828"
            page.update()
            return
        
        # Blood type validation
        if not blood_dropdown.value:
            status_text.value = "❌ Please select blood type"
            status_text.color = "#C62828"
            page.update()
            return
        
        # Phone validation
        if not phone_field.value:
            status_text.value = "❌ Please enter phone number"
            status_text.color = "#C62828"
            page.update()
            return
        
        if not validate_phone(phone_field.value):
            status_text.value = "❌ Phone number must be exactly 10 digits"
            status_text.color = "#C62828"
            page.update()
            return

        donor = Donor(
            id=editing_id[0],
            name=name_field.value.strip(),
            age=age,
            blood_type=blood_dropdown.value,
            phone=phone_field.value.strip(),
            gender=gender_dropdown.value or "",
        )

        if editing_id[0] is None:
            add_donor(donor)
            status_text.value = f"✅ Donor '{donor.name}' added."
        else:
            update_donor(donor)
            status_text.value = f"✅ Donor '{donor.name}' updated."

        status_text.color = "#2E7D32"
        clear_form()
        render_list()
        page.update()

    def do_delete(donor_id: int):
        delete_donor(donor_id)
        render_list()
        status_text.value = "✅ Donor deleted."
        status_text.color = "#2E7D32"
        page.update()

    render_list()

    form = ft.Column([
        ft.Row([name_field, age_field, blood_dropdown, phone_field, gender_dropdown],
               wrap=True, spacing=10),
        ft.Row([
            ft.ElevatedButton("Save Donor", on_click=submit,
                              bgcolor="#1565C0", color="#ffffff"),
            ft.OutlinedButton("Cancel / Clear", on_click=lambda e: clear_form()),
        ], spacing=10),
        status_text,
    ], spacing=10)

    return ft.Column([
        ft.Text("Donors Management", size=24, weight=ft.FontWeight.BOLD),
        section("Add / Edit Donor", form),
        ft.Text("All Donors", size=16, weight=ft.FontWeight.BOLD),
        ft.Container(height=8),
        list_col,
    ], expand=True, scroll=ft.ScrollMode.AUTO)