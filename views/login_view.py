"""
Tela Oficial de Login & Seleção de Perfil Multi-Usuário - Templo Fitness AI.
Permite alternar entre atletas ou cadastrar novos perfis.
Cada atleta possui histórico individual de treinos, dieta, fotos e IA personalizada.
"""
import flet as ft
from typing import Callable, Optional
from core.config import AppConfig
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder, AppBorderRadius
from services.db_service import DBService

class LoginView:
    def __init__(self, page: ft.Page, on_login_success: Callable):
        self.page = page
        self.on_login_success = on_login_success
        self.users_list_column = ft.Column(spacing=10)
        self.is_creating_new = False
        
        # Campos de cadastro
        self.name_field = ft.TextField(
            label="Nome Completo",
            hint_text="Ex: Pedro Henrique",
            bgcolor=SportColors.BG_INPUT,
            border_color=SportColors.BORDER_DEFAULT,
            color=SportColors.TEXT_WHITE,
            text_size=13
        )
        self.username_field = ft.TextField(
            label="Nome de Usuário (@login)",
            hint_text="Ex: pedro_treino",
            bgcolor=SportColors.BG_INPUT,
            border_color=SportColors.BORDER_DEFAULT,
            color=SportColors.TEXT_WHITE,
            text_size=13
        )
        self.role_drop = ft.Dropdown(
            label="Tipo de Conta",
            value="aluno",
            options=[
                ft.dropdown.Option("aluno", "Aluno / Atleta"),
                ft.dropdown.Option("personal", "Personal Trainer / Coach"),
            ],
            bgcolor=SportColors.BG_INPUT,
            color=SportColors.TEXT_WHITE
        )

    def build(self) -> ft.Control:
        users = DBService.list_users()
        active_u = DBService.get_active_user()

        # 1. Cabeçalho de Boas-Vindas
        header = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text(AppConfig.APP_ICON, size=40),
                ], alignment=ft.MainAxisAlignment.CENTER),
                margin=AppPadding.only(top=20, bottom=6)
            ),
            ft.Text(
                AppConfig.APP_NAME,
                size=22,
                weight=ft.FontWeight.BOLD,
                color=SportColors.TEXT_WHITE,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                "QUEM ESTÁ TREINANDO HOJE?",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=SportColors.PRIMARY_NEON,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                "Cada perfil possui seus próprios treinos, dieta, fotos e IA.",
                size=12,
                color=SportColors.TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)

        # 2. Lista de Perfis Cadastrados
        user_cards = []
        for u in users:
            is_current = u["id"] == active_u["id"]
            u_color = u.get("color_hex", SportColors.PRIMARY_NEON)
            user_cards.append(
                ft.Container(
                    content=ft.Row([
                        ft.CircleAvatar(
                            radius=22,
                            bgcolor=f"{u_color}33",
                            content=ft.Icon(
                                getattr(Icons, u.get("avatar_icon", "PERSON").upper(), Icons.PERSON),
                                color=u_color,
                                size=24
                            )
                        ),
                        ft.Column([
                            ft.Row([
                                ft.Text(u["name"], size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                                SportStyles.badge(u.get("role", "aluno").upper(), u_color)
                            ], spacing=6),
                            ft.Text(f"@{u['username']}", size=11, color=SportColors.TEXT_MUTED)
                        ], spacing=2, expand=True),
                        ft.ElevatedButton(
                            "Entrar",
                            icon=Icons.LOGIN,
                            style=ft.ButtonStyle(
                                bgcolor=u_color,
                                color=SportColors.BG_DARK,
                                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)
                            ),
                            height=36,
                            on_click=lambda _, uid=u["id"]: self._select_user(uid)
                        )
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=SportColors.BG_SURFACE,
                    padding=AppPadding.all(14),
                    border_radius=12,
                    border=AppBorder.all(1.5 if is_current else 1, u_color if is_current else SportColors.BORDER_DEFAULT),
                    on_click=lambda _, uid=u["id"]: self._select_user(uid)
                )
            )

        # 3. Painel de Cadastro de Novo Perfil
        create_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header("NOVO ATLETA / ALUNO", "Cadastre um novo perfil para este app", icon=Icons.PERSON_ADD),
                self.name_field,
                self.username_field,
                self.role_drop,
                ft.ElevatedButton(
                    "Criar Perfil e Começar",
                    icon=Icons.CHECK,
                    style=ft.ButtonStyle(
                        bgcolor=SportColors.CYAN_ELECTRIC,
                        color=SportColors.BG_DARK,
                        text_style=ft.TextStyle(size=13, weight=ft.FontWeight.BOLD)
                    ),
                    height=44,
                    on_click=lambda _: self._create_and_enter()
                )
            ], spacing=10),
            border_color=SportColors.BORDER_CYAN,
            padding=16
        )

        return ft.Container(
            content=ft.ListView([
                header,
                ft.Container(height=10),
                ft.Text("Perfis Disponíveis", size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_PRIMARY),
                ft.Column(user_cards, spacing=10),
                ft.Divider(color=SportColors.BORDER_DEFAULT, height=20),
                create_card,
                ft.Container(height=40)
            ], spacing=10, padding=AppPadding.all(16)),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _select_user(self, user_id: int):
        DBService.switch_user(user_id)
        if self.page:
            u = DBService.get_active_user()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Bem-vindo(a), {u['name']}!", color=SportColors.BG_DARK, weight=ft.FontWeight.BOLD),
                bgcolor=SportColors.PRIMARY_NEON,
                duration=1500
            )
            self.page.snack_bar.open = True
        self.on_login_success(user_id)

    def _create_and_enter(self):
        name = (self.name_field.value or "").strip()
        username = (self.username_field.value or "").strip()
        role = self.role_drop.value or "aluno"

        if not name:
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Por favor, digite o nome do atleta!", color=SportColors.TEXT_WHITE),
                    bgcolor=SportColors.CRIMSON_NEON
                )
                self.page.snack_bar.open = True
                self.page.update()
            return

        if not username:
            username = name.lower().replace(" ", "_")

        new_uid = DBService.create_user(name=name, username=username, role=role)
        self.name_field.value = ""
        self.username_field.value = ""
        self._select_user(new_uid)
