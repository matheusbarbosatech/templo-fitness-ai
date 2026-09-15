"""
Componente Oficial de Chat Especialista com IA - Templo Fitness AI.
Padrão Minimalista Monocromático (Preto, Cinza e Branco).
Interface fluida, de alto contraste, sem distrações e com tipografia limpa.
"""
from typing import Optional
import flet as ft
from core.theme import SportColors, Icons, AppPadding, AppBorder, AppBorderRadius, AppAlignment
from services.db_service import DBService
from services.devworld_ai_service import DevWorldAIService, PERSONA_CONFIGS

class SpecialistChatComponent:
    def __init__(self, page: ft.Page, persona_key: str = "personal", user_id: Optional[int] = None):
        self.page = page
        self.persona_key = persona_key
        self.user_id = user_id
        self.p_info = PERSONA_CONFIGS.get(persona_key, PERSONA_CONFIGS["personal"])
        
        self.messages_column = ft.Column(spacing=14, scroll=ft.ScrollMode.AUTO)
        
        self.input_field = ft.TextField(
            hint_text=f"Converse com o {self.p_info['name'].split()[0]} sobre cargas, postura, dúvidas...",
            hint_style=ft.TextStyle(color=SportColors.TEXT_MUTED, size=12),
            bgcolor=SportColors.BG_INPUT,
            border_color=SportColors.BORDER_DEFAULT,
            focused_border_color=SportColors.TEXT_WHITE,
            color=SportColors.TEXT_WHITE,
            text_size=13,
            content_padding=AppPadding.symmetric(horizontal=14, vertical=12),
            expand=True,
            on_submit=lambda _: self._send_message()
        )
        
        self.send_button = ft.Container(
            content=ft.Icon(Icons.ARROW_UPWARD, color=SportColors.BG_DARK, size=18),
            bgcolor=SportColors.TEXT_WHITE,
            border_radius=10,
            padding=AppPadding.all(10),
            ink=True,
            tooltip="Enviar mensagem",
            on_click=lambda _: self._send_message()
        )
        
        self.quick_prompts_row = ft.Row(spacing=6, scroll=ft.ScrollMode.AUTO)

    def build(self) -> ft.Control:
        # Header do Especialista em Preto, Cinza e Branco
        header = ft.Container(
            content=ft.Row([
                ft.CircleAvatar(
                    radius=18,
                    bgcolor="#27272A",
                    content=ft.Icon(
                        getattr(Icons, self.p_info["avatar_icon"].upper(), Icons.PERSON),
                        color=SportColors.TEXT_WHITE,
                        size=18
                    )
                ),
                ft.Column([
                    ft.Row([
                        ft.Text(self.p_info["name"], size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                        ft.Container(
                            content=ft.Text("IA ATIVA", size=8, weight=ft.FontWeight.BOLD, color=SportColors.BG_DARK),
                            bgcolor=SportColors.TEXT_WHITE,
                            padding=AppPadding.symmetric(horizontal=6, vertical=2),
                            border_radius=4
                        )
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Text(self.p_info["title"], size=11, color=SportColors.TEXT_SECONDARY),
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=Icons.DELETE_OUTLINE,
                    icon_color=SportColors.TEXT_MUTED,
                    icon_size=18,
                    tooltip="Limpar histórico",
                    on_click=lambda _: self._clear_chat()
                )
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=SportColors.BG_SURFACE_ALT,
            padding=AppPadding.symmetric(horizontal=14, vertical=10),
            border_radius=12,
            border=AppBorder.all(1, SportColors.BORDER_DEFAULT)
        )

        self._reload_messages()
        self._update_quick_prompts()

        input_dock = ft.Container(
            content=ft.Row([
                self.input_field,
                self.send_button
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
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
                input_dock,
                ft.Container(height=10)
            ], spacing=8),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _update_quick_prompts(self):
        self.quick_prompts_row.controls.clear()
        prompts = {
            "personal": [
                "Como substituir a máquina hoje?",
                "Qual a cadência de repetição ideal?",
                "Como saber se devo aumentar a carga?",
                "Dor no ombro no supino, o que fazer?",
                "Como aplicar RPE/RIR nas séries?"
            ],
            "nutri": [
                "O que comer no pré-treino para ter energia?",
                "Como bater 160g de proteína no dia?",
                "Como tomar creatina corretamente?",
                "Sugestão de refeição rápida pós-treino",
                "Substituição saudável para arroz branco"
            ]
        }

        for text in prompts.get(self.persona_key, []):
            self.quick_prompts_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(Icons.LIGHTBULB_OUTLINE, size=12, color=SportColors.TEXT_SECONDARY),
                        ft.Text(text, size=11, color=SportColors.TEXT_PRIMARY)
                    ], spacing=4, tight=True),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.symmetric(horizontal=10, vertical=6),
                    border_radius=16,
                    border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
                    on_click=lambda _, t=text: self._send_quick_prompt(t),
                    ink=True
                )
            )

    def _send_quick_prompt(self, prompt_text: str):
        self.input_field.value = prompt_text
        self._send_message()

    def _reload_messages(self):
        self.messages_column.controls.clear()
        uid = self.user_id or DBService.get_active_user_id()
        history = DBService.get_chat_history(self.persona_key, limit=30, user_id=uid)

        if not history:
            welcome_text = (
                f"Olá! Sou o **{self.p_info['name']}**, seu {self.p_info['title']}.\n\n"
                "Estou conectado aos seus dados de periodização, tonelagem e saúde. "
                "Pode me perguntar sobre substituições de aparelhos ocupados, ajustes de pegada, cadência ou dores articulares!"
            )
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
                    content=ft.Text(content, size=13, color=SportColors.TEXT_WHITE, selectable=True),
                    bgcolor="#27272A",
                    padding=AppPadding.symmetric(horizontal=14, vertical=10),
                    border_radius=AppBorderRadius.only(top_left=14, top_right=14, bottom_left=14, bottom_right=3),
                    border=AppBorder.all(1, "#3F3F46")
                )
            ], alignment=ft.MainAxisAlignment.END)
        else:
            return ft.Row([
                ft.CircleAvatar(
                    radius=14,
                    bgcolor="#27272A",
                    content=ft.Icon(
                        getattr(Icons, self.p_info["avatar_icon"].upper(), Icons.PERSON),
                        color=SportColors.TEXT_WHITE,
                        size=14
                    )
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(self.p_info["name"], size=11, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                            ft.Text("• Personal IA", size=10, color=SportColors.TEXT_MUTED)
                        ], spacing=4),
                        ft.Markdown(
                            content,
                            selectable=True,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            code_theme="atom-one-dark"
                        )
                    ], spacing=4),
                    bgcolor=SportColors.BG_SURFACE,
                    padding=AppPadding.all(14),
                    border_radius=AppBorderRadius.only(top_left=3, top_right=14, bottom_left=14, bottom_right=14),
                    border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
                    expand=True
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
            ft.Icon(Icons.MORE_HORIZ, size=16, color=SportColors.TEXT_MUTED),
            ft.Text(f"{self.p_info['name'].split()[0]} está analisando sua dúvida...", size=11, color=SportColors.TEXT_MUTED, italic=True)
        ], spacing=6)
        self.messages_column.controls.append(typing_indicator)
        if self.page:
            self.page.update()

        uid = self.user_id or DBService.get_active_user_id()
        bot_response = DevWorldAIService.send_message(self.persona_key, user_text, user_id=uid)
        
        self.messages_column.controls.remove(typing_indicator)
        self.messages_column.controls.append(
            self._render_message_bubble("assistant", bot_response)
        )
        if self.page:
            self.page.update()

    def _clear_chat(self):
        try:
            with DBService.get_connection() as conn:
                u_id = self.user_id or DBService.get_active_user_id()
                conn.execute("DELETE FROM ai_chat_history WHERE persona = ? AND user_id = ?", (self.persona_key, u_id))
                conn.commit()
        except Exception:
            pass
        self._reload_messages()
        if self.page:
            self.page.update()
