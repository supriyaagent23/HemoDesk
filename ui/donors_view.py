import flet as ft
import re
from data.repository import get_all_donors, add_donor, update_donor, delete_donor
from models.donor import Donor
from ui.components import section, blood_badge, BLOOD_TYPES_WITH_UNKNOWN


def build_donors_view(page: ft.Page):
    status_text = ft.Text("", size=12)
    list_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    
    # Form fields
    name_field = ft.TextField(label="Full Name *", width=220, hint_text="Enter donor's full name")
    age_field = ft.TextField(label="Age *", width=100, keyboard_type=ft.KeyboardType.NUMBER, max_length=3, hint_text="18-80")
    blood_dropdown = ft.Dropdown(
        label="Blood Type *", 
        width=180, 
        hint_text="Select blood type",
        options=[ft.dropdown.Option(b) for b in BLOOD_TYPES_WITH_UNKNOWN]
    )
    phone_field = ft.TextField(label="Phone *", width=180, keyboard_type=ft.KeyboardType.PHONE, max_length=10, hint_text="10 digits")
    gender_dropdown = ft.Dropdown(
        label="Gender", 
        width=140, 
        hint_text="Optional",
        options=[ft.dropdown.Option("Male"), ft.dropdown.Option("Female"), ft.dropdown.Option("Other")]
    )
    
    # Warning for unknown blood type
    unknown_warning = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.WARNING, size=16, color="#F57C00"),
            ft.Text("⚠️ Donors with 'Unknown' blood type cannot donate until tested in Lab Tests page", size=12, color="#F57C00"),
        ], spacing=8),
        bgcolor="#FFF8E1",
        padding=8,
        border_radius=8,
        visible=False,
    )
    
    def on_blood_type_change(e):
        unknown_warning.visible = (blood_dropdown.value == "Unknown")
        page.update()
    
    blood_dropdown.on_change = on_blood_type_change
    
    editing_id = [None]
    
    def validate_phone(phone):
        return bool(re.match(r"^\d{10}$", phone.strip()))
    
    def refresh_list():
        donors = get_all_donors()
        list_col.controls.clear()
        
        # Separate donors by blood type
        known_donors = [d for d in donors if d.blood_type != "Unknown"]
        unknown_donors = [d for d in donors if d.blood_type == "Unknown"]
        
        if unknown_donors:
            list_col.controls.append(
                ft.Text("🔬 Pending Lab Testing (Cannot Donate)", size=14, weight=ft.FontWeight.BOLD, color="#F57C00")
            )
            for d in unknown_donors:
                list_col.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row([
                                blood_badge(d.blood_type),
                                ft.Column([
                                    ft.Text(d.name, size=15, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Age: {d.age} | Phone: {d.phone} | {d.gender or 'Gender not set'}", 
                                           size=11, color="#666666"),
                                    ft.Text("⚠️ Blood type pending lab test - Click Lab Tests to determine type", 
                                           size=10, color="#F57C00", weight=ft.FontWeight.BOLD),
                                ], spacing=2, expand=True),
                                ft.Row([
                                    ft.IconButton(ft.Icons.EDIT, icon_color="#1565C0", icon_size=20, 
                                                on_click=lambda e, donor=d: start_edit(donor)),
                                    ft.IconButton(ft.Icons.DELETE, icon_color="#cc0000", icon_size=20, 
                                                on_click=lambda e, did=d.id: do_delete(did)),
                                ], spacing=5)
                            ], spacing=10),
                            padding=12,
                            bgcolor="#FFF8E1",
                        ),
                        elevation=2,
                    )
                )
        
        if known_donors:
            if unknown_donors:
                list_col.controls.append(ft.Divider(height=10))
                list_col.controls.append(
                    ft.Text("✅ Eligible Donors (Can Donate)", size=14, weight=ft.FontWeight.BOLD, color="#2E7D32")
                )
            
            for d in known_donors:
                list_col.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row([
                                blood_badge(d.blood_type),
                                ft.Column([
                                    ft.Text(d.name, size=15, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Age: {d.age} | Phone: {d.phone} | {d.gender or 'Gender not set'} | Donations: {d.total_donations}", 
                                           size=11, color="#666666"),
                                ], spacing=2, expand=True),
                                ft.Row([
                                    ft.IconButton(ft.Icons.EDIT, icon_color="#1565C0", icon_size=20, 
                                                on_click=lambda e, donor=d: start_edit(donor)),
                                    ft.IconButton(ft.Icons.DELETE, icon_color="#cc0000", icon_size=20, 
                                                on_click=lambda e, did=d.id: do_delete(did)),
                                ], spacing=0)
                            ], spacing=10),
                            padding=12,
                            bgcolor="white",
                        ),
                        elevation=1,
                    )
                )
        
        if not donors:
            list_col.controls.append(
                ft.Container(
                    content=ft.Text("No donors registered. Click 'Add Donor' to get started.", size=13, color="#888888"),
                    padding=20,
                )
            )
        
        page.update()
    
    def start_edit(donor):
        editing_id[0] = donor.id
        name_field.value = donor.name
        age_field.value = str(donor.age)
        blood_dropdown.value = donor.blood_type
        phone_field.value = donor.phone
        gender_dropdown.value = donor.gender or None
        unknown_warning.visible = (donor.blood_type == "Unknown")
        status_text.value = f"✏️ Editing donor: {donor.name}"
        status_text.color = "#1565C0"
        page.update()
    
    def clear_form():
        editing_id[0] = None
        name_field.value = ""
        age_field.value = ""
        blood_dropdown.value = None
        phone_field.value = ""
        gender_dropdown.value = None
        unknown_warning.visible = False
        status_text.value = ""
        page.update()
    
    def submit(e):
        if not all([name_field.value, age_field.value, blood_dropdown.value, phone_field.value]):
            status_text.value = "❌ Please fill all required fields"
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
        
        if not validate_phone(phone_field.value):
            status_text.value = "❌ Phone must be exactly 10 digits"
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
            status_text.value = f"✅ Donor '{donor.name}' added successfully!"
            if donor.blood_type == "Unknown":
                status_text.value += " Please visit Lab Tests to determine blood type."
        else:
            update_donor(donor)
            status_text.value = f"✅ Donor '{donor.name}' updated successfully!"
        
        status_text.color = "#2E7D32"
        clear_form()
        refresh_list()
        page.update()
    
    def do_delete(donor_id):
        delete_donor(donor_id)
        refresh_list()
        status_text.value = "✅ Donor deleted successfully."
        status_text.color = "#2E7D32"
        page.update()
    
    refresh_list()
    
    form = ft.Column([
        ft.Row([name_field, age_field, blood_dropdown, phone_field, gender_dropdown], wrap=True, spacing=10),
        unknown_warning,
        ft.Row([
            ft.ElevatedButton("💾 Save Donor", on_click=submit, bgcolor="#1565C0", color="white", icon=ft.Icons.SAVE), 
            ft.OutlinedButton("🗑️ Clear Form", on_click=lambda e: clear_form(), icon=ft.Icons.CLEAR),
            ft.ElevatedButton("🔄 Refresh List", on_click=lambda e: refresh_list(), bgcolor="#6A1B9A", color="white", icon=ft.Icons.REFRESH),
        ], spacing=10),
        status_text,
    ], spacing=10)
    
    return ft.Column([
        ft.Text("👥 Donors Management", size=28, weight=ft.FontWeight.BOLD),
        section("➕ Add / Edit Donor", form),
        ft.Text("📋 All Donors", size=18, weight=ft.FontWeight.BOLD),
        ft.Container(height=8),
        list_col,
    ], expand=True, scroll=ft.ScrollMode.AUTO)