"""
Hub Central do Personal Trainer - Templo Fitness AI.
Reúne:
1. Ficha & Execução do Treino (Séries, Cargas, RPE, Cronômetro de Descanso).
2. Consultoria em Tempo Real com o Personal Trainer IA (Treinador Márcio).
3. Biblioteca Biomecânica de Exercícios e Máquinas.
"""
import flet as ft
from core.theme import SportColors, Icons, AppPadding, AppBorder
from views.workout_view import WorkoutView
from views.exercise_catalog_view import ExerciseCatalogView
from views.specialist_chat_component import SpecialistChatComponent

class PersonalHubView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_sub_tab = 0  # 0: Treino, 1: Chat Personal IA, 2: Guia de Exercícios
        
        self.workout_view = WorkoutView(self.page, on_view_exercise_guide=self._on_guide_requested)
        self.chat_component = SpecialistChatComponent(self.page, persona_key="personal")
        self.catalog_view = ExerciseCatalogView(self.page)
        
        self.content_area = ft.Container(expand=True)

    def build(self) -> ft.Control:
        # Seletor de Sub-Abas do Personal Trainer
        tabs_data = [
            ("Treino do Dia", Icons.FITNESS_CENTER, 0),
            ("Personal IA (Márcio)", Icons.PSYCHOLOGY, 1),
            ("Guia de Exercícios", Icons.MENU_BOOK, 2)
        ]

        tab_controls = []
        for label, icon, idx in tabs_data:
            is_active = self.current_sub_tab == idx
            tab_controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            icon,
                            size=14,
                            color=SportColors.BG_DARK if is_active else SportColors.PRIMARY_NEON
                        ),
                        ft.Text(
                            label,
                            size=12,
                            weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500,
                            color=SportColors.BG_DARK if is_active else SportColors.TEXT_WHITE
                        )
                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=SportColors.PRIMARY_NEON if is_active else SportColors.BG_SURFACE_ALT,
                    border_radius=10,
                    padding=AppPadding.symmetric(horizontal=12, vertical=8),
                    border=AppBorder.all(1, SportColors.PRIMARY_NEON if is_active else SportColors.BORDER_DEFAULT),
                    on_click=lambda _, i=idx: self._switch_tab(i),
                    expand=True
                )
            )

        sub_nav_row = ft.Row(tab_controls, spacing=6)

        self._render_current_sub_view()

        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=sub_nav_row,
                    padding=AppPadding.only(left=12, right=12, top=10, bottom=4)
                ),
                self.content_area
            ], spacing=6, expand=True),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _switch_tab(self, index: int):
        self.current_sub_tab = index
        self.build()
        if self.page:
            self.page.update()

    def _on_guide_requested(self, exercise_name: str):
        self.current_sub_tab = 2
        self.build()
        if self.page:
            self.page.update()

    def _render_current_sub_view(self):
        if self.current_sub_tab == 0:
            self.content_area.content = self.workout_view.build()
        elif self.current_sub_tab == 1:
            self.content_area.content = self.chat_component.build()
        else:
            self.content_area.content = self.catalog_view.build()
