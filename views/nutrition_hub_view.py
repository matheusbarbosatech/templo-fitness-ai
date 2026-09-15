"""
Hub Central da Nutricionista - Templo Fitness AI.
Reúne:
1. Plano Alimentar & Macros (Calorias, Proteínas, Carbos, Gorduras, Diário de Refeições e Água).
2. Consultoria em Tempo Real com a Nutricionista IA.
"""
import flet as ft
from typing import Optional
from core.theme import SportColors, Icons, AppPadding, AppBorder
from views.nutrition_view import NutritionView
from views.specialist_chat_component import SpecialistChatComponent
from services.db_service import DBService

class NutritionHubView:
    def __init__(self, page: ft.Page, user_id: Optional[int] = None):
        self.page = page
        self.user_id = user_id or DBService.get_active_user_id()
        self.current_sub_tab = 0  # 0: Dieta & Macros, 1: Chat Nutri IA
        
        self.nutrition_view = NutritionView(self.page, user_id=self.user_id)
        self.chat_component = SpecialistChatComponent(self.page, persona_key="nutri", user_id=self.user_id)
        
        self.tabs_row = ft.Row(spacing=8)
        self.content_area = ft.Container(expand=True)

    def build(self) -> ft.Control:
        self._update_tabs_ui()
        self._render_current_sub_view()

        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=self.tabs_row,
                    padding=AppPadding.only(left=12, right=12, top=10, bottom=4)
                ),
                self.content_area
            ], spacing=6, expand=True),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _update_tabs_ui(self):
        tabs_data = [
            ("Minha Dieta & Macros", Icons.RESTAURANT_MENU, 0),
            ("Nutricionista IA", Icons.SPA, 1)
        ]

        self.tabs_row.controls.clear()
        for label, icon, idx in tabs_data:
            is_active = self.current_sub_tab == idx
            self.tabs_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            icon,
                            size=15,
                            color=SportColors.PRIMARY_TEXT_ON_NEON if is_active else SportColors.TEXT_PRIMARY
                        ),
                        ft.Text(
                            label,
                            size=12,
                            weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500,
                            color=SportColors.PRIMARY_TEXT_ON_NEON if is_active else SportColors.TEXT_WHITE
                        )
                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=SportColors.PRIMARY_NEON if is_active else SportColors.BG_SURFACE_ALT,
                    border_radius=10,
                    padding=AppPadding.symmetric(horizontal=12, vertical=8),
                    border=AppBorder.all(1, SportColors.PRIMARY_NEON if is_active else SportColors.BORDER_DEFAULT),
                    on_click=lambda _, i=idx: self._switch_tab(i),
                    expand=True,
                    ink=True
                )
            )

    def _switch_tab(self, index: int):
        self.current_sub_tab = index
        self._update_tabs_ui()
        self._render_current_sub_view()
        if self.page:
            self.page.update()

    def _render_current_sub_view(self):
        if self.current_sub_tab == 0:
            self.content_area.content = self.nutrition_view.build()
        else:
            self.content_area.content = self.chat_component.build()
