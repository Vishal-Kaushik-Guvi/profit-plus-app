import flet as ft
import os
from datetime import datetime

from app.api_client import api_client

BG = "#030711"
PANEL_BG = "#080d17"
BORDER = "#1a2231"
CYAN = "#16cdf2"
RED = "#e11d48"

def BusinessProfileEditView(page: ft.Page, business_id: str):
    error_text = ft.Text("", color="#fb7185", size=12)
    
    selected_logo_path = {"path": ""}
    selected_logo_text = ft.Text("No file chosen", color="#6d788d", size=11)
    
    logo_file_picker = ft.FilePicker()
    
    async def choose_logo(e):
        files = await logo_file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["jpg", "jpeg", "png", "webp"],
        )
        if files:
            selected_logo_path["path"] = files[0].path
            selected_logo_text.value = os.path.basename(files[0].path)
        else:
            selected_logo_path["path"] = ""
            selected_logo_text.value = "No file chosen"
        page.update()

    def input_field(label, value="", hint="", read_only=False):
        return ft.Column(
            expand=True,
            spacing=8,
            controls=[
                ft.Text(label, color="#8792a7", size=10, weight=ft.FontWeight.BOLD),
                ft.TextField(
                    value=value,
                    hint_text=hint,
                    color="white",
                    text_size=14,
                    read_only=read_only,
                    bgcolor=PANEL_BG,
                    border_color=BORDER,
                    focused_border_color=CYAN if not read_only else BORDER,
                    border_radius=12,
                    content_padding=ft.padding.symmetric(horizontal=18, vertical=17),
                ),
            ],
        )

    # Fields
    f_business_name = input_field("BUSINESS NAME")
    f_gst = input_field("GST NUMBER")
    f_phone = input_field("CONTACT PHONE")
    f_email = input_field("CONTACT EMAIL")
    
    f_address = input_field("STREET ADDRESS")
    f_city = input_field("CITY")
    f_pincode = input_field("PINCODE")
    f_state = input_field("STATE")
    f_country = input_field("COUNTRY")
    
    # Status Fields
    s_plan = ft.Text("BUSINESS", color=CYAN, size=10, weight=ft.FontWeight.BOLD)
    s_expiry = ft.Text("-", color="white", size=11, weight=ft.FontWeight.BOLD)
    s_established = ft.Text("-", color="white", size=11, weight=ft.FontWeight.BOLD)
    s_updated = ft.Text("-", color="white", size=11, weight=ft.FontWeight.BOLD)

    def load_profile():
        try:
            data, status = api_client.get_business(business_id)
            if status == 200:
                f_business_name.controls[1].value = data.get("business_name") or ""
                f_gst.controls[1].value = data.get("gst") or ""
                f_phone.controls[1].value = data.get("phone") or ""
                f_email.controls[1].value = data.get("email") or ""
                
                f_address.controls[1].value = data.get("address") or ""
                f_city.controls[1].value = data.get("city") or ""
                f_pincode.controls[1].value = data.get("pincode") or ""
                f_state.controls[1].value = data.get("state") or ""
                f_country.controls[1].value = data.get("country") or ""
                
                s_plan.value = (data.get("subscription_type") or "FREE").upper()
                s_plan.color = CYAN if s_plan.value != "FREE" else "#6d788d"
                
                def fmt_date(d_str):
                    if not d_str: return "-"
                    try:
                        dt = datetime.fromisoformat(d_str)
                        return dt.strftime("%d %b %Y")
                    except: return d_str
                
                s_established.value = fmt_date(data.get("created_at"))
                s_updated.value = fmt_date(data.get("updated_at") or data.get("created_at"))
                
                if s_plan.value != "FREE" and data.get("subscription_expiry"):
                    days = data.get("subscription_days_remaining", 0)
                    s_expiry.value = f"{fmt_date(data.get('subscription_expiry'))} ({days} days left)"
                else:
                    s_expiry.value = "N/A (Free Plan)"
                
                page.update()
        except Exception as e:
            error_text.value = str(e)
            page.update()

    load_profile()

    def update_profile(e):
        error_text.value = ""
        payload = {
            "business_name": f_business_name.controls[1].value,
            "gst": f_gst.controls[1].value,
            "phone": f_phone.controls[1].value,
            "email": f_email.controls[1].value,
            "address": f_address.controls[1].value,
            "city": f_city.controls[1].value,
            "pincode": f_pincode.controls[1].value,
            "state": f_state.controls[1].value,
            "country": f_country.controls[1].value,
        }
        try:
            res, status = api_client.update_business(
                business_id, payload, selected_logo_path["path"]
            )
            if status == 200:
                sb = ft.SnackBar(ft.Text("Profile updated successfully!"), bgcolor="green")
                page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.SnackBar)]
                page.overlay.append(sb)
                sb.open = True
                page.go(f"/businesses/{business_id}/dashboard")
            else:
                error_text.value = res.get("detail", "Failed to update profile")
        except Exception as ex:
            error_text.value = str(ex)
        page.update()

    for field in [f_business_name, f_gst, f_phone, f_email, f_address, f_city, f_pincode, f_state, f_country]:
        field.controls[1].on_submit = update_profile

    def delete_business(e):
        try:
            res, status = api_client.delete_business(business_id)
            if status == 200:
                page.go("/businesses")
            else:
                error_text.value = res.get("detail", "Failed to delete business")
                page.update()
        except Exception as ex:
            error_text.value = str(ex)
            page.update()

    def panel_section(title, controls):
        return ft.Container(
            padding=32,
            border_radius=24,
            bgcolor="#050a13",
            border=ft.border.all(1, BORDER),
            content=ft.Column(
                spacing=24,
                controls=[
                    ft.Text(title, color="white", size=14, weight=ft.FontWeight.BOLD),
                    ft.Divider(color=BORDER, height=1),
                    *controls
                ]
            )
        )

    logo_picker = ft.Column(
        expand=True,
        spacing=8,
        controls=[
            ft.Text("BUSINESS LOGO", color="#8792a7", size=10, weight=ft.FontWeight.BOLD),
            ft.Row(
                spacing=12,
                controls=[
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        border_radius=7, bgcolor="#073042", ink=True,
                        on_click=choose_logo,
                        content=ft.Text("CHOOSE FILE", color=CYAN, size=9, weight=ft.FontWeight.BOLD),
                    ),
                    selected_logo_text,
                ],
            )
        ]
    )

    left_column = ft.Column(
        expand=True,
        spacing=24,
        controls=[
            panel_section("Identity & Communication", [
                ft.Row(spacing=24, controls=[f_business_name, logo_picker]),
                ft.Row(spacing=24, controls=[f_gst, f_phone]),
                ft.Row(spacing=24, controls=[
                    f_email,
                    ft.Container(expand=True)
                ])
            ]),
            panel_section("Operational Base", [
                ft.Row(spacing=24, controls=[f_address]),
                ft.Row(spacing=24, controls=[f_city, f_pincode]),
                ft.Row(spacing=24, controls=[f_state, f_country]),
            ])
        ]
    )

    def status_row(label, control):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(label, color="#8792a7", size=10, weight=ft.FontWeight.BOLD),
                control
            ]
        )

    right_column = ft.Container(
        width=300,
        content=ft.Column(
            spacing=24,
            controls=[
                ft.Container(
                    padding=24, border_radius=24, bgcolor="#050a13", border=ft.border.all(1, BORDER),
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            ft.Text("ENTITY STATUS", color="white", size=12, weight=ft.FontWeight.BOLD),
                            ft.Divider(color=BORDER, height=1),
                            status_row("PLAN LEVEL", s_plan),
                            ft.Divider(color=BORDER, height=1),
                            status_row("PLAN EXPIRY", s_expiry),
                            ft.Divider(color=BORDER, height=1),
                            status_row("ESTABLISHED", s_established),
                            ft.Divider(color=BORDER, height=1),
                            status_row("LAST UPDATE", s_updated),
                        ]
                    )
                ),
                ft.Container(
                    height=56, border_radius=11, bgcolor=CYAN, alignment=ft.Alignment(0, 0), ink=True,
                    on_click=update_profile,
                    content=ft.Row(
                        tight=True, spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.CHECK, color="#02101a", size=19),
                            ft.Text("UPDATE PROFILE", color="#02101a", size=11, weight=ft.FontWeight.BOLD),
                        ]
                    )
                ),
                ft.Text(
                    "CHANGES ARE SYNCHRONIZED ACROSS ALL CONNECTED OPERATIONAL UNITS",
                    color="#6d788d", size=9, text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=8),
                ft.Container(
                    height=56, border_radius=11, border=ft.border.all(1, RED), alignment=ft.Alignment(0, 0), ink=True,
                    on_click=delete_business,
                    content=ft.Row(
                        tight=True, spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.DELETE_OUTLINE, color=RED, size=19),
                            ft.Text("DELETE BUSINESS", color=RED, size=11, weight=ft.FontWeight.BOLD),
                        ]
                    )
                ),
                ft.Text("IRREVERSIBLE ACTION", color=RED, size=9, text_align=ft.TextAlign.CENTER)
            ]
        )
    )

    main_content = ft.Container(
        expand=True,
        padding=40,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Business Profile", color="white", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("MANAGE ENTITY DETAILS AND SETTINGS", color="#8792a7", size=10, weight=ft.FontWeight.BOLD),
                ft.Container(height=16),
                ft.Divider(color=BORDER, height=1),
                ft.Container(height=16),
                error_text,
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=32,
                    controls=[left_column, right_column]
                )
            ]
        )
    )
    
    def handle_keyboard(e: ft.KeyboardEvent):
        if page.route == f"/businesses/{business_id}/profile":
            if e.key == "Enter":
                update_profile(None)
            elif e.key == "Escape":
                page.go(f"/businesses/{business_id}/dashboard")
                
    page.on_keyboard_event = handle_keyboard
    
    return main_content
