"""
Módulo de Execução de Treino em Tempo Real - Templo Fitness AI (Estilo Apple Fitness+ / Whoop).
"""
import flet as ft
import time
import threading
from typing import List, Dict, Any
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder
from services.db_service import DBService

class WorkoutView:
    def __init__(self, page: ft.Page, on_view_exercise_guide=None, user_id=None):
        self.page = page
        self.on_view_exercise_guide = on_view_exercise_guide
        self.user_id = user_id
        uid = self.user_id or DBService.get_active_user_id()
        self.routines = DBService.get_routines(user_id=uid)
        self.selected_routine_index = 0
        
        self.is_active_session = False
        self.session_start_time = None
        self.completed_sets: List[Dict[str, Any]] = []
        
        self.rest_seconds_left = 0
        self.timer_running = False
        self.timer_thread = None
        
        self.timer_text = ft.Text("01:30", size=22, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON)
        self.timer_progress = ft.ProgressBar(value=1.0, color=SportColors.PRIMARY_NEON, bgcolor=SportColors.BG_SURFACE_ALT, height=4)
        self.timer_card = None
        self.exercise_cards_column = ft.Column(spacing=10)

    def build(self) -> ft.Control:
        uid = self.user_id or DBService.get_active_user_id()
        self.routines = DBService.get_routines(user_id=uid)
        if not self.routines:
            return ft.Container(
                content=ft.Text("Nenhuma rotina cadastrada.", color=SportColors.TEXT_WHITE),
                padding=AppPadding.all(20)
            )

        if self.selected_routine_index >= len(self.routines):
            self.selected_routine_index = 0
        current_routine = self.routines[self.selected_routine_index]
        
        # 1. Seletor de Rotinas e Botão de Prescrições do Personal
        tabs = []
        for idx, r in enumerate(self.routines):
            is_sel = idx == self.selected_routine_index
            tabs.append(
                ft.Container(
                    content=ft.Text(
                        r["name"].split("-")[0].strip(),
                        size=12,
                        weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.NORMAL,
                        color=SportColors.TEXT_WHITE if is_sel else SportColors.TEXT_SECONDARY
                    ),
                    bgcolor=SportColors.PRIMARY_NEON_DARK if is_sel else SportColors.BG_SURFACE_ALT,
                    border_radius=8,
                    padding=AppPadding.symmetric(horizontal=12, vertical=8),
                    border=AppBorder.all(1, SportColors.PRIMARY_NEON if is_sel else SportColors.BORDER_DEFAULT),
                    on_click=lambda _, i=idx: self._select_routine(i)
                )
            )
        routine_selector_row = ft.Row(tabs, spacing=8, scroll=ft.ScrollMode.AUTO)

        # Botão de Ação Rápida: Prescrições do Personal Márcio
        coach_action_bar = ft.Row([
            ft.Text("Ficha de Treino Ativa", size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY),
            ft.ElevatedButton(
                "Prescrições do Personal",
                icon=Icons.AUTO_FIX_HIGH,
                style=ft.ButtonStyle(
                    bgcolor=SportColors.PRIMARY_NEON_DARK,
                    color=SportColors.TEXT_WHITE,
                    text_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD)
                ),
                height=32,
                on_click=lambda _: self._show_coach_presets_dialog()
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # 2. Card do Cronômetro de Descanso
        self.timer_card = SportStyles.card_container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(Icons.TIMER_OUTLINED, color=SportColors.PRIMARY_NEON, size=18),
                        ft.Text("TEMPO DE RECUPERAÇÃO", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY),
                    ], spacing=6),
                    ft.Row([
                        ft.IconButton(
                            icon=Icons.REPLAY_30,
                            icon_color=SportColors.TEXT_SECONDARY,
                            icon_size=18,
                            tooltip="+30 segundos",
                            on_click=lambda _: self._add_rest_time(30)
                        ),
                        ft.IconButton(
                            icon=Icons.STOP_CIRCLE_OUTLINED,
                            icon_color=SportColors.TEXT_MUTED,
                            icon_size=18,
                            tooltip="Parar Timer",
                            on_click=lambda _: self._stop_timer()
                        ),
                    ], spacing=0)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    self.timer_text,
                    ft.Row([
                        self._quick_timer_button(45),
                        self._quick_timer_button(60),
                        self._quick_timer_button(90),
                        self._quick_timer_button(120),
                    ], spacing=4)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                self.timer_progress
            ], spacing=6),
            border_color=SportColors.BORDER_DEFAULT,
            padding=12
        )

        # 3. Cabeçalho da Ficha
        routine_header = SportStyles.card_container(
            content=ft.Column([
                ft.Row([
                    ft.Text(current_routine["name"], size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                    SportStyles.badge(f"{len(current_routine.get('exercises', []))} Exercícios", SportColors.PRIMARY_NEON)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(current_routine.get("description", ""), size=12, color=SportColors.TEXT_SECONDARY),
            ], spacing=2),
            border_color=SportColors.BORDER_DEFAULT,
            padding=12
        )

        # 4. Renderização dos Cards de Exercício
        self._build_exercise_cards(current_routine.get("exercises", []), routine_id=current_routine["id"])

        # 5. Botão de Finalizar Treino
        finish_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(Icons.CHECK_CIRCLE_OUTLINE, color=SportColors.TEXT_WHITE, size=20),
                ft.Text("FINALIZAR SESSÃO DE TREINO", size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            bgcolor=SportColors.PRIMARY_NEON_DARK,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=lambda _: self._finish_workout_session(current_routine["name"]),
            height=46
        )

        return ft.Container(
            content=ft.ListView([
                coach_action_bar,
                routine_selector_row,
                self.timer_card,
                routine_header,
                self.exercise_cards_column,
                finish_button,
                ft.Container(height=90)
            ], spacing=12, padding=AppPadding.all(14)),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _quick_timer_button(self, seconds: int):
        return ft.Container(
            content=ft.Text(f"{seconds}s", size=11, color=SportColors.TEXT_SECONDARY),
            bgcolor=SportColors.BG_SURFACE_ALT,
            padding=AppPadding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
            border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
            on_click=lambda _, s=seconds: self._start_timer(s)
        )

    def _build_exercise_cards(self, exercises: List[Dict[str, Any]], routine_id: int = 1):
        self.exercise_cards_column.controls.clear()
        
        for ex_idx, ex in enumerate(exercises):
            ex_name = ex.get("exercise_name", "Exercício")
            target_sets = ex.get("target_sets", 4)
            target_reps = ex.get("target_reps", "8-12")
            target_weight = ex.get("target_weight", 20.0)
            rest_sec = ex.get("rest_seconds", 90)

            sets_rows = []
            for s_num in range(1, target_sets + 1):
                weight_input = ft.TextField(
                    value=str(int(target_weight)),
                    width=60,
                    height=34,
                    text_size=12,
                    text_align=ft.TextAlign.CENTER,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    bgcolor=SportColors.BG_INPUT,
                    border_color=SportColors.BORDER_DEFAULT,
                    color=SportColors.TEXT_WHITE,
                    content_padding=AppPadding.all(4)
                )
                reps_input = ft.TextField(
                    value="10",
                    width=50,
                    height=34,
                    text_size=12,
                    text_align=ft.TextAlign.CENTER,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    bgcolor=SportColors.BG_INPUT,
                    border_color=SportColors.BORDER_DEFAULT,
                    color=SportColors.TEXT_WHITE,
                    content_padding=AppPadding.all(4)
                )
                
                check_btn = ft.IconButton(
                    icon=Icons.CHECK_BOX_OUTLINE_BLANK,
                    icon_color=SportColors.TEXT_MUTED,
                    icon_size=20,
                    tooltip="Concluir Série & Iniciar Descanso",
                    on_click=None
                )

                def make_on_check(btn=check_btn, w_inp=weight_input, r_inp=reps_input, s=s_num, name=ex_name, r_time=rest_sec):
                    def handler(_):
                        btn.icon = Icons.CHECK_BOX
                        btn.icon_color = SportColors.PRIMARY_NEON
                        btn.disabled = True
                        
                        w_val = float(w_inp.value or 0)
                        r_val = int(r_inp.value or 0)
                        self.completed_sets.append({
                            "exercise_name": name,
                            "set_number": s,
                            "weight_kg": w_val,
                            "reps": r_val,
                            "rpe": 8.0
                        })
                        
                        self._start_timer(r_time)
                        if self.page:
                            self.page.update()
                    return handler

                check_btn.on_click = make_on_check()

                sets_rows.append(
                    ft.Row([
                        ft.Text(f"#{s_num}", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY, width=28),
                        weight_input,
                        ft.Text("kg", size=11, color=SportColors.TEXT_MUTED),
                        reps_input,
                        ft.Text("reps", size=11, color=SportColors.TEXT_MUTED),
                        check_btn
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                )

            card = SportStyles.card_container(
                content=ft.Column([
                    ft.Row([
                        ft.Row([
                            ft.Icon(Icons.FITNESS_CENTER, color=SportColors.PRIMARY_NEON, size=18),
                            ft.Text(ex_name, size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                        ], spacing=6, expand=True),
                        ft.Row([
                            ft.IconButton(
                                icon=Icons.SWAP_HORIZ,
                                icon_color=SportColors.CYAN_ELECTRIC,
                                icon_size=18,
                                tooltip="Trocar Exercício (Máquina Ocupada / Dor)",
                                on_click=lambda _, name=ex_name, rid=routine_id: self._show_swap_exercise_dialog(rid, name)
                            ),
                            ft.IconButton(
                                icon=Icons.INFO_OUTLINE,
                                icon_color=SportColors.TEXT_SECONDARY,
                                icon_size=18,
                                tooltip="Ver Guia Biomecânico",
                                on_click=lambda _, name=ex_name: self._open_exercise_guide(name)
                            ),
                        ], spacing=0)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        SportStyles.badge(f"{target_sets} séries × {target_reps}", SportColors.TEXT_SECONDARY),
                        SportStyles.badge(f"Descanso: {rest_sec}s", SportColors.TEXT_MUTED),
                        ft.TextButton(
                            "Substituir Exercício",
                            icon=Icons.AUTO_FIX_NORMAL,
                            style=ft.ButtonStyle(color=SportColors.CYAN_ELECTRIC, padding=AppPadding.all(0)),
                            on_click=lambda _, name=ex_name, rid=routine_id: self._show_swap_exercise_dialog(rid, name)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(color=SportColors.BORDER_DEFAULT, height=6),
                    ft.Column(sets_rows, spacing=4),
                ], spacing=6),
                border_color=SportColors.BORDER_DEFAULT,
                padding=12
            )
            self.exercise_cards_column.controls.append(card)

    def _select_routine(self, index: int):
        self.selected_routine_index = index
        if self.page:
            self.build()
            self.page.update()

    def _open_exercise_guide(self, exercise_name: str):
        if self.on_view_exercise_guide:
            self.on_view_exercise_guide(exercise_name)

    def _start_timer(self, seconds: int):
        self.rest_seconds_left = seconds
        self.total_timer_duration = seconds
        self.timer_running = True
        
        def countdown():
            while self.timer_running and self.rest_seconds_left > 0:
                mins, secs = divmod(self.rest_seconds_left, 60)
                self.timer_text.value = f"{mins:02d}:{secs:02d}"
                self.timer_progress.value = self.rest_seconds_left / max(self.total_timer_duration, 1)
                if self.page:
                    try:
                        self.page.update()
                    except Exception:
                        pass
                time.sleep(1)
                self.rest_seconds_left -= 1
            
            if self.rest_seconds_left <= 0 and self.timer_running:
                self.timer_text.value = "✓ Próxima Série"
                self.timer_progress.value = 0.0
                if self.page:
                    try:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text("Descanso finalizado! Inicie a próxima série.", color=SportColors.TEXT_WHITE),
                            bgcolor=SportColors.BG_SURFACE_ALT,
                            duration=2500
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    except Exception:
                        pass

        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_running = False
            time.sleep(0.1)
        
        self.timer_running = True
        self.timer_thread = threading.Thread(target=countdown, daemon=True)
        self.timer_thread.start()

    def _add_rest_time(self, extra_seconds: int):
        self.rest_seconds_left += extra_seconds
        self.total_timer_duration = max(self.total_timer_duration, self.rest_seconds_left)
        if self.page:
            self.page.update()

    def _stop_timer(self):
        self.timer_running = False
        self.rest_seconds_left = 0
        self.timer_text.value = "00:00"
        self.timer_progress.value = 0.0
        if self.page:
            self.page.update()

    def _finish_workout_session(self, routine_name: str):
        if not self.completed_sets:
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Complete pelo menos 1 série antes de finalizar o treino!", color=SportColors.TEXT_WHITE),
                    bgcolor=SportColors.BG_SURFACE_ALT
                )
                self.page.snack_bar.open = True
                self.page.update()
            return

        total_vol = sum(s["weight_kg"] * s["reps"] for s in self.completed_sets)
        uid = self.user_id or DBService.get_active_user_id()
        session_id = DBService.save_workout_session(
            routine_name=routine_name,
            duration_min=45,
            total_volume=total_vol,
            sets=self.completed_sets,
            notes="Treino executado com sucesso e excelente cadência.",
            user_id=uid
        )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.CHECK_CIRCLE, color=SportColors.PRIMARY_NEON, size=24),
                ft.Text("Treino Concluído", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
            ], spacing=8),
            content=ft.Column([
                ft.Text(f"Excelente! Você finalizou o {routine_name}.", size=13, color=SportColors.TEXT_PRIMARY),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Séries Concluídas:", size=12, color=SportColors.TEXT_SECONDARY),
                            ft.Text(f"{len(self.completed_sets)} séries", size=12, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Text("Volume Total:", size=12, color=SportColors.TEXT_SECONDARY),
                            ft.Text(f"{int(total_vol)} kg", size=12, weight=ft.FontWeight.BOLD, color=SportColors.CYAN_ELECTRIC)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=4),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.all(10),
                    border_radius=8
                ),
            ], tight=True, spacing=10),
            actions=[
                ft.ElevatedButton(
                    "Concluir",
                    style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON_DARK, color=SportColors.TEXT_WHITE),
                    on_click=lambda _: self._close_dialog_and_reset(dialog)
                )
            ]
        )
        if self.page:
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

    def _close_dialog_and_reset(self, dialog):
        dialog.open = False
        self.completed_sets.clear()
        self._stop_timer()
        if self.page:
            self.page.update()

    # ==================== ESPAÇO PARA TROCA DE TREINO & RECOMENDAÇÕES DO PERSONAL ====================
    def _show_swap_exercise_dialog(self, routine_id: int, current_exercise: str):
        """Abre modal com alternativas recomendadas pelo Treinador Márcio quando a máquina está ocupada ou há dor."""
        subs = DBService.get_exercise_substitutions(current_exercise)
        sub_cards = []

        if not subs:
            sub_cards.append(
                ft.Text(
                    f"Nenhuma recomendação cadastrada para {current_exercise}. Você pode consultar o Treinador Márcio no IA Team!",
                    size=12,
                    color=SportColors.TEXT_SECONDARY
                )
            )
        else:
            for s in subs:
                alt_name = s["alternative_name"]
                reason = s.get("reason", "")
                equip = s.get("equipment", "")
                muscle = s.get("primary_muscle", "")
                tips = s.get("execution_tips", "")

                card = SportStyles.card_container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(alt_name, size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                            SportStyles.badge(muscle, SportColors.PRIMARY_NEON)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            SportStyles.badge(f"Equipamento: {equip}", SportColors.TEXT_SECONDARY),
                        ]),
                        ft.Text(f"💡 Dica do Personal: {reason}", size=11, color=SportColors.CYAN_ELECTRIC),
                        ft.Text(f"🎯 Execução: {tips}", size=11, color=SportColors.TEXT_MUTED),
                        ft.ElevatedButton(
                            f"Substituir por {alt_name}",
                            icon=Icons.CHECK,
                            style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.BG_DARK),
                            height=34,
                            on_click=lambda _, an=alt_name: self._execute_exercise_swap(dialog, routine_id, current_exercise, an)
                        )
                    ], spacing=6),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    border_color=SportColors.BORDER_DEFAULT,
                    padding=10
                )
                sub_cards.append(card)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.SWAP_HORIZ, color=SportColors.CYAN_ELECTRIC, size=22),
                ft.Text("Trocar Exercício (Personal Márcio)", size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text(
                        f"Exercício atual: {current_exercise}\n"
                        "Máquina ocupada ou sentindo dor? Escolha uma alternativa biomecanicamente equivalente:",
                        size=12,
                        color=SportColors.TEXT_SECONDARY
                    ),
                    ft.Column(sub_cards, spacing=8)
                ], spacing=10),
                width=350,
                height=450
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda _: self._close_dialog(dialog))
            ]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _execute_exercise_swap(self, dialog, routine_id: int, old_ex: str, new_ex: str):
        success = DBService.swap_routine_exercise(routine_id, old_ex, new_ex)
        self._close_dialog(dialog)
        if success:
            uid = self.user_id or DBService.get_active_user_id()
            self.routines = DBService.get_routines(user_id=uid)
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Exercício trocado com sucesso para: {new_ex}!", color=SportColors.TEXT_WHITE),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    duration=2000
                )
                self.page.snack_bar.open = True
                self.build()
                self.page.update()

    def _show_coach_presets_dialog(self):
        """Abre modal para troca completa da divisão de treino segundo prescrição do treinador."""
        presets = [
            ("PPL", "Push / Pull / Legs (6 dias)", "Prescrição de alta frequência e hipertrofia máxima. Divisão em Empurrar, Puxar e Pernas.", "#FF3366"),
            ("UpperLower", "Upper / Lower (4 dias)", "Prescrição balanceada ideal para progressão pesada de cargas e descanso articular.", "#FFB800"),
            ("ABC", "Clássica ABC (3 a 5 dias)", "Divisão clássica de hipertrofia: Peito/Tríceps, Costas/Bíceps e Pernas/Ombros.", "#00FFA3"),
        ]

        preset_cards = []
        for key, name, desc, col in presets:
            card = SportStyles.card_container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(name, size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                        SportStyles.badge(key, col)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(desc, size=11, color=SportColors.TEXT_SECONDARY),
                    ft.ElevatedButton(
                        f"Aplicar Divisão {key}",
                        icon=Icons.CHECK,
                        style=ft.ButtonStyle(bgcolor=col, color=SportColors.BG_DARK),
                        height=34,
                        on_click=lambda _, pk=key: self._apply_preset(dialog, pk)
                    )
                ], spacing=6),
                bgcolor=SportColors.BG_SURFACE_ALT,
                border_color=SportColors.BORDER_DEFAULT,
                padding=10
            )
            preset_cards.append(card)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.AUTO_FIX_HIGH, color=SportColors.PRIMARY_NEON, size=22),
                ft.Text("Prescrições do Treinador Márcio", size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text("Selecione uma das prescrições científicas para reconfigurar todo o seu programa de treinos:", size=12, color=SportColors.TEXT_SECONDARY),
                    ft.Column(preset_cards, spacing=8)
                ], spacing=10),
                width=350,
                height=420
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda _: self._close_dialog(dialog))
            ]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _apply_preset(self, dialog, preset_key: str):
        uid = self.user_id or DBService.get_active_user_id()
        DBService.apply_coach_routine_preset(preset_key, user_id=uid)
        self._close_dialog(dialog)
        self.routines = DBService.get_routines(user_id=uid)
        self.selected_routine_index = 0
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Prescrição {preset_key} aplicada com sucesso no seu programa!", color=SportColors.TEXT_WHITE),
                bgcolor=SportColors.BG_SURFACE_ALT,
                duration=2000
            )
            self.page.snack_bar.open = True
            self.build()
            self.page.update()

    def _close_dialog(self, dialog):
        dialog.open = False
        if self.page:
            self.page.update()

