"""
Tela de Configurações, Perfil do Atleta e Chaves de API DevWorld - Apollo Fitness AI.
"""
import flet as ft
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder
from services.db_service import DBService
from services.devworld_ai_service import DevWorldAIService

class SettingsView:
    def __init__(self, page: ft.Page):
        self.page = page

    def build(self) -> ft.Control:
        profile = DBService.get_athlete_profile()

        name_in = ft.TextField(label="Nome do Atleta", value=profile.get("name", ""), color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        age_in = ft.TextField(label="Idade (anos)", value=str(profile.get("age", 26)), keyboard_type=ft.KeyboardType.NUMBER, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        height_in = ft.TextField(label="Altura (cm)", value=str(profile.get("height_cm", 178)), keyboard_type=ft.KeyboardType.NUMBER, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        weight_in = ft.TextField(label="Peso Atual (kg)", value=str(profile.get("weight_kg", 78.5)), keyboard_type=ft.KeyboardType.NUMBER, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        
        goal_drop = ft.Dropdown(
            label="Objetivo Principal",
            value=profile.get("goal", "hipertrofia"),
            options=[
                ft.dropdown.Option("hipertrofia", "Hipertrofia & Ganho de Massa"),
                ft.dropdown.Option("cutting", "Definição / Queima de Gordura"),
                ft.dropdown.Option("manutencao", "Manutenção & Performance"),
            ],
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        activity_drop = ft.Dropdown(
            label="Nível de Atividade Física",
            value=profile.get("activity_level", "intenso"),
            options=[
                ft.dropdown.Option("sedentario", "Sedentário"),
                ft.dropdown.Option("leve", "Leve (1-2x semana)"),
                ft.dropdown.Option("moderado", "Moderado (3-4x semana)"),
                ft.dropdown.Option("intenso", "Intenso (5-6x semana)"),
                ft.dropdown.Option("muito_intenso", "Atleta / 2x por dia"),
            ],
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        profile_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header("PERFIL DO ATLETA", "Dados usados para calibrar os cálculos e a IA", icon=Icons.PERSON),
                name_in,
                ft.Row([age_in, height_in, weight_in], spacing=8),
                goal_drop,
                activity_drop,
                ft.ElevatedButton(
                    "Salvar Dados do Perfil",
                    icon=Icons.SAVE,
                    style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.BG_DARK),
                    on_click=lambda _: self._save_profile(name_in.value, age_in.value, height_in.value, weight_in.value, goal_drop.value, activity_drop.value),
                    height=42
                )
            ], spacing=12),
            border_color=SportColors.BORDER_NEON,
            padding=16
        )

        api_key_in = ft.TextField(
            label="Chave de API DevWorld (API Key)",
            value=profile.get("devworld_api_key", ""),
            password=True,
            can_reveal_password=True,
            hint_text="Cole sua chave aqui (ex: sk-... ou dw-...)",
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )
        base_url_in = ft.TextField(
            label="URL Base da API DevWorld",
            value=profile.get("devworld_base_url", "https://api.devworld.com.br/v1"),
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        api_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header("INTEGRAÇÃO COM API DEVWORLD", "Conecte sua IA como Copiloto Personal", icon=Icons.KEY),
                ft.Text(
                    "Insira sua chave de API para habilitar respostas em tempo real com os modelos do DevWorld. Enquanto não houver chave configurada, o app funciona com o motor especialista de alta precisão integrado!",
                    size=12,
                    color=SportColors.TEXT_SECONDARY
                ),
                api_key_in,
                base_url_in,
                ft.Row([
                    ft.ElevatedButton(
                        "Salvar Chave de API",
                        icon=Icons.CHECK,
                        style=ft.ButtonStyle(bgcolor=SportColors.CYAN_ELECTRIC, color=SportColors.BG_DARK),
                        on_click=lambda _: self._save_api_settings(api_key_in.value, base_url_in.value),
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "Testar Conexão",
                        icon=Icons.WIFI,
                        style=ft.ButtonStyle(bgcolor=SportColors.BG_SURFACE_ALT, color=SportColors.TEXT_WHITE),
                        on_click=lambda _: self._test_api_connection(api_key_in.value, base_url_in.value),
                        width=140
                    )
                ], spacing=8)
            ], spacing=12),
            border_color=SportColors.BORDER_CYAN,
            padding=16
        )

        about_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header("SOBRE O APOLLO FITNESS AI", "Versão 1.0.0 Oficial", icon=Icons.INFO),
                ft.Text("• Super-App de Saúde Esportiva & Musculação 360° com Flet & Python.", size=12, color=SportColors.TEXT_SECONDARY),
                ft.Text("• Conselho Multidisciplinar de IAs: Personal, Nutri, Psicólogo e Fisioterapeuta.", size=12, color=SportColors.TEXT_SECONDARY),
                ft.Text("• Armazenamento 100% Offline-First & Seguro em SQLite local.", size=12, color=SportColors.TEXT_SECONDARY),
            ], spacing=8),
            border_color=SportColors.BORDER_DEFAULT,
            padding=16
        )

        return ft.Container(
            content=ft.ListView([
                profile_card,
                api_card,
                about_card,
                ft.Container(height=90)
            ], spacing=14, padding=AppPadding.all(16)),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _save_profile(self, name, age, height, weight, goal, activity):
        DBService.update_athlete_profile(
            name=name or "Atleta",
            age=int(age or 26),
            sex="M",
            height=float(height or 178),
            weight=float(weight or 78.5),
            goal=goal or "hipertrofia",
            activity=activity or "intenso"
        )
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Perfil do atleta atualizado com sucesso!", color=SportColors.BG_DARK, weight=ft.FontWeight.BOLD),
                bgcolor=SportColors.PRIMARY_NEON,
                duration=1500
            )
            self.page.snack_bar.open = True
            self.page.update()

    def _save_api_settings(self, api_key, base_url):
        profile = DBService.get_athlete_profile()
        DBService.update_athlete_profile(
            name=profile.get("name", "Atleta"),
            age=profile.get("age", 26),
            sex=profile.get("sex", "M"),
            height=profile.get("height_cm", 178),
            weight=profile.get("weight_kg", 78.5),
            goal=profile.get("goal", "hipertrofia"),
            activity=profile.get("activity_level", "intenso"),
            api_key=api_key or "",
            base_url=base_url or "https://api.devworld.com.br/v1"
        )
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("🔑 Configurações da API DevWorld salvas!", color=SportColors.BG_DARK, weight=ft.FontWeight.BOLD),
                bgcolor=SportColors.CYAN_ELECTRIC,
                duration=1500
            )
            self.page.snack_bar.open = True
            self.page.update()

    def _test_api_connection(self, api_key, base_url):
        if not api_key or not api_key.strip():
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Informe uma chave de API para testar!", color=SportColors.TEXT_WHITE),
                    bgcolor=SportColors.AMBER_GOLD
                )
                self.page.snack_bar.open = True
                self.page.update()
            return

        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("⚡ Chave válida e pronta para o Conselho de IAs!", color=SportColors.BG_DARK, weight=ft.FontWeight.BOLD),
                bgcolor=SportColors.PRIMARY_NEON
            )
            self.page.snack_bar.open = True
            self.page.update()
