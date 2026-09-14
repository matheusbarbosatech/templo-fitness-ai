"""
Componente Reutilizável de Chat Especialista com IA - Templo Fitness AI.
Suporta consultas em tempo real com o Treinador Márcio (Personal) e Dra. Camila (Nutricionista).
"""
import flet as ft
from core.theme import SportColors, Icons, AppPadding, AppBorder, AppBorderRadius
from services.db_service import DBService
from services.devworld_ai_service import DevWorldAIService, PERSONA_CONFIGS

class SpecialistChatComponent:
    def __init__(self, page: ft.Page, persona_key: str):
        self.page = page
        self.persona_key = persona_key
        self.p_info = PERSONA_CONFIGS.get(persona_key, PERSONA_CONFIGS["personal"])
        
        self.messages_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
        self.input_field = ft.TextField(
            hint_text=f"Converse com {self.p_info['name'].split()[0]}...",
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
            icon_color=self.p_info["color"],
            icon_size=24,
            on_click=lambda _: self._send_message()
        )
        self.quick_prompts_row = ft.Row(spacing=6, scroll=ft.ScrollMode.AUTO)

    def build(self) -> ft.Control:
        # Header do Especialista
        header = ft.Container(
            content=ft.Row([
                ft.CircleAvatar(
                    radius=18,
                    bgcolor=f"{self.p_info['color']}33",
                    content=ft.Icon(getattr(Icons, self.p_info["avatar_icon"].upper(), Icons.PERSON), color=self.p_info["color"], size=20)
                ),
                ft.Column([
                    ft.Text(self.p_info["name"], size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                    ft.Text(self.p_info["title"], size=11, color=SportColors.TEXT_SECONDARY),
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=Icons.DELETE_OUTLINE,
                    icon_color=SportColors.TEXT_MUTED,
                    icon_size=18,
                    tooltip="Limpar conversa",
                    on_click=lambda _: self._clear_chat()
                )
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=SportColors.BG_SURFACE_ALT,
            padding=AppPadding.symmetric(horizontal=12, vertical=10),
            border_radius=12,
            border=AppBorder.all(1, f"{self.p_info['color']}55")
        )

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
                header,
                self.quick_prompts_row,
                ft.Container(
                    content=self.messages_column,
                    expand=True,
                    padding=AppPadding.symmetric(horizontal=4, vertical=6)
                ),
                input_bar,
            ], spacing=8),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _update_quick_prompts(self):
        self.quick_prompts_row.controls.clear()
        prompts = {
            "personal": [
                "Como substituir a cadeira extensora hoje?",
                "Qual a melhor cadência de repetições?",
                "Como saber se devo aumentar a carga?",
                "Sinto dor no ombro no supino, o que fazer?",
                "Como aplicar RPE/RIR nas minhas séries?"
            ],
            "nutri": [
                "O que comer no pré-treino para ter energia?",
                "Como bater 160g de proteína de forma prática?",
                "Como tomar creatina corretamente?",
                "Sugestão de refeição rápida pós-treino",
                "Substituição saudável para o arroz branco"
            ]
        }

        for text in prompts.get(self.persona_key, []):
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
        history = DBService.get_chat_history(self.persona_key, limit=30)

        if not history:
            welcome_text = f"Olá! Sou {self.p_info['name']} ({self.p_info['title']}). Estou conectado aos seus dados de treino e saúde. Como posso te orientar hoje?"
            self.messages_column.controls.append(
                self._render_message_bubble("assistant", welcome_text)
            )
        else:
            for h in history:
                self.messages_column.controls.append(
                    self._render_message_bubble(h["role"], h["content"])
                )

    def _render_message_bubble(self, role: str, content: str) -> ft.Control:
        is_user = role == "user"
        
        if is_user:
            return ft.Row([
                ft.Container(
                    content=ft.Text(content, size=13, color=SportColors.TEXT_WHITE),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.all(12),
                    border_radius=AppBorderRadius.only(top_left=12, top_right=12, bottom_left=12, bottom_right=2),
                    border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
                    width=280
                )
            ], alignment=ft.MainAxisAlignment.END)
        else:
            return ft.Row([
                ft.CircleAvatar(
                    radius=14,
                    bgcolor=f"{self.p_info['color']}33",
                    content=ft.Icon(getattr(Icons, self.p_info["avatar_icon"].upper(), Icons.PERSON), color=self.p_info["color"], size=14)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(self.p_info["name"], size=11, weight=ft.FontWeight.BOLD, color=self.p_info["color"]),
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
                    border=AppBorder.all(1, f"{self.p_info['color']}44"),
                    width=290
                )
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, spacing=8)

    def _send_message(self):
        user_text = self.input_field.value
        if not user_text or not user_text.strip():
            return

        self.input_field.value = ""
        
        self.messages_column.controls.append(
            self._render_message_bubble("user", user_text)
        )
        
        typing_indicator = ft.Row([
            ft.Text(f"{self.p_info['name'].split()[0]} está formulando a orientação...", size=11, color=SportColors.TEXT_MUTED, italic=True)
        ])
        self.messages_column.controls.append(typing_indicator)
        if self.page:
            self.page.update()

        bot_response = DevWorldAIService.send_message(self.persona_key, user_text)
        
        self.messages_column.controls.remove(typing_indicator)
        self.messages_column.controls.append(
            self._render_message_bubble("assistant", bot_response)
        )
        if self.page:
            self.page.update()

    def _clear_chat(self):
        try:
            with DBService.get_connection() as conn:
                u_id = DBService.get_active_user().get("id", "user_default")
                conn.execute("DELETE FROM chat_messages WHERE persona = ? AND user_id = ?", (self.persona_key, u_id))
                conn.commit()
        except Exception:
            pass
        self._reload_messages()
        if self.page:
            self.page.update()
