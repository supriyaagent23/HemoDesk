import flet as ft
from data.repository import get_pending_donations, update_donation_blood_type
from ui.components import blood_badge, BLOOD_TYPES


def build_donation_tests_view(page: ft.Page):
    list_col    = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    status_text = ft.Text("", size=12)

    def render_list():
        donations = get_pending_donations()
        list_col.controls.clear()

        if not donations:
            list_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SCIENCE, size=48, color="#CCCCCC"),
                        ft.Text("No pending donations to test", size=14, color="#888888"),
                        ft.Text("Register donations with 'Unknown' blood type to see them here",
                               size=12, color="#AAAAAA")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40, alignment=ft.Alignment(0, 0)
                )
            )
        else:
            list_col.controls.append(
                ft.Text(f"{len(donations)} donation(s) pending testing",
                       size=12, color="#888888")
            )

            for donation in donations:
                blood_type_dropdown = ft.Dropdown(
                    width=150,
                    options=[ft.dropdown.Option(bt) for bt in BLOOD_TYPES],
                    hint_text="Select tested blood type",
                    label="Blood Type"
                )
                notes_field = ft.TextField(
                    label="Test Notes (optional)", width=300,
                    multiline=True, max_lines=2
                )

                def make_update(don_id, units, donor_name, dropdown, notes):
                    return lambda e: update_donation_entry(don_id, units, donor_name, dropdown, notes)

                list_col.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.BLOODTYPE, size=20, color="#FF9800"),
                                ft.Text("PENDING TESTING", size=12,
                                       weight=ft.FontWeight.BOLD, color="#FF9800"),
                                blood_badge("Unknown"),
                                ft.Text(
                                    donation['donation_date'][:10] if donation['donation_date'] else "Unknown date",
                                    size=11, color="#aaaaaa"
                                )
                            ], spacing=8),
                            ft.Text(f"Donor: {donation['donor_name']}",
                                   size=16, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.Text(f"Age: {donation['donor_age']}", size=13, color="#555555"),
                                ft.Text(f"Gender: {donation['donor_gender'] or 'Not specified'}",
                                       size=13, color="#555555"),
                                ft.Text(f"Phone: {donation['donor_phone']}", size=13, color="#555555"),
                            ], spacing=15),
                            ft.Text(f"Units Donated: {donation['units']}", size=14,
                                   weight=ft.FontWeight.BOLD),
                            ft.Divider(height=5),
                            ft.Row([
                                blood_type_dropdown,
                                notes_field,
                                ft.ElevatedButton(
                                    "Save & Add to Stock",
                                    bgcolor="#1565C0", color="#ffffff",
                                    icon=ft.Icons.SAVE,
                                    on_click=make_update(
                                        donation['id'], donation['units'],
                                        donation['donor_name'],
                                        blood_type_dropdown, notes_field
                                    )
                                )
                            ], spacing=10, wrap=True)
                        ], spacing=8),
                        padding=14, bgcolor="#FFF8E1", border_radius=8,
                        border=ft.Border.all(1, "#FFB74D")
                    )
                )

        page.update()

    def update_donation_entry(donation_id, units, donor_name, dropdown, notes_field):
        if not dropdown.value:
            status_text.value = "❌ Please select the tested blood type"
            status_text.color = "#C62828"
            page.update()
            return

        update_donation_blood_type(donation_id, dropdown.value, notes_field.value)
        status_text.value = (
            f"✅ Donation from {donor_name} updated! "
            f"{units} unit(s) of {dropdown.value} added to stock."
        )
        status_text.color = "#2E7D32"
        render_list()
        page.update()

    render_list()

    return ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Text("Blood Donation Testing", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Review and test donations registered with unknown blood type",
                       size=14, color="#555555"),
            ]),
            margin=ft.Margin.only(bottom=10)
        ),
        ft.Divider(height=1),
        ft.Row([
            ft.ElevatedButton("🔄 Refresh", on_click=lambda e: render_list(),
                            bgcolor="#F57C00", color="#ffffff"),
        ], alignment=ft.MainAxisAlignment.END),
        ft.Container(height=10),
        list_col,
        ft.Container(height=10),
        status_text
    ], expand=True)