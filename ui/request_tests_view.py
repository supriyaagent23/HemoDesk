import flet as ft
from data.repository import get_pending_requests_unknown, update_request_blood_type_and_units
from ui.components import urgency_badge, BLOOD_TYPES


def build_request_tests_view(page: ft.Page):
    list_col   = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    status_text = ft.Text("", size=12)

    # ── render ─────────────────────────────────────────────────────
    def render_list():
        requests = get_pending_requests_unknown()
        list_col.controls.clear()

        if not requests:
            list_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SCIENCE, size=52, color="#CCCCCC"),
                        ft.Text("No pending requests awaiting blood type confirmation",
                                size=14, color="#888888"),
                        ft.Text(
                            "Add a request with 'Unknown' blood type to see it here",
                            size=12, color="#AAAAAA"
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=50, alignment=ft.Alignment(0, 0),
                )
            )
        else:
            list_col.controls.append(
                ft.Text(f"{len(requests)} request(s) awaiting lab confirmation",
                        size=12, color="#888888")
            )

            for row in requests:
                req_id, patient_name, blood_type, units, urgency, status, created_date = row

                blood_dd = ft.Dropdown(
                    width=160,
                    label="Confirmed Blood Type *",
                    hint_text="Select after test",
                    options=[ft.dropdown.Option(bt) for bt in BLOOD_TYPES],
                )

                units_field = ft.TextField(
                    label="Units Needed *",
                    width=130,
                    value=str(units),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    max_length=4,
                )

                def make_save(rid, pname, dd, uf):
                    return lambda e: do_save(rid, pname, dd, uf)

                list_col.controls.append(
                    ft.Container(
                        content=ft.Column([
                            # Header row
                            ft.Row([
                                ft.Icon(ft.Icons.SCIENCE, size=20, color="#9C27B0"),
                                ft.Text("AWAITING BLOOD TYPE CONFIRMATION",
                                        size=12, weight=ft.FontWeight.BOLD, color="#9C27B0"),
                                urgency_badge(urgency),
                                ft.Text(
                                    created_date[:10] if created_date else "—",
                                    size=11, color="#aaaaaa"
                                ),
                            ], spacing=8, wrap=True),

                            # Patient info
                            ft.Text(f"Patient: {patient_name}",
                                    size=17, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Originally requested: {units} unit(s)",
                                    size=13, color="#555555"),

                            ft.Divider(height=6),

                            ft.Text(
                                "Enter lab-confirmed blood type and final units needed:",
                                size=12, color="#6A1B9A", italic=True
                            ),

                            # Input row
                            ft.Row([
                                blood_dd,
                                units_field,
                                ft.ElevatedButton(
                                    "Confirm & Update",
                                    bgcolor="#6A1B9A", color="#ffffff",
                                    icon=ft.Icons.CHECK_CIRCLE,
                                    on_click=make_save(req_id, patient_name, blood_dd, units_field)
                                ),
                            ], spacing=12, wrap=True),
                        ], spacing=8),
                        padding=16,
                        bgcolor="#F3E5F5",
                        border_radius=10,
                        border=ft.Border.all(1, "#CE93D8"),
                    )
                )

        page.update()

    # ── save handler ───────────────────────────────────────────────
    def do_save(req_id, patient_name, blood_dd, units_field):
        if not blood_dd.value:
            status_text.value = "❌ Please select the confirmed blood type."
            status_text.color = "#C62828"
            page.update()
            return

        raw = units_field.value.strip()
        if not raw.isdigit() or int(raw) <= 0:
            status_text.value = "❌ Please enter a valid unit count (number > 0)."
            status_text.color = "#C62828"
            page.update()
            return

        update_request_blood_type_and_units(req_id, blood_dd.value, int(raw))
        status_text.value = (
            f"✅ Request for {patient_name} confirmed — "
            f"{raw} unit(s) of {blood_dd.value}. It is now fulfillable."
        )
        status_text.color = "#2E7D32"
        render_list()
        page.update()

    render_list()

    return ft.Column([
        # Page header
        ft.Container(
            content=ft.Column([
                ft.Text("Request Blood Type Testing", size=26, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Confirm blood type for patient requests that were registered as 'Unknown'",
                    size=13, color="#555555"
                ),
            ], spacing=4),
            margin=ft.Margin.only(bottom=10),
        ),
        ft.Divider(height=1),
        ft.Row([
            ft.ElevatedButton(
                "🔄 Refresh", on_click=lambda e: render_list(),
                bgcolor="#6A1B9A", color="#ffffff"
            ),
        ], alignment=ft.MainAxisAlignment.END),
        ft.Container(height=10),
        list_col,
        ft.Container(height=10),
        status_text,
    ], expand=True)