import flet as ft
from data.repository import get_all_donors, add_donation, get_all_donations, update_donor_blood_type
from models.donation import Donation
from ui.components import blood_badge, BLOOD_TYPES


def build_blood_check_view(page: ft.Page):
    status_text = ft.Text("", size=12)
    
    # Lists for different sections
    pending_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    completed_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def refresh_and_render():
        # Get all donors
        all_donors = get_all_donors()
        
        # Separate donors with Unknown blood type (pending)
        unknown_donors = [d for d in all_donors if d.blood_type == "Unknown"]
        
        # Get recent completed donations (last 10)
        all_donations = get_all_donations()
        recent_donations = all_donations[:10] if all_donations else []
        
        # Render PENDING section (Unknown donors)
        pending_list.controls.clear()
        
        if not unknown_donors:
            pending_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=48, color="#4CAF50"),
                        ft.Text("No pending donors with Unknown blood type", 
                               size=14, color="#888888"),
                        ft.Text("Add donors with 'Unknown' blood type in Donors page", 
                               size=12, color="#AAAAAA")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40, alignment=ft.Alignment(0, 0)
                )
            )
        else:
            for donor in unknown_donors:
                # Create controls
                blood_type_dropdown = ft.Dropdown(
                    width=150,
                    label="Blood Type *",
                    options=[ft.dropdown.Option(bt) for bt in BLOOD_TYPES],
                    hint_text="Select blood type"
                )
                
                units_field = ft.TextField(
                    label="Units Donated *", width=120,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    input_filter=ft.InputFilter(regex_string=r"[0-9]", allow=True),
                    max_length=3,
                    hint_text="Number only"
                )
                
                # Create button with proper closure
                def make_record_button(d_id, d_name, d_age, d_phone, d_gender, dd, uf):
                    return lambda e: record_donation(d_id, d_name, d_age, d_phone, d_gender, dd, uf)
                
                record_button = ft.ElevatedButton(
                    "Record Donation & Update Blood Type",
                    bgcolor="#2E7D32", color="#ffffff",
                    icon=ft.Icons.FAVORITE,
                    on_click=make_record_button(
                        donor.id, donor.name, donor.age, 
                        donor.phone, donor.gender,
                        blood_type_dropdown, units_field
                    )
                )
                
                # Create donor card
                donor_card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.BLOODTYPE, size=20, color="#FF9800"),
                            ft.Text("PENDING - BLOOD TYPE UNKNOWN", size=12, 
                                   weight=ft.FontWeight.BOLD, color="#FF9800"),
                            blood_badge("Unknown"),
                        ], spacing=8),
                        ft.Text(f"Donor: {donor.name}", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Text(f"Age: {donor.age}", size=13, color="#555555"),
                            ft.Text(f"Gender: {donor.gender or 'Not specified'}", size=13, color="#555555"),
                            ft.Text(f"Phone: {donor.phone}", size=13, color="#555555"),
                        ], spacing=15),
                        ft.Divider(height=5),
                        ft.Text("Enter donation details:", size=13, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            blood_type_dropdown,
                            units_field,
                            record_button
                        ], spacing=10, wrap=True)
                    ], spacing=8),
                    padding=14, 
                    bgcolor="#FFF8E1", 
                    border_radius=8,
                    border=ft.Border.all(1, "#FFB74D")
                )
                
                pending_list.controls.append(donor_card)
        
        # Render COMPLETED section (Recent donations)
        completed_list.controls.clear()
        
        if not recent_donations:
            completed_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.HISTORY, size=48, color="#CCCCCC"),
                        ft.Text("No donations recorded yet", size=14, color="#888888"),
                        ft.Text("Record donations from the pending list above", 
                               size=12, color="#AAAAAA")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40, alignment=ft.Alignment(0, 0)
                )
            )
        else:
            for donation in recent_donations:
                # donation format: (id, donor_id, donor_name, blood_type, units, date)
                if len(donation) >= 6:
                    donation_id, donor_id, donor_name, blood_type, units, date = donation[:6]
                    
                    completed_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE, size=20, color="#4CAF50"),
                                ft.Column([
                                    ft.Text(donor_name, size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{date[:10] if date else 'Unknown date'}", 
                                           size=11, color="#888888"),
                                ], spacing=2, expand=True),
                                blood_badge(blood_type),
                                ft.Container(
                                    content=ft.Text(f"+{units} units", size=13, 
                                                   weight=ft.FontWeight.BOLD, color="#2E7D32"),
                                    bgcolor="#E8F5E9",
                                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=12,
                                ),
                            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=12,
                            bgcolor="#ffffff",
                            border_radius=8,
                            border=ft.Border.all(1, "#E0E0E0")
                        )
                    )
        
        # Update stats
        update_stats()
        page.update()
    
    def update_stats():
        all_donors = get_all_donors()
        unknown_count = len([d for d in all_donors if d.blood_type == "Unknown"])
        all_donations = get_all_donations()
        donation_count = len(all_donations)
        
        pending_count.value = str(unknown_count)
        total_donations_count.value = str(donation_count)
        page.update()
    
    def record_donation(donor_id, donor_name, donor_age, donor_phone, donor_gender, 
                       dropdown, units_field):
        # Validation
        if not dropdown.value:
            status_text.value = "❌ Please select the blood type"
            status_text.color = "#C62828"
            page.update()
            return
        
        if not units_field.value:
            status_text.value = "❌ Please enter units donated"
            status_text.color = "#C62828"
            page.update()
            return
        
        if not units_field.value.isdigit():
            status_text.value = "❌ Units must be a number"
            status_text.color = "#C62828"
            page.update()
            return
        
        units = int(units_field.value)
        if units <= 0:
            status_text.value = "❌ Units must be greater than 0"
            status_text.color = "#C62828"
            page.update()
            return
        
        if units > 10:
            status_text.value = "⚠️ Units cannot exceed 10 per donation"
            status_text.color = "#C62828"
            page.update()
            return
        
        # FIRST: Update donor's blood type in donors table
        update_donor_blood_type(donor_id, dropdown.value)
        
        # SECOND: Record the donation
        success, message = add_donation(Donation(
            donor_id=donor_id,
            blood_type=dropdown.value,
            units=units
        ))
        
        if success:
            status_text.value = f"✅ Donor blood type updated to {dropdown.value}! {units} unit(s) added to stock."
            status_text.color = "#2E7D32"
            
            # Refresh both lists (donor will disappear from pending)
            refresh_and_render()
        else:
            status_text.value = f"❌ {message}"
            status_text.color = "#C62828"
        
        page.update()
    
    # Stats display
    all_donors = get_all_donors()
    unknown_count = len([d for d in all_donors if d.blood_type == "Unknown"])
    all_donations = get_all_donations()
    donation_count = len(all_donations)
    
    pending_count = ft.Text(str(unknown_count), size=24, weight=ft.FontWeight.BOLD, color="#FF9800")
    total_donations_count = ft.Text(str(donation_count), size=24, weight=ft.FontWeight.BOLD, color="#2E7D32")
    
    stats_row = ft.Row([
        ft.Container(
            content=ft.Column([
                pending_count,
                ft.Text("Pending Donors", size=12, color="#555555"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            bgcolor="#FFF8E1",
            border_radius=10,
            expand=True,
        ),
        ft.Container(
            content=ft.Column([
                total_donations_count,
                ft.Text("Total Donations", size=12, color="#555555"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            bgcolor="#E8F5E9",
            border_radius=10,
            expand=True,
        ),
    ], spacing=15)
    
    # Initial render
    refresh_and_render()
    
    return ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Text("Blood Donation Management", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Process donors with unknown blood type and view donation history", 
                       size=13, color="#555555"),
            ]),
            margin=ft.Margin.only(bottom=10)
        ),
        stats_row,
        ft.Divider(height=20),
        
        # Pending Donors Section
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PENDING, color="#FF9800", size=20),
                    ft.Text("Pending Donors (Unknown Blood Type)", 
                           size=16, weight=ft.FontWeight.BOLD, color="#FF9800"),
                    ft.Container(
                        content=ft.Text(str(unknown_count), size=12, color="#ffffff"),
                        bgcolor="#FF9800",
                        border_radius=10,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                    ),
                ], spacing=8),
                ft.Divider(height=5),
                pending_list,
            ], spacing=10),
            margin=ft.Margin.only(bottom=20),
        ),
        
        # Completed Donations Section
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.HISTORY, color="#4CAF50", size=20),
                    ft.Text("Recent Donations", size=16, weight=ft.FontWeight.BOLD, color="#2E7D32"),
                    ft.Container(
                        content=ft.Text(str(donation_count), size=12, color="#ffffff"),
                        bgcolor="#2E7D32",
                        border_radius=10,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                    ),
                ], spacing=8),
                ft.Divider(height=5),
                completed_list,
            ], spacing=10),
        ),
        
        ft.Container(height=10),
        status_text,
        
        # Refresh button
        ft.Container(
            content=ft.ElevatedButton(
                "🔄 Refresh Lists", 
                on_click=lambda e: refresh_and_render(),
                bgcolor="#F57C00", 
                color="#ffffff"
            ),
            alignment=ft.Alignment(0, 0),
            margin=ft.Margin.only(top=10),
        ),
        
    ], expand=True, scroll=ft.ScrollMode.AUTO)