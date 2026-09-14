"""
Módulo de Saúde Mental, Mindset do Atleta & Sono - Templo Fitness AI.
Diário de humor, score de recuperação e respiração guiada diafragmática (Box Breathing).
"""
import flet as ft
import time
import threading
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder, AppAlignment
from services.db_service import DBService

class MentalView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_mood = 4
        self.selected_stress = 2
        self.sleep_hours = 7.5
        self.energy_score = 4
        
        # Estado da Respiração Guiada
        self.breathing_active = False
        self.breathing_thread = None
        self.breathing_phase_text = ft.Text("Pronto para relaxar", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
        self.breathing_timer_text = ft.Text("4", size=32, weight=ft.FontWeight.BOLD, color=SportColors.PURPLE_MIND)
        self.breathing_progress = ft.ProgressBar(value=0.0, color=SportColors.PURPLE_MIND, bgcolor=SportColors.BG_SURFACE_ALT, height=8)

    def build(self) -> ft.Control:
        wellness = DBService.get_today_wellness()
        self.selected_mood = wellness.get("mood_score", 4)
        self.selected_stress = wellness.get("stress_score", 2)
        self.sleep_hours = float(wellness.get("sleep_hours", 7.5))
        self.energy_score = wellness.get("energy_score", 4)

        # 1. Diário de Humor
        mood_emojis = [
            (1, "😫", "Esgotado"),
            (2, "😕", "Cansado"),
            (3, "😐", "Normal"),
            (4, "😃", "Motivado"),
            (5, "🦁", "Foco Total")
        ]

        mood_buttons = []
        for score, emo, label in mood_emojis:
            is_sel = score == self.selected_mood
            mood_buttons.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(emo, size=24),
                        ft.Text(label, size=10, weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.NORMAL, color=SportColors.PURPLE_MIND if is_sel else SportColors.TEXT_MUTED)
                    ], spacing=2, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=f"{SportColors.PURPLE_MIND}33" if is_sel else SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.all(8),
                    border_radius=10,
                    border=AppBorder.all(1.5 if is_sel else 1, SportColors.PURPLE_MIND if is_sel else SportColors.BORDER_DEFAULT),
                    on_click=lambda _, sc=score: self._select_mood(sc),
                    expand=True
                )
            )

        mood_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header("CHECK-IN EMOCIONAL & DISPOSIÇÃO", "Como você está se sentindo hoje?", icon=Icons.PSYCHOLOGY),
                ft.Row(mood_buttons, spacing=6),
                ft.Divider(color=SportColors.BORDER_DEFAULT, height=6),
                
                # Horas de Sono
                ft.Row([
                    ft.Column([
                        ft.Text("Horas de Sono:", size=12, color=SportColors.TEXT_SECONDARY),
                        ft.Text(f"{self.sleep_hours} horas", size=15, weight=ft.FontWeight.BOLD, color=SportColors.CYAN_ELECTRIC)
                    ], spacing=2),
                    ft.Row([
                        ft.IconButton(
                            icon=Icons.REMOVE_CIRCLE_OUTLINE,
                            icon_color=SportColors.TEXT_MUTED,
                            on_click=lambda _: self._adj_sleep(-0.5)
                        ),
                        ft.IconButton(
                            icon=Icons.ADD_CIRCLE_OUTLINE,
                            icon_color=SportColors.CYAN_ELECTRIC,
                            on_click=lambda _: self._adj_sleep(0.5)
                        ),
                    ], spacing=0)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # Salvar Check-in
                ft.ElevatedButton(
                    "Salvar Check-in no Prontuário da IA",
                    icon=Icons.CHECK,
                    style=ft.ButtonStyle(bgcolor=SportColors.PURPLE_MIND, color=SportColors.TEXT_WHITE),
                    on_click=lambda _: self._save_wellness(),
                    height=40
                )
            ], spacing=10),
            border_color=SportColors.BORDER_PURPLE,
            padding=16
        )

        # 2. Respiração Guiada Box Breathing
        box_breathing_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header("PROTOCOLO DE RESPIRAÇÃO (BOX BREATHING)", "4s Inspira • 4s Segura • 4s Expira • 4s Segura", icon=Icons.AIR),
                ft.Text(
                    "Técnica usada por forças especiais e atletas de elite para desacelerar o ritmo cardíaco, reduzir o cortisol e restaurar o foco total.",
                    size=12,
                    color=SportColors.TEXT_SECONDARY
                ),
                
                ft.Container(
                    content=ft.Column([
                        self.breathing_phase_text,
                        self.breathing_timer_text,
                        self.breathing_progress,
                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.all(16),
                    border_radius=12,
                    alignment=AppAlignment.CENTER
                ),

                ft.Row([
                    ft.ElevatedButton(
                        "Iniciar 2 Min de Respiração",
                        icon=Icons.PLAY_ARROW,
                        style=ft.ButtonStyle(bgcolor=SportColors.PURPLE_MIND, color=SportColors.TEXT_WHITE),
                        on_click=lambda _: self._start_box_breathing(),
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "Parar",
                        icon=Icons.STOP,
                        style=ft.ButtonStyle(bgcolor=SportColors.BG_SURFACE_ALT, color=SportColors.CRIMSON_NEON),
                        on_click=lambda _: self._stop_box_breathing(),
                        width=100
                    ),
                ], spacing=10)
            ], spacing=10),
            padding=16
        )

        # 3. Consagração do Templo & Oração Pré-Treino
        prayer_card = SportStyles.card_container(
            content=ft.Column([
                SportStyles.section_header("ORAÇÃO DO TEMPLO & CONSAGRAÇÃO", "Dedique seu esforço, corpo e saúde a Deus", icon=Icons.AUTO_AWESOME),
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "\"Senhor meu Deus, Criador e Sustentador,\n"
                            "Consagro a Ti o meu corpo, que é santuário do Teu Espírito Santo (1 Coríntios 6:19).\n"
                            "Dá-me a firmeza na fé, o vigor da Tua presença para vencer a fadiga e o fruto do domínio próprio para subjugar toda preguiça.\n"
                            "Que este treino não seja fruto de vaidade passageira, mas instrumento de saúde, força e prontidão para a Tua obra. Em nome de Jesus, Amém!\"",
                            size=12,
                            italic=True,
                            color=SportColors.TEXT_WHITE
                        ),
                        ft.Divider(color=SportColors.BORDER_DEFAULT, height=6),
                        ft.Row([
                            SportStyles.badge("Filipenses 4:13", SportColors.AMBER_ALERT),
                            SportStyles.badge("1 Coríntios 9:27", SportColors.PRIMARY_NEON),
                            SportStyles.badge("Provérbios 24:5", SportColors.CYAN_ELECTRIC),
                        ], spacing=6)
                    ], spacing=8),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.all(12),
                    border_radius=10,
                    border=AppBorder.all(1, SportColors.BORDER_AMBER)
                )
            ], spacing=10),
            border_color=SportColors.BORDER_AMBER,
            padding=16
        )

        return ft.Container(
            content=ft.ListView([
                mood_card,
                prayer_card,
                box_breathing_card,
                ft.Container(height=90)
            ], spacing=14, padding=AppPadding.all(16)),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _select_mood(self, score: int):
        self.selected_mood = score
        self._save_wellness()
        if self.page:
            self.build()
            self.page.update()

    def _adj_sleep(self, delta: float):
        self.sleep_hours = max(round(self.sleep_hours + delta, 1), 3.0)
        self._save_wellness()
        if self.page:
            self.build()
            self.page.update()

    def _save_wellness(self):
        DBService.save_wellness_log(
            mood=self.selected_mood,
            stress=self.selected_stress,
            sleep=self.sleep_hours,
            energy=self.energy_score,
            soreness="Postura alinhada e pronta para treinar",
            reflection="Constância inabalável e foco no processo."
        )
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("🧠 Prontuário mental e sono atualizados com sucesso!", color=SportColors.TEXT_WHITE, weight=ft.FontWeight.BOLD),
                bgcolor=SportColors.PURPLE_MIND,
                duration=1500
            )
            self.page.snack_bar.open = True
            self.page.update()

    def _start_box_breathing(self):
        if self.breathing_thread and self.breathing_thread.is_alive():
            self.breathing_active = False
            time.sleep(0.1)

        self.breathing_active = True

        def loop():
            phases = [
                ("🫁 1. INSPIRE profundamente pelo nariz...", SportColors.CYAN_ELECTRIC),
                ("⏸️ 2. SEGURE o ar nos pulmões...", SportColors.AMBER_GOLD),
                ("🌬️ 3. EXPIRE lentamente pela boca...", SportColors.PRIMARY_NEON),
                ("⏸️ 4. SEGURE os pulmões vazios...", SportColors.PURPLE_MIND),
            ]
            
            cycles = 0
            while self.breathing_active and cycles < 8:
                for phase_name, color in phases:
                    if not self.breathing_active:
                        break
                    self.breathing_phase_text.value = phase_name
                    self.breathing_phase_text.color = color
                    self.breathing_progress.color = color
                    
                    for sec in range(4, 0, -1):
                        if not self.breathing_active:
                            break
                        self.breathing_timer_text.value = str(sec)
                        self.breathing_timer_text.color = color
                        self.breathing_progress.value = sec / 4.0
                        if self.page:
                            try:
                                self.page.update()
                            except Exception:
                                pass
                        time.sleep(1)
                cycles += 1

            self.breathing_phase_text.value = "✨ Sessão Finalizada! Mente calma e focada."
            self.breathing_timer_text.value = "✓"
            self.breathing_progress.value = 1.0
            if self.page:
                try:
                    self.page.update()
                except Exception:
                    pass

        self.breathing_thread = threading.Thread(target=loop, daemon=True)
        self.breathing_thread.start()

    def _stop_box_breathing(self):
        self.breathing_active = False
        self.breathing_phase_text.value = "Pronto para relaxar"
        self.breathing_timer_text.value = "4"
        self.breathing_progress.value = 0.0
        if self.page:
            self.page.update()
