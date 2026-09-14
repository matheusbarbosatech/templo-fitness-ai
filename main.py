"""
Apollo Fitness AI / Templo Fitness AI - Super-App Oficial de Saúde Esportiva & Musculação.
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

    # 3. Gerenciamento das Telas e Navegação (3 Seções: Personal, Nutrição e Evolução)
    current_index = 0
    content_container = ft.Container(expand=True)

    personal_hub = PersonalHubView(page)
    nutrition_hub = NutritionHubView(page)
    photos_evolution = PhotosEvolutionView(page)

    views = [
        lambda: personal_hub.build(),
        lambda: nutrition_hub.build(),
        lambda: photos_evolution.build(),
    ]

    def render_view():
        content_container.content = views[current_index]()
        page.update()

    def navigate_to(index: int):
        nonlocal current_index
        current_index = index
        if nav_bar:
            nav_bar.selected_index = index
        render_view()

    # 4. Barra Superior (AppBar) Totalmente Limpa (Apenas Logo e Título)
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
    page.navigation_bar = nav_bar

    # 6. Montagem Inicial
    page.add(content_container)
    render_view()

if __name__ == "__main__":
    ft.run(main)
