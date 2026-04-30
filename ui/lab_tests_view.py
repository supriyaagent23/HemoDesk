import flet as ft
from data.repository import get_all_donors, update_donor_blood_type, add_donation, get_settings
from models.donation import Donation
from ui.components import blood_badge


BLOOD_COLORS = {
    "A+": "#D32F2F", "A-": "#C62828",
    "B+": "#1976D2", "B-": "#0D47A1",
    "AB+": "#8E24AA", "AB-": "#7B1FA2",
    "O+": "#43A047", "O-": "#2E7D32",
}


def build_lab_tests_view(page: ft.Page):
    status_text = ft.Text("", size=12)
    pending_list = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def refresh_list():
        # Get all donors with unknown blood type
        all_donors = get_all_donors()
        unknown_donors = [d for d in all_donors if d.blood_type == "Unknown"]
        
        pending_list.controls.clear()
        
        if not unknown_donors:
            # Show eligible donors for donation
            eligible_donors = [d for d in all_donors if d.blood_type != "Unknown"]
            if eligible_donors:
                pending_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=60, color="#4CAF50"),
                            ft.Text("No Pending Lab Tests", size=20, weight=ft.FontWeight.BOLD, color="#2E7D32"),
                            ft.Text("All donors have known blood types!", size=14, color="#666666"),
                            ft.Container(height=10),
                            ft.Text("💡 To record a donation, go to the Donations page", size=12, color="#1976D2"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=40,
                        bgcolor="white",
                        border_radius=12,
                    )
                )
            else:
                pending_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.BLOODTYPE, size=60, color="#D32F2F"),
                            ft.Text("No Donors Yet!", size=20, weight=ft.FontWeight.BOLD, color="#D32F2F"),
                            ft.Text("Add your first donor to get started", size=14, color="#666666"),
                            ft.Container(height=10),
                            ft.ElevatedButton("➕ Add Donor", on_click=lambda e: go_to_donors(), 
                                            icon=ft.Icons.PERSON_ADD, bgcolor="#1976D2", color="white"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=40,
                        bgcolor="white",
                        border_radius=12,
                    )
                )
        else:
            pending_list.controls.append(
                ft.Text(f"🧪 {len(unknown_donors)} donor(s) need blood type testing", 
                       size=14, weight=ft.FontWeight.BOLD, color="#F57C00")
            )
            
            for donor in unknown_donors:
                # Blood type selection buttons
                blood_buttons = ft.Row(spacing=8, wrap=True)
                
                def make_update_and_donate(donor_id, donor_name, donor_age, donor_phone, bt):
                    return lambda e: test_and_donate(donor_id, donor_name, donor_age, donor_phone, bt)
                
                for bt in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
                    blood_buttons.controls.append(
                        ft.ElevatedButton(
                            bt,
                            on_click=make_update_and_donate(donor.id, donor.name, donor.age, donor.phone, bt),
                            bgcolor=BLOOD_COLORS.get(bt, "#333"),
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        )
                    )
                
                # Units field for donation
                units_field = ft.TextField(
                    label="Units to Donate",
                    width=150,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    max_length=2,
                    hint_text="1-10 units",
                    value="1"
                )
                
                pending_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.BIOTECH, color="#F57C00", size=30),
                                    ft.Text("BLOOD TYPE TEST REQUIRED", size=16, weight=ft.FontWeight.BOLD, color="#F57C00"),
                                    blood_badge("Unknown"),
                                ], spacing=10),
                                ft.Divider(),
                                ft.Text(f"Donor: {donor.name}", size=20, weight=ft.FontWeight.BOLD),
                                ft.Row([
                                    ft.Text(f"📅 Age: {donor.age}", size=14),
                                    ft.Text(f"⚥ Gender: {donor.gender or 'Not specified'}", size=14),
                                    ft.Text(f"📞 Phone: {donor.phone}", size=14),
                                ], spacing=20, wrap=True),
                                ft.Divider(),
                                ft.Text("🔬 Step 1: Select Tested Blood Type:", size=14, weight=ft.FontWeight.BOLD),
                                blood_buttons,
                                ft.Container(height=10),
                                ft.Text("💉 Step 2: Enter Donation Units:", size=14, weight=ft.FontWeight.BOLD),
                                ft.Row([
                                    units_field,
                                    ft.Text("Note: After testing, donation will be automatically recorded", size=11, color="#666666"),
                                ], spacing=10, wrap=True),
                                ft.Container(
                                    content=ft.Text("⚠️ Tip: Select blood type and units, then click the blood type button", 
                                                   size=11, color="#F57C00"),
                                    bgcolor="#FFF8E1",
                                    padding=ft.padding.all(8),
                                    border_radius=8,
                                    margin=ft.Margin.only(top=5),
                                ),
                            ], spacing=12),
                            padding=20,
                        ),
                        elevation=3,
                    )
                )
        
        page.update()
    
    def test_and_donate(donor_id, donor_name, donor_age, donor_phone, blood_type):
        # First, update donor's blood type
        update_donor_blood_type(donor_id, blood_type)
        
        # Then, record donation with 1 unit (default)
        units = 1
        
        settings = get_settings()
        max_limit = settings.get("max_stock_limit", 100)
        
        success, message = add_donation(Donation(
            donor_id=donor_id,
            blood_type=blood_type,
            units=units
        ), max_limit=max_limit)
        
        if success:
            status_text.value = f"✅ SUCCESS! {donor_name}'s blood type confirmed as {blood_type} and {units} unit(s) donated!"
            status_text.color = "#2E7D32"
            
            # Show thank you message
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"🎉 Thank you {donor_name}! Your {blood_type} blood donation will save lives!"),
                bgcolor="#2E7D32",
                duration=5000,
            )
            page.snack_bar.open = True
        else:
            status_text.value = f"❌ Error: {message}"
            status_text.color = "#C62828"
        
        # Refresh the list
        refresh_list()
        page.update()
    
    def go_to_donors():
        page.go("/donors")
        page.update()
    
    refresh_list()
    
    return ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.SCIENCE, size=45, color="#F57C00"),
                    ft.Column([
                        ft.Text("🔬 Blood Test & Donation Center", size=28, weight=ft.FontWeight.BOLD, color="#F57C00"),
                        ft.Text("Test unknown blood types and record donations in one place", size=14, color="#666666"),
                    ]),
                ], spacing=15),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO, size=14, color="#1976D2"),
                        ft.Text("For donors with unknown blood type: Select blood type → Donation will be automatically recorded", size=12, color="#1976D2"),
                    ], spacing=5),
                    bgcolor="#E3F2FD",
                    padding=8,
                    border_radius=8,
                    margin=ft.Margin.only(top=10),
                ),
            ]),
            margin=ft.Margin.only(bottom=20)
        ),
        ft.Divider(),
        ft.Row([
            ft.ElevatedButton("🔄 Refresh", on_click=lambda e: refresh_list(), bgcolor="#F57C00", color="white", icon=ft.Icons.REFRESH),
            ft.TextButton("➕ Add New Donor", on_click=lambda e: go_to_donors(), icon=ft.Icons.PERSON_ADD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=10),
        pending_list,
        ft.Container(height=10),
        status_text,
    ], expand=True, scroll=ft.ScrollMode.AUTO)