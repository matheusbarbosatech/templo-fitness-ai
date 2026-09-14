"""
Sala da Junta Técnica Multidisciplinar com IA (DevWorld) - Apollo Fitness AI.
Permite alternar entre os 4 Especialistas em Ciências do Esporte e conversar em tempo real.
"""
import flet as ft
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder, AppBorderRadius
from services.db_service import DBService
from services.devworld_ai_service import DevWorldAIService, PERSONA_CONFIGS

class AITeamView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_persona = "personal"
        self.messages_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
        self.input_field = ft.TextField(
            hint_text="Pergunte ao especialista...",
            bgcolor=SportColors.BG_INPUT,
            border_color=SportColors.BORDER_DEFAULT,
            color=SportColors.TEXT_WHITE,
            text_size=13,
            content_padding=AppPadding.symmetric(horizontal=12, vertical=10),
            expand=True,
            on_submit=lambda _: self._send_message()
        )
        self.send_button = ft.IconButton(
            icon=Icons.SEND_ROUNDED,
            icon_color=SportColors.PRIMARY_NEON,
            icon_size=24,
            on_click=lambda _: self._send_message()
        )
        self.quick_prompts_row = ft.Row(spacing=6, scroll=ft.ScrollMode.AUTO)

    def build(self) -> ft.Control:
        # 1. Seletor dos 4 Especialistas
        persona_buttons = []
        for key, p in PERSONA_CONFIGS.items():
            is_active = key == self.current_persona
            persona_buttons.append(
                ft.Container(
                    content=ft.Row([
                        ft.CircleAvatar(
                            radius=14,
                            bgcolor=f"{p['color']}33",
                            content=ft.Icon(getattr(Icons, p["avatar_icon"].upper(), Icons.PERSON), color=p["color"], size=16)
                        ),
                        ft.Column([
                            ft.Text(p["name"], size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE if is_active else SportColors.TEXT_SECONDARY),
                            ft.Text(p["title"].split("&")[0].strip(), size=10, color=SportColors.TEXT_MUTED),
                        ], spacing=1)
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=SportColors.BG_SURFACE_ALT if is_active else SportColors.BG_SURFACE,
                    border_radius=10,
                    padding=AppPadding.symmetric(horizontal=10, vertical=6),
                    border=AppBorder.all(1.5 if is_active else 1, p["color"] if is_active else SportColors.BORDER_DEFAULT),
                    on_click=lambda _, pk=key: self._switch_persona(pk)
                )
            )
        specialists_row = ft.Row(persona_buttons, spacing=8, scroll=ft.ScrollMode.AUTO)

        self._reload_messages()
        self._update_quick_prompts()

        input_bar = ft.Container(
            content=ft.Row([
                self.input_field,
                self.send_button
            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=AppPadding.all(8),
            bgcolor=SportColors.BG_SURFACE,
            border_radius=12,
            border=AppBorder.all(1, SportColors.BORDER_DEFAULT)
        )

        return ft.Container(
            content=ft.Column([
                specialists_row,
                ft.Divider(color=SportColors.BORDER_DEFAULT, height=1),
                self.quick_prompts_row,
                ft.Container(
                    content=self.messages_column,
                    expand=True,
                    padding=AppPadding.symmetric(horizontal=4, vertical=6)
                ),
                input_bar,
                ft.Container(height=70)
            ], spacing=8),
            bgcolor=SportColors.BG_DARK,
            padding=AppPadding.all(14),
            expand=True
        )

    def _switch_persona(self, persona_key: str):
        self.current_persona = persona_key
        self._reload_messages()
        self._update_quick_prompts()
        if self.page:
            self.page.update()

    def _update_quick_prompts(self):
        self.quick_prompts_row.controls.clear()
        prompts = {
            "personal": [
                "Como substituir a cadeira extensora?",
                "Qual a melhor cadência para hipertrofia?",
                "Como saber se devo aumentar a carga?"
            ],
            "nutri": [
                "O que comer no pós-treino imediato?",
                "Como tomar a creatina corretamente?",
                "Ideias de refeição com 40g de proteína"
            ],
            "mente": [
                "Tô sem motivação para treinar hoje",
                "Como ter mais foco durante a série?",
                "Exercício rápido para diminuir a ansiedade"
            ],
            "fisio": [
                "Como aquecer o manguito rotador?",
                "Como evitar dor no joelho no leg press?",
                "Alongamento para quem fica muito sentado"
            ]
        }

        for text in prompts.get(self.current_persona, []):
            self.quick_prompts_row.controls.append(
                ft.Container(
                    content=ft.Text(text, size=11, color=SportColors.TEXT_PRIMARY),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.symmetric(horizontal=10, vertical=6),
                    border_radius=16,
                    border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
                    on_click=lambda _, t=text: self._send_quick_prompt(t)
                )
            )

    def _send_quick_prompt(self, prompt_text: str):
        self.input_field.value = prompt_text
        self._send_message()

    def _reload_messages(self):
        self.messages_column.controls.clear()
        history = DBService.get_chat_history(self.current_persona, limit=30)
        p_info = PERSONA_CONFIGS[self.current_persona]

        if not history:
            welcome_text = f"Olá! Sou o {p_info['name']} ({p_info['title']}). Estou conectado ao seu prontuário e pronto para te ajudar a evoluir. Como posso te orientar agora?"
            self.messages_column.controls.append(
                self._render_message_bubble("assistant", welcome_text, p_info)
            )
        else:
            for h in history:
                self.messages_column.controls.append(
                    self._render_message_bubble(h["role"], h["content"], p_info)
                )

    def _render_message_bubble(self, role: str, content: str, p_info: dict) -> ft.Control:
        is_user = role == "user"
        
        if is_user:
            return ft.Row([
                ft.Container(
                    content=ft.Text(content, size=13, color=SportColors.TEXT_WHITE),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.all(12),
                    border_radius=AppBorderRadius.only(top_left=12, top_right=12, bottom_left=12, bottom_right=2),
                    border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
                    width=290
                )
            ], alignment=ft.MainAxisAlignment.END)
        else:
            return ft.Row([
                ft.CircleAvatar(
                    radius=16,
                    bgcolor=f"{p_info['color']}33",
                    content=ft.Icon(getattr(Icons, p_info["avatar_icon"].upper(), Icons.PERSON), color=p_info["color"], size=16)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(p_info["name"], size=11, weight=ft.FontWeight.BOLD, color=p_info["color"]),
                        ft.Markdown(
                            content,
                            selectable=True,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            code_theme="atom-one-dark"
                        )
                    ], spacing=4),
                    bgcolor=SportColors.BG_SURFACE,
                    padding=AppPadding.all(12),
                    border_radius=AppBorderRadius.only(top_left=2, top_right=12, bottom_left=12, bottom_right=12),
                    border=AppBorder.all(1, f"{p_info['color']}55"),
                    width=310
                )
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, spacing=8)

    def _send_message(self):
        user_text = self.input_field.value
        if not user_text or not user_text.strip():
            return

        self.input_field.value = ""
        p_info = PERSONA_CONFIGS[self.current_persona]
        
        self.messages_column.controls.append(
            self._render_message_bubble("user", user_text, p_info)
        )
        
        typing_indicator = ft.Row([
            ft.Text(f"{p_info['name']} está analisando...", size=11, color=SportColors.TEXT_MUTED, italic=True)
        ])
        self.messages_column.controls.append(typing_indicator)
        if self.page:
            self.page.update()

        bot_response = DevWorldAIService.send_message(self.current_persona, user_text)
        
        self.messages_column.controls.remove(typing_indicator)
        self.messages_column.controls.append(
            self._render_message_bubble("assistant", bot_response, p_info)
        )
        if self.page:
            self.page.update()
