import flet as ft
from data.repository import get_all_stock, update_stock, get_settings, update_setting
from ui.components import section, BLOOD_COLORS


def build_stock_view(page: ft.Page):
    status_text = ft.Text("", size=12)
    stock_col = ft.Column(spacing=10)
    
    settings = get_settings()

    # Form fields
    blood_dropdown = ft.Dropdown(
        label="Blood Type",
        width=150,
        options=[ft.dropdown.Option(b) for b in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]]
    )
    
    units_field = ft.TextField(
        label="Units",
        width=120,
        keyboard_type=ft.KeyboardType.NUMBER,
        hint_text="Number"
    )
    
    action_dropdown = ft.Dropdown(
        label="Action",
        width=120,
        options=[ft.dropdown.Option("Add"), ft.dropdown.Option("Remove")]
    )
    
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
            percentage = min(100, int((s.units / 100) * 100))
            
            stock_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(s.blood_type, size=16, weight=ft.FontWeight.BOLD, color=color),
                            width=80,
                        ),
                        ft.Text(f"{s.units} units", size=14, width=100),
                        ft.ProgressBar(value=percentage/100, width=150, color=color, bgcolor="#EEEEEE"),
                        ft.Text(f"{percentage}%", size=12, width=50),
                        ft.Text("⚠️ LOW" if is_low else "✅ OK", size=12, color="#C62828" if is_low else "#2E7D32"),
                    ], spacing=10),
                    padding=10,
                    bgcolor="#FFF5F5" if is_low else "#FAFAFA",
                    border_radius=8,
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
        
    def submit(e):
        if not blood_dropdown.value or not units_field.value or not action_dropdown.value:
            status_text.value = "❌ Please fill all fields"
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
        change = units if action_dropdown.value == "Add" else -units
        try:
            max_limit = int(max_stock_limit_field.value) if max_stock_limit_field.value else 100
        except:
            max_limit = 100
        success, message = update_stock(blood_dropdown.value, change, max_limit if change > 0 else None)
        if success:
            status_text.value = f"✅ {action_dropdown.value}ed {units} units of {blood_dropdown.value}"
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
        ft.Row([ft.ElevatedButton("Update Stock", on_click=submit, bgcolor="#1565C0", color="white")]),
        status_text
    ], spacing=10)
    settings_form = ft.Column([
        ft.Row([low_stock_threshold_field, max_stock_limit_field], spacing=10),
        ft.Row([ft.ElevatedButton("Save Settings", on_click=save_settings, bgcolor="#6A1B9A", color="white")]),
    ], spacing=10)
    return ft.Column([
        ft.Text("📦 Blood Stock Management", size=24, weight=ft.FontWeight.BOLD),
        section("🔄 Update Stock", form),
        section("⚙️ Settings", settings_form),
        ft.Text("📊 Current Stock Levels", size=16, weight=ft.FontWeight.BOLD),
        ft.Container(height=8),
        stock_col,
    ], scroll=ft.ScrollMode.AUTO, expand=True)