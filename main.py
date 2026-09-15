"""
Templo Fitness AI - Super-App Oficial de Treino, Força & Mordomia do Templo.
Foco exclusivo e enxuto: Personal Trainer, Nutricionista & Evolução com IA Integrada.
Tecnologias: Python Flet, SQLite Local (Offline-First), API DevWorld.
"""
import sys
from pathlib import Path

# Garante resolução de caminhos
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import flet as ft
from core.config import AppConfig
from core.theme import SportColors, Icons, NavigationDestination, AppPadding, AppBorder, AppBorderRadius, AppAlignment
from core.ui_helper import UIHelper
from services.db_service import DBService

# Views Centrais
from views.personal_hub_view import PersonalHubView
from views.nutrition_hub_view import NutritionHubView
from views.photos_evolution_view import PhotosEvolutionView
from views.login_view import LoginView

def main(page: ft.Page):
    # 1. Configurações Globais da Página e Tema
    page.title = f"{AppConfig.APP_ICON} {AppConfig.APP_NAME} - Personal, Nutrição & Evolução"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = SportColors.BG_DARK
    page.padding = 0
    try:
        page.theme = ft.Theme(
            color_scheme_seed="#71717A",
            color_scheme=ft.ColorScheme(
                primary="#FFFFFF",
                on_primary="#0A0A0A",
                secondary="#A1A1AA",
                surface="#141414",
                background="#0A0A0A",
            )
        )
    except Exception:
        pass
    
    try:
        page.window.width = 440
        page.window.height = 900
        page.window.min_width = 380
        page.window.min_height = 700
        page.window.resizable = True
    except Exception:
        pass

    # 2. Inicialização do Banco de Dados SQLite
    try:
        DBService.init_db()
    except Exception as err:
        print(f"[DB INIT ERROR]: {err}")

    # 3. Estado de Autenticação e Navegação
    is_logged_in = False
    active_user_id = 1
    current_index = 0
    
    # Containers do App
    content_area = ft.Container(expand=True)
    
    personal_hub = None
    nutrition_hub = None
    photos_evolution = None

    def on_login_success(user_id=None):
        nonlocal is_logged_in, personal_hub, nutrition_hub, photos_evolution, active_user_id
        if user_id:
            active_user_id = int(user_id)
            DBService.switch_user(active_user_id)
            try:
                page.client_storage.set("logged_user_id", active_user_id)
            except Exception:
                pass
        else:
            active_user_id = DBService.get_active_user_id()

        is_logged_in = True
        personal_hub = PersonalHubView(page, user_id=active_user_id)
        nutrition_hub = NutritionHubView(page, user_id=active_user_id)
        photos_evolution = PhotosEvolutionView(page, user_id=active_user_id)
        render_app()

    def on_logout():
        nonlocal is_logged_in
        is_logged_in = False
        try:
            page.client_storage.remove("logged_user_id")
        except Exception:
            pass
        render_login()

    def render_login():
        page.appbar = None
        page.navigation_bar = None
        content_area.content = LoginView(page, on_login_success=on_login_success).build()
        page.update()

    def render_app():
        views = [
            lambda: personal_hub.build(),
            lambda: nutrition_hub.build(),
            lambda: photos_evolution.build(),
        ]
        content_area.content = views[current_index]()
        update_app_bar()
        page.navigation_bar = nav_bar
        page.update()

    def navigate_to(index: int):
        nonlocal current_index
        current_index = index
        if nav_bar:
            nav_bar.selected_index = index
        render_app()

    # 4. Barra Superior (AppBar) com Identificação do Atleta e Troca Rápida
    def update_app_bar():
        try:
            active_u = DBService.get_active_user(active_user_id)
        except Exception:
            active_u = {"name": "Atleta", "color_hex": SportColors.PRIMARY_NEON, "role": "aluno"}
            
        u_name = active_u.get("name", "Atleta").split()[0]
        u_color = active_u.get("color_hex", SportColors.PRIMARY_NEON)

        page.appbar = ft.AppBar(
            leading=ft.Container(
                content=ft.Text(AppConfig.APP_ICON, size=24),
                padding=AppPadding.only(left=12),
                alignment=AppAlignment.CENTER
            ),
            title=ft.Row([
                ft.Text(AppConfig.APP_NAME, size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                ft.Container(
                    content=ft.Text("PRO", size=9, weight=ft.FontWeight.BOLD, color=SportColors.BG_DARK),
                    bgcolor=SportColors.PRIMARY_NEON,
                    padding=AppPadding.symmetric(horizontal=6, vertical=2),
                    border_radius=4
                )
            ], spacing=6, alignment=ft.MainAxisAlignment.START),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.CircleAvatar(
                            radius=11,
                            bgcolor="#27272A",
                            content=ft.Icon(Icons.PERSON, color=SportColors.TEXT_WHITE, size=13)
                        ),
                        ft.Text(u_name, size=11, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                    ], spacing=4),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.symmetric(horizontal=8, vertical=4),
                    border_radius=12,
                    border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
                    tooltip=f"Atleta Conectado: {active_u.get('name')}. Clique para trocar.",
                    on_click=lambda _: on_logout()
                ),
                ft.IconButton(
                    icon=Icons.SWAP_HORIZ,
                    icon_color=SportColors.TEXT_SECONDARY,
                    icon_size=18,
                    tooltip="Trocar Atleta / Sair",
                    on_click=lambda _: on_logout()
                ),
                ft.Container(width=4)
            ],
            bgcolor=SportColors.BG_SURFACE,
            elevation=0
        )

    # 5. Barra Inferior Enxuta (Personal Trainer, Nutricionista & Evolução)
    nav_bar = ft.NavigationBar(
        selected_index=0,
        bgcolor=SportColors.BG_SURFACE,
        indicator_color="#27272A",
        destinations=[
            NavigationDestination(
                icon=Icons.FITNESS_CENTER_OUTLINED,
                selected_icon=Icons.FITNESS_CENTER,
                label="Personal"
            ),
            NavigationDestination(
                icon=Icons.RESTAURANT_OUTLINED,
                selected_icon=Icons.RESTAURANT,
                label="Nutrição"
            ),
            NavigationDestination(
                icon=Icons.PHOTO_CAMERA_OUTLINED,
                selected_icon=Icons.PHOTO_CAMERA,
                label="Evolução"
            ),
        ],
        on_change=lambda e: navigate_to(e.control.selected_index)
    )

    # 6. Container Principal Responsivo
    app_wrapper = ft.Container(
        content=content_area,
        bgcolor=SportColors.BG_DARK,
        expand=True
    )

    page.add(app_wrapper)

    # 7. Verificação de Sessão Salva
    saved_uid = None
    try:
        saved_uid = page.client_storage.get("logged_user_id")
    except Exception:
        pass

    if saved_uid:
        try:
            valid_ids = [u["id"] for u in DBService.list_users()]
            if saved_uid in valid_ids:
                on_login_success(saved_uid)
                return
        except Exception:
            pass

    render_login()

if __name__ == "__main__":
    ft.run(main)
