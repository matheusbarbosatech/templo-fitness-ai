"""
Dashboard Principal 360° - Apollo Fitness AI (Estilo Minimalista Apple Fitness+ / Whoop).
Apresenta o resumo holístico diário do atleta com design limpo, legibilidade perfeita e tons elegantes.
"""
import flet as ft
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder
from core.health_math import HealthMath
from services.db_service import DBService

from views.goal_setting_dialog import GoalSettingDialog
from views.auth_dialog import AuthDialog

class HomeDashboardView:
    def __init__(self, page: ft.Page, on_navigate_callback=None):
        self.page = page
        self.on_navigate = on_navigate_callback

    def build(self) -> ft.Control:
        profile = DBService.get_athlete_profile()
        nutrition = DBService.get_daily_nutrition()
        wellness = DBService.get_today_wellness()
        routines = DBService.get_routines()
        
        # Cálculos de Metas
        tmb = HealthMath.calculate_tmb_mifflin(
            float(profile.get("weight_kg", 78.5)),
            float(profile.get("height_cm", 178)),
            int(profile.get("age", 26)),
            str(profile.get("sex", "M"))
        )
        tdee = HealthMath.calculate_tdee(tmb, str(profile.get("activity_level", "intenso")))
        macros_target = HealthMath.calculate_macros_target(
            tdee,
            str(profile.get("goal", "hipertrofia")),
            float(profile.get("weight_kg", 78.5))
        )

        water_consumed = int(nutrition.get("total_water_ml", 0))
        water_goal = int(macros_target.get("water_ml", 3000))
        water_pct = min(water_consumed / max(water_goal, 1), 1.0)

        cal_consumed = int(nutrition.get("total_calories", 0))
        cal_goal = int(macros_target.get("target_calories", 2600))
        cal_pct = min(cal_consumed / max(cal_goal, 1), 1.0)

        prot_consumed = int(nutrition.get("total_protein", 0))
        prot_goal = int(macros_target.get("protein_g", 160))

        # 1. Header do Atleta
        header_card = SportStyles.card_container(
            content=ft.Column([
                ft.Row([
                    ft.CircleAvatar(
                        radius=24,
                        bgcolor=SportColors.BG_SURFACE_ALT,
                        content=ft.Icon(Icons.PERSON, color=SportColors.PRIMARY_NEON, size=24)
                    ),
                    ft.Column([
                        ft.Text(f"Olá, {profile.get('name', 'Atleta')}", size=18, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                        ft.Row([
                            SportStyles.badge(profile.get('goal', 'Hipertrofia').capitalize(), SportColors.PRIMARY_NEON),
                            SportStyles.badge(f"{profile.get('weight_kg')} kg", SportColors.TEXT_SECONDARY),
                            SportStyles.badge(f"Divisão: {profile.get('recommended_routine', 'ABC')}", SportColors.CYAN_ELECTRIC),
                        ], spacing=6)
                    ], spacing=2, expand=True),
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(color=SportColors.BORDER_DEFAULT, height=6),
                ft.Row([
                    ft.ElevatedButton(
                        "🎯 Definir Metas 360°",
                        style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON_DARK, color=SportColors.TEXT_WHITE),
                        height=32,
                        on_click=lambda _: GoalSettingDialog(self.page, on_saved=lambda: self._nav_to(0)).show()
                    ),
                    ft.ElevatedButton(
                        "👥 Alternar Atleta",
                        style=ft.ButtonStyle(bgcolor=SportColors.BG_SURFACE_ALT, color=SportColors.TEXT_WHITE),
                        height=32,
                        on_click=lambda _: AuthDialog(self.page, on_user_changed=lambda: self._nav_to(0)).show()
                    ),
                ], spacing=8)
            ], spacing=10),
            border_color=SportColors.BORDER_DEFAULT,
            padding=14
        )

        # 2. Card de Treino Ativo do Dia
        active_routine = routines[0] if routines else None
        routine_name = active_routine.get("name", "Treino A - Push") if active_routine else "Treino A"
        routine_desc = active_routine.get("description", "Peito, Ombros e Tríceps") if active_routine else "Peito e Ombros"
        
        workout_card = SportStyles.card_container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(Icons.FITNESS_CENTER, color=SportColors.PRIMARY_NEON, size=20),
                        ft.Text("TREINO PROGRAMADO", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY),
                    ], spacing=6),
                    SportStyles.badge("Hoje", SportColors.PRIMARY_NEON)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(routine_name, size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                ft.Text(routine_desc, size=12, color=SportColors.TEXT_SECONDARY),
                ft.Divider(color=SportColors.BORDER_DEFAULT, height=10),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(Icons.PLAY_ARROW_ROUNDED, color=SportColors.TEXT_WHITE, size=18),
                        ft.Text("INICIAR TREINO", size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
                    bgcolor=SportColors.PRIMARY_NEON_DARK,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=lambda _: self._nav_to(1),
                    height=42
                )
            ], spacing=8),
            border_color=SportColors.BORDER_DEFAULT,
            padding=14
        )

        # 3. Prontuário Multidisciplinar da IA
        team_card = SportStyles.card_container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(Icons.GROUPS_OUTLINED, color=SportColors.CYAN_ELECTRIC, size=20),
                        ft.Text("EQUIPE TÉCNICA DE IA", size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                    ], spacing=6),
                    ft.TextButton(
                        "Abrir Chat >",
                        style=ft.ButtonStyle(color=SportColors.PRIMARY_NEON),
                        on_click=lambda _: self._nav_to(3)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                self._specialist_mini_row(Icons.FITNESS_CENTER, SportColors.PRIMARY_NEON, "Personal Márcio", "Foco em cadência controlada de 2s na descida."),
                self._specialist_mini_row(Icons.RESTAURANT, SportColors.AMBER_GOLD, "Dra. Camila (Nutri)", f"Meta: {cal_consumed}/{cal_goal} kcal • {prot_consumed}/{prot_goal}g proteína."),
                self._specialist_mini_row(Icons.PSYCHOLOGY, SportColors.PURPLE_MIND, "Dr. Gabriel (Mente)", f"Prontidão {wellness.get('mood_score', 4)}/5 • Sono {wellness.get('sleep_hours', 7.5)}h."),
                self._specialist_mini_row(Icons.HEALING, SportColors.TEAL_PHYSIO, "Dr. Rafael (Fisio)", f"{wellness.get('soreness_notes', 'Sem queixas articulares')}."),
            ], spacing=8),
            border_color=SportColors.BORDER_DEFAULT,
            padding=14
        )

        # 4. Progresso de Metas Diárias (Água & Calorias)
        goals_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header("METAS DO DIA", "Nutrição & Hidratação", icon=Icons.SHOW_CHART),
                
                # Água
                ft.Column([
                    ft.Row([
                        ft.Text("Hidratação", size=12, color=SportColors.TEXT_SECONDARY),
                        ft.Text(f"{water_consumed} / {water_goal} ml", size=12, weight=ft.FontWeight.BOLD, color=SportColors.CYAN_ELECTRIC)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ProgressBar(value=water_pct, color=SportColors.CYAN_ELECTRIC, bgcolor=SportColors.BG_SURFACE_ALT, height=6),
                ], spacing=4),

                # Calorias
                ft.Column([
                    ft.Row([
                        ft.Text("Calorias", size=12, color=SportColors.TEXT_SECONDARY),
                        ft.Text(f"{cal_consumed} / {cal_goal} kcal", size=12, weight=ft.FontWeight.BOLD, color=SportColors.AMBER_GOLD)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ProgressBar(value=cal_pct, color=SportColors.AMBER_GOLD, bgcolor=SportColors.BG_SURFACE_ALT, height=6),
                ], spacing=4),

                # Botões de Ação Rápida
                ft.Row([
                    ft.ElevatedButton(
                        "+ 300ml Água",
                        icon=Icons.WATER_DROP,
                        style=ft.ButtonStyle(bgcolor=SportColors.BG_SURFACE_ALT, color=SportColors.TEXT_PRIMARY),
                        on_click=lambda _: self._quick_add_water(300),
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "+ Registrar Prato",
                        icon=Icons.ADD,
                        style=ft.ButtonStyle(bgcolor=SportColors.BG_SURFACE_ALT, color=SportColors.TEXT_PRIMARY),
                        on_click=lambda _: self._nav_to(4),
                        expand=True
                    ),
                ], spacing=8)
            ], spacing=12),
            border_color=SportColors.BORDER_DEFAULT,
            padding=14
        )

        # Card Bíblico: O Corpo como Templo do Espírito Santo
        temple_card = SportStyles.card_container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(Icons.LOCAL_FIRE_DEPARTMENT, color=SportColors.AMBER_ALERT, size=20),
                        ft.Text("TEMPLO DO ESPÍRITO SANTO", size=12, weight=ft.FontWeight.BOLD, color=SportColors.AMBER_ALERT),
                    ], spacing=6),
                    SportStyles.badge("1 Coríntios 6:19-20", SportColors.AMBER_ALERT)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(
                    "\"Acaso não sabem que o corpo de vocês é santuário do Espírito Santo? Vocês foram comprados por alto preço. Portanto, glorifiquem a Deus com o seu próprio corpo.\"",
                    size=12,
                    italic=True,
                    color=SportColors.TEXT_WHITE
                ),
                ft.Row([
                    ft.Text("🛡️ Treino com Propósito & Força Consagrada", size=11, color=SportColors.TEXT_SECONDARY),
                    SportStyles.badge("Templo AI", SportColors.PRIMARY_NEON)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=6),
            bgcolor=SportColors.BG_SURFACE,
            border_color=SportColors.BORDER_AMBER,
            padding=12
        )

        return ft.Container(
            content=ft.ListView([
                header_card,
                temple_card,
                workout_card,
                team_card,
                goals_card,
                ft.Container(height=80)
            ], spacing=12, padding=AppPadding.all(14)),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _specialist_mini_row(self, icon, color, title, text):
        return ft.Container(
            content=ft.Row([
                ft.CircleAvatar(radius=14, bgcolor=SportColors.BG_SURFACE_ALT, content=ft.Icon(icon, color=color, size=15)),
                ft.Column([
                    ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                    ft.Text(text, size=11, color=SportColors.TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ], spacing=1, expand=True)
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=AppPadding.symmetric(vertical=2)
        )

    def _quick_add_water(self, amount: int):
        DBService.add_water(amount)
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"+{amount}ml de água registrados!", color=SportColors.TEXT_WHITE),
                bgcolor=SportColors.BG_SURFACE_ALT,
                duration=1200
            )
            self.page.snack_bar.open = True
            self.page.update()
            if self.on_navigate:
                self.on_navigate(0)

    def _nav_to(self, index: int):
        if self.on_navigate:
            self.on_navigate(index)
