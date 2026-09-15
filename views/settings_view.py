"""
Tela e Diálogo de Configurações, Perfil do Usuário e Chave de API DevWorld - Templo Fitness AI.
"""
import requests
import flet as ft
from typing import Optional, Callable
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder
from core.ui_helper import UIHelper
from services.db_service import DBService

class SettingsView:
    def __init__(self, page: ft.Page, on_saved: Optional[Callable] = None):
        self.page = page
        self.on_saved = on_saved
        self.dialog: Optional[ft.AlertDialog] = None

    @classmethod
    def open_dialog(cls, page: ft.Page, on_saved: Optional[Callable] = None):
        """Abre a tela de configurações em modal de forma direta e rápida."""
        instance = cls(page, on_saved=on_saved)
        instance.show_modal()

    def show_modal(self):
        content = self.build(is_modal=True)
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.SETTINGS, color=SportColors.PRIMARY_NEON, size=20),
                ft.Text("Configurações & API DevWorld", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=8),
            content=ft.Container(
                content=content,
                width=370,
                height=520
            ),
            actions=[
                ft.ElevatedButton(
                    "Fechar",
                    icon=Icons.CHECK,
                    style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.BG_DARK),
                    on_click=lambda _: self._close_modal()
                )
            ]
        )
        UIHelper.open_dialog(self.page, self.dialog)

    def _close_modal(self):
        if self.dialog:
            UIHelper.close_dialog(self.page, self.dialog)
        if self.on_saved:
            self.on_saved()

    def build(self, is_modal: bool = False) -> ft.Control:
        profile = DBService.get_athlete_profile()

        name_in = ft.TextField(label="Nome do Usuário", value=profile.get("name", ""), color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
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
                ft.dropdown.Option("muito_intenso", "Muito Intenso / 2x por dia"),
            ],
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        profile_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header("PERFIL DO USUÁRIO", "Dados usados pela IA do DevWorld", icon=Icons.PERSON),
                name_in,
                ft.Row([age_in, height_in, weight_in], spacing=8),
                goal_drop,
                activity_drop,
                ft.ElevatedButton(
                    "Salvar Dados do Perfil",
                    icon=Icons.SAVE,
                    style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.BG_DARK),
                    on_click=lambda _: self._save_profile(name_in.value, age_in.value, height_in.value, weight_in.value, goal_drop.value, activity_drop.value),
                    height=40
                )
            ], spacing=10),
            border_color=SportColors.BORDER_NEON,
            padding=14
        )

        api_key_in = ft.TextField(
            label="Chave de API DevWorld (API Key)",
            value=profile.get("devworld_api_key", ""),
            password=True,
            can_reveal_password=True,
            hint_text="Cole sua chave da DevWorld aqui",
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
                SportStyles.section_header("INTEGRAÇÃO COM API DEVWORLD", "Copiloto Personal Inteligente Oficial", icon=Icons.KEY),
                ft.Text(
                    "Conecte sua chave da DevWorld para o Personal IA responder com inteligência total em tempo real.",
                    size=12,
                    color=SportColors.TEXT_SECONDARY
                ),
                api_key_in,
                base_url_in,
                ft.Row([
                    ft.ElevatedButton(
                        "Salvar Chave DevWorld",
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
            ], spacing=10),
            border_color=SportColors.BORDER_CYAN,
            padding=14
        )

        about_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header("SOBRE O TEMPLO FITNESS AI", "Super-App Oficial com API DevWorld", icon=Icons.INFO),
                ft.Text("• Powered by DevWorld AI Platform.", size=12, color=SportColors.TEXT_SECONDARY),
                ft.Text("• Base Bíblica: 1 Coríntios 6:19-20 — O corpo como santuário do Espírito Santo.", size=12, color=SportColors.TEXT_SECONDARY),
                ft.Text("• Armazenamento 100% Offline-First & Seguro em SQLite local.", size=12, color=SportColors.TEXT_SECONDARY),
            ], spacing=6),
            border_color=SportColors.BORDER_DEFAULT,
            padding=14
        )

        items = [api_card, profile_card]
        if not is_modal:
            items.append(about_card)
            items.append(ft.Container(height=90))

        return ft.Container(
            content=ft.ListView(items, spacing=14, padding=AppPadding.all(12) if is_modal else AppPadding.all(16)),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _save_profile(self, name, age, height, weight, goal, activity):
        DBService.update_athlete_profile(
            name=name or "Usuário",
            age=int(age or 26),
            sex="M",
            height=float(height or 178),
            weight=float(weight or 78.5),
            goal=goal or "hipertrofia",
            activity=activity or "intenso"
        )
        UIHelper.show_toast(self.page, "Perfil do usuário atualizado com sucesso!", color=SportColors.PRIMARY_NEON)
        if self.on_saved:
            self.on_saved()

    def _save_api_settings(self, api_key, base_url):
        profile = DBService.get_athlete_profile()
        DBService.update_athlete_profile(
            name=profile.get("name", "Usuário"),
            age=profile.get("age", 26),
            sex=profile.get("sex", "M"),
            height=profile.get("height_cm", 178),
            weight=profile.get("weight_kg", 78.5),
            goal=profile.get("goal", "hipertrofia"),
            activity=profile.get("activity_level", "intenso"),
            api_key=(api_key or "").strip(),
            base_url=(base_url or "https://api.devworld.com.br/v1").strip()
        )
        UIHelper.show_toast(self.page, "Chave da API DevWorld salva com sucesso!", color=SportColors.CYAN_ELECTRIC)
        if self.on_saved:
            self.on_saved()

    def _test_api_connection(self, api_key, base_url):
        key = (api_key or "").strip()
        url = (base_url or "https://api.devworld.com.br/v1").strip()
        if not key:
            UIHelper.show_toast(self.page, "Informe a chave de API DevWorld para testar!", color=SportColors.AMBER_GOLD, text_color=SportColors.TEXT_WHITE)
            return

        UIHelper.show_toast(self.page, "Conectando à API DevWorld...", color=SportColors.CYAN_ELECTRIC)
        try:
            endpoint = f"{url.rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "devworld-gpt-4o-mini",
                "messages": [{"role": "user", "content": "Ping"}],
                "max_tokens": 5
            }
            res = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                UIHelper.show_toast(self.page, "⚡ Conexão com API DevWorld estabelecida com sucesso!", color=SportColors.PRIMARY_NEON)
            elif res.status_code == 401:
                UIHelper.show_toast(self.page, "❌ Chave DevWorld não autorizada (401). Verifique a chave.", color=SportColors.RED_ERROR, text_color=SportColors.TEXT_WHITE)
            elif res.status_code == 429:
                UIHelper.show_toast(self.page, "⚠️ Limite de requisições DevWorld atingido (429).", color=SportColors.AMBER_GOLD, text_color=SportColors.TEXT_WHITE)
            else:
                UIHelper.show_toast(self.page, f"⚠️ Resposta da DevWorld: Status {res.status_code}", color=SportColors.AMBER_GOLD, text_color=SportColors.TEXT_WHITE)
        except requests.exceptions.Timeout:
            UIHelper.show_toast(self.page, "⏳ Tempo limite esgotado ao conectar à DevWorld.", color=SportColors.RED_ERROR, text_color=SportColors.TEXT_WHITE)
        except Exception as err:
            UIHelper.show_toast(self.page, f"❌ Erro de conexão: {str(err)[:45]}", color=SportColors.RED_ERROR, text_color=SportColors.TEXT_WHITE)
