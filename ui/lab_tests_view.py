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
            pending_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=80, color="#4CAF50"),
                        ft.Text("No Donors Pending Lab Test", size=20, weight=ft.FontWeight.BOLD, color="#2E7D32"),
                        ft.Text("All donors have known blood types!", size=14, color="#666666"),
                        ft.Container(height=20),
                        ft.Text("💡 Go to Donors page to add new donors", size=12, color="#1976D2"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                )
            )
        else:
            pending_list.controls.append(
                ft.Text(f"🧪 {len(unknown_donors)} donor(s) awaiting blood type testing", 
                       size=14, weight=ft.FontWeight.BOLD, color="#F57C00")
            )
            
            for donor in unknown_donors:
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
                        )
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
                                ft.Text("🔬 Select Tested Blood Type:", size=14, weight=ft.FontWeight.BOLD),
                                blood_buttons,
                                ft.Text("💡 Note: Donation will be automatically recorded", size=11, color="#666666", italic=True),
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
        
        # Record donation with 1 unit
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
            refresh_list()
        else:
            status_text.value = f"❌ Error: {message}"
            status_text.color = "#C62828"
        
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
            ]),
            margin=ft.Margin.only(bottom=20)
        ),
        ft.Divider(),
        ft.Row([
            ft.ElevatedButton("🔄 Refresh", on_click=lambda e: refresh_list(), bgcolor="#F57C00", color="white", icon=ft.Icons.REFRESH),
        ], alignment=ft.MainAxisAlignment.END),
        ft.Container(height=10),
        pending_list,
        ft.Container(height=10),
        status_text,
    ], expand=True, scroll=ft.ScrollMode.AUTO)