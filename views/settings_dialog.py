"""
Modal de Configurações, Perfil do Atleta e Chave de API - Templo Fitness AI.
Permite configurar parâmetros corporais e integração de IA sem ocupar a barra de navegação principal.
"""
import flet as ft
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder
from services.db_service import DBService

class SettingsDialog:
    def __init__(self, page: ft.Page, on_saved=None):
        self.page = page
        self.on_saved = on_saved
        self.dialog = None

    def show(self):
        profile = DBService.get_athlete_profile()

        name_in = ft.TextField(
            label="Nome do Atleta",
            value=profile.get("name", "Atleta"),
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT,
            text_size=13
        )
        age_in = ft.TextField(
            label="Idade (anos)",
            value=str(profile.get("age", 26)),
            keyboard_type=ft.KeyboardType.NUMBER,
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT,
            text_size=13
        )
        height_in = ft.TextField(
            label="Altura (cm)",
            value=str(profile.get("height_cm", 178)),
            keyboard_type=ft.KeyboardType.NUMBER,
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT,
            text_size=13
        )
        weight_in = ft.TextField(
            label="Peso Atual (kg)",
            value=str(profile.get("weight_kg", 78.5)),
            keyboard_type=ft.KeyboardType.NUMBER,
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT,
            text_size=13
        )

        api_key_in = ft.TextField(
            label="Chave de API (DevWorld / IA)",
            value=profile.get("devworld_api_key", ""),
            password=True,
            can_reveal_password=True,
            hint_text="sk-... ou dw-...",
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT,
            text_size=13
        )
        base_url_in = ft.TextField(
            label="URL Base da API",
            value=profile.get("devworld_base_url", "https://api.devworld.com.br/v1"),
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT,
            text_size=13
        )

        def save_all():
            try:
                DBService.update_athlete_profile(
                    name=name_in.value or "Atleta",
                    age=int(age_in.value or 26),
                    sex=profile.get("sex", "M"),
                    height=float(height_in.value or 178),
                    weight=float(weight_in.value or 78.5),
                    goal=profile.get("goal", "hipertrofia"),
                    activity=profile.get("activity_level", "intenso"),
                    api_key=api_key_in.value or "",
                    base_url=base_url_in.value or "https://api.devworld.com.br/v1"
                )
            except Exception as err:
                print(f"[SETTINGS SAVE ERROR]: {err}")

            self.dialog.open = False
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Configurações e Chave de API salvas!", color=SportColors.BG_DARK, weight=ft.FontWeight.BOLD),
                    bgcolor=SportColors.PRIMARY_NEON,
                    duration=1500
                )
                self.page.snack_bar.open = True
                self.page.update()

            if self.on_saved:
                self.on_saved()

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.SETTINGS, color=SportColors.PRIMARY_NEON),
                ft.Text("Configurações & API", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text("Dados do Atleta", size=12, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON),
                    name_in,
                    ft.Row([age_in, height_in, weight_in], spacing=6),
                    ft.Divider(color=SportColors.BORDER_DEFAULT, height=12),
                    ft.Text("Integração de IA (DevWorld / Chave de API)", size=12, weight=ft.FontWeight.BOLD, color=SportColors.CYAN_ELECTRIC),
                    ft.Text("Insira sua chave para ativar respostas dinâmicas em tempo real:", size=11, color=SportColors.TEXT_SECONDARY),
                    api_key_in,
                    base_url_in,
                ], spacing=10),
                width=340,
                height=380
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda _: self._close()),
                ft.ElevatedButton(
                    "Salvar",
                    style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.BG_DARK),
                    on_click=lambda _: save_all()
                )
            ]
        )

        if self.page:
            self.page.dialog = self.dialog
            self.dialog.open = True
            self.page.update()

    def _close(self):
        if self.dialog:
            self.dialog.open = False
        if self.page:
            self.page.update()
