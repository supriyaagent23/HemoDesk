import flet as ft
from data.repository import (
    add_request, get_all_requests, update_request_status,
    delete_request, get_stock_for_type, update_stock
)
from models.request import Request
from ui.components import (
    section, blood_badge, status_badge, urgency_badge,
    BLOOD_TYPES_NO_ALL, URGENCY_LEVELS, STATUS_OPTIONS
)


def build_requests_view(page: ft.Page):
    status_text = ft.Text("", color="green", size=12)
    list_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    # Form fields with FIXED widths for proper alignment
    patient_field = ft.TextField(label="Patient Name *", width=220, hint_text="Enter patient name")
    
    blood_dropdown = ft.Dropdown(
        label="Blood Type *", width=150,
        options=[ft.dropdown.Option(b) for b in BLOOD_TYPES_NO_ALL],
        hint_text="Select blood type"
    )

    units_field = ft.TextField(
        label="Units *", width=120,
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=4,
        hint_text="Enter number"
    )

    urgency_dropdown = ft.Dropdown(
        label="Urgency *", width=160,
        options=[ft.dropdown.Option(u) for u in URGENCY_LEVELS],
        hint_text="Select urgency"
    )

    filter_status = ft.Dropdown(
        label="Filter by Status", width=180, value="All",
        options=[ft.dropdown.Option("All")] +
                [ft.dropdown.Option(s) for s in STATUS_OPTIONS]
    )

    def render_list():
        requests = get_all_requests()
        if filter_status.value and filter_status.value != "All":
            requests = [r for r in requests if r.status == filter_status.value]

        list_col.controls.clear()
        list_col.controls.append(
            ft.Text(f"{len(requests)} request(s)", size=12, color="#888888"))

        if not requests:
            list_col.controls.append(
                ft.Container(
                    content=ft.Text("No requests found.", size=13, color="#888888"),
                    padding=20,
                )
            )

        for r in requests:
            is_unknown = r.blood_type == "Unknown"
            available = 0 if is_unknown else get_stock_for_type(r.blood_type)

            def make_fulfill(rr):
                return lambda e: fulfill_request(rr)
            def make_reject(rid):
                return lambda e: do_update(rid, "Rejected")
            def make_delete(rid):
                return lambda e: do_delete(rid)

            unknown_notice = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SCIENCE, size=14, color="#9C27B0"),
                    ft.Text(
                        "Blood type unconfirmed — go to Lab Tests to update",
                        size=11, color="#9C27B0", italic=True
                    ),
                ], spacing=6),
                bgcolor="#F3E5F5",
                border_radius=6,
                padding=ft.padding.symmetric(vertical=4, horizontal=8),
                visible=is_unknown,
            )

            request_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            blood_badge(r.blood_type),
                            urgency_badge(r.urgency),
                            status_badge(r.status),
                            ft.Text(r.created_date[:10] if r.created_date else "", size=11, color="#aaaaaa")
                        ], spacing=8),
                        ft.Text(f"Patient: {r.patient_name}", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Text(f"📦 Requested: {r.units} units", size=13, color="#555555"),
                            ft.Text(f"📊 Available: {available} units" if not is_unknown else "⏳ Pending lab test", 
                                   size=13, color="#C62828" if not is_unknown and available < r.units else "#2E7D32"),
                        ], spacing=20),
                        unknown_notice,
                        ft.Row([
                            ft.ElevatedButton(
                                "✅ Fulfill", bgcolor="#2E7D32", color="#ffffff",
                                on_click=make_fulfill(r),
                                disabled=r.status != "Pending" or is_unknown or available < r.units
                            ),
                            ft.OutlinedButton(
                                "❌ Reject", on_click=make_reject(r.id),
                                disabled=r.status != "Pending"
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE, icon_color="#cc0000",
                                icon_size=18, on_click=make_delete(r.id)
                            )
                        ], spacing=8)
                    ], spacing=8),
                    padding=15,
                    bgcolor="#FFF8FF" if is_unknown else "#ffffff",
                ),
                elevation=2 if is_unknown else 1,
            )
            list_col.controls.append(request_card)

        page.update()

    def fulfill_request(r):
        update_stock(r.blood_type, -r.units)
        do_update(r.id, "Fulfilled")

    def do_update(rid, new_status):
        update_request_status(rid, new_status)
        render_list()

    def do_delete(rid):
        delete_request(rid)
        render_list()

    def submit(e):
        if (not patient_field.value or not blood_dropdown.value
                or not units_field.value or not urgency_dropdown.value):
            status_text.value = "❌ Please fill all required fields"
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

        add_request(Request(
            patient_name=patient_field.value.strip(),
            blood_type=blood_dropdown.value,
            units=units,
            urgency=urgency_dropdown.value
        ))

        patient_field.value = ""
        units_field.value = ""
        blood_dropdown.value = None
        urgency_dropdown.value = None

        status_text.value = "✅ Request added successfully"
        status_text.color = "#2E7D32"

        render_list()
        page.update()

    render_list()

    form = ft.Column([
        ft.Row([
            patient_field,
            blood_dropdown,
            units_field,
            urgency_dropdown,
        ], spacing=15, wrap=False, vertical_alignment=ft.CrossAxisAlignment.START),
        ft.ElevatedButton("📝 Add Request", on_click=submit, bgcolor="#1565C0", color="#ffffff"),
        status_text
    ], spacing=12)

    return ft.Column([
        ft.Text("📋 Patient Blood Requests", size=28, weight=ft.FontWeight.BOLD),
        section("➕ New Request", form),
        ft.Row([
            filter_status,
            ft.ElevatedButton("🔄 Filter", on_click=lambda e: render_list(), bgcolor="#F57C00", color="#ffffff")
        ], spacing=10),
        ft.Container(height=8),
        list_col,
    ], expand=True)