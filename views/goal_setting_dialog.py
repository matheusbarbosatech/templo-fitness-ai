"""
Formulário de Definição de Objetivos, Anamnese & Metas 360° - Templo Fitness AI.
Calcula necessidades metabólicas (TMB, TDEE), metas de macros e calibra a divisão de treino ideal.
"""
import flet as ft
from typing import Callable, Optional
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder
from core.ui_helper import UIHelper
from services.db_service import DBService

class GoalSettingDialog:
    def __init__(self, page: ft.Page, on_saved: Optional[Callable] = None, user_id: Optional[int] = None):
        self.page = page
        self.on_saved = on_saved
        self.user_id = user_id
        self.dialog: Optional[ft.AlertDialog] = None

    def show(self):
        uid = self.user_id or DBService.get_active_user_id()
        profile = DBService.get_athlete_profile(user_id=uid)

        goal_drop = ft.Dropdown(
            label="Objetivo Principal",
            value=profile.get("goal", "hipertrofia"),
            options=[
                ft.dropdown.Option("hipertrofia", "💪 Hipertrofia & Ganho de Massa"),
                ft.dropdown.Option("cutting", "🔥 Definição / Queima de Gordura"),
                ft.dropdown.Option("recomposicao", "⚡ Recomposição Corporal (Massa + Secar)"),
                ft.dropdown.Option("forca", "🏋️ Força Máxima (Powerlifting)"),
                ft.dropdown.Option("saude", "❤️ Saúde, Postura & Longevidade"),
            ],
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        target_weight_in = ft.TextField(
            label="Peso Alvo (kg)",
            value=str(profile.get("target_weight_kg", 75.0)),
            keyboard_type=ft.KeyboardType.NUMBER,
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        target_weeks_in = ft.TextField(
            label="Prazo Desejado (semanas)",
            value=str(profile.get("target_weeks", 12)),
            keyboard_type=ft.KeyboardType.NUMBER,
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        days_drop = ft.Dropdown(
            label="Frequência Semanal de Treino",
            value=str(profile.get("training_days_week", 4)),
            options=[
                ft.dropdown.Option("3", "3 dias por semana (Full Body ou ABC)"),
                ft.dropdown.Option("4", "4 dias por semana (Upper / Lower)"),
                ft.dropdown.Option("5", "5 dias por semana (Push Pull Legs + Upper)"),
                ft.dropdown.Option("6", "6 dias por semana (Push Pull Legs 2x)"),
            ],
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        time_drop = ft.Dropdown(
            label="Tempo Disponível por Treino",
            value=str(profile.get("session_minutes", 60)),
            options=[
                ft.dropdown.Option("30", "30 minutos (Treino Expresso)"),
                ft.dropdown.Option("45", "45 minutos (Foco e Intensidade)"),
                ft.dropdown.Option("60", "60 minutos (Padrão Ouro)"),
                ft.dropdown.Option("90", "90 minutos (Volume Completo)"),
            ],
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        exp_drop = ft.Dropdown(
            label="Nível de Experiência na Musculação",
            value=profile.get("experience_level", "intermediario"),
            options=[
                ft.dropdown.Option("iniciante", "Iniciante (menos de 6 meses)"),
                ft.dropdown.Option("intermediario", "Intermediário (6 meses a 2 anos)"),
                ft.dropdown.Option("avancado", "Avançado (+2 anos de treino sério)"),
            ],
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        pain_drop = ft.Dropdown(
            label="Histórico de Dor / Limitação Articular",
            value=profile.get("joint_pain", "nenhuma"),
            options=[
                ft.dropdown.Option("nenhuma", "Nenhuma dor articular"),
                ft.dropdown.Option("ombro", "Desconforto no Ombro / Manguito"),
                ft.dropdown.Option("joelho", "Dor no Joelho / Condromalácia"),
                ft.dropdown.Option("lombar", "Desconforto Lombar / Hérnia"),
            ],
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        diet_drop = ft.Dropdown(
            label="Estratégia Alimentar Preferida",
            value=profile.get("diet_strategy", "equilibrada"),
            options=[
                ft.dropdown.Option("equilibrada", "Dieta Equilibrada / Flexível"),
                ft.dropdown.Option("hiperproteica", "Hiperproteica (2.2g - 2.5g/kg)"),
                ft.dropdown.Option("low_carb", "Low Carb"),
                ft.dropdown.Option("vegetariana", "Vegetariana / Plant-Based"),
            ],
            color=SportColors.TEXT_WHITE,
            bgcolor=SportColors.BG_INPUT
        )

        result_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(Icons.AUTO_AWESOME, color=SportColors.PRIMARY_NEON, size=16),
                    ft.Text("PRESCRIÇÃO AUTOMÁTICA DA IA", size=11, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON),
                ], spacing=4),
                ft.Text(
                    f"• Calorias Alvo: ~{int(profile.get('daily_calories_target', 2400))} kcal/dia\n"
                    f"• Proteína Diária: ~{int(profile.get('daily_protein_target', 160))}g/dia\n"
                    f"• Hidratação Recomendada: ~{int(profile.get('daily_water_target_ml', 3000))} ml\n"
                    f"• Divisão de Treino Sugerida: {profile.get('recommended_routine', 'ABC')}",
                    size=12,
                    color=SportColors.TEXT_WHITE
                )
            ], spacing=4),
            bgcolor=SportColors.BG_SURFACE_ALT,
            padding=AppPadding.all(10),
            border_radius=8,
            border=AppBorder.all(1, SportColors.BORDER_NEON)
        )

        def on_field_changed(_):
            try:
                days = int(days_drop.value or 4)
                g = goal_drop.value or "hipertrofia"
                calc = DBService.save_goals(
                    goal=g,
                    target_weight=float(target_weight_in.value or 75.0),
                    target_weeks=int(target_weeks_in.value or 12),
                    days_week=days,
                    session_mins=int(time_drop.value or 60),
                    experience=exp_drop.value or "intermediario",
                    joint_pain=pain_drop.value or "nenhuma",
                    diet_strategy=diet_drop.value or "equilibrada"
                )
                result_container.content.controls[1].value = (
                    f"• Calorias Alvo: ~{int(calc['daily_calories'])} kcal/dia\n"
                    f"• Proteína Diária: ~{int(calc['daily_protein'])}g/dia\n"
                    f"• Hidratação Recomendada: ~{int(calc['daily_water_ml'])} ml\n"
                    f"• Divisão de Treino Sugerida: {calc['recommended_routine']}"
                )
                self.page.update()
            except Exception:
                pass

        for c in [goal_drop, days_drop, time_drop, exp_drop, pain_drop, diet_drop]:
            c.on_change = on_field_changed

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.TRACK_CHANGES, color=SportColors.PRIMARY_NEON, size=22),
                ft.Text("Definição de Metas & Objetivos", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=8),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text("Responda às questões abaixo para que o Templo Fitness AI calibre seu treino e mordomia com precisão científica:", size=12, color=SportColors.TEXT_SECONDARY),
                    goal_drop,
                    ft.Row([target_weight_in, target_weeks_in], spacing=8),
                    days_drop,
                    time_drop,
                    exp_drop,
                    pain_drop,
                    diet_drop,
                    result_container
                ], spacing=10),
                width=350,
                height=460
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self._close()),
                ft.ElevatedButton(
                    "Calibrar Meu Treino & Metas",
                    icon=Icons.CHECK,
                    style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.BG_DARK),
                    on_click=lambda _: self._save_and_apply(
                        goal_drop.value, target_weight_in.value, target_weeks_in.value,
                        days_drop.value, time_drop.value, exp_drop.value, pain_drop.value, diet_drop.value
                    )
                )
            ]
        )

        UIHelper.open_dialog(self.page, self.dialog)

    def _save_and_apply(self, goal, target_w, target_weeks, days, time_m, exp, pain, diet):
        uid = self.user_id or DBService.get_active_user_id()
        calc = DBService.save_goals(
            goal=goal or "hipertrofia",
            target_weight=float(target_w or 75.0),
            target_weeks=int(target_weeks or 12),
            days_week=int(days or 4),
            session_mins=int(time_m or 60),
            experience=exp or "intermediario",
            joint_pain=pain or "nenhuma",
            diet_strategy=diet or "equilibrada",
            user_id=uid
        )
        # Se for PPL ou UpperLower, aplica a rotina prescrita
        rec_routine = calc.get("recommended_routine", "ABC")
        DBService.apply_coach_routine_preset(rec_routine, user_id=uid)

        self._close()
        UIHelper.show_toast(self.page, f"Metas salvas! Divisão recomendada aplicada: {rec_routine}", color=SportColors.PRIMARY_NEON)
        if self.on_saved:
            self.on_saved()

    def _close(self):
        if self.dialog:
            UIHelper.close_dialog(self.page, self.dialog)
