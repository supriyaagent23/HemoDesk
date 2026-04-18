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

    patient_field = ft.TextField(label="Patient Name *", width=220)

    # "Unknown" is included via BLOOD_TYPES_NO_ALL
    blood_dropdown = ft.Dropdown(
        label="Blood Type *", width=140,
        options=[ft.dropdown.Option(b) for b in BLOOD_TYPES_NO_ALL]
    )

    units_field = ft.TextField(
        label="Units *", width=100,
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=4,
        hint_text="Enter number"
    )

    urgency_dropdown = ft.Dropdown(
        label="Urgency *", width=130,
        options=[ft.dropdown.Option(u) for u in URGENCY_LEVELS]
    )

    filter_status = ft.Dropdown(
        label="Filter by Status", width=160, value="All",
        options=[ft.dropdown.Option("All")] +
                [ft.dropdown.Option(s) for s in STATUS_OPTIONS]
    )

    # ── list renderer ──────────────────────────────────────────────
    def render_list():
        requests = get_all_requests()
        if filter_status.value and filter_status.value != "All":
            requests = [r for r in requests if r.status == filter_status.value]

        list_col.controls.clear()
        list_col.controls.append(
            ft.Text(f"{len(requests)} request(s)", size=12, color="#888888"))

        for r in requests:
            is_unknown = r.blood_type == "Unknown"
            available  = 0 if is_unknown else get_stock_for_type(r.blood_type)

            def make_fulfill(rr):
                return lambda e: fulfill_request(rr)
            def make_reject(rid):
                return lambda e: do_update(rid, "Rejected")
            def make_delete(rid):
                return lambda e: do_delete(rid)

            # Extra notice row for Unknown blood type requests
            unknown_notice = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SCIENCE, size=14, color="#9C27B0"),
                    ft.Text(
                        "Blood type unconfirmed — go to Request Testing to update after lab results",
                        size=11, color="#9C27B0", italic=True
                    ),
                ], spacing=6),
                bgcolor="#F3E5F5",
                border_radius=6,
                padding=ft.Padding.symmetric(vertical=4, horizontal=8),
                visible=is_unknown,
            )

            list_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            blood_badge(r.blood_type),
                            urgency_badge(r.urgency),
                            status_badge(r.status),
                            ft.Text(r.created_date, size=11, color="#aaaaaa")
                        ], spacing=6),
                        ft.Text(f"Patient: {r.patient_name}", size=14,
                                weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"Requested: {r.units} units  |  "
                            + ("Blood type pending lab test" if is_unknown
                               else f"Available in stock: {available} units"),
                            size=12, color="#555555"
                        ),
                        unknown_notice,
                        ft.Row([
                            ft.ElevatedButton(
                                "Fulfill", bgcolor="#2E7D32", color="#ffffff",
                                on_click=make_fulfill(r),
                                disabled=r.status != "Pending" or is_unknown or available < r.units
                            ),
                            ft.OutlinedButton(
                                "Reject", on_click=make_reject(r.id),
                                disabled=r.status != "Pending"
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE, icon_color="#cc0000",
                                icon_size=18, on_click=make_delete(r.id)
                            )
                        ], spacing=8)
                    ], spacing=6),
                    padding=14,
                    bgcolor="#FFF8FF" if is_unknown else "#ffffff",
                    border_radius=8,
                    border=ft.Border.all(1, "#CE93D8" if is_unknown else "#e0e0e0")
                )
            )

        page.update()

    # ── actions ────────────────────────────────────────────────────
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
            status_text.value = "Please fill all required fields."
            status_text.color = "#C62828"
            page.update()
            return

        if not units_field.value.isdigit():
            status_text.value = "Units must be a number."
            status_text.color = "#C62828"
            page.update()
            return

        units = int(units_field.value)
        if units <= 0:
            status_text.value = "Units must be greater than 0."
            status_text.color = "#C62828"
            page.update()
            return

        add_request(Request(
            patient_name=patient_field.value.strip(),
            blood_type=blood_dropdown.value,
            units=units,
            urgency=urgency_dropdown.value
        ))

        patient_field.value  = ""
        units_field.value    = ""
        blood_dropdown.value = None
        urgency_dropdown.value = None

        if blood_dropdown.value == "Unknown":
            status_text.value = "Request added. Visit 'Request Testing' after lab results."
        else:
            status_text.value = "Request added."
        status_text.color = "#2E7D32"

        render_list()
        page.update()

    render_list()

    form = ft.Column([
        ft.Row([patient_field, blood_dropdown, units_field, urgency_dropdown],
               wrap=True, spacing=10),
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color="#9C27B0"),
                ft.Text(
                    "Select 'Unknown' if blood type is not yet confirmed — "
                    "update it later in the Request Testing page.",
                    size=11, color="#9C27B0"
                ),
            ], spacing=6),
            bgcolor="#F3E5F5", border_radius=6,
            padding=ft.Padding.symmetric(vertical=6, horizontal=10),
        ),
        ft.ElevatedButton("Add Request", on_click=submit,
                          bgcolor="#1565C0", color="#ffffff"),
        status_text
    ], spacing=10)

    return ft.Column([
        ft.Text("Blood Requests", size=24, weight=ft.FontWeight.BOLD),
        section("New Request", form),
        ft.Row([
            filter_status,
            ft.ElevatedButton("Filter", on_click=lambda e: render_list(),
                              bgcolor="#F57C00", color="#ffffff")
        ], spacing=8),
        ft.Container(height=8),
        list_col,
    ], expand=True)