"""
Módulo Oficial de Execução de Treino - Templo Fitness AI.
Design Enxuto, Minimalista e Direto ao Ponto (Padrão Apple Fitness / Whoop / Hevy / Nike Training Club).
Fluxo Mobile First: 1 exercício por tela ("virar a página"), cronômetro local em cada card e salvamento infalível.
"""
import flet as ft
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from core.theme import SportColors, SportStyles, Icons, AppPadding, AppBorder, AppBorderRadius, AppAlignment
from core.ui_helper import UIHelper
from services.db_service import DBService

class WorkoutView:
    def __init__(self, page: ft.Page, on_view_exercise_guide=None, user_id: Optional[int] = None):
        self.page = page
        self.on_view_exercise_guide = on_view_exercise_guide
        self.user_id = user_id or DBService.get_active_user_id()
        
        self.routines = DBService.get_routines(user_id=self.user_id)
        self.selected_routine_index = 0
        self.current_exercise_index = 0
        
        # Estado reativo unificado de todas as séries da rotina
        self.exercise_state: Dict[str, Dict[str, Any]] = {}
        self.completed_sets: List[Dict[str, Any]] = []
        self.active_inputs: Dict[str, Dict[str, ft.TextField]] = {}
        self.session_start_time = time.time()
        
        # Cronômetro de descanso integrado dentro do card
        self.rest_seconds_left = 0
        self.timer_running = False
        self.timer_thread = None
        self.timer_text = ft.Text("00:00", size=14, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON)
        self.timer_progress = ft.ProgressBar(value=0.0, color=SportColors.PRIMARY_NEON, bgcolor="#181824", height=3)
        
        # Elementos estruturais da interface
        self.routine_selector_row = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
        self.routine_header_title = ft.Text("", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
        self.routine_header_desc = ft.Text("", size=12, color=SportColors.TEXT_SECONDARY)
        
        # Containers dinâmicos para o modo 1 exercício por tela
        self.stepper_container = ft.Container()
        self.active_exercise_container = ft.Container()
        self.history_column = ft.Column(spacing=8)

    def build(self) -> ft.Control:
        uid = self.user_id or DBService.get_active_user_id()
        self.routines = DBService.get_routines(user_id=uid)
        
        if not self.routines:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(Icons.FITNESS_CENTER, size=48, color=SportColors.TEXT_MUTED),
                    ft.Text("Nenhuma ficha de treino cadastrada.", size=15, color=SportColors.TEXT_WHITE),
                    ft.ElevatedButton(
                        "Carregar Treinos Prescritos",
                        icon=Icons.AUTO_FIX_HIGH,
                        style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.PRIMARY_TEXT_ON_NEON),
                        on_click=lambda _: self._apply_default_routine()
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                padding=AppPadding.all(20),
                expand=True
            )

        if self.selected_routine_index >= len(self.routines):
            self.selected_routine_index = 0

        # 1. Inicializa o estado se ainda não estiver carregado
        self._initialize_exercise_state()

        # 2. Atualiza os componentes da tela
        self._update_routine_selector_ui()
        self._render_stepper_ui()
        self._render_active_exercise_card()
        self._render_history()

        # Barra Superior Minimalista de Rotinas e Prescrições
        top_bar = ft.Row([
            ft.Text("ROTINAS DISPONÍVEIS", size=11, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED),
            ft.Row([
                ft.TextButton(
                    "Avaliação",
                    icon=Icons.ASSIGNMENT_IND_OUTLINED,
                    style=ft.ButtonStyle(color=SportColors.TEXT_SECONDARY),
                    on_click=lambda _: self._show_goal_setting_dialog()
                ),
                ft.TextButton(
                    "Mudar Ficha",
                    icon=Icons.AUTO_FIX_HIGH,
                    style=ft.ButtonStyle(color=SportColors.PRIMARY_NEON),
                    on_click=lambda _: self._show_coach_presets_dialog()
                )
            ], spacing=2)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True)

        # Cabeçalho da Rotina Selecionada
        routine_info_card = SportStyles.card_container(
            content=ft.Row([
                ft.Icon(Icons.FITNESS_CENTER, color=SportColors.PRIMARY_NEON, size=20),
                ft.Column([
                    self.routine_header_title,
                    self.routine_header_desc,
                ], spacing=1, expand=True)
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=SportColors.BG_SURFACE,
            border_color=SportColors.BORDER_DEFAULT,
            padding=10
        )

        # Seção do Histórico Recente
        history_section = ft.Column([
            ft.Divider(color=SportColors.BORDER_DEFAULT, height=20),
            ft.Row([
                ft.Icon(Icons.HISTORY, color=SportColors.TEXT_MUTED, size=18),
                ft.Text("HISTÓRICO DE TREINOS SALVOS", size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY),
            ], spacing=8),
            self.history_column
        ], spacing=10)

        # Coluna principal centralizada e responsiva Mobile First (1 exercício por tela)
        main_content_column = ft.Column([
            top_bar,
            self.routine_selector_row,
            routine_info_card,
            self.stepper_container,
            self.active_exercise_container,
            history_section,
            ft.Container(height=40)
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        content_wrapper = ft.Container(
            content=main_content_column,
            col={"xs": 12, "sm": 12, "md": 10, "lg": 8, "xl": 7}
        )

        responsive_workout_row = ft.ResponsiveRow([content_wrapper], alignment=ft.MainAxisAlignment.CENTER)

        return ft.Container(
            content=ft.ListView([
                ft.Container(height=4),
                responsive_workout_row,
                ft.Container(height=24)
            ], spacing=0, padding=AppPadding.symmetric(horizontal=8, vertical=4)),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _initialize_exercise_state(self):
        """Inicializa ou preserva o estado de séries e cargas de todos os exercícios da rotina."""
        if not self.routines or self.selected_routine_index >= len(self.routines):
            return
            
        current_routine = self.routines[self.selected_routine_index]
        exercises = current_routine.get("exercises", [])
        
        # Garante índice de exercício válido
        if self.current_exercise_index >= len(exercises):
            self.current_exercise_index = 0

        for ex in exercises:
            ex_name = ex.get("exercise_name", "Exercício")
            if ex_name in self.exercise_state:
                continue

            target_sets = int(ex.get("target_sets", 3))
            target_reps = str(ex.get("target_reps", "10-12"))
            target_weight = float(ex.get("target_weight", 20.0) or 0.0)
            rest_sec = int(ex.get("rest_seconds", 60))

            initial_reps = 10
            if "-" in target_reps:
                try:
                    initial_reps = int(target_reps.split("-")[0].strip())
                except Exception:
                    initial_reps = 10
            elif target_reps.isdigit():
                initial_reps = int(target_reps)

            self.exercise_state[ex_name] = {
                "target_sets": target_sets,
                "target_reps": target_reps,
                "target_weight": target_weight,
                "rest_seconds": rest_sec,
                "sets": [
                    {
                        "set_num": s_num,
                        "weight": target_weight,
                        "reps": initial_reps,
                        "completed": False
                    }
                    for s_num in range(1, target_sets + 1)
                ]
            }

    def _update_routine_selector_ui(self):
        """Atualiza dinamicamente os botões de alternância de rotinas (Treino A, B, C...)."""
        self.routine_selector_row.controls.clear()
        
        for idx, r in enumerate(self.routines):
            is_selected = idx == self.selected_routine_index
            r_label = r["name"].split("-")[0].strip()
            
            self.routine_selector_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            Icons.FITNESS_CENTER,
                            size=13,
                            color=SportColors.PRIMARY_TEXT_ON_NEON if is_selected else SportColors.PRIMARY_NEON
                        ),
                        ft.Text(
                            r_label,
                            size=12,
                            weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.W_500,
                            color=SportColors.PRIMARY_TEXT_ON_NEON if is_selected else SportColors.TEXT_WHITE
                        )
                    ], spacing=5, alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=SportColors.PRIMARY_NEON if is_selected else SportColors.BG_SURFACE_ALT,
                    border_radius=8,
                    padding=AppPadding.symmetric(horizontal=12, vertical=8),
                    border=AppBorder.all(1, SportColors.PRIMARY_NEON if is_selected else SportColors.BORDER_DEFAULT),
                    on_click=lambda _, i=idx: self._select_routine(i),
                    ink=True
                )
            )

        if self.routines and self.selected_routine_index < len(self.routines):
            current = self.routines[self.selected_routine_index]
            self.routine_header_title.value = current.get('name', 'Treino')
            self.routine_header_desc.value = current.get('description', 'Foco de hipertrofia muscular')

    def _select_routine(self, index: int):
        """Alterna a rotina em 1 clique e reseta para a página 1 da nova rotina."""
        self.selected_routine_index = index
        self.current_exercise_index = 0
        self.exercise_state.clear()
        self.completed_sets.clear()
        self._initialize_exercise_state()
        self._update_routine_selector_ui()
        self._render_stepper_ui()
        self._render_active_exercise_card()
        if self.page:
            self.page.update()

    def _navigate_exercise(self, delta: int):
        """Navega entre os exercícios da rotina estilo virar a página do livro."""
        current_routine = self.routines[self.selected_routine_index] if self.routines else {}
        exercises = current_routine.get("exercises", [])
        new_idx = self.current_exercise_index + delta
        if 0 <= new_idx < len(exercises):
            self.current_exercise_index = new_idx
            self._render_stepper_ui()
            self._render_active_exercise_card()
            if self.page:
                self.page.update()

    def _render_stepper_ui(self):
        """Renderiza a barra de navegação estilo virar a página com indicador de progresso."""
        current_routine = self.routines[self.selected_routine_index] if self.routines else {}
        exercises = current_routine.get("exercises", [])
        total_ex = len(exercises)
        
        if total_ex == 0:
            self.stepper_container.content = ft.Container()
            return

        current_idx = self.current_exercise_index
        has_prev = current_idx > 0
        has_next = current_idx < total_ex - 1
        progress_val = (current_idx + 1) / total_ex

        self.stepper_container.content = SportStyles.card_container(
            content=ft.Column([
                ft.Row([
                    ft.IconButton(
                        icon=Icons.CHEVRON_LEFT,
                        icon_color=SportColors.PRIMARY_NEON if has_prev else SportColors.TEXT_MUTED,
                        icon_size=24,
                        tooltip="Exercício Anterior (Voltar página)",
                        disabled=not has_prev,
                        on_click=lambda _: self._navigate_exercise(-1)
                    ),
                    ft.Column([
                        ft.Row([
                            ft.Text(f"EXERCÍCIO {current_idx + 1} DE {total_ex}", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(Icons.VIEW_LIST, size=11, color=SportColors.PRIMARY_NEON),
                                    ft.Text("Ver Ficha", size=10, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON),
                                ], spacing=3),
                                bgcolor="#181824",
                                border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
                                border_radius=6,
                                padding=AppPadding.symmetric(horizontal=8, vertical=3),
                                on_click=lambda _: self._show_all_exercises_modal(),
                                ink=True
                            )
                        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=3),
                        ft.ProgressBar(
                            value=progress_val,
                            color=SportColors.PRIMARY_NEON,
                            bgcolor="#181822",
                            height=4,
                            border_radius=2
                        )
                    ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                    ft.IconButton(
                        icon=Icons.CHEVRON_RIGHT,
                        icon_color=SportColors.PRIMARY_NEON if has_next else SportColors.TEXT_MUTED,
                        icon_size=24,
                        tooltip="Próximo Exercício (Virar página)",
                        disabled=not has_next,
                        on_click=lambda _: self._navigate_exercise(1)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=2),
            bgcolor=SportColors.BG_SURFACE,
            border_color=SportColors.BORDER_DEFAULT,
            padding=AppPadding.symmetric(horizontal=6, vertical=6),
            radius=12
        )

    def _render_active_exercise_card(self):
        """Renderiza exclusivamente o card do exercício ativo na tela atual."""
        current_routine = self.routines[self.selected_routine_index] if self.routines else {}
        exercises = current_routine.get("exercises", [])
        
        if not exercises or self.current_exercise_index >= len(exercises):
            self.active_exercise_container.content = ft.Container(
                content=ft.Text("Nenhum exercício selecionado.", color=SportColors.TEXT_MUTED),
                padding=AppPadding.all(16)
            )
            return

        ex_idx = self.current_exercise_index
        ex = exercises[ex_idx]
        ex_name = ex.get("exercise_name", "Exercício")
        target_sets = ex.get("target_sets", 3)
        target_reps = ex.get("target_reps", "10-12")
        target_weight = ex.get("target_weight", 20.0)
        rest_sec = ex.get("rest_seconds", 60)
        
        p_muscle = ex.get("primary_muscle") or "Músculo Alvo"
        equipment = ex.get("equipment") or "Aparelho"
        guide = ex.get("execution_guide") or "Realize o movimento com postura firme e controle excêntrico."
        mistakes = ex.get("common_mistakes") or "Evite roubar com impulsos ou reduzir a amplitude."
        why_do_it = ex.get("why_do_it") or "Exercício fundamental para força e hipertrofia."
        gif_url = ex.get("gif_url") or DBService.get_exercise_gif(ex_name)

        def _metric_pill(label: str, value: str):
            return ft.Container(
                content=ft.Column([
                    ft.Text(value, size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE, text_align=ft.TextAlign.CENTER),
                    ft.Text(label, size=8, weight=ft.FontWeight.W_600, color=SportColors.TEXT_MUTED, text_align=ft.TextAlign.CENTER)
                ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#14141E",
                border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
                border_radius=8,
                padding=AppPadding.symmetric(horizontal=4, vertical=5),
                expand=True
            )

        # 1. Demonstração Visual / GIF Grande e Fluido
        img_control = ft.Image(
            src=gif_url,
            height=200,
            fit="contain",
            border_radius=10,
            error_content=ft.Container(
                content=ft.Column([
                    ft.Icon(Icons.FITNESS_CENTER, size=36, color=SportColors.TEXT_MUTED),
                    ft.Text(f"{ex_name}", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                height=180,
                alignment=AppAlignment.CENTER,
                bgcolor=SportColors.BG_SURFACE_ALT
            )
        )

        visual_media = ft.Container(
            content=img_control,
            alignment=AppAlignment.CENTER,
            height=200,
            bgcolor="#09090E",
            border_radius=12,
            border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
            padding=AppPadding.all(4)
        )

        # 2. Métricas do Exercício
        weight_display = f"{int(target_weight)} kg" if target_weight else "Livre"
        metrics_row = ft.Row([
            _metric_pill("SÉRIES", str(target_sets)),
            _metric_pill("REPS", str(target_reps)),
            _metric_pill("CARGA", weight_display),
            _metric_pill("DESCANSO", f"{rest_sec}s")
        ], spacing=6)

        # 3. Cronômetro de Descanso Local do Próprio Card
        card_timer_strip = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(Icons.TIMER_OUTLINED, color=SportColors.PRIMARY_NEON, size=15),
                        ft.Text("DESCANSO:", size=10, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY),
                        self.timer_text,
                    ], spacing=6),
                    ft.Row([
                        self._timer_preset_chip(30),
                        self._timer_preset_chip(45),
                        self._timer_preset_chip(60),
                        self._timer_preset_chip(90),
                        ft.IconButton(
                            icon=Icons.STOP_CIRCLE_OUTLINED,
                            icon_color=SportColors.TEXT_MUTED,
                            icon_size=16,
                            tooltip="Zerar cronômetro",
                            on_click=lambda _: self._stop_timer()
                        )
                    ], spacing=3)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, wrap=True),
                self.timer_progress
            ], spacing=4),
            bgcolor="#101018",
            border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
            border_radius=8,
            padding=AppPadding.symmetric(horizontal=8, vertical=6)
        )

        # 4. Tabela de Séries Mobile First (Sincronizada em tempo real com o estado)
        table_header = ft.Container(
            content=ft.Row([
                ft.Text("SET", size=9, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED, width=32, text_align=ft.TextAlign.CENTER),
                ft.Text("CARGA", size=9, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED, width=76, text_align=ft.TextAlign.CENTER),
                ft.Text("REPS", size=9, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED, width=70, text_align=ft.TextAlign.CENTER),
                ft.Text("FEITO", size=9, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED, width=44, text_align=ft.TextAlign.CENTER),
            ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor="#101018",
            border_radius=6,
            padding=AppPadding.symmetric(horizontal=6, vertical=5)
        )

        sets_rows = []
        self.active_inputs[ex_name] = {}
        ex_state_sets = self.exercise_state.get(ex_name, {}).get("sets", [])

        for s_data in ex_state_sets:
            s_num = s_data["set_num"]
            is_done = s_data.get("completed", False)
            curr_w = s_data.get("weight", target_weight)
            curr_r = s_data.get("reps", 10)

            s_pill = ft.Container(
                content=ft.Text(f"{s_num}", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                bgcolor="#1C1C26",
                border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
                border_radius=6,
                width=32,
                height=36,
                alignment=AppAlignment.CENTER
            )

            w_input = ft.TextField(
                value=str(int(curr_w)) if curr_w == int(curr_w) else str(curr_w),
                width=76,
                height=36,
                text_size=13,
                text_align=ft.TextAlign.CENTER,
                suffix=ft.Text("kg", size=10, color=SportColors.TEXT_MUTED),
                keyboard_type=ft.KeyboardType.NUMBER,
                bgcolor=SportColors.BG_INPUT,
                border_color=SportColors.BORDER_DEFAULT,
                focused_border_color=SportColors.PRIMARY_NEON,
                color=SportColors.TEXT_WHITE,
                content_padding=AppPadding.symmetric(horizontal=4, vertical=2)
            )

            r_input = ft.TextField(
                value=str(curr_r),
                width=70,
                height=36,
                text_size=13,
                text_align=ft.TextAlign.CENTER,
                suffix=ft.Text("reps", size=10, color=SportColors.TEXT_MUTED),
                keyboard_type=ft.KeyboardType.NUMBER,
                bgcolor=SportColors.BG_INPUT,
                border_color=SportColors.BORDER_DEFAULT,
                focused_border_color=SportColors.PRIMARY_NEON,
                color=SportColors.TEXT_WHITE,
                content_padding=AppPadding.symmetric(horizontal=4, vertical=2)
            )

            # Sincronização em tempo real das alterações do usuário no estado
            def make_w_change(name=ex_name, s_idx=s_num - 1):
                def handler(e):
                    try:
                        val = float(e.control.value or 0)
                    except Exception:
                        val = 0.0
                    if name in self.exercise_state and s_idx < len(self.exercise_state[name]["sets"]):
                        self.exercise_state[name]["sets"][s_idx]["weight"] = val
                return handler

            def make_r_change(name=ex_name, s_idx=s_num - 1):
                def handler(e):
                    try:
                        val = int(e.control.value or 0)
                    except Exception:
                        val = 10
                    if name in self.exercise_state and s_idx < len(self.exercise_state[name]["sets"]):
                        self.exercise_state[name]["sets"][s_idx]["reps"] = val
                return handler

            w_input.on_change = make_w_change()
            r_input.on_change = make_r_change()

            check_btn = ft.Container(
                content=ft.Icon(
                    Icons.CHECK,
                    size=18 if is_done else 16,
                    color=SportColors.PRIMARY_TEXT_ON_NEON if is_done else SportColors.TEXT_MUTED
                ),
                bgcolor=SportColors.PRIMARY_NEON if is_done else SportColors.BG_SURFACE_ALT,
                border=AppBorder.all(1, SportColors.PRIMARY_NEON if is_done else SportColors.BORDER_DEFAULT),
                border_radius=6,
                width=44,
                height=36,
                alignment=AppAlignment.CENTER,
                tooltip="Concluir série e iniciar cronômetro" if not is_done else "Série já concluída",
                ink=True
            )

            self.active_inputs[ex_name][f"s{s_num}_w"] = w_input
            self.active_inputs[ex_name][f"s{s_num}_r"] = r_input

            def make_on_check(btn=check_btn, w_inp=w_input, r_inp=r_input, s=s_num, name=ex_name, r_time=rest_sec, s_idx=s_num - 1):
                def handler(_):
                    btn.content = ft.Icon(Icons.CHECK, size=18, color=SportColors.PRIMARY_TEXT_ON_NEON)
                    btn.bgcolor = SportColors.PRIMARY_NEON
                    btn.border = AppBorder.all(1, SportColors.PRIMARY_NEON)
                    btn.on_click = None
                    
                    try:
                        w_val = float(w_inp.value or 0)
                    except Exception:
                        w_val = 0.0
                    try:
                        r_val = int(r_inp.value or 0)
                    except Exception:
                        r_val = 10
                        
                    # Atualiza o estado centralizado
                    if name in self.exercise_state and s_idx < len(self.exercise_state[name]["sets"]):
                        self.exercise_state[name]["sets"][s_idx]["weight"] = w_val
                        self.exercise_state[name]["sets"][s_idx]["reps"] = r_val
                        self.exercise_state[name]["sets"][s_idx]["completed"] = True

                    self.completed_sets.append({
                        "exercise_name": name,
                        "set_number": s,
                        "weight_kg": w_val,
                        "reps": r_val,
                        "rpe": 8.0
                    })
                    
                    UIHelper.show_toast(self.page, f"Série #{s} de {name} concluída! Descanso iniciado ({r_time}s).", color=SportColors.PRIMARY_NEON)
                    self._start_timer(r_time)
                    if self.page:
                        self.page.update()
                return handler

            if not is_done:
                check_btn.on_click = make_on_check()

            sets_rows.append(
                ft.Row([
                    s_pill,
                    w_input,
                    r_input,
                    check_btn
                ], spacing=6, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            )

        sets_table = ft.Container(
            content=ft.Column([
                table_header,
                ft.Column(sets_rows, spacing=6)
            ], spacing=6),
            bgcolor="#111118",
            border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
            border_radius=10,
            padding=8
        )

        # Modal de Instruções Sob Demanda
        def show_instructions_dialog(name=ex_name, g=guide, m=mistakes, w=why_do_it):
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(Icons.INFO_OUTLINE, color=SportColors.CYAN_ELECTRIC, size=20),
                    ft.Text(f"Guia: {name}", size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
                ], spacing=6),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🎯 O QUE FAZER (POSTURA):", size=11, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON),
                        ft.Text(g, size=12, color=SportColors.TEXT_PRIMARY),
                        ft.Container(height=4),
                        ft.Text("💡 POR QUE FAZER:", size=11, weight=ft.FontWeight.BOLD, color=SportColors.CYAN_ELECTRIC),
                        ft.Text(w, size=12, color=SportColors.TEXT_SECONDARY),
                        ft.Container(height=4),
                        ft.Text("⚠️ ERROS A EVITAR:", size=11, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED),
                        ft.Text(m, size=12, color=SportColors.TEXT_MUTED),
                    ], spacing=4, tight=True),
                    width=320
                ),
                actions=[
                    ft.TextButton("Entendi", on_click=lambda _: UIHelper.close_dialog(self.page, dlg))
                ]
            )
            UIHelper.open_dialog(self.page, dlg)

        # Cabeçalho do Card com Número e Informações
        card_header = ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Text(f"{ex_idx + 1}", size=14, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_TEXT_ON_NEON),
                    bgcolor=SportColors.PRIMARY_NEON,
                    width=28,
                    height=28,
                    border_radius=14,
                    alignment=AppAlignment.CENTER
                ),
                ft.Column([
                    ft.Text(f"{ex_name}", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                    ft.Row([
                        SportStyles.badge(p_muscle, SportColors.PRIMARY_NEON, icon=Icons.FITNESS_CENTER),
                        SportStyles.badge(equipment, SportColors.TEXT_SECONDARY, icon=Icons.SETTINGS),
                    ], spacing=4, wrap=True),
                ], spacing=2, expand=True),
            ], spacing=10, expand=True, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row([
                ft.IconButton(
                    icon=Icons.INFO_OUTLINE,
                    icon_color=SportColors.CYAN_ELECTRIC,
                    icon_size=20,
                    tooltip="Ver instruções e postura",
                    on_click=lambda _, n=ex_name, g=guide, m=mistakes, w=why_do_it: show_instructions_dialog(n, g, m, w)
                ),
                ft.IconButton(
                    icon=Icons.SWAP_HORIZ,
                    icon_color=SportColors.TEXT_MUTED,
                    icon_size=20,
                    tooltip="Substituir exercício",
                    on_click=lambda _, name=ex_name, rid=current_routine["id"]: self._show_swap_exercise_dialog(rid, name)
                )
            ], spacing=2)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # 5. Botão de Ação Inferior (Próximo Exercício ou Finalizar Treino)
        total_ex = len(exercises)
        is_last_exercise = self.current_exercise_index >= total_ex - 1

        if not is_last_exercise:
            card_action_section = ft.Column([
                ft.Row([
                    ft.ElevatedButton(
                        "AVANÇAR PARA O PRÓXIMO EXERCÍCIO ➔",
                        icon=Icons.ARROW_FORWARD,
                        style=ft.ButtonStyle(
                            bgcolor=SportColors.PRIMARY_NEON,
                            color=SportColors.PRIMARY_TEXT_ON_NEON,
                            text_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD),
                            shape=ft.RoundedRectangleBorder(radius=12) if hasattr(ft, "RoundedRectangleBorder") else None
                        ),
                        height=48,
                        expand=True,
                        on_click=lambda _: self._navigate_exercise(1)
                    )
                ]),
                ft.Row([
                    ft.TextButton(
                        "Ou finalizar treino agora",
                        style=ft.ButtonStyle(color=SportColors.TEXT_MUTED),
                        on_click=lambda _: self._finish_workout_session()
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=4)
        else:
            card_action_section = ft.Row([
                ft.ElevatedButton(
                    "FINALIZAR TREINO & SALVAR ✓",
                    icon=Icons.CHECK_CIRCLE,
                    style=ft.ButtonStyle(
                        bgcolor=SportColors.PRIMARY_NEON,
                        color=SportColors.PRIMARY_TEXT_ON_NEON,
                        text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
                        shape=ft.RoundedRectangleBorder(radius=12) if hasattr(ft, "RoundedRectangleBorder") else None
                    ),
                    height=52,
                    expand=True,
                    on_click=lambda _: self._finish_workout_session()
                )
            ])

        # Card Completo do Exercício Único
        card = SportStyles.card_container(
            content=ft.Column([
                card_header,
                metrics_row,
                visual_media,
                card_timer_strip,
                sets_table,
                ft.Container(height=4),
                card_action_section
            ], spacing=12),
            bgcolor=SportColors.BG_SURFACE,
            border_color=SportColors.BORDER_DEFAULT,
            padding=14,
            radius=16
        )

        self.active_exercise_container.content = card

    def _show_all_exercises_modal(self):
        """Abre modal com índice de todos os exercícios da ficha para navegação direta rápida."""
        current_routine = self.routines[self.selected_routine_index] if self.routines else {}
        exercises = current_routine.get("exercises", [])
        
        items = []
        for idx, ex in enumerate(exercises):
            ex_name = ex.get("exercise_name", "Exercício")
            muscle = ex.get("primary_muscle", "Geral")
            sets_count = ex.get("target_sets", 3)
            is_active = idx == self.current_exercise_index
            
            # Verifica se todas as séries foram concluídas
            state_sets = self.exercise_state.get(ex_name, {}).get("sets", [])
            completed_count = sum(1 for s in state_sets if s.get("completed", False))
            is_done = completed_count >= sets_count and sets_count > 0

            status_chip = ft.Text("✓ Concluído", size=10, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON) if is_done else ft.Text(f"{completed_count}/{sets_count} séries", size=10, color=SportColors.TEXT_MUTED)

            def make_jump(target_idx=idx):
                def handler(_):
                    UIHelper.close_dialog(self.page, dialog)
                    self.current_exercise_index = target_idx
                    self._render_stepper_ui()
                    self._render_active_exercise_card()
                    if self.page:
                        self.page.update()
                return handler

            items.append(
                SportStyles.card_container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(f"{idx + 1}", size=12, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_TEXT_ON_NEON if is_active else SportColors.TEXT_WHITE),
                            bgcolor=SportColors.PRIMARY_NEON if is_active else "#27272A",
                            width=26,
                            height=26,
                            border_radius=13,
                            alignment=AppAlignment.CENTER
                        ),
                        ft.Column([
                            ft.Text(ex_name, size=13, weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL, color=SportColors.TEXT_WHITE),
                            ft.Text(f"{muscle} • {sets_count} séries", size=10, color=SportColors.TEXT_SECONDARY)
                        ], spacing=1, expand=True),
                        status_chip,
                        ft.Icon(Icons.CHEVRON_RIGHT, size=18, color=SportColors.PRIMARY_NEON if is_active else SportColors.TEXT_MUTED)
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=SportColors.BG_SURFACE_ALT if not is_active else "#161B26",
                    border_color=SportColors.PRIMARY_NEON if is_active else SportColors.BORDER_DEFAULT,
                    padding=10,
                    radius=10,
                    on_click=make_jump()
                )
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.VIEW_LIST, color=SportColors.PRIMARY_NEON, size=20),
                ft.Text("Índice de Exercícios", size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text("Clique em qualquer exercício para pular diretamente:", size=11, color=SportColors.TEXT_SECONDARY),
                    ft.Column(items, spacing=6)
                ], spacing=8),
                width=320,
                height=380
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda _: UIHelper.close_dialog(self.page, dialog))
            ]
        )
        UIHelper.open_dialog(self.page, dialog)

    def _timer_preset_chip(self, seconds: int):
        return ft.Container(
            content=ft.Text(f"{seconds}s", size=10, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_PRIMARY),
            bgcolor=SportColors.BG_SURFACE,
            padding=AppPadding.symmetric(horizontal=6, vertical=3),
            border_radius=6,
            border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
            on_click=lambda _, s=seconds: self._start_timer(s)
        )

    def _start_timer(self, seconds: int):
        self._stop_timer()
        self.rest_seconds_left = seconds
        self.timer_running = True
        total_time = max(seconds, 1)

        def countdown():
            while self.timer_running and self.rest_seconds_left > 0:
                mins, secs = divmod(self.rest_seconds_left, 60)
                self.timer_text.value = f"{mins:02d}:{secs:02d}"
                self.timer_progress.value = 1.0 - (self.rest_seconds_left / total_time)
                if self.page:
                    try:
                        self.page.update()
                    except Exception:
                        pass
                time.sleep(1)
                self.rest_seconds_left -= 1

            if self.timer_running and self.rest_seconds_left <= 0:
                self.timer_text.value = "PRONTO!"
                self.timer_progress.value = 1.0
                if self.page:
                    try:
                        self.page.update()
                        UIHelper.show_toast(self.page, "Tempo de descanso encerrado! Próxima série!", color=SportColors.PRIMARY_NEON)
                    except Exception:
                        pass

        self.timer_thread = threading.Thread(target=countdown, daemon=True)
        self.timer_thread.start()

    def _stop_timer(self):
        self.timer_running = False
        self.rest_seconds_left = 0
        self.timer_text.value = "00:00"
        self.timer_progress.value = 0.0
        if self.page:
            try:
                self.page.update()
            except Exception:
                pass

    def _finish_workout_session(self):
        """
        Finaliza o treino consolidando 100% de todas as séries de todos os exercícios da rotina,
        mesmo os que foram navegados via páginas ou preenchidos com os valores alvo!
        """
        uid = self.user_id or DBService.get_active_user_id()
        current_routine = self.routines[self.selected_routine_index] if self.routines else {}
        r_name = current_routine.get("name", "Treino Concluído")
        exercises = current_routine.get("exercises", [])

        # Coleta todas as séries de todos os exercícios do estado consolidado
        sets_to_save = []
        for ex in exercises:
            ex_name = ex.get("exercise_name", "Exercício")
            state = self.exercise_state.get(ex_name, {})
            sets = state.get("sets", [])
            target_w = float(ex.get("target_weight", 0.0) or 0.0)
            
            for s in sets:
                w_val = float(s.get("weight", target_w) or 0.0)
                r_val = int(s.get("reps", 10) or 10)
                sets_to_save.append({
                    "exercise_name": ex_name,
                    "set_number": s.get("set_num", 1),
                    "weight_kg": w_val,
                    "reps": r_val,
                    "rpe": 8.0
                })

        total_vol = sum(s.get("weight_kg", 0) * s.get("reps", 10) for s in sets_to_save)
        duration_min = max(int((time.time() - self.session_start_time) / 60), 1)

        # 1. Salva no SQLite com persistência imediata
        session_id = DBService.save_workout_session(
            routine_name=r_name,
            duration_min=duration_min,
            total_volume=total_vol,
            sets=sets_to_save,
            notes="Treino executado e registrado com sucesso.",
            user_id=uid
        )

        # 2. Registra mensagem de debriefing do Treinador IA
        debrief_chat_msg = (
            f"📋 **Debriefing do Treino: {r_name}**\n\n"
            f"• **Séries Salvas**: {len(sets_to_save)} séries computadas.\n"
            f"• **Tonelagem Total**: {int(total_vol)} kg levantados.\n"
            f"• **Duração**: {duration_min} minutos.\n\n"
            f"💬 **Parecer do Treinador**: Excelente treino! Fibras musculares estimuladas com sobrecarga progressiva. "
            f"Mantenha boa hidratação (500-800ml) e garanta seu aporte proteico nas próximas horas."
        )
        try:
            DBService.add_chat_message("personal", "assistant", debrief_chat_msg, user_id=uid)
        except Exception:
            pass

        # 3. Limpa estado e atualiza histórico na tela
        self.completed_sets.clear()
        self.exercise_state.clear()
        self.current_exercise_index = 0
        self._initialize_exercise_state()
        self._stop_timer()
        self._render_stepper_ui()
        self._render_active_exercise_card()
        self._render_history()

        # 4. Modal de Sucesso Limpo e Confortável
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.CHECK_CIRCLE, color=SportColors.PRIMARY_NEON, size=22),
                ft.Text("Treino Salvo com Sucesso!", size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
            ], spacing=6),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Parabéns! Você finalizou o {r_name}.", size=12, color=SportColors.TEXT_PRIMARY),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Duração:", size=11, color=SportColors.TEXT_SECONDARY),
                                ft.Text(f"{duration_min} min", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.Text("Séries Computadas:", size=11, color=SportColors.TEXT_SECONDARY),
                                ft.Text(f"{len(sets_to_save)} séries", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.Text("Carga Total Movida:", size=11, color=SportColors.TEXT_SECONDARY),
                                ft.Text(f"{int(total_vol)} kg", size=13, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ], spacing=3),
                        bgcolor=SportColors.BG_SURFACE_ALT,
                        padding=10,
                        border_radius=8
                    ),
                    ft.Text("✓ O treino já está no seu histórico e no chat com o Treinador IA.", size=10, color=SportColors.TEXT_MUTED)
                ], spacing=8, tight=True),
                width=300
            ),
            actions=[
                ft.ElevatedButton(
                    "OK, Concluído",
                    style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.PRIMARY_TEXT_ON_NEON),
                    on_click=lambda _: UIHelper.close_dialog(self.page, dialog)
                )
            ]
        )
        UIHelper.open_dialog(self.page, dialog)
        if self.page:
            self.page.update()

    def _render_history(self):
        """Renderiza os treinos salvos recentemente pelo usuário ativo."""
        self.history_column.controls.clear()
        uid = self.user_id or DBService.get_active_user_id()
        recent_sessions = DBService.get_recent_workout_sessions(limit=5, user_id=uid)

        if not recent_sessions:
            self.history_column.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(Icons.CHECK_CIRCLE_OUTLINE, color=SportColors.TEXT_MUTED, size=16),
                        ft.Text("Nenhum treino registrado ainda. Finalize um treino acima!", size=11, color=SportColors.TEXT_MUTED),
                    ], spacing=6),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=10,
                    border_radius=8
                )
            )
            return

        for s in recent_sessions:
            date_str = str(s.get("start_time", ""))[:16]
            r_name = s.get("routine_name", "Treino")
            vol = s.get("total_volume_kg", 0)
            dur = s.get("duration_minutes", 0)
            
            self.history_column.controls.append(
                SportStyles.card_container(
                    content=ft.Row([
                        ft.CircleAvatar(
                            radius=16,
                            bgcolor="#27272A",
                            content=ft.Icon(Icons.FITNESS_CENTER, color=SportColors.PRIMARY_NEON, size=14)
                        ),
                        ft.Column([
                            ft.Text(r_name, size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                            ft.Text(f"📅 {date_str} • ⏱️ {dur} min • ⚡ {int(vol)} kg total", size=10, color=SportColors.TEXT_SECONDARY)
                        ], spacing=1, expand=True),
                        ft.Container(
                            content=ft.Text("SALVO", size=9, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_TEXT_ON_NEON),
                            bgcolor=SportColors.PRIMARY_NEON,
                            padding=AppPadding.symmetric(horizontal=6, vertical=2),
                            border_radius=4
                        )
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    border_color=SportColors.BORDER_DEFAULT,
                    padding=8
                )
            )

    def _show_swap_exercise_dialog(self, routine_id: int, current_exercise: str):
        """Abre modal com alternativas recomendadas pelo Treinador quando a máquina está ocupada."""
        subs = DBService.get_exercise_substitutions(current_exercise)
        sub_cards = []

        if not subs:
            sub_cards.append(
                ft.Text(
                    f"Nenhuma recomendação automática para {current_exercise}. Consulte o Personal IA!",
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

                card = SportStyles.card_container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(alt_name, size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                            SportStyles.badge(muscle, SportColors.PRIMARY_NEON)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        SportStyles.badge(f"Equipamento: {equip}", SportColors.TEXT_SECONDARY),
                        ft.Text(f"💡 {reason}", size=11, color=SportColors.CYAN_ELECTRIC),
                        ft.ElevatedButton(
                            f"Substituir por {alt_name}",
                            icon=Icons.CHECK,
                            style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.PRIMARY_TEXT_ON_NEON),
                            height=32,
                            on_click=lambda _, an=alt_name: self._execute_exercise_swap(dialog, routine_id, current_exercise, an)
                        )
                    ], spacing=5),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    border_color=SportColors.BORDER_DEFAULT,
                    padding=8
                )
                sub_cards.append(card)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.SWAP_HORIZ, color=SportColors.CYAN_ELECTRIC, size=20),
                ft.Text("Trocar Exercício", size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text(f"Alternativas para: {current_exercise}", size=11, color=SportColors.TEXT_SECONDARY),
                    ft.Column(sub_cards, spacing=6)
                ], spacing=8),
                width=320,
                height=380
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda _: UIHelper.close_dialog(self.page, dialog))
            ]
        )
        UIHelper.open_dialog(self.page, dialog)

    def _execute_exercise_swap(self, dialog, routine_id: int, old_ex: str, new_ex: str):
        success = DBService.swap_routine_exercise(routine_id, old_ex, new_ex)
        UIHelper.close_dialog(self.page, dialog)
        if success:
            uid = self.user_id or DBService.get_active_user_id()
            self.routines = DBService.get_routines(user_id=uid)
            UIHelper.show_toast(self.page, f"Substituído com sucesso para: {new_ex}!", color=SportColors.PRIMARY_NEON)
            self.exercise_state.clear()
            self._initialize_exercise_state()
            self._update_routine_selector_ui()
            self._render_stepper_ui()
            self._render_active_exercise_card()
            if self.page:
                self.page.update()

    def _show_goal_setting_dialog(self):
        """Abre a avaliação física e anamnese 360° para calibrar o perfil e a divisão de treino."""
        from views.goal_setting_dialog import GoalSettingDialog
        def on_saved():
            uid = self.user_id or DBService.get_active_user_id()
            self.routines = DBService.get_routines(user_id=uid)
            self.selected_routine_index = 0
            self.current_exercise_index = 0
            self.exercise_state.clear()
            self._initialize_exercise_state()
            self._update_routine_selector_ui()
            self._render_stepper_ui()
            self._render_active_exercise_card()
            self._render_history()
            if self.page:
                self.page.update()
        dialog = GoalSettingDialog(self.page, on_saved=on_saved, user_id=self.user_id)
        dialog.show()

    def _show_coach_presets_dialog(self):
        """Abre modal com prescrições completas da periodização."""
        presets = [
            ("Superiores", "Foco em Superiores & Postura", "Peitoral, Costas, Ombros e Coluna (3 dias).", Icons.FITNESS_CENTER),
            ("PPL", "Push / Pull / Legs", "3 treinos com divisão clássica de hipertrofia.", Icons.FITNESS_CENTER),
            ("UpperLower", "Upper / Lower", "2 treinos divididos entre membros superiores e inferiores.", Icons.SPORTS_GYMNASTICS),
            ("ABC", "ABC Tradicional", "Peito/Tríceps, Costas/Bíceps, Pernas.", Icons.FITNESS_CENTER),
        ]

        preset_cards = []
        for key, title, desc, icon in presets:
            card = SportStyles.card_container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=SportColors.PRIMARY_NEON, size=16),
                        ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                    ], spacing=6),
                    ft.Text(desc, size=10, color=SportColors.TEXT_SECONDARY),
                    ft.ElevatedButton(
                        f"Aplicar {key}",
                        icon=Icons.CHECK,
                        style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.PRIMARY_TEXT_ON_NEON),
                        height=28,
                        on_click=lambda _, pk=key: self._apply_preset(dialog, pk)
                    )
                ], spacing=4),
                bgcolor=SportColors.BG_SURFACE_ALT,
                border_color=SportColors.BORDER_DEFAULT,
                padding=8
            )
            preset_cards.append(card)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.AUTO_FIX_HIGH, color=SportColors.PRIMARY_NEON, size=20),
                ft.Text("Prescrições de Treino", size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text("Escolha a divisão desejada para reconfigurar a ficha:", size=11, color=SportColors.TEXT_SECONDARY),
                    ft.Column(preset_cards, spacing=6)
                ], spacing=8),
                width=320,
                height=360
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda _: UIHelper.close_dialog(self.page, dialog))
            ]
        )
        UIHelper.open_dialog(self.page, dialog)

    def _apply_preset(self, dialog, preset_key: str):
        uid = self.user_id or DBService.get_active_user_id()
        DBService.apply_coach_routine_preset(preset_key, user_id=uid)
        UIHelper.close_dialog(self.page, dialog)
        self.routines = DBService.get_routines(user_id=uid)
        self.selected_routine_index = 0
        self.current_exercise_index = 0
        self.exercise_state.clear()
        self._initialize_exercise_state()
        UIHelper.show_toast(self.page, f"Prescrição {preset_key} aplicada com sucesso!", color=SportColors.PRIMARY_NEON)
        self._update_routine_selector_ui()
        self._render_stepper_ui()
        self._render_active_exercise_card()
        if self.page:
            self.page.update()

    def _apply_default_routine(self):
        uid = self.user_id or DBService.get_active_user_id()
        DBService.apply_coach_routine_preset("ABC", user_id=uid)
        self.routines = DBService.get_routines(user_id=uid)
        self.selected_routine_index = 0
        self.current_exercise_index = 0
        self.exercise_state.clear()
        self.build()
        if self.page:
            self.page.update()
