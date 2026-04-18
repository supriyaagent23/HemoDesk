import flet as ft
from datetime import datetime
from data.repository import (
    get_stats, get_all_stock, get_expiring_blood, 
    get_expiry_stats, get_settings, get_all_donors,
    get_all_requests, is_eligible_to_donate
)
from ui.components import section, stat_card, BLOOD_COLORS, blood_badge

def build_dashboard_view(page: ft.Page, navigate_to=None):
    
    def refresh_data():
        stats = get_stats()
        stock = get_all_stock()
        settings = get_settings()
        expiry_warning_days = settings.get("expiry_warning_days", 14)
        expiring_blood = get_expiring_blood(expiry_warning_days)
        expiry_stats = get_expiry_stats()
        donors = get_all_donors()
        requests = get_all_requests()
        
        eligible_count = 0
        for donor in donors:
            eligible, _ = is_eligible_to_donate(donor.id)
            if eligible:
                eligible_count += 1
        
        urgent_requests = len([r for r in requests if r.urgency == "Critical" and r.status == "Pending"])
        total_blood = sum(s.units for s in stock)
        
        # Get recent donations (last 5)
        recent_donations = []
        for donor in donors[:5]:
            if donor.last_donation:
                recent_donations.append({
                    "name": donor.name,
                    "blood_type": donor.blood_type,
                    "date": donor.last_donation
                })
        
        # Get recent requests (last 5)
        recent_requests = requests[:5] if requests else []
        
        return {
            "stats": stats,
            "stock": stock,
            "expiring_blood": expiring_blood,
            "expiry_stats": expiry_stats,
            "eligible_count": eligible_count,
            "urgent_requests": urgent_requests,
            "total_blood": total_blood,
            "settings": settings,
            "recent_donations": recent_donations,
            "recent_requests": recent_requests
        }
    
    data = refresh_data()
    
    # ========== HEADER ==========
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning 🌅"
    elif current_hour < 17:
        greeting = "Good Afternoon ☀️"
    else:
        greeting = "Good Evening 🌙"
    
    header = ft.Container(
        content=ft.Column([
            ft.Text(greeting, size=20, color="#1565C0", weight=ft.FontWeight.BOLD),
            ft.Text("Welcome to HemoDesk Blood Bank Management System", 
                   size=16, color="#555555"),
            ft.Text(f"Today is {datetime.now().strftime('%A, %B %d, %Y')}", 
                   size=13, color="#888888"),
        ], spacing=5),
        padding=20,
        bgcolor="#E3F2FD",
        border_radius=15,
    )
    
    # ========== STAT CARDS ==========
    stat_cards_row1 = ft.Row([
        stat_card("🩸 Total Donors", data["stats"]["total_donors"], "#1565C0"),
        stat_card("💉 Total Donations", data["stats"]["total_donations"], "#2E7D32"),
        stat_card("⏳ Pending Requests", data["stats"]["pending_requests"], "#F57C00", 
                 warning=data["stats"]["pending_requests"] > 0),
        stat_card("🆘 Urgent Requests", data["urgent_requests"], "#C62828", 
                 warning=data["urgent_requests"] > 0),
    ], wrap=True, spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    stat_cards_row2 = ft.Row([
        stat_card("✅ Eligible Donors", data["eligible_count"], "#6A1B9A"),
        stat_card("📦 Total Blood Units", data["total_blood"], "#00695C"),
        stat_card("⚠️ Low Stock Types", data["stats"]["low_stock"], "#E65100", 
                 warning=data["stats"]["low_stock"] > 0),
        stat_card("🕐 Expiring Soon", data["expiry_stats"]["expiring_soon_units"], "#F57C00", 
                 warning=data["expiry_stats"]["expiring_soon_units"] > 0),
    ], wrap=True, spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # ========== BLOOD STOCK OVERVIEW ==========
    low_threshold = data["settings"].get("low_stock_threshold", 5)
    max_limit = data["settings"].get("max_stock_limit", 100)
    
    stock_header = ft.Container(
        content=ft.Row([
            ft.Text("Blood Type", size=14, weight=ft.FontWeight.BOLD, width=100),
            ft.Text("Units", size=14, weight=ft.FontWeight.BOLD, width=80),
            ft.Text("Status", size=14, weight=ft.FontWeight.BOLD, width=100),
            ft.Text("Progress", size=14, weight=ft.FontWeight.BOLD, expand=True),
        ], spacing=10),
        padding=10,
        bgcolor="#E0E0E0",
        border_radius=8,
    )
    
    stock_rows = ft.Column(spacing=5)
    
    for s in data["stock"]:
        color = BLOOD_COLORS.get(s.blood_type, "#888888")
        is_low = s.units < low_threshold
        percentage = min(100, int((s.units / max_limit) * 100))
        
        if is_low:
            status_text = "⚠️ LOW STOCK"
            status_color = "#C62828"
        elif s.units >= max_limit * 0.8:
            status_text = "✅ High"
            status_color = "#2E7D32"
        elif s.units >= max_limit * 0.5:
            status_text = "📦 Medium"
            status_color = "#F57C00"
        else:
            status_text = "🩸 Normal"
            status_color = "#1565C0"
        
        stock_rows.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        ft.Text(s.blood_type, size=16, weight=ft.FontWeight.BOLD, color=color),
                        width=100,
                    ),
                    ft.Text(f"{s.units} / {max_limit}", size=14, width=80),
                    ft.Text(status_text, size=13, color=status_color, weight=ft.FontWeight.BOLD, width=100),
                    ft.Column([
                        ft.ProgressBar(value=percentage/100, color=color, bgcolor="#EEEEEE", height=8),
                        ft.Text(f"{percentage}% of max capacity", size=10, color="#888888"),
                    ], expand=True, spacing=2),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding.symmetric(vertical=8, horizontal=10),
                bgcolor="#FAFAFA",
                border_radius=6,
                border=ft.Border.all(1, color if is_low else "#E0E0E0"),
            )
        )
    
    stock_overview = ft.Column([
        stock_header,
        stock_rows,
        ft.Text(f"📌 Low stock threshold: {low_threshold} units | Maximum capacity: {max_limit} units", 
               size=11, color="#888888", italic=True),
    ], spacing=5)
    
    # ========== EXPIRING BLOOD SECTION ==========
    expiring_col = ft.Column(spacing=8)
    
    if data["expiry_stats"]["expired_units"] > 0:
        expiring_col.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.WARNING, color="#C62828", size=20),
                    ft.Text(f"⚠️ {data['expiry_stats']['expired_units']} units have EXPIRED!", 
                           size=13, color="#C62828", weight=ft.FontWeight.BOLD),
                ], spacing=10),
                padding=10,
                bgcolor="#FFCDD2",
                border_radius=8,
            )
        )
    
    if data["expiring_blood"]:
        for item in data["expiring_blood"][:3]:
            days_left = item['days_left']
            if days_left < 0:
                status_text = "EXPIRED"
                bgcolor = "#FFCDD2"
                color = "#C62828"
            elif days_left <= 7:
                status_text = f"CRITICAL - {days_left} days left"
                bgcolor = "#FFEBEE"
                color = "#C62828"
            elif days_left <= 14:
                status_text = f"Expiring soon - {days_left} days left"
                bgcolor = "#FFF8E1"
                color = "#F57C00"
            else:
                status_text = f"Expires in {days_left} days"
                bgcolor = "#E3F2FD"
                color = "#1565C0"
            
            expiring_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"🩸 {item['blood_type']}", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{item['units']} units", size=12),
                        ft.Text(status_text, size=12, color=color, weight=ft.FontWeight.BOLD),
                    ], spacing=10, wrap=True),
                    padding=10,
                    bgcolor=bgcolor,
                    border_radius=8,
                    border=ft.Border.all(1, color)
                )
            )
    else:
        expiring_col.controls.append(
            ft.Text(f"✅ No blood units expiring soon", size=12, color="#2E7D32")
        )
    
        # ========== QUICK ACTIONS (Clearly visible buttons) ==========
    quick_actions = ft.Container(
        content=ft.Column([
            ft.Text("⚡ Quick Actions", size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(height=5),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PERSON_ADD, size=30, color="#1565C0"),
                        ft.Text("Add Donor", size=12, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    on_click=lambda e: navigate_to(1) if navigate_to else None,
                    padding=15,
                    bgcolor="#E3F2FD",
                    border_radius=10,
                    expand=True,
                    ink=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.FAVORITE, size=30, color="#2E7D32"),
                        ft.Text("Record Donation", size=12, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    on_click=lambda e: navigate_to(4) if navigate_to else None,
                    padding=15,
                    bgcolor="#E8F5E9",
                    border_radius=10,
                    expand=True,
                    ink=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ASSIGNMENT, size=30, color="#F57C00"),
                        ft.Text("New Request", size=12, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    on_click=lambda e: navigate_to(3) if navigate_to else None,
                    padding=15,
                    bgcolor="#FFF3E0",
                    border_radius=10,
                    expand=True,
                    ink=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.HEALTH_AND_SAFETY, size=30, color="#6A1B9A"),
                        ft.Text("Check Eligibility", size=12, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    on_click=lambda e: navigate_to(6) if navigate_to else None,
                    padding=15,
                    bgcolor="#F3E5F5",
                    border_radius=10,
                    expand=True,
                    ink=True,
                ),
            ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=10),
        padding=15,
        bgcolor="#ffffff",
        border_radius=12,
        border=ft.Border.all(1, "#E0E0E0"),
        margin=ft.Margin.only(bottom=15),
    )
    
    # ========== RECENT ACTIVITY SECTION ==========
    
    # Recent Donations
    recent_donations_col = ft.Column(spacing=5)
    if data["recent_donations"]:
        for donation in data["recent_donations"]:
            recent_donations_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("🩸", size=16),
                        ft.Text(donation["name"], size=13, weight=ft.FontWeight.BOLD, expand=True),
                        blood_badge(donation["blood_type"]),
                        ft.Text(donation["date"], size=11, color="#888888"),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=8,
                    bgcolor="#FAFAFA",
                    border_radius=6,
                )
            )
    else:
        recent_donations_col.controls.append(
            ft.Text("No donations recorded yet", size=12, color="#888888")
        )
    
    # Recent Requests
    recent_requests_col = ft.Column(spacing=5)
    if data["recent_requests"]:
        for request in data["recent_requests"]:
            status_color = "#F57C00" if request.status == "Pending" else "#2E7D32" if request.status == "Fulfilled" else "#C62828"
            recent_requests_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("📋", size=16),
                        ft.Text(request.patient_name, size=13, weight=ft.FontWeight.BOLD, expand=True),
                        blood_badge(request.blood_type),
                        ft.Text(f"{request.units} units", size=11),
                        ft.Container(
                            content=ft.Text(request.status, size=10, color="#ffffff"),
                            bgcolor=status_color,
                            padding=ft.Padding.symmetric(vertical=2, horizontal=6),
                            border_radius=4,
                        ),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=8,
                    bgcolor="#FAFAFA",
                    border_radius=6,
                )
            )
    else:
        recent_requests_col.controls.append(
            ft.Text("No requests yet", size=12, color="#888888")
        )
    
    # ========== TWO COLUMN LAYOUT FOR RECENT ACTIVITIES ==========
    recent_activities = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Text("📋 Recent Donations", size=14, weight=ft.FontWeight.BOLD),
                ft.Divider(height=5),
                recent_donations_col,
            ], spacing=8),
            expand=True,
            padding=12,
            bgcolor="#ffffff",
            border_radius=10,
            border=ft.Border.all(1, "#E0E0E0"),
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("📌 Recent Blood Requests", size=14, weight=ft.FontWeight.BOLD),
                ft.Divider(height=5),
                recent_requests_col,
            ], spacing=8),
            expand=True,
            padding=12,
            bgcolor="#ffffff",
            border_radius=10,
            border=ft.Border.all(1, "#E0E0E0"),
        ),
    ], spacing=15, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # ========== TIPS & COMPATIBILITY SECTION ==========
    tips_section = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LIGHTBULB, color="#F57C00", size=18),
                    ft.Text("Did You Know?", size=14, weight=ft.FontWeight.BOLD, color="#F57C00"),
                ], spacing=5),
                ft.Text("• Blood can be stored for only 42 days after donation", size=11, color="#555555"),
                ft.Text("• Donors must wait 90 days between whole blood donations", size=11, color="#555555"),
                ft.Text("• One donation can save up to 3 lives", size=11, color="#555555"),
                ft.Text("• Only 37% of the population is eligible to donate blood", size=11, color="#555555"),
            ], spacing=5),
            padding=12,
            bgcolor="#FFF8E1",
            border_radius=10,
            expand=True,
        ),
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.FAVORITE, color="#C62828", size=18),
                    ft.Text("Quick Compatibility", size=14, weight=ft.FontWeight.BOLD, color="#C62828"),
                ], spacing=5),
                ft.Text("🩸 O- → Universal Donor", size=11),
                ft.Text("🩸 AB+ → Universal Recipient", size=11),
                ft.Text("🩸 O+ → Most Common (37%)", size=11),
                ft.Text("🩸 AB- → Rarest (<1%)", size=11),
            ], spacing=5),
            padding=12,
            bgcolor="#FFEBEE",
            border_radius=10,
            expand=True,
        ),
    ], spacing=15)
    
    # ========== MAIN RETURN ==========
    return ft.Column([
        header,
        section("📊 Key Metrics", stat_cards_row1),
        section("📈 More Metrics", stat_cards_row2),
        section("🩸 Blood Stock Overview", stock_overview),
        section("⚠️ Blood Expiry Alerts", expiring_col),
        section("⚡ Quick Actions", quick_actions),
        section("📋 Recent Activity", recent_activities),
        tips_section,
    ], scroll=ft.ScrollMode.AUTO, expand=True)