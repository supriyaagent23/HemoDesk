import flet as ft
from data.repository import get_all_donors, is_eligible_to_donate, get_donor_donation_history, get_settings
from ui.components import section, blood_badge

def build_eligibility_view(page: ft.Page):
    result_text = ft.Text("", size=14)
    history_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=300)
    
    settings = get_settings()
    wait_days = settings.get("donation_wait_days", 90)
    
    donors = get_all_donors()
    # Only show donors with known blood type (not "Unknown")
    eligible_donors = [d for d in donors if d.blood_type != "Unknown"]
    
    donor_dropdown = ft.Dropdown(
        label="Select Donor *",
        width=400,
        options=[ft.dropdown.Option(key=str(d.id), text=f"{d.name} ({d.blood_type}) - Last: {d.last_donation or 'Never'}")
                 for d in eligible_donors],
        hint_text="Choose a donor with known blood type"
    )
    
    def refresh_donors():
        nonlocal donors, eligible_donors
        donors = get_all_donors()
        eligible_donors = [d for d in donors if d.blood_type != "Unknown"]
        donor_dropdown.options = [
            ft.dropdown.Option(key=str(d.id), text=f"{d.name} ({d.blood_type}) - Last: {d.last_donation or 'Never'}")
            for d in eligible_donors
        ]
        page.update()
    
    def check_eligibility(e):
        if not donor_dropdown.value:
            result_text.value = "❌ Please select a donor first."
            result_text.color = "#C62828"
            page.update()
            return
        
        donor_id = int(donor_dropdown.value)
        eligible, message = is_eligible_to_donate(donor_id, wait_days)
        
        result_text.value = message
        result_text.color = "#2E7D32" if eligible else "#C62828"
        
        # Show donation history
        history = get_donor_donation_history(donor_id)
        history_col.controls.clear()
        
        if history:
            history_col.controls.append(
                ft.Text(f"📋 Donation History ({len(history)} records)", 
                       size=14, weight=ft.FontWeight.BOLD)
            )
            for h in history:
                history_col.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(h[1], size=12, width=100),  # date
                            blood_badge(h[3]),                   # blood type
                            ft.Text(f"{h[2]} units", size=12, width=80),  # units
                        ], spacing=10),
                        padding=8,
                        bgcolor="#f5f5f5",
                        border_radius=6,
                    )
                )
        else:
            history_col.controls.append(
                ft.Text("No donation history found for this donor.", size=12, color="#888888")
            )
        
        page.update()
    
    rules_info = ft.Container(
        content=ft.Column([
            ft.Text("📋 Donation Eligibility Rules", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• Must wait at least {wait_days} days between whole blood donations", size=13),
            ft.Text("• Hemoglobin level must be ≥ 12.5 g/dL", size=13),
            ft.Text("• Must be between 18-65 years old", size=13),
            ft.Text("• Should not have any infectious diseases", size=13),
            ft.Text("• Should not be on certain medications", size=13),
            ft.Text("• Should weigh at least 50 kg", size=13),
        ], spacing=6),
        padding=15,
        bgcolor="#E3F2FD",
        border_radius=10,
    )
    
    return ft.Column([
        ft.Text("Donor Eligibility Check", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(height=10, color="transparent"),
        
        section("Check Donor Eligibility", ft.Column([
            donor_dropdown,
            ft.Row([
                ft.ElevatedButton("Check Eligibility", on_click=check_eligibility, 
                                bgcolor="#1565C0", color="white"),
                ft.ElevatedButton("🔄 Refresh", on_click=lambda e: refresh_donors(), 
                                bgcolor="#6A1B9A", color="white", icon=ft.Icons.REFRESH),
            ], spacing=10),
            result_text,
        ], spacing=10)),
        
        section("Donation History", history_col),
        
        rules_info,
        
    ], scroll=ft.ScrollMode.AUTO, expand=True)