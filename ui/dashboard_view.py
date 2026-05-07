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
        "primary":"#C0152A",   
        "primary_soft": "#F9E5E8",   
        "primary_mid": "#E8A0AA",   
        "success": "#0D7A5F", 
        "success_soft": "#E3F5F0",
        "warning": "#B45309",   
        "warning_soft": "#FEF3C7",
        "info": "#1D4ED8", 
        "info_soft": "#EFF6FF",
        "background": "#F4F5F7",   
        "card": "#FFFFFF",
        "card_elevated": "#FAFAFA",
        "border": "#E2E4E9",
        "divider": "#ECEEF2",

        # Text
        "text_heading": "#111827",
        "text_primary": "#1F2937",
        "text_secondary": "#6B7280",
        "text_muted": "#9CA3AF",

        # Blood-type accent map
        "bt_red_dark": "#991B1B",
        "bt_red_mid": "#DC2626",
        "bt_red_light": "#F87171",
        "bt_green_dark": "#065F46",
        "bt_green_mid": "#059669",
        "bt_green_light": "#34D399",
        "bt_purple_dark": "#5B21B6",
        "bt_purple_mid": "#7C3AED",
        "bt_purple_light": "#A78BFA",
        "bt_blue_dark": "#1E40AF",
        "bt_blue_mid": "#3B82F6",
        "bt_blue_light": "#93C5FD",
    }

    sections = []

    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting, emoji, sub_emoji = "Good Morning", "🌅", "Rise & save lives"
    elif current_hour < 17:
        greeting, emoji, sub_emoji = "Good Afternoon", "☀️", "Every drop counts"
    else:
        greeting, emoji, sub_emoji = "Good Evening", "🌙", "End the day strong"

    header = ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text(
                    f"{emoji}  {greeting}",
                    size=20,
                    weight=ft.FontWeight.W_700,
                    color=colors["text_heading"],
                ),
                ft.Text(
                    datetime.now().strftime("%A, %B %d, %Y"),
                    size=12,
                    color=colors["text_secondary"],
                ),
                ft.Text(
                    sub_emoji,
                    size=11,
                    color=colors["primary"],
                    italic=True,
                ),
            ], spacing=4),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.BLOODTYPE, size=32, color=colors["primary"]),
                    ft.Text("BloodBank", size=10, weight=ft.FontWeight.W_600, color=colors["primary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                bgcolor=colors["primary_soft"],
                border_radius=14,
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.symmetric(horizontal=18, vertical=16),
        bgcolor=colors["card"],
        border_radius=16,
        border=ft.border.all(1, colors["border"]),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )
    sections.append(header)

    def stat_card(value, label, color, bg_color, icon):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icon, size=18, color=color),
                    bgcolor=bg_color,
                    border_radius=8,
                    padding=6,
                    width=34,
                    height=34,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text(
                    str(value),
                    size=26,
                    weight=ft.FontWeight.W_800,
                    color=colors["text_heading"],
                ),
                ft.Text(
                    label,
                    size=11,
                    color=colors["text_secondary"],
                    text_align=ft.TextAlign.CENTER,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            padding=ft.padding.symmetric(horizontal=10, vertical=14),
            bgcolor=colors["card"],
            border_radius=14,
            border=ft.border.all(1, colors["border"]),
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    stats_row = ft.Row(
        controls=[
            stat_card(stats["total_donors"], "Donors", colors["primary"], colors["primary_soft"], ft.Icons.PEOPLE_ALT),
            stat_card(stats["total_donations"], "Donations", colors["success"], colors["success_soft"], ft.Icons.VOLUNTEER_ACTIVISM),
            stat_card(total_blood, "Units", colors["info"], colors["info_soft"], ft.Icons.WATER_DROP),
            stat_card(len(pending_lab), "Pending", colors["warning"], colors["warning_soft"], ft.Icons.SCIENCE),
        ],
        spacing=10,
    )
    sections.append(stats_row)

    def action_btn(label, icon, color, bg, index):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=20, color=color),
                ft.Text(label, size=11, weight=ft.FontWeight.W_600, color=color, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            on_click=lambda e: navigate_to(index),
            expand=True,
            bgcolor=bg,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=8, vertical=12),
            border=ft.border.all(1.5, color),
            ink=True,
        )

    actions_row = ft.Row(
        controls=[
            action_btn("Add Donor", ft.Icons.PERSON_ADD,colors["primary"], colors["primary_soft"], 1),
            action_btn("Test & Donate", ft.Icons.SCIENCE, colors["success"], colors["success_soft"], 4),
            action_btn("View Stock", ft.Icons.INVENTORY_2, colors["info"], colors["info_soft"], 2),
            action_btn("New Request", ft.Icons.NOTE_ADD, "#7C3AED", "#F5F3FF", 3),
        ],
        spacing=10,
    )
    sections.append(actions_row)

    blood_meta = {
        "A+":  (colors["bt_red_mid"],    "#FEF2F2"),
        "A-":  (colors["bt_red_dark"],   "#FEF2F2"),
        "B+":  (colors["bt_green_mid"],  "#F0FDF4"),
        "B-":  (colors["bt_green_dark"], "#F0FDF4"),
        "AB+": (colors["bt_purple_mid"], "#F5F3FF"),
        "AB-": (colors["bt_purple_dark"],"#F5F3FF"),
        "O+":  (colors["bt_blue_mid"],   "#EFF6FF"),
        "O-":  (colors["bt_blue_dark"],  "#EFF6FF"),
    }

    stock_title = ft.Row([
        ft.Icon(ft.Icons.WATER_DROP, size=16, color=colors["primary"]),
        ft.Text("Blood Stock Levels", size=15, weight=ft.FontWeight.W_700, color=colors["text_heading"]),
    ], spacing=6)

    stock_grid = ft.Row(wrap=True, spacing=10, run_spacing=10)

    for s in stock:
        color, bg = blood_meta.get(s.blood_type, ("#6B7280", "#F9FAFB"))
        is_low = s.units < 5
        bar_color = "#EF4444" if is_low else color
        percentage = min(100, s.units)  # treat 100 units as full

        stock_grid.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(
                                s.blood_type,
                                size=13,
                                weight=ft.FontWeight.W_800,
                                color=color,
                            ),
                            bgcolor=bg,
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=7, vertical=3),
                        ),
                        ft.Container(expand=True),
                        ft.Text(
                            "⚠" if is_low else "✓",
                            size=12,
                            color=bar_color,
                        ),
                    ]),
                    ft.Text(
                        f"{s.units}",
                        size=24,
                        weight=ft.FontWeight.W_800,
                        color=colors["text_heading"],
                    ),
                    ft.Text("units", size=10, color=colors["text_muted"]),
                    ft.ProgressBar(
                        value=percentage / 100,
                        width=110,
                        height=5,
                        color=bar_color,
                        bgcolor=colors["divider"],
                        border_radius=3,
                    ),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.START),
                width=130,
                padding=12,
                bgcolor=colors["card"],
                border_radius=12,
                border=ft.border.all(1, colors["border"]),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=5,
                    color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK),
                    offset=ft.Offset(0, 1),
                ),
            )
        )

    stock_section = ft.Container(
        content=ft.Column([stock_title, ft.Divider(height=1, color=colors["divider"]), stock_grid], spacing=12),
        padding=16,
        bgcolor=colors["card"],
        border_radius=16,
        border=ft.border.all(1, colors["border"]),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )
    sections.append(stock_section)

    if pending_lab:
        lab_title = ft.Row([
            ft.Icon(ft.Icons.SCIENCE, size=16, color=colors["warning"]),
            ft.Text("Pending Lab Tests", size=15, weight=ft.FontWeight.W_700, color=colors["text_heading"]),
            ft.Container(
                content=ft.Text(str(len(pending_lab)), size=11, color="#FFFFFF", weight=ft.FontWeight.W_700),
                bgcolor=colors["warning"],
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=7, vertical=2),
            ),
        ], spacing=6)

        lab_list = ft.Column(spacing=8)

        for lab in pending_lab[:3]:
            lab_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.PERSON, size=18, color=colors["warning"]),
                            bgcolor=colors["warning_soft"],
                            border_radius=8,
                            padding=7,
                            width=34,
                            height=34,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text(
                            lab['donor_name'],
                            size=13,
                            weight=ft.FontWeight.W_500,
                            expand=True,
                            color=colors["text_primary"],
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Test Now",
                                size=12,
                                color=colors["warning"],
                                weight=ft.FontWeight.W_600,
                            ),
                            on_click=lambda e: navigate_to(4),
                            bgcolor=colors["warning_soft"],
                            border_radius=8,
                            padding=ft.padding.symmetric(horizontal=10, vertical=6),
                            border=ft.border.all(1, colors["warning"]),
                            ink=True,
                        ),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    bgcolor="#FFFCF5",
                    border_radius=10,
                    border=ft.border.all(1, "#FDE68A"),
                )
            )

        if len(pending_lab) > 3:
            lab_list.controls.append(
                ft.Text(
                    f"+ {len(pending_lab) - 3} more pending",
                    size=12,
                    color=colors["text_muted"],
                    italic=True,
                )
            )

        lab_section = ft.Container(
            content=ft.Column([lab_title, ft.Divider(height=1, color=colors["divider"]), lab_list], spacing=12),
            padding=16,
            bgcolor=colors["card"],
            border_radius=16,
            border=ft.border.all(1, colors["border"]),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
        sections.append(lab_section)

    def bottom_stat(icon_str, value, label, color, bg):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(icon_str, size=20),
                    bgcolor=bg,
                    border_radius=10,
                    padding=8,
                    width=40,
                    height=40,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(str(value), size=20, weight=ft.FontWeight.W_800, color=colors["text_heading"]),
                    ft.Text(label, size=11, color=colors["text_secondary"]),
                ], spacing=2),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            padding=ft.padding.symmetric(horizontal=14, vertical=14),
            bgcolor=colors["card"],
            border_radius=14,
            border=ft.border.all(1, colors["border"]),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    bottom_row = ft.Row(
        controls=[
            bottom_stat("📊", stats["pending_requests"], "Pending Requests", colors["info"],    colors["info_soft"]),
            bottom_stat("🎉", stats["thank_you_sent"],   "Thank Yous Sent",  colors["success"], colors["success_soft"]),
        ],
        spacing=12,
    )
    sections.append(bottom_row)

    dashboard_content = ft.Column(
        controls=sections,
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Container(
        content=dashboard_content,
        expand=True,
        padding=14,
        bgcolor=colors["background"],
    )