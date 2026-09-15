"""
Catálogo Visual de Exercícios, Máquinas e Biomecânica - Templo Fitness AI.
Permite buscar exercícios, filtrar por grupos musculares e estudar a execução correta,
dicas biomecânicas e erros comuns a evitar.
"""
import flet as ft
from typing import Optional
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder
from core.ui_helper import UIHelper
from services.db_service import DBService

class ExerciseCatalogView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_category = "Todos"
        self.search_query = ""
        self.exercises_grid = ft.Column(spacing=10)

    def build(self) -> ft.Control:
        categories = ["Todos", "Peito", "Costas", "Pernas", "Ombros", "Braços", "Abdômen"]
        
        # 1. Barra de Busca
        search_field = ft.TextField(
            hint_text="Buscar exercício ou músculo (ex: Supino, Dorsal...)",
            prefix_icon=Icons.SEARCH,
            bgcolor=SportColors.BG_INPUT,
            border_color=SportColors.BORDER_DEFAULT,
            color=SportColors.TEXT_WHITE,
            text_size=13,
            content_padding=AppPadding.symmetric(horizontal=12, vertical=8),
            on_change=lambda e: self._on_search_change(e.control.value)
        )

        # 2. Chips de Categorias Musculares
        chips = []
        for cat in categories:
            is_active = cat == self.selected_category
            chips.append(
                ft.Container(
                    content=ft.Text(
                        cat,
                        size=12,
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                        color=SportColors.BG_DARK if is_active else SportColors.TEXT_PRIMARY
                    ),
                    bgcolor=SportColors.PRIMARY_NEON if is_active else SportColors.BG_SURFACE_ALT,
                    border_radius=20,
                    padding=AppPadding.symmetric(horizontal=14, vertical=6),
                    border=AppBorder.all(1, SportColors.PRIMARY_NEON if is_active else SportColors.BORDER_DEFAULT),
                    on_click=lambda _, c=cat: self._on_category_select(c)
                )
            )
        categories_row = ft.Row(chips, spacing=6, scroll=ft.ScrollMode.AUTO)

        # 3. Carrega lista inicial
        self._reload_exercises()

        return ft.Container(
            content=ft.ListView([
                SportStyles.section_header("BIBLIOTECA BIOMECÂNICA", "Catálogo visual de máquinas e execução correta", icon=Icons.MENU_BOOK),
                search_field,
                categories_row,
                ft.Divider(color=SportColors.BORDER_DEFAULT, height=10),
                self.exercises_grid,
                ft.Container(height=90)
            ], spacing=12, padding=AppPadding.all(16)),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _on_search_change(self, query: str):
        self.search_query = query
        self._reload_exercises()
        if self.page:
            self.page.update()

    def _on_category_select(self, category: str):
        self.selected_category = category
        self._reload_exercises()
        if self.page:
            self.page.update()

    def _reload_exercises(self):
        self.exercises_grid.controls.clear()
        exercises = DBService.get_exercises(self.selected_category, self.search_query)

        if not exercises:
            self.exercises_grid.controls.append(
                ft.Container(
                    content=ft.Text("Nenhum exercício encontrado com esses termos.", color=SportColors.TEXT_MUTED),
                    padding=AppPadding.all(20)
                )
            )
            return

        for ex in exercises:
            card = SportStyles.card_container(
                content=ft.Row([
                    ft.CircleAvatar(
                        radius=22,
                        bgcolor=f"{SportColors.PRIMARY_NEON}22",
                        content=ft.Icon(Icons.FITNESS_CENTER, color=SportColors.PRIMARY_NEON, size=22)
                    ),
                    ft.Column([
                        ft.Text(ex["name"], size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                        ft.Row([
                            SportStyles.badge(ex["category"], SportColors.CYAN_ELECTRIC),
                            SportStyles.badge(ex["equipment"], SportColors.AMBER_GOLD),
                        ], spacing=6),
                        ft.Text(f"Músculo Principal: {ex['primary_muscle']}", size=11, color=SportColors.TEXT_SECONDARY),
                    ], spacing=3, expand=True),
                    ft.IconButton(
                        icon=Icons.ARROW_FORWARD_IOS,
                        icon_size=16,
                        icon_color=SportColors.PRIMARY_NEON,
                        on_click=lambda _, item=ex: self.show_exercise_detail_modal(item)
                    )
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                border_color=SportColors.BORDER_DEFAULT,
                padding=12,
                on_click=lambda _, item=ex: self.show_exercise_detail_modal(item)
            )
            self.exercises_grid.controls.append(card)

    def show_exercise_detail_modal(self, ex: dict):
        """Abre modal com guia biomecânico completo."""
        gif_url = DBService.get_exercise_gif(ex["name"])
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.FITNESS_CENTER, color=SportColors.PRIMARY_NEON, size=24),
                ft.Text(ex["name"], size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
            ], spacing=8),
            content=ft.Container(
                content=ft.ListView([
                    ft.Container(
                        content=ft.Image(
                            src=gif_url,
                            height=150,
                            fit="contain",
                            border_radius=10,
                            repeat=ft.ImageRepeat.NO_REPEAT
                        ),
                        bgcolor=SportColors.BG_SURFACE_ALT,
                        border_radius=10,
                        padding=AppPadding.all(4),
                        border=AppBorder.all(1, SportColors.BORDER_DEFAULT)
                    ),
                    ft.Row([
                        SportStyles.badge(f"Grupo: {ex['category']}", SportColors.PRIMARY_NEON),
                        SportStyles.badge(f"Aparelho: {ex['equipment']}", SportColors.AMBER_GOLD),
                    ], spacing=6),
                    
                    SportStyles.card_container(
                        content=ft.Column([
                            ft.Text("🎯 MÚSCULOS ALVO", size=12, weight=ft.FontWeight.BOLD, color=SportColors.CYAN_ELECTRIC),
                            ft.Text(f"• Primário: {ex['primary_muscle']}", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                            ft.Text(f"• Secundários: {ex.get('secondary_muscles', 'Nenhum')}", size=12, color=SportColors.TEXT_SECONDARY),
                        ], spacing=4),
                        padding=10,
                        border_color=SportColors.BORDER_CYAN
                    ),

                    SportStyles.card_container(
                        content=ft.Column([
                            ft.Text("💡 POR QUE FAZER ESTE EXERCÍCIO?", size=12, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON),
                            ft.Text(ex.get("why_do_it", ""), size=12, color=SportColors.TEXT_PRIMARY),
                        ], spacing=4),
                        padding=10,
                        border_color=SportColors.BORDER_NEON
                    ),

                    SportStyles.card_container(
                        content=ft.Column([
                            ft.Text("📋 PASSO A PASSO DE EXECUÇÃO", size=12, weight=ft.FontWeight.BOLD, color=SportColors.AMBER_GOLD),
                            ft.Text(ex.get("execution_guide", ""), size=12, color=SportColors.TEXT_PRIMARY),
                        ], spacing=4),
                        padding=10,
                        border_color=SportColors.BORDER_GOLD
                    ),

                    SportStyles.card_container(
                        content=ft.Column([
                            ft.Text("⚠️ ERROS COMUNS & RISCO DE LESÃO", size=12, weight=ft.FontWeight.BOLD, color=SportColors.CRIMSON_NEON),
                            ft.Text(ex.get("common_mistakes", ""), size=12, color=SportColors.TEXT_PRIMARY),
                        ], spacing=4),
                        padding=10,
                        border_color=SportColors.BORDER_CRIMSON
                    ),
                ], spacing=10),
                width=380,
                height=450
            ),
            actions=[
                ft.ElevatedButton(
                    "Fechar",
                    style=ft.ButtonStyle(bgcolor=SportColors.BG_SURFACE_ALT, color=SportColors.TEXT_WHITE),
                    on_click=lambda _: self._close_dialog(dialog)
                )
            ]
        )
        UIHelper.open_dialog(self.page, dialog)

    def _close_dialog(self, dialog):
        UIHelper.close_dialog(self.page, dialog)
