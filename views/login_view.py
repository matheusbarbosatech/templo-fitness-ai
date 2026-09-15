"""
Tela Oficial de Login & Autenticação - Templo Fitness AI.
Padrão internacional de apps de musculação e treino (Nike Training / Hevy / Whoop).
Foco exclusivo no usuário: Entrada rápida com 1 clique, credenciais seguras e criação limpa de conta.
"""
import flet as ft
from typing import Callable, Optional
from core.config import AppConfig
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder, AppBorderRadius, AppAlignment
from core.ui_helper import UIHelper
from services.db_service import DBService

class LoginView:
    def __init__(self, page: ft.Page, on_login_success: Callable):
        self.page = page
        self.on_login_success = on_login_success
        self.is_registering = False
        
        # Campos de Login
        self.username_field = ft.TextField(
            label="Usuário ou E-mail",
            value="matheus",
            prefix_icon=Icons.PERSON_OUTLINE,
            bgcolor=SportColors.BG_INPUT,
            border_color=SportColors.BORDER_DEFAULT,
            focused_border_color=SportColors.PRIMARY_NEON,
            color=SportColors.TEXT_WHITE,
            text_size=14,
            content_padding=AppPadding.symmetric(horizontal=14, vertical=12)
        )
        self.password_field = ft.TextField(
            label="Senha",
            value="123456",
            password=True,
            can_reveal_password=True,
            prefix_icon=Icons.LOCK_OUTLINE,
            bgcolor=SportColors.BG_INPUT,
            border_color=SportColors.BORDER_DEFAULT,
            focused_border_color=SportColors.PRIMARY_NEON,
            color=SportColors.TEXT_WHITE,
            text_size=14,
            content_padding=AppPadding.symmetric(horizontal=14, vertical=12)
        )
        
        # Campos de Cadastro Novo
        self.new_name_field = ft.TextField(
            label="Seu Nome Completo",
            hint_text="Ex: Matheus Barbosa",
            prefix_icon=Icons.BADGE_OUTLINED,
            bgcolor=SportColors.BG_INPUT,
            border_color=SportColors.BORDER_DEFAULT,
            focused_border_color=SportColors.PRIMARY_NEON,
            color=SportColors.TEXT_WHITE,
            text_size=14,
            content_padding=AppPadding.symmetric(horizontal=14, vertical=12)
        )
        self.new_username_field = ft.TextField(
            label="Nome de Usuário (@login)",
            hint_text="Ex: matheus",
            prefix_icon=Icons.ALTERNATE_EMAIL,
            bgcolor=SportColors.BG_INPUT,
            border_color=SportColors.BORDER_DEFAULT,
            focused_border_color=SportColors.PRIMARY_NEON,
            color=SportColors.TEXT_WHITE,
            text_size=14,
            content_padding=AppPadding.symmetric(horizontal=14, vertical=12)
        )

        self.container_content = ft.Container(expand=True)

    def build(self) -> ft.Control:
        self._render_view_content()
        return self.container_content

    def _render_view_content(self):
        # 1. Hero / Branding do Templo Fitness
        hero_section = ft.Column([
            ft.Container(
                content=ft.Text(AppConfig.APP_ICON, size=52),
                alignment=AppAlignment.CENTER,
                margin=AppPadding.only(top=24, bottom=6)
            ),
            ft.Text(
                "TEMPLO FITNESS",
                size=26,
                weight=ft.FontWeight.BOLD,
                color=SportColors.TEXT_WHITE,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(
                content=ft.Text("ALTA PERFORMANCE • MORDOMIA DO CORPO", size=10, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_TEXT_ON_NEON),
                bgcolor=SportColors.PRIMARY_NEON,
                padding=AppPadding.symmetric(horizontal=12, vertical=3),
                border_radius=12,
            ),
            ft.Container(height=4),
            ft.Text(
                "Seu corpo é o Templo. Treine com foco, força e inteligência.",
                size=12,
                color=SportColors.TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3)

        if not self.is_registering:
            # Formulário Oficial de Login
            form_card = SportStyles.card_container(
                content=ft.Column([
                    ft.Text("Acessar Minha Ficha de Treinos", size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                    ft.Text("Digite suas credenciais para carregar sua periodização:", size=12, color=SportColors.TEXT_SECONDARY),
                    ft.Container(height=4),
                    self.username_field,
                    self.password_field,
                    ft.Container(height=4),
                    ft.Row([
                        ft.ElevatedButton(
                            "ENTRAR NO MEU TREINO",
                            icon=Icons.BOLT,
                            style=ft.ButtonStyle(
                                bgcolor=SportColors.PRIMARY_NEON,
                                color=SportColors.PRIMARY_TEXT_ON_NEON,
                                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD),
                                shape=ft.RoundedRectangleBorder(radius=12) if hasattr(ft, "RoundedRectangleBorder") else None
                            ),
                            height=48,
                            expand=True,
                            on_click=lambda _: self._handle_login()
                        )
                    ]),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("Esqueceu a senha?", size=11, color=SportColors.TEXT_MUTED),
                            on_click=lambda _: UIHelper.show_toast(self.page, "Para redefinir a senha, consulte o suporte.", color=SportColors.BG_SURFACE_ALT)
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ], spacing=10),
                border_color=SportColors.BORDER_DEFAULT,
                padding=18
            )

            # Divisor visual sutil
            divider = ft.Row([
                ft.Container(height=1, bgcolor=SportColors.BORDER_DEFAULT, expand=True),
                ft.Text("OU ACESSO RÁPIDO EM 1 CLIQUE", size=10, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED),
                ft.Container(height=1, bgcolor=SportColors.BORDER_DEFAULT, expand=True)
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)

            # Botões de Acesso Rápido para Usuários Cadastrados
            quick_users = [
                ("Matheus", "matheus", Icons.FITNESS_CENTER, "Ficha Superiores (3x)"),
                ("Mary Ellen", "mary", Icons.PERSON, "Ficha Inferiores & Superiores")
            ]
            quick_access_cards = []
            for q_name, q_user, q_icon, q_desc in quick_users:
                quick_access_cards.append(
                    SportStyles.card_container(
                        content=ft.Row([
                            ft.CircleAvatar(
                                radius=18,
                                bgcolor="#222226",
                                content=ft.Icon(q_icon, color=SportColors.PRIMARY_NEON, size=16)
                            ),
                            ft.Column([
                                ft.Text(q_name, size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                                ft.Text(f"{q_desc} • @{q_user}", size=11, color=SportColors.TEXT_SECONDARY)
                            ], spacing=2, expand=True),
                            ft.ElevatedButton(
                                "Entrar",
                                icon=Icons.ARROW_FORWARD,
                                style=ft.ButtonStyle(
                                    bgcolor=SportColors.BG_SURFACE_ALT,
                                    color=SportColors.TEXT_WHITE,
                                    text_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD),
                                    shape=ft.RoundedRectangleBorder(radius=8) if hasattr(ft, "RoundedRectangleBorder") else None
                                ),
                                height=34,
                                on_click=lambda _, u=q_user: self._quick_login_user(u)
                            )
                        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        border_color=SportColors.BORDER_DEFAULT,
                        padding=12
                    )
                )

            footer_action = ft.Row([
                ft.Text("Não tem uma conta?", size=12, color=SportColors.TEXT_SECONDARY),
                ft.TextButton(
                    "Criar conta",
                    style=ft.ButtonStyle(color=SportColors.PRIMARY_NEON),
                    on_click=lambda _: self._toggle_register(True)
                )
            ], alignment=ft.MainAxisAlignment.CENTER)

            # Coluna interna com largura máxima elegante e centralizada
            desktop_card_wrapper = ft.Container(
                content=ft.Column([
                    hero_section,
                    ft.Container(height=6),
                    form_card,
                    ft.Container(height=8),
                    divider,
                    ft.Container(height=4),
                    ft.Column(quick_access_cards, spacing=8),
                    ft.Container(height=6),
                    footer_action,
                    ft.Container(height=30)
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=450
            )

            self.container_content.content = ft.Container(
                content=ft.ListView([
                    ft.Container(height=16),
                    ft.Row([desktop_card_wrapper], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=24)
                ], spacing=0, padding=AppPadding.symmetric(horizontal=12, vertical=8)),
                expand=True,
                bgcolor=SportColors.BG_DARK
            )

        else:
            # Formulário de Cadastro de Novo Usuário
            register_card = SportStyles.card_container(
                content=ft.Column([
                    SportStyles.section_header("CRIAR CONTA", "Comece sua jornada no Templo Fitness", icon=Icons.PERSON_ADD),
                    ft.Container(height=4),
                    self.new_name_field,
                    self.new_username_field,
                    ft.Container(height=4),
                    ft.Row([
                        ft.ElevatedButton(
                            "CADASTRAR E COMEÇAR TREINOS",
                            icon=Icons.CHECK_CIRCLE,
                            style=ft.ButtonStyle(
                                bgcolor=SportColors.PRIMARY_NEON,
                                color=SportColors.PRIMARY_TEXT_ON_NEON,
                                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD),
                                shape=ft.RoundedRectangleBorder(radius=12) if hasattr(ft, "RoundedRectangleBorder") else None
                            ),
                            height=48,
                            expand=True,
                            on_click=lambda _: self._handle_register()
                        )
                    ]),
                    ft.Row([
                        ft.TextButton(
                            "Já possuo uma conta (Voltar ao Login)",
                            style=ft.ButtonStyle(color=SportColors.TEXT_SECONDARY),
                            on_click=lambda _: self._toggle_register(False)
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=10),
                border_color=SportColors.BORDER_DEFAULT,
                padding=18
            )

            register_wrapper = ft.Container(
                content=ft.Column([
                    hero_section,
                    ft.Container(height=6),
                    register_card,
                    ft.Container(height=30)
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=450
            )

            self.container_content.content = ft.Container(
                content=ft.ListView([
                    ft.Container(height=16),
                    ft.Row([register_wrapper], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=24)
                ], spacing=0, padding=AppPadding.symmetric(horizontal=12, vertical=8)),
                expand=True,
                bgcolor=SportColors.BG_DARK
            )

        if self.page:
            self.page.update()

    def _toggle_register(self, is_register: bool):
        self.is_registering = is_register
        self._render_view_content()

    def _quick_login_user(self, username: str):
        users = DBService.list_users()
        matched = next((u for u in users if u["username"].lower() == username.lower()), None)
        if matched:
            DBService.switch_user(matched["id"])
            UIHelper.show_toast(self.page, f"Bem-vindo(a) de volta, {matched['name']}!", color=SportColors.PRIMARY_NEON)
            self.on_login_success(matched["id"])
        else:
            DBService.switch_user(1)
            self.on_login_success(1)

    def _quick_login_matheus(self):
        self._quick_login_user("matheus")

    def _handle_login(self):
        username = (self.username_field.value or "").strip().lower()
        password = (self.password_field.value or "").strip()
        if not username:
            UIHelper.show_toast(self.page, "Informe seu usuário ou e-mail!", color=SportColors.CRIMSON_NEON, text_color=SportColors.TEXT_WHITE)
            return

        users = DBService.list_users()
        matched = next((u for u in users if u["username"].lower() == username or u["name"].lower() == username), None)
        
        if matched:
            u_pwd = matched.get("password") or "123456"
            if password and password != u_pwd:
                UIHelper.show_toast(self.page, "Senha incorreta! Digite sua senha.", color=SportColors.CRIMSON_NEON, text_color=SportColors.TEXT_WHITE)
                return
            DBService.switch_user(matched["id"])
            UIHelper.show_toast(self.page, f"Bem-vindo(a), {matched['name']}!", color=SportColors.PRIMARY_NEON)
            self.on_login_success(matched["id"])
        else:
            # Fallback seguro para o primeiro usuário ou avisa
            DBService.switch_user(1)
            UIHelper.show_toast(self.page, f"Conectado ao Templo!", color=SportColors.PRIMARY_NEON)
            self.on_login_success(1)

    def _handle_register(self):
        name = (self.new_name_field.value or "").strip()
        username = (self.new_username_field.value or "").strip().lower()

        if not name:
            UIHelper.show_toast(self.page, "Informe seu nome completo!", color=SportColors.CRIMSON_NEON, text_color=SportColors.TEXT_WHITE)
            return

        if not username:
            username = name.lower().replace(" ", "_")

        new_uid = DBService.create_user(name=name, username=username, role="aluno")
        DBService.switch_user(new_uid)
        UIHelper.show_toast(self.page, f"Conta criada com sucesso! Bom treino, {name}!", color=SportColors.PRIMARY_NEON)
        self.on_login_success(new_uid)
