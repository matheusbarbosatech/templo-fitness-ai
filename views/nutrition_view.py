"""
Módulo de Nutrição, Macros e Hidratação - Apollo Fitness AI.
Controle diário de calorias, proteínas, carboidratos, gorduras, registro de refeições
e contador interativo de água.
"""
import flet as ft
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder
from core.health_math import HealthMath
from services.db_service import DBService
from views.goal_setting_dialog import GoalSettingDialog
from typing import Optional

class NutritionView:
    def __init__(self, page: ft.Page, user_id: Optional[int] = None):
        self.page = page
        self.user_id = user_id

    def build(self) -> ft.Control:
        uid = self.user_id or DBService.get_active_user_id()
        profile = DBService.get_athlete_profile(user_id=uid)
        nutrition = DBService.get_daily_nutrition(user_id=uid)
        
        tmb = HealthMath.calculate_tmb_mifflin(
            float(profile.get("weight_kg", 78.5)),
            float(profile.get("height_cm", 178)),
            int(profile.get("age", 26)),
            str(profile.get("sex", "M"))
        )
        tdee = HealthMath.calculate_tdee(tmb, str(profile.get("activity_level", "intenso")))
        targets = HealthMath.calculate_macros_target(
            tdee,
            str(profile.get("goal", "hipertrofia")),
            float(profile.get("weight_kg", 78.5))
        )

        cal_cons = int(nutrition.get("total_calories", 0))
        cal_goal = int(targets.get("target_calories", 2600))
        
        prot_cons = int(nutrition.get("total_protein", 0))
        prot_goal = int(targets.get("protein_g", 160))
        
        carbs_cons = int(nutrition.get("total_carbs", 0))
        carbs_goal = int(targets.get("carbs_g", 300))
        
        fat_cons = int(nutrition.get("total_fat", 0))
        fat_goal = int(targets.get("fat_g", 65))
        
        water_cons = int(nutrition.get("total_water_ml", 0))
        water_goal = int(targets.get("water_ml", 3000))

        # 1. Card de Macros Principais
        macros_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header(
                    "BALANÇO DE MACROS DO DIA",
                    f"Foco: {profile.get('goal', 'Hipertrofia').upper()} ({profile.get('weight_kg', 78.5)}kg)",
                    icon=Icons.PIE_CHART,
                    action_button=ft.ElevatedButton(
                        "🎯 Ajustar Metas",
                        icon=Icons.TRACK_CHANGES,
                        style=ft.ButtonStyle(
                            bgcolor=SportColors.BG_SURFACE_ALT,
                            color=SportColors.AMBER_GOLD,
                            text_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD)
                        ),
                        height=30,
                        on_click=lambda _: GoalSettingDialog(self.page, on_saved=self._on_goals_saved, user_id=uid).show()
                    )
                ),
                
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("Calorias Totais", size=12, color=SportColors.TEXT_SECONDARY),
                            ft.Text(f"{cal_cons} / {cal_goal} kcal", size=20, weight=ft.FontWeight.BOLD, color=SportColors.AMBER_GOLD),
                        ], spacing=2),
                        ft.Icon(Icons.LOCAL_FIRE_DEPARTMENT, color=SportColors.AMBER_GOLD, size=32)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.all(12),
                    border_radius=10
                ),
                
                self._macro_progress_bar("Proteínas", prot_cons, prot_goal, "g", SportColors.CRIMSON_NEON),
                self._macro_progress_bar("Carboidratos", carbs_cons, carbs_goal, "g", SportColors.CYAN_ELECTRIC),
                self._macro_progress_bar("Gorduras Boas", fat_cons, fat_goal, "g", SportColors.PRIMARY_NEON),
            ], spacing=12),
            border_color=SportColors.BORDER_GOLD,
            padding=16
        )

        # 2. Contador de Água Interativo
        water_pct = min(water_cons / max(water_goal, 1), 1.0)
        water_card = SportStyles.card_container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(Icons.WATER_DROP, color=SportColors.CYAN_ELECTRIC, size=22),
                        ft.Text("CONTROLE DE HIDRATAÇÃO", size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                    ], spacing=6),
                    SportStyles.badge(f"{water_cons}/{water_goal} ml", SportColors.CYAN_ELECTRIC)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.ProgressBar(value=water_pct, color=SportColors.CYAN_ELECTRIC, bgcolor=SportColors.BG_SURFACE_ALT, height=10),
                
                ft.Row([
                    ft.ElevatedButton(
                        "+250ml Copo",
                        icon=Icons.LOCAL_DRINK,
                        style=ft.ButtonStyle(bgcolor=SportColors.BG_SURFACE_ALT, color=SportColors.CYAN_ELECTRIC),
                        on_click=lambda _: self._add_water(250),
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "+500ml Garrafa",
                        icon=Icons.WATER_DROP,
                        style=ft.ButtonStyle(bgcolor=SportColors.BG_SURFACE_ALT, color=SportColors.CYAN_ELECTRIC),
                        on_click=lambda _: self._add_water(500),
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "+1L Garrafão",
                        icon=Icons.LOCAL_BAR,
                        style=ft.ButtonStyle(bgcolor=SportColors.BG_SURFACE_ALT, color=SportColors.CYAN_ELECTRIC),
                        on_click=lambda _: self._add_water(1000),
                        expand=True
                    ),
                ], spacing=6)
            ], spacing=10),
            border_color=SportColors.BORDER_CYAN,
            padding=16
        )

        # 3. Refeições Registradas
        meals = nutrition.get("meals", [])
        meals_list = ft.Column(spacing=8)
        if not meals:
            meals_list.controls.append(
                ft.Container(
                    content=ft.Text("Nenhuma refeição registrada hoje. Use os botões abaixo!", color=SportColors.TEXT_MUTED, italic=True),
                    padding=AppPadding.all(10)
                )
            )
        else:
            for m in meals:
                meals_list.controls.append(
                    SportStyles.card_container(
                        content=ft.Row([
                            ft.Icon(Icons.RESTAURANT_MENU, color=SportColors.AMBER_GOLD, size=20),
                            ft.Column([
                                ft.Text(m["meal_name"], size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                                ft.Text(f"Horário: {m.get('meal_time', '--:--')} | {int(m['calories'])} kcal", size=11, color=SportColors.TEXT_SECONDARY),
                            ], spacing=2, expand=True),
                            SportStyles.badge(f"{int(m['protein_g'])}g Prot", SportColors.CRIMSON_NEON)
                        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        border_color=SportColors.BORDER_DEFAULT,
                        padding=10
                    )
                )

        meals_section = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header(
                    "DIÁRIO DE REFEIÇÕES",
                    "Registro do que você comeu hoje",
                    icon=Icons.FASTFOOD,
                    action_button=ft.ElevatedButton(
                        "+ Nova Refeição",
                        icon=Icons.ADD,
                        style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.BG_DARK),
                        on_click=lambda _: self._show_add_meal_dialog()
                    )
                ),
                meals_list,
                
                ft.Text("⚡ Sugestões Rápidas de Pratos:", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY),
                ft.Row([
                    self._quick_preset_button("Shake Whey + Banana + Aveia", 380, 32, 50, 6),
                    self._quick_preset_button("150g Frango + 200g Arroz", 450, 46, 56, 4),
                ], spacing=6),
                ft.Row([
                    self._quick_preset_button("3 Ovos Mexidos + 2 Pães", 360, 22, 28, 16),
                    self._quick_preset_button("150g Patinho + Mandioca", 480, 44, 48, 12),
                ], spacing=6)
            ], spacing=12),
            border_color=SportColors.BORDER_DEFAULT,
            padding=16
        )

        return ft.Container(
            content=ft.ListView([
                macros_card,
                water_card,
                meals_section,
                ft.Container(height=90)
            ], spacing=14, padding=AppPadding.all(16)),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _macro_progress_bar(self, label: str, val: int, goal: int, unit: str, color: str):
        pct = min(val / max(goal, 1), 1.0)
        return ft.Column([
            ft.Row([
                ft.Text(label, size=12, weight=ft.FontWeight.W_500, color=SportColors.TEXT_WHITE),
                ft.Text(f"{val} / {goal}{unit} ({int(pct*100)}%)", size=12, weight=ft.FontWeight.BOLD, color=color),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ProgressBar(value=pct, color=color, bgcolor=SportColors.BG_SURFACE_ALT, height=6),
        ], spacing=4)

    def _quick_preset_button(self, name: str, kcal: float, prot: float, carbs: float, fat: float):
        return ft.ElevatedButton(
            content=ft.Text(name, size=10, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_PRIMARY),
            bgcolor=SportColors.BG_SURFACE_ALT,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=AppPadding.all(8)),
            on_click=lambda _: self._save_preset(name, kcal, prot, carbs, fat),
            expand=True
        )

    def _on_goals_saved(self):
        self.build()
        if self.page:
            self.page.update()

    def _save_preset(self, name: str, kcal: float, prot: float, carbs: float, fat: float):
        uid = self.user_id or DBService.get_active_user_id()
        DBService.add_meal(name, kcal, prot, carbs, fat, user_id=uid)
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ Refeição '{name}' adicionada!", color=SportColors.BG_DARK, weight=ft.FontWeight.BOLD),
                bgcolor=SportColors.PRIMARY_NEON,
                duration=1500
            )
            self.page.snack_bar.open = True
            self.build()
            self.page.update()

    def _add_water(self, amount: int):
        uid = self.user_id or DBService.get_active_user_id()
        DBService.add_water(amount, user_id=uid)
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"💧 +{amount}ml de água registrados!", color=SportColors.BG_DARK, weight=ft.FontWeight.BOLD),
                bgcolor=SportColors.CYAN_ELECTRIC,
                duration=1500
            )
            self.page.snack_bar.open = True
            self.build()
            self.page.update()

    def _show_add_meal_dialog(self):
        name_in = ft.TextField(label="Nome do Prato/Refeição", hint_text="Ex: Almoço Pós-Treino", color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        kcal_in = ft.TextField(label="Calorias (kcal)", value="500", keyboard_type=ft.KeyboardType.NUMBER, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        prot_in = ft.TextField(label="Proteína (g)", value="40", keyboard_type=ft.KeyboardType.NUMBER, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        carbs_in = ft.TextField(label="Carboidratos (g)", value="50", keyboard_type=ft.KeyboardType.NUMBER, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)
        fat_in = ft.TextField(label="Gorduras (g)", value="10", keyboard_type=ft.KeyboardType.NUMBER, color=SportColors.TEXT_WHITE, bgcolor=SportColors.BG_INPUT)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.ADD_RESTAURANT, color=SportColors.AMBER_GOLD),
                ft.Text("Adicionar Refeição", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            content=ft.Container(
                content=ft.Column([name_in, kcal_in, prot_in, carbs_in, fat_in], spacing=10),
                width=320,
                height=320
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self._close_dialog(dialog)),
                ft.ElevatedButton(
                    "Salvar",
                    style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.BG_DARK),
                    on_click=lambda _: self._save_custom_meal(dialog, name_in.value, kcal_in.value, prot_in.value, carbs_in.value, fat_in.value)
                )
            ]
        )
        if self.page:
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

    def _save_custom_meal(self, dialog, name, kcal, prot, carbs, fat):
        if not name:
            name = "Refeição"
        uid = self.user_id or DBService.get_active_user_id()
        DBService.add_meal(
            name,
            float(kcal or 0),
            float(prot or 0),
            float(carbs or 0),
            float(fat or 0),
            user_id=uid
        )
        self._close_dialog(dialog)
        if self.page:
            self.build()
            self.page.update()

    def _close_dialog(self, dialog):
        dialog.open = False
        if self.page:
            self.page.update()
