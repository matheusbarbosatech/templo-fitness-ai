"""
Módulo de Evolução Corporal & Galeria de Fotos - Apollo Fitness AI.
Acompanhamento fotográfico (Frente, Costas, Lado), medição de circunferências,
comparativo visual Antes & Depois e histórico de pesagem. 100% compatível com Web e Desktop.
"""
import flet as ft
from datetime import date
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder, AppAlignment
from services.db_service import DBService

from typing import Optional

class PhotosEvolutionView:
    def __init__(self, page: ft.Page, user_id: Optional[int] = None):
        self.page = page
        self.user_id = user_id

    def build(self) -> ft.Control:
        uid = self.user_id or DBService.get_active_user_id()
        profile = DBService.get_athlete_profile(user_id=uid)
        logs = DBService.get_evolution_logs(user_id=uid)

        latest_weight = logs[0]["weight_kg"] if logs and logs[0].get("weight_kg") else profile.get("weight_kg", 78.5)
        
        # 1. Card de Resumo de Medidas
        summary_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header(
                    "EVOLUÇÃO CORPORAL",
                    "Acompanhamento de medidas e fotos",
                    icon=Icons.SHOW_CHART,
                    action_button=ft.ElevatedButton(
                        "+ Novo Registro",
                        icon=Icons.ADD_A_PHOTO,
                        style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.BG_DARK),
                        on_click=lambda _: self._show_add_log_dialog()
                    )
                ),
                ft.Row([
                    self._metric_stat_box("Peso Atual", f"{latest_weight} kg", SportColors.PRIMARY_NEON),
                    self._metric_stat_box("Peso Alvo", f"{profile.get('target_weight_kg', 75.0)} kg", SportColors.CYAN_ELECTRIC),
                    self._metric_stat_box("Registros", f"{len(logs)}", SportColors.TEXT_SECONDARY),
                ], spacing=6)
            ], spacing=12),
            border_color=SportColors.BORDER_DEFAULT,
            padding=14
        )

        # 2. Card Comparativo "Antes e Depois"
        comparison_widget = self._build_before_after_card(logs)

        # 3. Galeria de Fotos e Histórico
        gallery_column = ft.Column(spacing=10)
        if not logs:
            gallery_column.controls.append(
                SportStyles.card_container(
                    content=ft.Column([
                        ft.Icon(Icons.PHOTO_CAMERA_OUTLINED, color=SportColors.TEXT_MUTED, size=36),
                        ft.Text("Nenhum registro corporal cadastrado ainda.", size=13, weight=ft.FontWeight.W_500, color=SportColors.TEXT_WHITE),
                        ft.Text("Clique no botão '+ Novo Registro' acima para adicionar seu peso, medidas ou foto!", size=11, color=SportColors.TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=6),
                    padding=20,
                    border_color=SportColors.BORDER_DEFAULT
                )
            )
        else:
            for l in logs:
                photo_path = l.get("photo_path", "")
                photo_widget = self._render_photo_thumbnail(photo_path)

                card = SportStyles.card_container(
                    content=ft.Row([
                        photo_widget,
                        ft.Column([
                            ft.Row([
                                SportStyles.badge(f"Ângulo: {l.get('angle', 'Frente')}", SportColors.PRIMARY_NEON),
                                ft.Text(str(l.get("log_date", "")), size=11, color=SportColors.TEXT_MUTED)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"Peso: {l.get('weight_kg', '--')} kg", size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                            ft.Text(f"Tórax: {l.get('chest_cm', '--')}cm • Braço: {l.get('arm_cm', '--')}cm • Cintura: {l.get('waist_cm', '--')}cm", size=11, color=SportColors.TEXT_SECONDARY),
                            ft.Text(str(l.get("notes", "Sem observações")), size=11, color=SportColors.TEXT_MUTED, italic=True)
                        ], spacing=2, expand=True)
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    border_color=SportColors.BORDER_DEFAULT,
                    padding=10
                )
                gallery_column.controls.append(card)

        content_list = [summary_card]
        if comparison_widget:
            content_list.append(comparison_widget)
        content_list.extend([
            ft.Text("Histórico de Registros Corporais:", size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY),
            gallery_column,
            ft.Container(height=90)
        ])

        return ft.Container(
            content=ft.ListView(content_list, spacing=12, padding=AppPadding.all(14)),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _render_photo_thumbnail(self, photo_path: str, size: int = 70):
        if photo_path and (photo_path.startswith("http://") or photo_path.startswith("https://") or photo_path.startswith("data:image/")):
            try:
                return ft.Image(
                    src=photo_path,
                    width=size,
                    height=size,
                    fit=ft.ImageFit.COVER,
                    border_radius=8
                )
            except Exception:
                pass
        return ft.Container(
            content=ft.Icon(Icons.PERSON_OUTLINE, color=SportColors.PRIMARY_NEON, size=28),
            width=size,
            height=size,
            bgcolor=SportColors.BG_SURFACE_ALT,
            border_radius=8,
            alignment=AppAlignment.CENTER
        )

    def _build_before_after_card(self, logs):
        if len(logs) < 2:
            return None

        newest = logs[0]
        oldest = logs[-1]

        diff_weight = round(float(newest.get("weight_kg", 0)) - float(oldest.get("weight_kg", 0)), 1)
        diff_str = f"+{diff_weight}kg" if diff_weight > 0 else f"{diff_weight}kg"
        badge_color = SportColors.PRIMARY_NEON if diff_weight <= 0 else SportColors.CYAN_ELECTRIC

        return SportStyles.card_container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(Icons.COMPARE, color=SportColors.PRIMARY_NEON, size=18),
                        ft.Text("COMPARATIVO: ANTES & DEPOIS", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
                    ], spacing=6),
                    SportStyles.badge(f"Variação: {diff_str}", badge_color)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    # Antes
                    ft.Column([
                        self._render_photo_thumbnail(oldest.get("photo_path", ""), size=80),
                        ft.Text("Início", size=11, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED),
                        ft.Text(f"{oldest.get('weight_kg', '--')}kg", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                        ft.Text(str(oldest.get("log_date", "")), size=10, color=SportColors.TEXT_MUTED)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    ft.Icon(Icons.ARROW_FORWARD, color=SportColors.PRIMARY_NEON, size=22),
                    # Depois
                    ft.Column([
                        self._render_photo_thumbnail(newest.get("photo_path", ""), size=80),
                        ft.Text("Atual", size=11, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON),
                        ft.Text(f"{newest.get('weight_kg', '--')}kg", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                        ft.Text(str(newest.get("log_date", "")), size=10, color=SportColors.TEXT_MUTED)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ], spacing=10),
            bgcolor=SportColors.BG_SURFACE,
            border_color=SportColors.BORDER_NEON,
            padding=12
        )

    def _metric_stat_box(self, label: str, value: str, color: str):
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=11, color=SportColors.TEXT_SECONDARY),
                ft.Text(value, size=14, weight=ft.FontWeight.BOLD, color=color),
            ], spacing=2, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=SportColors.BG_SURFACE_ALT,
            padding=AppPadding.symmetric(vertical=8, horizontal=10),
            border_radius=8,
            expand=True
        )

    def _show_add_log_dialog(self):
        angle_drop = ft.Dropdown(
            label="Ângulo da Foto / Registro",
            value="Frente",
            options=[
                ft.dropdown.Option("Frente"),
                ft.dropdown.Option("Costas"),
                ft.dropdown.Option("Perfil Esquerdo"),
                ft.dropdown.Option("Perfil Direito"),
            ],
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )
        weight_in = ft.TextField(label="Peso Corporal (kg)", value="78.5", keyboard_type=ft.KeyboardType.NUMBER, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        arm_in = ft.TextField(label="Braço Contraído (cm)", value="38.0", keyboard_type=ft.KeyboardType.NUMBER, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        waist_in = ft.TextField(label="Cintura na Linha Umbilical (cm)", value="82.0", keyboard_type=ft.KeyboardType.NUMBER, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        chest_in = ft.TextField(label="Tórax / Peitoral (cm)", value="102.0", keyboard_type=ft.KeyboardType.NUMBER, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        
        photo_url_in = ft.TextField(
            label="URL / Link da Foto (ou deixe vazio)",
            hint_text="Ex: https://... ou cole link direto",
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )
        notes_in = ft.TextField(label="Notas & Sensação Muscular", hint_text="Ex: Mais definição abdominal e vascularização", color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.ADD_A_PHOTO, color=SportColors.PRIMARY_NEON),
                ft.Text("Novo Registro de Evolução", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text("Registre suas medidas e foto para alimentar o comparativo visual e a IA:", size=11, color=SportColors.TEXT_SECONDARY),
                    angle_drop,
                    weight_in,
                    ft.Row([arm_in, waist_in], spacing=8),
                    chest_in,
                    photo_url_in,
                    notes_in,
                ], spacing=8),
                width=330,
                height=380
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self._close_dialog(dialog)),
                ft.ElevatedButton(
                    "Salvar Registro",
                    style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.BG_DARK),
                    on_click=lambda _: self._save_log(dialog, angle_drop.value, weight_in.value, chest_in.value, arm_in.value, waist_in.value, photo_url_in.value, notes_in.value)
                )
            ]
        )
        if self.page:
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

    def _save_log(self, dialog, angle, weight, chest, arm, waist, photo_path, notes):
        uid = self.user_id or DBService.get_active_user_id()
        DBService.add_evolution_log(
            angle=angle or "Frente",
            photo_path=photo_path or "",
            weight=float(weight or 0),
            chest=float(chest or 0),
            arm=float(arm or 0),
            waist=float(waist or 0),
            thigh=0.0,
            notes=notes or "Registro regular de evolução.",
            user_id=uid
        )
        self._close_dialog(dialog)
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Evolução corporal registrada com sucesso!", color=SportColors.TEXT_WHITE),
                bgcolor=SportColors.BG_SURFACE_ALT,
                duration=1500
            )
            self.page.snack_bar.open = True
            self.build()
            self.page.update()

    def _close_dialog(self, dialog):
        dialog.open = False
        if self.page:
            self.page.update()
