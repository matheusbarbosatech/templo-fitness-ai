"""
Modal de Autenticação e Alternância Multi-Usuário (Alunos & Personal Trainer) - Templo Fitness AI.
Permite alternar perfis em 1 clique e cadastrar novos alunos/atletas.
"""
import flet as ft
from typing import Callable, Optional
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder
from core.ui_helper import UIHelper
from services.db_service import DBService

class AuthDialog:
    def __init__(self, page: ft.Page, on_user_changed: Optional[Callable] = None):
        self.page = page
        self.on_user_changed = on_user_changed
        self.dialog: Optional[ft.AlertDialog] = None

    def show(self):
        active_user = DBService.get_active_user()
        users = DBService.list_users()

        user_cards = []
        for u in users:
            is_active = u["id"] == active_user["id"]
            user_cards.append(
                ft.Container(
                    content=ft.Row([
                        ft.CircleAvatar(
                            radius=18,
                            bgcolor=f"{u.get('color_hex', SportColors.PRIMARY_NEON)}33",
                            content=ft.Icon(
                                getattr(Icons, u.get("avatar_icon", "PERSON").upper(), Icons.PERSON),
                                color=u.get("color_hex", SportColors.PRIMARY_NEON),
                                size=20
                            )
                        ),
                        ft.Column([
                            ft.Row([
                                ft.Text(u["name"], size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                                SportStyles.badge(u.get("role", "aluno").upper(), u.get("color_hex", SportColors.PRIMARY_NEON)),
                            ], spacing=6),
                            ft.Text(f"@{u['username']}", size=11, color=SportColors.TEXT_MUTED),
                        ], spacing=2, expand=True),
                        ft.Icon(
                            Icons.CHECK_CIRCLE if is_active else Icons.ARROW_FORWARD_IOS,
                            color=SportColors.PRIMARY_NEON if is_active else SportColors.TEXT_MUTED,
                            size=16
                        )
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=SportColors.BG_SURFACE_ALT if is_active else SportColors.BG_SURFACE,
                    border_radius=10,
                    padding=AppPadding.symmetric(horizontal=12, vertical=10),
                    border=AppBorder.all(1.5 if is_active else 1, SportColors.PRIMARY_NEON if is_active else SportColors.BORDER_DEFAULT),
                    on_click=lambda _, uid=u["id"]: self._switch_user(uid)
                )
            )

        # Campos para novo usuário
        new_name = ft.TextField(label="Nome Completo", hint_text="Ex: Carlos Silva", text_size=12, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        new_username = ft.TextField(label="Nome de Usuário (@login)", hint_text="Ex: carlossilva", text_size=12, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        role_drop = ft.Dropdown(
            label="Tipo de Conta",
            value="aluno",
            options=[
                ft.dropdown.Option("aluno", "Aluno / Atleta"),
                ft.dropdown.Option("personal", "Personal Trainer / Coach"),
            ],
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        create_panel = ft.ExpansionTile(
            title=ft.Row([
                ft.Icon(Icons.PERSON_ADD_ALT_1, color=SportColors.CYAN_ELECTRIC, size=18),
                ft.Text("Cadastrar Novo Atleta / Usuário", size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            controls=[
                ft.Container(
                    content=ft.Column([
                        new_name,
                        new_username,
                        role_drop,
                        ft.ElevatedButton(
                            "Criar e Conectar",
                            icon=Icons.CHECK,
                            style=ft.ButtonStyle(bgcolor=SportColors.CYAN_ELECTRIC, color=SportColors.BG_DARK),
                            on_click=lambda _: self._create_user(new_name.value, new_username.value, role_drop.value)
                        )
                    ], spacing=8),
                    padding=AppPadding.all(8)
                )
            ]
        )

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.SWITCH_ACCOUNT, color=SportColors.PRIMARY_NEON, size=22),
                ft.Text("Alternar Perfil / Usuário", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=8),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text("Selecione qual atleta está usando o Templo Fitness AI:", size=12, color=SportColors.TEXT_SECONDARY),
                    ft.Column(user_cards, spacing=8),
                    ft.Divider(color=SportColors.BORDER_DEFAULT, height=1),
                    create_panel
                ], spacing=10),
                width=340,
                height=420
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda _: self._close())
            ]
        )

        UIHelper.open_dialog(self.page, self.dialog)

    def _switch_user(self, user_id: int):
        DBService.switch_user(user_id)
        self._close()
        UIHelper.show_toast(self.page, f"Perfil alternado para: {DBService.get_active_user()['name']}!", color=SportColors.PRIMARY_NEON)
        if self.on_user_changed:
            self.on_user_changed()

    def _create_user(self, name: str, username: str, role: str):
        if not name or not username:
            return
        uid = DBService.create_user(name=name, username=username, role=role)
        self._switch_user(uid)

    def _close(self):
        if self.dialog:
            UIHelper.close_dialog(self.page, self.dialog)
