"""
Templo Fitness AI - Super-App Oficial de Treino, Força & Mordomia do Templo.
Foco exclusivo e enxuto: Personal Trainer & Nutricionista com IA Integrada.
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
from core.theme import SportColors, Icons, NavigationDestination, AppPadding, AppBorder
from services.db_service import DBService

# Views Centrais Enxutas
from views.personal_hub_view import PersonalHubView
from views.nutrition_hub_view import NutritionHubView
from views.photos_evolution_view import PhotosEvolutionView
from views.login_view import LoginView

def main(page: ft.Page):
    # 1. Configurações Globais da Janela e Tema
    page.title = f"{AppConfig.APP_ICON} {AppConfig.APP_NAME} - Personal, Nutrição & Evolução"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = SportColors.BG_DARK
    page.padding = 0
    
    try:
        page.window.width = 440
        page.window.height = 920
        page.window.min_width = 380
        page.window.min_height = 720
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
    content_container = ft.Container(expand=True)

    personal_hub = None
    nutrition_hub = None
    photos_evolution = None

    def on_login_success(user_id=None):
        nonlocal is_logged_in, personal_hub, nutrition_hub, photos_evolution, active_user_id
        if user_id:
            active_user_id = user_id
            DBService.switch_user(user_id)
            try:
                page.client_storage.set("logged_user_id", user_id)
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
        page.navigation_bar = None
        render_login()

    def render_login():
        page.appbar = None
        page.navigation_bar = None
        content_container.content = LoginView(page, on_login_success=on_login_success).build()
        page.update()

    def render_app():
        views = [
            lambda: personal_hub.build(),
            lambda: nutrition_hub.build(),
            lambda: photos_evolution.build(),
        ]
        content_container.content = views[current_index]()
        update_app_bar()
        page.navigation_bar = nav_bar
        page.update()

    def navigate_to(index: int):
        nonlocal current_index
        current_index = index
        if nav_bar:
            nav_bar.selected_index = index
        render_app()

    # 4. Barra Superior (AppBar) com Identificação do Atleta e Troca de Perfil
    def update_app_bar():
        active_u = DBService.get_active_user(user_id=active_user_id)
        u_name = active_u.get("name", "Atleta").split()[0]
        u_color = active_u.get("color_hex", SportColors.PRIMARY_NEON)

        page.appbar = ft.AppBar(
            leading=ft.Container(
                content=ft.Text(AppConfig.APP_ICON, size=24),
                padding=AppPadding.only(left=12),
                alignment=ft.alignment.center if hasattr(ft, "alignment") else None
            ),
            title=ft.Row([
                ft.Text(AppConfig.APP_NAME, size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                ft.Container(
                    content=ft.Text("PRO", size=10, weight=ft.FontWeight.BOLD, color=SportColors.BG_DARK),
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
                            bgcolor=f"{u_color}33",
                            content=ft.Icon(Icons.PERSON, color=u_color, size=13)
                        ),
                        ft.Text(u_name, size=11, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                    ], spacing=4),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.symmetric(horizontal=8, vertical=4),
                    border_radius=12,
                    border=AppBorder.all(1, u_color),
                    tooltip=f"Atleta Conectado: {active_u.get('name')}",
                    on_click=lambda _: on_logout()
                ),
                ft.IconButton(
                    icon=Icons.LOGOUT,
                    icon_color=SportColors.TEXT_MUTED,
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
        indicator_color=f"{SportColors.PRIMARY_NEON}33",
        destinations=[
            NavigationDestination(
                icon=Icons.FITNESS_CENTER_OUTLINED,
                selected_icon=Icons.FITNESS_CENTER,
                label="Personal"
            ),
            NavigationDestination(
                icon=Icons.RESTAURANT_OUTLINED,
                selected_icon=Icons.RESTAURANT,
                label="Nutricionista"
            ),
            NavigationDestination(
                icon=Icons.PHOTO_CAMERA_OUTLINED,
                selected_icon=Icons.PHOTO_CAMERA,
                label="Evolução"
            ),
        ],
        on_change=lambda e: navigate_to(e.control.selected_index)
    )

    # 6. Montagem Inicial e Auto-Login
    page.add(content_container)

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
