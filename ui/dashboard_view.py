import flet as ft
from datetime import datetime
from data.repository import get_stats, get_all_stock, get_pending_lab_donations


def build_dashboard_view(page: ft.Page, navigate_to):
    
    # Get fresh data
    stats = get_stats()
    stock = get_all_stock()
    pending_lab = get_pending_lab_donations()
    total_blood = sum(s.units for s in stock)
    
    
    colors = {
        "primary": "#2563EB",
        "success": "#10B981",
        "warning": "#F59E0B",
        "info": "#06B6D4",
        "background": "#F9FAFB",
        "card": "#FFFFFF",
        "text_primary": "#1F2937",
        "text_secondary": "#6B7280",
        "border": "#E5E7EB",
    }
    
    
    sections = []
    
    # 1. Header
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
        emoji = "🌅"
    elif current_hour < 17:
        greeting = "Good Afternoon"
        emoji = "☀️"
    else:
        greeting = "Good Evening"
        emoji = "🌙"
    
    header = ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text(f"{greeting}, {emoji}", size=22, weight=ft.FontWeight.BOLD, color=colors["text_primary"]),
                ft.Text(datetime.now().strftime("%A, %B %d, %Y"), size=13, color=colors["text_secondary"]),
            ], spacing=5),
            ft.Container(
                content=ft.Icon(ft.Icons.BLOODTYPE, size=45, color=colors["primary"]),
                bgcolor="#EFF6FF",
                border_radius=25,
                padding=10,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.all(20),
        bgcolor=colors["card"],
        border_radius=15,
    )
    sections.append(header)
    
    # 2. Stats Row
    stats_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text(str(stats["total_donors"]), size=28, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                    ft.Text("Total Donors", size=12, color=colors["text_secondary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=15,
                bgcolor=colors["card"],
                border_radius=12,
                expand=True,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(str(stats["total_donations"]), size=28, weight=ft.FontWeight.BOLD, color=colors["success"]),
                    ft.Text("Donations", size=12, color=colors["text_secondary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=15,
                bgcolor=colors["card"],
                border_radius=12,
                expand=True,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(str(total_blood), size=28, weight=ft.FontWeight.BOLD, color=colors["info"]),
                    ft.Text("Blood Units", size=12, color=colors["text_secondary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=15,
                bgcolor=colors["card"],
                border_radius=12,
                expand=True,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(str(len(pending_lab)), size=28, weight=ft.FontWeight.BOLD, color=colors["warning"]),
                    ft.Text("Pending Tests", size=12, color=colors["text_secondary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=15,
                bgcolor=colors["card"],
                border_radius=12,
                expand=True,
            ),
        ],
        spacing=12,
    )
    sections.append(stats_row)
    
    # 3. Quick Actions
    actions_row = ft.Row(
        controls=[
            ft.ElevatedButton("➕ Add Donor", on_click=lambda e: navigate_to(1), 
                            bgcolor=colors["primary"], color="white", expand=True),
            ft.ElevatedButton("🔬 Test & Donate", on_click=lambda e: navigate_to(4), 
                            bgcolor=colors["success"], color="white", expand=True),
            ft.ElevatedButton("📦 View Stock", on_click=lambda e: navigate_to(2), 
                            bgcolor=colors["info"], color="white", expand=True),
            ft.ElevatedButton("📋 New Request", on_click=lambda e: navigate_to(3), 
                            bgcolor="#8B5CF6", color="white", expand=True),
        ],
        spacing=10,
    )
    sections.append(actions_row)
    
    # 4. Blood Stock Section
    blood_colors = {
        "A+": "#2563EB", "A-": "#3B82F6",
        "B+": "#10B981", "B-": "#34D399",
        "AB+": "#8B5CF6", "AB-": "#A78BFA",
        "O+": "#EF4444", "O-": "#F87171",
    }
    
    stock_title = ft.Text("🩸 Blood Stock Levels", size=16, weight=ft.FontWeight.BOLD)
    stock_grid = ft.Row(wrap=True, spacing=10)
    
    for s in stock:
        color = blood_colors.get(s.blood_type, "#6B7280")
        is_low = s.units < 5
        percentage = min(100, (s.units / 100) * 100)
        
        stock_grid.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(s.blood_type, size=18, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(f"{s.units} units", size=20, weight=ft.FontWeight.BOLD),
                    ft.ProgressBar(value=percentage/100, width=100, height=6, 
                                  color=colors["warning"] if is_low else color, bgcolor="#F3F4F6"),
                    ft.Text(f"{percentage:.0f}%", size=11, color=colors["text_secondary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                width=130,
                padding=12,
                bgcolor="#F9FAFB",
                border_radius=10,
            )
        )
    
    stock_section = ft.Container(
        content=ft.Column([stock_title, ft.Divider(), stock_grid], spacing=10),
        padding=15,
        bgcolor=colors["card"],
        border_radius=12,
    )
    sections.append(stock_section)
    
    # 5. Pending Lab Tests (if any)
    if pending_lab:
        lab_title = ft.Text("🔬 Pending Lab Tests", size=16, weight=ft.FontWeight.BOLD)
        lab_list = ft.Column(spacing=8)
        
        for lab in pending_lab[:3]:
            lab_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON, size=20, color=colors["warning"]),
                        ft.Text(lab['donor_name'], size=14, weight=ft.FontWeight.W_500, expand=True),
                        ft.ElevatedButton("Test Now", on_click=lambda e: navigate_to(4), 
                                        bgcolor=colors["warning"], color="white", height=35),
                    ], spacing=10),
                    padding=10,
                    bgcolor="#FFFBEB",
                    border_radius=8,
                )
            )
        
        if len(pending_lab) > 3:
            lab_list.controls.append(
                ft.Text(f"+ {len(pending_lab) - 3} more donors", size=12, color=colors["text_secondary"])
            )
        
        lab_section = ft.Container(
            content=ft.Column([lab_title, ft.Divider(), lab_list], spacing=10),
            padding=15,
            bgcolor=colors["card"],
            border_radius=12,
        )
        sections.append(lab_section)
    
    # 6. Bottom Stats
    bottom_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text("📊", size=24),
                    ft.Text(str(stats["pending_requests"]), size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Pending Requests", size=11, color=colors["text_secondary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                expand=True,
                padding=15,
                bgcolor=colors["card"],
                border_radius=12,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("🎉", size=24),
                    ft.Text(str(stats["thank_you_sent"]), size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Thank Yous Sent", size=11, color=colors["text_secondary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                expand=True,
                padding=15,
                bgcolor=colors["card"],
                border_radius=12,
            ),
        ],
        spacing=12,
    )
    sections.append(bottom_row)
    
    # Combine all sections with spacing
    dashboard_content = ft.Column(
        controls=sections,
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
    )
    
    return ft.Container(
        content=dashboard_content,
        expand=True,
        padding=15,
        bgcolor=colors["background"],
    )