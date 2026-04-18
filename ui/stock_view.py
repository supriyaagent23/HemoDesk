import flet as ft
from data.repository import get_all_stock, update_stock, get_settings, update_setting
from ui.components import section, BLOOD_COLORS

def build_stock_view(page: ft.Page):
    status_text = ft.Text("", size=12)
    stock_col = ft.Column(spacing=8)
    
    settings = get_settings()

    blood_dropdown = ft.Dropdown(
        label="Blood Type *", width=150,
        options=[ft.dropdown.Option(b) for b in
                 ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]]
    )
    
    units_field = ft.TextField(
        label="Units *", 
        width=120,
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=4,
        hint_text="Enter number only"
    )
    
    action_dropdown = ft.Dropdown(
        label="Action *", width=150,
        options=[ft.dropdown.Option("Add"), ft.dropdown.Option("Remove")]
    )
    
    low_stock_threshold_field = ft.TextField(
        label="Low Stock Alert (units)", width=200,
        value=str(settings.get("low_stock_threshold", 5)),
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=3,
    )
    max_stock_limit_field = ft.TextField(
        label="Maximum Stock Limit (units)", width=200,
        value=str(settings.get("max_stock_limit", 100)),
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=4,
    )
    donation_wait_days_field = ft.TextField(
        label="Donation Wait Period (days)", width=200,
        value=str(settings.get("donation_wait_days", 90)),
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=3,
    )
    expiry_warning_days_field = ft.TextField(
        label="Expiry Warning (days before expiry)", width=200,
        value=str(settings.get("expiry_warning_days", 14)),
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=3,
    )

    def render_stock():
        stock = get_all_stock()
        try:
            low_threshold = int(low_stock_threshold_field.value) if low_stock_threshold_field.value else 5
        except:
            low_threshold = 5
            
        stock_col.controls.clear()
        for s in stock:
            color = BLOOD_COLORS.get(s.blood_type, "#888888")
            is_low = s.units < low_threshold
            stock_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            ft.Text(s.blood_type, size=16, weight=ft.FontWeight.BOLD,
                                    color="#ffffff"),
                            bgcolor=color, border_radius=6,
                            padding=8,
                            width=70
                        ),
                        ft.Text(f"{s.units} units available",
                                size=14, expand=True),
                        ft.Container(
                            ft.Text(f"LOW STOCK", size=11, color="#ffffff"),
                            bgcolor="#C62828", border_radius=4,
                            padding=5,
                            visible=is_low
                        )
                    ], spacing=12),
                    padding=10,
                    bgcolor="#ffffff",
                    border_radius=8,
                    border=ft.Border.all(2 if is_low else 1, "#C62828" if is_low else "#e0e0e0")
                )
            )
        page.update()

    def save_settings(e):
        try:
            new_threshold = int(low_stock_threshold_field.value) if low_stock_threshold_field.value else 5
            new_max_limit = int(max_stock_limit_field.value) if max_stock_limit_field.value else 100
            new_wait_days = int(donation_wait_days_field.value) if donation_wait_days_field.value else 90
            new_expiry_warning = int(expiry_warning_days_field.value) if expiry_warning_days_field.value else 14
            
            update_setting("low_stock_threshold", new_threshold)
            update_setting("max_stock_limit", new_max_limit)
            update_setting("donation_wait_days", new_wait_days)
            update_setting("expiry_warning_days", new_expiry_warning)
            
            status_text.value = "✅ Settings saved!"
            status_text.color = "#2E7D32"
            render_stock()
        except ValueError:
            status_text.value = "❌ Please enter valid numbers."
            status_text.color = "#C62828"
        page.update()

    def submit(e):
        if not blood_dropdown.value or not units_field.value or not action_dropdown.value:
            status_text.value = "Please fill all fields."
            status_text.color = "#C62828"
            page.update()
            return
        
        if not units_field.value.isdigit():
            status_text.value = "Units must contain only numbers."
            status_text.color = "#C62828"
            page.update()
            return
            
        units = int(units_field.value)
        if units <= 0:
            status_text.value = "Units must be greater than 0."
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
            status_text.value = f"✅ {action_dropdown.value}ed {units} units of {blood_dropdown.value}."
            status_text.color = "#2E7D32"
            units_field.value = ""
            blood_dropdown.value = None
            action_dropdown.value = None
            render_stock()
        else:
            status_text.value = f"❌ {message}"
            status_text.color = "#C62828"
        page.update()

    render_stock()

    form = ft.Column([
        ft.Row([blood_dropdown, units_field, action_dropdown], spacing=10),
        ft.ElevatedButton("Update Stock", on_click=submit, bgcolor="#1565C0", color="#ffffff"),
        status_text
    ], spacing=10)
    
    settings_form = ft.Column([
        ft.Row([low_stock_threshold_field, max_stock_limit_field], spacing=10, wrap=True),
        ft.Row([donation_wait_days_field, expiry_warning_days_field], spacing=10, wrap=True),
        ft.ElevatedButton("Save Settings", on_click=save_settings, bgcolor="#6A1B9A", color="#ffffff"),
    ], spacing=10)

    return ft.Column([
        ft.Text("Blood Stock Management", size=24, weight=ft.FontWeight.BOLD),
        section("Update Stock", form),
        section("⚙️ App Settings", settings_form),
        ft.Text("Current Stock Levels", size=16, weight=ft.FontWeight.BOLD),
        ft.Container(height=10),
        stock_col,
    ], scroll=ft.ScrollMode.AUTO, expand=True)