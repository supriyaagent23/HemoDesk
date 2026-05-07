import flet as ft
from data.repository import get_all_stock, update_stock, get_settings, update_setting, get_all_donors, add_donation, is_eligible_to_donate
from models.donation import Donation
from ui.components import section, BLOOD_COLORS, blood_badge


def build_stock_view(page: ft.Page):
    status_text = ft.Text("", size=12)
    stock_col = ft.Column(spacing=10)
    
    settings = get_settings()
    
    # Search Section
    search_field = ft.TextField(
        label="Search Donor by Name or Passport",
        width=350,
        hint_text="Type name or passport number...",
        prefix_icon=ft.Icons.SEARCH,
    )
    
    search_results = ft.Column(spacing=8, visible=False)
    selected_donor_info = ft.Container(visible=False)
    
    donation_units = ft.TextField(
        label="Units to Donate",
        width=120,
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=2,
        hint_text="1-10",
        value="1"
    )
    
    # Stock update fields
    blood_dropdown = ft.Dropdown(
        label="Blood Type",
        width=150,
        options=[ft.dropdown.Option(b) for b in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]]
    )
    
    stock_units = ft.TextField(
        label="Units",
        width=100,
        keyboard_type=ft.KeyboardType.NUMBER,
        hint_text="Number"
    )
    
    action_dropdown = ft.Dropdown(
        label="Action",
        width=100,
        options=[ft.dropdown.Option("Add"), ft.dropdown.Option("Remove")]
    )
    
    # Settings fields
    low_stock_threshold_field = ft.TextField(
        label="Low Stock Alert (units)",
        width=180,
        value=str(settings.get("low_stock_threshold", 5)),
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    max_stock_limit_field = ft.TextField(
        label="Maximum Stock Limit (units)",
        width=180,
        value=str(settings.get("max_stock_limit", 100)),
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    
    # Variable to store selected donor
    selected_donor = [None]
    all_donors = []  # Will be populated on refresh
    
    def refresh_donor_list():
        """Refresh the donor list and reset search"""
        nonlocal all_donors
        all_donors = get_all_donors()
        # Clear search and results
        search_field.value = ""
        search_results.visible = False
        selected_donor_info.visible = False
        selected_donor[0] = None
        status_text.value = "✅ Donor list refreshed!"
        status_text.color = "#2E7D32"
        page.update()
    
    def on_search_change(e):
        search_text = search_field.value.strip().lower()
        if not search_text:
            search_results.visible = False
            selected_donor_info.visible = False
            page.update()
            return
        
        # Search donors
        matching_donors = []
        for d in all_donors:
            if d.blood_type != "Unknown":  # Only show donors with known blood type
                if search_text in d.name.lower() or (d.passport_no and search_text in d.passport_no.lower()):
                    matching_donors.append(d)
        
        if matching_donors:
            search_results.controls.clear()
            for donor in matching_donors[:5]:  # Show top 5 results
                eligible, msg = is_eligible_to_donate(donor.id)
                eligible_text = "✅ Eligible" if eligible else "⏳ Not Eligible"
                eligible_color = "#2E7D32" if eligible else "#F57C00"
                
                search_results.controls.append(
                    ft.Container(
                        content=ft.Row([
                            blood_badge(donor.blood_type),
                            ft.Column([
                                ft.Text(donor.name, size=14, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Passport: {donor.passport_no or 'N/A'} | {eligible_text}", size=11, color=eligible_color),
                            ], expand=True),
                            ft.ElevatedButton(
                                "Select", 
                                on_click=lambda e, d=donor: select_donor(d),
                                bgcolor="#1976D2",
                                color="white",
                                height=35,
                            ),
                        ], spacing=10),
                        padding=8,
                        bgcolor="#F5F5F5",
                        border_radius=8,
                    )
                )
            search_results.visible = True
            selected_donor_info.visible = False
        else:
            search_results.controls.clear()
            search_results.controls.append(
                ft.Container(
                    content=ft.Text("No donors found with known blood type", size=13, color="#888888"),
                    padding=10,
                )
            )
            search_results.visible = True
            selected_donor_info.visible = False
        
        page.update()
    
    def select_donor(donor):
        selected_donor[0] = donor
        eligible, msg = is_eligible_to_donate(donor.id)
        
        selected_donor_info.content = ft.Column([
            ft.Row([
                blood_badge(donor.blood_type),
                ft.Text(donor.name, size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Text("✅ ELIGIBLE" if eligible else "⏳ NOT ELIGIBLE", size=11, color="white"),
                    bgcolor="#2E7D32" if eligible else "#F57C00",
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                ),
            ], spacing=10),
            ft.Text(f"📅 Age: {donor.age} | 📞 Phone: {donor.phone}", size=12),
            ft.Text(f"🪪 Passport: {donor.passport_no or 'Not provided'} | 💉 Total Donations: {donor.total_donations}", size=12),
            ft.Text(f"📋 {msg}", size=11, color="#1976D2"),
            ft.Divider(),
            ft.Row([
                donation_units,
                ft.ElevatedButton(
                    "💉 Record Donation", 
                    on_click=record_donation, 
                    bgcolor="#E91E63", 
                    color="white",
                    disabled=not eligible,
                ),
            ], spacing=10),
        ], spacing=8)
        
        selected_donor_info.visible = True
        search_results.visible = False
        search_field.value = donor.name
        page.update()
    
    def record_donation(e):
        if selected_donor[0] is None:
            status_text.value = "❌ Please select a donor first"
            status_text.color = "#C62828"
            page.update()
            return
        
        if not donation_units.value:
            status_text.value = "❌ Please enter units"
            status_text.color = "#C62828"
            page.update()
            return
        
        if not donation_units.value.isdigit():
            status_text.value = "❌ Units must be a number"
            status_text.color = "#C62828"
            page.update()
            return
        
        units = int(donation_units.value)
        if units <= 0 or units > 10:
            status_text.value = "❌ Units must be between 1 and 10"
            status_text.color = "#C62828"
            page.update()
            return
        
        donor = selected_donor[0]
        
        # Check eligibility again
        eligible, msg = is_eligible_to_donate(donor.id)
        if not eligible:
            status_text.value = f"❌ {msg}"
            status_text.color = "#C62828"
            page.update()
            return
        
        # Record donation
        max_limit = settings.get("max_stock_limit", 100)
        success, message = add_donation(Donation(
            donor_id=donor.id,
            blood_type=donor.blood_type,
            units=units
        ), max_limit=max_limit)
        
        if success:
            status_text.value = f"✅ {message} from {donor.name}!"
            status_text.color = "#2E7D32"
            
            # Show thank you
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"🎉 Thank you {donor.name}! Your {units} unit(s) of {donor.blood_type} blood will save lives!"),
                bgcolor="#2E7D32",
                duration=4000,
            )
            page.snack_bar.open = True
            
            # Reset selection
            selected_donor[0] = None
            selected_donor_info.visible = False
            search_field.value = ""
            search_results.visible = False
            donation_units.value = "1"
            
            # Refresh donor list and stock display
            refresh_donor_list()
            render_stock()
        else:
            status_text.value = f"❌ {message}"
            status_text.color = "#C62828"
        
        page.update()

    def render_stock():
        stock = get_all_stock()
        try:
            low_threshold = int(low_stock_threshold_field.value) if low_stock_threshold_field.value else 5
        except:
            low_threshold = 5
            
        stock_col.controls.clear()
        
        # Add header row
        stock_col.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Text("Blood Type", size=13, weight=ft.FontWeight.BOLD, width=90),
                    ft.Text("Units", size=13, weight=ft.FontWeight.BOLD, width=60),
                    ft.Text("Status", size=13, weight=ft.FontWeight.BOLD, width=80),
                    ft.Text("Capacity", size=13, weight=ft.FontWeight.BOLD, expand=True),
                ], spacing=8),
                padding=ft.padding.symmetric(vertical=6, horizontal=8),
                bgcolor="#F5F5F5",
                border_radius=6,
            )
        )
        
        for s in stock:
            color = BLOOD_COLORS.get(s.blood_type, "#888888")
            is_low = s.units < low_threshold
            percentage = min(100, int((s.units / 100) * 100))
            
            stock_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(s.blood_type, size=14, weight=ft.FontWeight.BOLD, color=color),
                            width=90,
                        ),
                        ft.Text(f"{s.units}", size=14, width=60, weight=ft.FontWeight.BOLD if is_low else None,
                               color="#C62828" if is_low else "#333333"),
                        ft.Container(
                            content=ft.Text("⚠️ LOW" if is_low else "✅ OK", 
                                          size=11, weight=ft.FontWeight.BOLD,
                                          color="white" if is_low else "#2E7D32"),
                            bgcolor="#C62828" if is_low else "#E8F5E9",
                            border_radius=10,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            width=70,
                        ),
                        ft.Column([
                            ft.ProgressBar(value=percentage/100, color=color, bgcolor="#EEEEEE", height=6),
                            ft.Text(f"{percentage}%", size=9, color="#888888"),
                        ], expand=True, spacing=1),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=8, horizontal=8),
                    bgcolor="#FFF5F5" if is_low else "#FAFAFA",
                    border_radius=6,
                    border=ft.border.all(1, "#FFCDD2" if is_low else "#E0E0E0"),
                )
            )
        page.update()

    def save_settings(e):
        try:
            new_threshold = int(low_stock_threshold_field.value) if low_stock_threshold_field.value else 5
            new_max_limit = int(max_stock_limit_field.value) if max_stock_limit_field.value else 100
            
            update_setting("low_stock_threshold", new_threshold)
            update_setting("max_stock_limit", new_max_limit)
            
            status_text.value = "✅ Settings saved!"
            status_text.color = "#2E7D32"
            render_stock()
        except ValueError:
            status_text.value = "❌ Please enter valid numbers."
            status_text.color = "#C62828"
        page.update()
        
    def update_stock_action(e):
        if not blood_dropdown.value or not stock_units.value or not action_dropdown.value:
            status_text.value = "❌ Please fill all fields"
            status_text.color = "#C62828"
            page.update()
            return
        if not stock_units.value.isdigit():
            status_text.value = "❌ Units must be a number"
            status_text.color = "#C62828"
            page.update()
            return
        units = int(stock_units.value)
        if units <= 0:
            status_text.value = "❌ Units must be greater than 0"
            status_text.color = "#C62828"
            page.update()
            return
        change = units if action_dropdown.value == "Add" else -units
        try:
            max_limit = int(max_stock_limit_field.value) if max_stock_limit_field.value else 100
        except:
            max_limit = 100
        success, message = update_stock(blood_dropdown.value, change, max_limit if change > 0 else None)
        if success:
            status_text.value = f"✅ {action_dropdown.value}ed {units} units of {blood_dropdown.value}"
            status_text.color = "#2E7D32"
            stock_units.value = ""
            blood_dropdown.value = None
            action_dropdown.value = None
            render_stock()
        else:
            status_text.value = f"❌ {message}"
            status_text.color = "#C62828"
        page.update()
    
    # Initial load
    refresh_donor_list()
    search_field.on_change = on_search_change
    render_stock()
    
    donation_section = ft.Column([
        ft.Row([
            ft.Text("💉 Record Donation", size=16, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "🔄 Refresh Donors", 
                on_click=lambda e: refresh_donor_list(), 
                bgcolor="#1976D2", 
                color="white", 
                icon=ft.Icons.REFRESH,
                height=35,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        search_field,
        search_results,
        selected_donor_info,
    ], spacing=8)
    
    # Stock Update Section
    stock_update_section = ft.Column([
        ft.Text("🔄 Manual Stock Update", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([blood_dropdown, stock_units, action_dropdown, ft.ElevatedButton("Update", on_click=update_stock_action, bgcolor="#1565C0", color="white")], spacing=10),
    ], spacing=8)
    
    # Settings Section
    settings_section = ft.Column([
        ft.Text("⚙️ Settings", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([low_stock_threshold_field, max_stock_limit_field, ft.ElevatedButton("Save", on_click=save_settings, bgcolor="#6A1B9A", color="white")], spacing=10),
    ], spacing=8)
    
    return ft.Column([
        ft.Text("📦 Blood Stock Management", size=24, weight=ft.FontWeight.BOLD),
        section("💉 Record Donation", donation_section),
        section("🔄 Update Stock", stock_update_section),
        section("⚙️ Settings", settings_section),
        ft.Text("📊 Current Stock Levels", size=16, weight=ft.FontWeight.BOLD),
        ft.Container(height=8),
        stock_col,
    ], scroll=ft.ScrollMode.AUTO, expand=True)