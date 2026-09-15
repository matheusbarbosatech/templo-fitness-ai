"""
Módulo Oficial de Execução de Treino - Templo Fitness AI.
Design Ultra-Clean 100% Encaixotado (Zero Rolagem de Tela).
Tudo contido em uma única seção do celular:
1. A Foto / GIF compacto
2. O Nome do Exercício e detalhes
3. O Quadro de Repetição Otimizado
4. O Cronômetro de Descanso
5. O Botão de Avançar
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
        
        # Cronômetro de descanso integrado e discreto
        self.rest_seconds_left = 0
        self.timer_running = False
        self.timer_thread = None
        self.timer_text = ft.Text("00:00", size=12, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON)
        
        # Área de exibição dinâmica do card encaixotado
        self.boxed_section_area = ft.Container()

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

        # Inicializa o estado de séries
        self._initialize_exercise_state()
        self._render_boxed_card()

        # Barra Superior Minimalista (Abas de Ficha [A] [B] [C] e Progresso 1/5)
        top_header = self._build_top_header()

        # Encaixotamento perfeito: 1 única coluna centralizada, sem ListView, SEM ROLAGEM!
        content_box = ft.Container(
            content=ft.Column([
                top_header,
                ft.Container(height=4),
                self.boxed_section_area
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            col={"xs": 12, "sm": 12, "md": 9, "lg": 7, "xl": 5}
        )

        responsive_row = ft.ResponsiveRow([content_box], alignment=ft.MainAxisAlignment.CENTER)

        # Retorna container fixo com expand=True (ZERO rolagem)
        return ft.Container(
            content=responsive_row,
            padding=AppPadding.symmetric(horizontal=8, vertical=4),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _initialize_exercise_state(self):
        """Inicializa ou preserva o estado de séries e cargas de todos os exercícios da rotina."""
        if not self.routines or self.selected_routine_index >= len(self.routines):
            return
            
        current_routine = self.routines[self.selected_routine_index]
        exercises = current_routine.get("exercises", [])
        
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

    def _build_top_header(self) -> ft.Control:
        """Topo minimalista: Abas das Fichas, Progresso e Ações."""
        current_routine = self.routines[self.selected_routine_index] if self.routines else {}
        exercises = current_routine.get("exercises", [])
        total_ex = len(exercises)
        curr_num = self.current_exercise_index + 1 if total_ex > 0 else 0

        routine_pills = []
        for idx, r in enumerate(self.routines):
            is_sel = idx == self.selected_routine_index
            r_name = r["name"].split("-")[0].strip()
            
            routine_pills.append(
                ft.Container(
                    content=ft.Text(
                        r_name,
                        size=11,
                        weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.NORMAL,
                        color=SportColors.BG_DARK if is_sel else SportColors.TEXT_WHITE
                    ),
                    bgcolor=SportColors.PRIMARY_NEON if is_sel else SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.symmetric(horizontal=10, vertical=4),
                    border_radius=10,
                    border=AppBorder.all(1, SportColors.PRIMARY_NEON if is_sel else SportColors.BORDER_DEFAULT),
                    on_click=lambda _, i=idx: self._select_routine(i),
                    ink=True
                )
            )

        return ft.Row([
            ft.Row(routine_pills, spacing=4, scroll=ft.ScrollMode.AUTO, expand=True),
            ft.Row([
                ft.Container(
                    content=ft.Text(f"{curr_num}/{total_ex}", size=11, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON),
                    bgcolor="#181824",
                    padding=AppPadding.symmetric(horizontal=7, vertical=3),
                    border_radius=6,
                    border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
                    tooltip="Progresso do exercício"
                ),
                ft.IconButton(
                    icon=Icons.VIEW_LIST,
                    icon_color=SportColors.TEXT_WHITE,
                    icon_size=17,
                    tooltip="Ver lista completa de exercícios",
                    on_click=lambda _: self._show_all_exercises_modal()
                ),
                ft.IconButton(
                    icon=Icons.CHECK_CIRCLE_OUTLINE,
                    icon_color=SportColors.PRIMARY_NEON,
                    icon_size=17,
                    tooltip="Finalizar e Salvar Treino Agora",
                    on_click=lambda _: self._finish_workout_session()
                ),
                ft.IconButton(
                    icon=Icons.TUNE,
                    icon_color=SportColors.TEXT_MUTED,
                    icon_size=16,
                    tooltip="Mudar divisão de treino",
                    on_click=lambda _: self._show_coach_presets_dialog()
                )
            ], spacing=1, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _render_boxed_card(self):
        """Constrói a seção única encaixotada: Foto, Nome, Quadro Otimizado, Cronômetro e Botão."""
        current_routine = self.routines[self.selected_routine_index] if self.routines else {}
        exercises = current_routine.get("exercises", [])
        total_ex = len(exercises)
        
        if not exercises or self.current_exercise_index >= len(exercises):
            self.boxed_section_area.content = ft.Container(
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

        # 1. A FOTO / GIF DO EXERCÍCIO (Compacto 120px)
        img_control = ft.Image(
            src=gif_url,
            height=120,
            fit="contain",
            border_radius=8,
            error_content=ft.Container(
                content=ft.Column([
                    ft.Icon(Icons.FITNESS_CENTER, size=26, color=SportColors.TEXT_MUTED),
                    ft.Text(f"{ex_name}", size=10, color=SportColors.TEXT_SECONDARY)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                height=110,
                alignment=AppAlignment.CENTER,
                bgcolor="#121218"
            )
        )
        photo_container = ft.Container(
            content=img_control,
            alignment=AppAlignment.CENTER,
            height=120,
            bgcolor="#0A0A10",
            border_radius=8,
            padding=2
        )

        # 2. O NOME DO EXERCÍCIO + PRESCRIÇÃO + AÇÕES
        def show_instructions_dialog(name=ex_name, g=guide, m=mistakes, w=why_do_it):
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(Icons.INFO_OUTLINE, color=SportColors.CYAN_ELECTRIC, size=18),
                    ft.Text(f"Guia: {name}", size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
                ], spacing=6),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("🎯 O QUE FAZER (POSTURA):", size=10, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON),
                        ft.Text(g, size=11, color=SportColors.TEXT_PRIMARY),
                        ft.Container(height=4),
                        ft.Text("💡 POR QUE FAZER:", size=10, weight=ft.FontWeight.BOLD, color=SportColors.CYAN_ELECTRIC),
                        ft.Text(w, size=11, color=SportColors.TEXT_SECONDARY),
                        ft.Container(height=4),
                        ft.Text("⚠️ ERROS A EVITAR:", size=10, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED),
                        ft.Text(m, size=11, color=SportColors.TEXT_MUTED),
                    ], spacing=4, tight=True),
                    width=300
                ),
                actions=[
                    ft.TextButton("Entendi", on_click=lambda _: UIHelper.close_dialog(self.page, dlg))
                ]
            )
            UIHelper.open_dialog(self.page, dlg)

        title_row = ft.Row([
            ft.Column([
                ft.Text(f"{ex_name}", size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(f"{p_muscle} • {equipment} • {target_sets}x {target_reps}", size=10, color=SportColors.TEXT_SECONDARY, no_wrap=True),
            ], spacing=1, expand=True),
            ft.Row([
                ft.IconButton(
                    icon=Icons.INFO_OUTLINE,
                    icon_color=SportColors.CYAN_ELECTRIC,
                    icon_size=18,
                    tooltip="Guia de postura",
                    on_click=lambda _, n=ex_name, g=guide, m=mistakes, w=why_do_it: show_instructions_dialog(n, g, m, w)
                ),
                ft.IconButton(
                    icon=Icons.SWAP_HORIZ,
                    icon_color=SportColors.TEXT_MUTED,
                    icon_size=18,
                    tooltip="Aparelho ocupado? Trocar exercício",
                    on_click=lambda _, name=ex_name, rid=current_routine["id"]: self._show_swap_exercise_dialog(rid, name)
                )
            ], spacing=0)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # 3. O QUADRO DE REPETIÇÃO OTIMIZADO (Harmonioso, limpo e profissional)
        quadro_header = ft.Container(
            content=ft.Row([
                ft.Text("SÉRIE", size=8, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED, width=32, text_align=ft.TextAlign.CENTER),
                ft.Text("CARGA", size=8, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED, width=96, text_align=ft.TextAlign.CENTER),
                ft.Text("REPS", size=8, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED, width=86, text_align=ft.TextAlign.CENTER),
                ft.Text("FEITO", size=8, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED, width=38, text_align=ft.TextAlign.CENTER),
            ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor="#0F0F16",
            padding=AppPadding.symmetric(horizontal=4, vertical=2),
            border_radius=4
        )

        sets_rows = []
        self.active_inputs[ex_name] = {}
        ex_state_sets = self.exercise_state.get(ex_name, {}).get("sets", [])

        # Identifica primeira série pendente para destacar como ativa
        active_set_num = None
        for s in ex_state_sets:
            if not s.get("completed", False):
                active_set_num = s["set_num"]
                break

        for s_data in ex_state_sets:
            s_num = s_data["set_num"]
            is_done = s_data.get("completed", False)
            is_active = (s_num == active_set_num)
            curr_w = s_data.get("weight", target_weight)
            curr_r = s_data.get("reps", 10)

            # 1. Badge Série
            s_badge = ft.Container(
                content=ft.Text(
                    f"{s_num}ª",
                    size=10,
                    weight=ft.FontWeight.BOLD,
                    color=SportColors.PRIMARY_NEON if is_active else (SportColors.TEXT_WHITE if not is_done else "#22C55E")
                ),
                width=32,
                alignment=AppAlignment.CENTER
            )

            # 2. Stepper Carga (Capsule Integrado)
            w_input = ft.TextField(
                value=str(int(curr_w)) if curr_w == int(curr_w) else str(curr_w),
                width=36,
                height=28,
                text_size=11,
                text_align=ft.TextAlign.CENTER,
                border=ft.InputBorder.NONE,
                content_padding=AppPadding.symmetric(0, 0),
                dense=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                color=SportColors.TEXT_WHITE
            )

            def make_adjust_w(name=ex_name, s_idx=s_num - 1, w_inp=w_input):
                def adjust(delta: float):
                    def handler(_):
                        try:
                            current_val = float(w_inp.value or 0)
                        except Exception:
                            current_val = 0.0
                        new_val = max(0.0, current_val + delta)
                        w_inp.value = str(int(new_val)) if new_val == int(new_val) else str(new_val)
                        if name in self.exercise_state and s_idx < len(self.exercise_state[name]["sets"]):
                            self.exercise_state[name]["sets"][s_idx]["weight"] = new_val
                        if self.page:
                            self.page.update()
                    return handler
                return adjust

            btn_minus_w = ft.Container(
                content=ft.Text("-", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                width=18,
                height=28,
                alignment=AppAlignment.CENTER,
                tooltip="Diminuir 1 kg",
                on_click=make_adjust_w()( -1.0 ),
                ink=True
            )

            btn_plus_w = ft.Container(
                content=ft.Text("+", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                width=18,
                height=28,
                alignment=AppAlignment.CENTER,
                tooltip="Aumentar 1 kg",
                on_click=make_adjust_w()( 1.0 ),
                ink=True
            )

            carga_capsule = ft.Container(
                content=ft.Row([
                    btn_minus_w,
                    w_input,
                    ft.Text("kg", size=8, color=SportColors.TEXT_MUTED),
                    btn_plus_w
                ], spacing=1, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#161622" if not is_done else "#0E1812",
                border=AppBorder.all(1, "#262638" if not is_done else "#1D3B28"),
                border_radius=6,
                width=96,
                height=28,
                alignment=AppAlignment.CENTER
            )

            # 3. Stepper Repetições (Capsule Integrado)
            r_input = ft.TextField(
                value=str(curr_r),
                width=32,
                height=28,
                text_size=11,
                text_align=ft.TextAlign.CENTER,
                border=ft.InputBorder.NONE,
                content_padding=AppPadding.symmetric(0, 0),
                dense=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                color=SportColors.TEXT_WHITE
            )

            def make_adjust_r(name=ex_name, s_idx=s_num - 1, r_inp=r_input):
                def adjust(delta: int):
                    def handler(_):
                        try:
                            current_val = int(r_inp.value or 0)
                        except Exception:
                            current_val = 10
                        new_val = max(1, current_val + delta)
                        r_inp.value = str(new_val)
                        if name in self.exercise_state and s_idx < len(self.exercise_state[name]["sets"]):
                            self.exercise_state[name]["sets"][s_idx]["reps"] = new_val
                        if self.page:
                            self.page.update()
                    return handler
                return adjust

            btn_minus_r = ft.Container(
                content=ft.Text("-", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                width=18,
                height=28,
                alignment=AppAlignment.CENTER,
                tooltip="Diminuir 1 repetição",
                on_click=make_adjust_r()( -1 ),
                ink=True
            )

            btn_plus_r = ft.Container(
                content=ft.Text("+", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                width=18,
                height=28,
                alignment=AppAlignment.CENTER,
                tooltip="Aumentar 1 repetição",
                on_click=make_adjust_r()( 1 ),
                ink=True
            )

            reps_capsule = ft.Container(
                content=ft.Row([
                    btn_minus_r,
                    r_input,
                    ft.Text("x", size=8, color=SportColors.TEXT_MUTED),
                    btn_plus_r
                ], spacing=1, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#161622" if not is_done else "#0E1812",
                border=AppBorder.all(1, "#262638" if not is_done else "#1D3B28"),
                border_radius=6,
                width=86,
                height=28,
                alignment=AppAlignment.CENTER
            )

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

            # 4. Botão Check de Série
            check_btn = ft.Container(
                content=ft.Icon(
                    Icons.CHECK,
                    size=15 if is_done else 14,
                    color=SportColors.PRIMARY_TEXT_ON_NEON if is_done else SportColors.TEXT_MUTED
                ),
                bgcolor=SportColors.PRIMARY_NEON if is_done else "#181824",
                border=AppBorder.all(1, SportColors.PRIMARY_NEON if is_done else "#2A2A3C"),
                border_radius=6,
                width=38,
                height=28,
                alignment=AppAlignment.CENTER,
                tooltip="Concluir série" if not is_done else "Série concluída",
                ink=True
            )

            self.active_inputs[ex_name][f"s{s_num}_w"] = w_input
            self.active_inputs[ex_name][f"s{s_num}_r"] = r_input

            def make_on_check(btn=check_btn, w_inp=w_input, r_inp=r_input, s=s_num, name=ex_name, r_time=rest_sec, s_idx=s_num - 1):
                def handler(_):
                    try:
                        w_val = float(w_inp.value or 0)
                    except Exception:
                        w_val = 0.0
                    try:
                        r_val = int(r_inp.value or 0)
                    except Exception:
                        r_val = 10
                        
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
                    
                    UIHelper.show_toast(self.page, f"Série #{s} concluída! Descanso ({r_time}s).", color=SportColors.PRIMARY_NEON)
                    self._start_timer(r_time)
                    self._render_boxed_card()
                    if self.page:
                        self.page.update()
                return handler

            if not is_done:
                check_btn.on_click = make_on_check()

            # Linha da Série Unificada
            row_bg = "#0D1612" if is_done else ("#141822" if is_active else "#12121A")
            row_border_color = "#1A3D28" if is_done else (SportColors.PRIMARY_NEON if is_active else "#1E1E2A")

            sets_rows.append(
                ft.Container(
                    content=ft.Row([
                        s_badge,
                        carga_capsule,
                        reps_capsule,
                        check_btn
                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=row_bg,
                    border=AppBorder.all(1, row_border_color),
                    border_radius=6,
                    padding=AppPadding.symmetric(horizontal=4, vertical=2),
                    height=34
                )
            )

        quadro_repeticoes = ft.Container(
            content=ft.Column([
                quadro_header,
                ft.Column(sets_rows, spacing=3)
            ], spacing=3),
            bgcolor="#101018",
            border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
            border_radius=8,
            padding=AppPadding.symmetric(horizontal=4, vertical=4)
        )

        # 4. O CRONÔMETRO DE DESCANSO SUTIL
        cronometro_bar = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(Icons.TIMER_OUTLINED, color=SportColors.PRIMARY_NEON, size=14),
                    ft.Text("Descanso:", size=10, color=SportColors.TEXT_SECONDARY),
                    self.timer_text,
                ], spacing=3),
                ft.Row([
                    ft.Container(
                        content=ft.Text("+30s", size=9, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                        bgcolor="#1C1C28",
                        padding=AppPadding.symmetric(horizontal=7, vertical=3),
                        border_radius=4,
                        on_click=lambda _: self._add_rest_time(30),
                        ink=True
                    ),
                    ft.Container(
                        content=ft.Text("Pular", size=9, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_MUTED),
                        bgcolor="#1C1C28",
                        padding=AppPadding.symmetric(horizontal=7, vertical=3),
                        border_radius=4,
                        on_click=lambda _: self._stop_timer(),
                        ink=True
                    )
                ], spacing=4)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#0E0E16",
            border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
            border_radius=6,
            padding=AppPadding.symmetric(horizontal=8, vertical=3),
            height=30
        )

        # 5. O BOTÃO DE AVANÇAR
        has_prev = self.current_exercise_index > 0
        is_last = self.current_exercise_index >= total_ex - 1

        prev_btn = ft.IconButton(
            icon=Icons.ARROW_BACK_IOS_NEW,
            icon_color=SportColors.TEXT_WHITE if has_prev else SportColors.TEXT_MUTED,
            icon_size=16,
            disabled=not has_prev,
            tooltip="Exercício Anterior",
            on_click=lambda _: self._navigate_exercise(-1)
        )

        if not is_last:
            next_btn = ft.ElevatedButton(
                "PRÓXIMO EXERCÍCIO ➔",
                icon=Icons.ARROW_FORWARD,
                style=ft.ButtonStyle(
                    bgcolor=SportColors.PRIMARY_NEON,
                    color=SportColors.PRIMARY_TEXT_ON_NEON,
                    text_style=ft.TextStyle(size=13, weight=ft.FontWeight.BOLD),
                    shape=ft.RoundedRectangleBorder(radius=8) if hasattr(ft, "RoundedRectangleBorder") else None
                ),
                height=42,
                expand=True,
                on_click=lambda _: self._navigate_exercise(1)
            )
        else:
            next_btn = ft.ElevatedButton(
                "FINALIZAR TREINO & SALVAR ✓",
                icon=Icons.CHECK_CIRCLE,
                style=ft.ButtonStyle(
                    bgcolor=SportColors.PRIMARY_NEON,
                    color=SportColors.PRIMARY_TEXT_ON_NEON,
                    text_style=ft.TextStyle(size=13, weight=ft.FontWeight.BOLD),
                    shape=ft.RoundedRectangleBorder(radius=8) if hasattr(ft, "RoundedRectangleBorder") else None
                ),
                height=42,
                expand=True,
                on_click=lambda _: self._finish_workout_session()
            )

        action_row = ft.Row([
            prev_btn,
            next_btn
        ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # ENCAIXOTAMENTO TOTAL NUMA SEÇÃO SÓ (ZERO SCROLL)
        self.boxed_section_area.content = SportStyles.card_container(
            content=ft.Column([
                photo_container,
                title_row,
                quadro_repeticoes,
                cronometro_bar,
                action_row
            ], spacing=5),
            bgcolor=SportColors.BG_SURFACE,
            border_color=SportColors.BORDER_DEFAULT,
            padding=8,
            radius=10
        )

    def _select_routine(self, index: int):
        """Alterna a rotina em 1 clique."""
        self.selected_routine_index = index
        self.current_exercise_index = 0
        self.exercise_state.clear()
        self.completed_sets.clear()
        self._initialize_exercise_state()
        self._render_boxed_card()
        if self.page:
            self.page.update()

    def _navigate_exercise(self, delta: int):
        """Navega entre os exercícios da rotina estilo virar a página do livro."""
        current_routine = self.routines[self.selected_routine_index] if self.routines else {}
        exercises = current_routine.get("exercises", [])
        new_idx = self.current_exercise_index + delta
        if 0 <= new_idx < len(exercises):
            self.current_exercise_index = new_idx
            self._render_boxed_card()
            if self.page:
                self.page.update()

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
            
            state_sets = self.exercise_state.get(ex_name, {}).get("sets", [])
            completed_count = sum(1 for s in state_sets if s.get("completed", False))
            is_done = completed_count >= sets_count and sets_count > 0

            status_chip = ft.Text("✓ Concluído", size=10, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON) if is_done else ft.Text(f"{completed_count}/{sets_count} séries", size=10, color=SportColors.TEXT_MUTED)

            def make_jump(target_idx=idx):
                def handler(_):
                    UIHelper.close_dialog(self.page, dialog)
                    self.current_exercise_index = target_idx
                    self._render_boxed_card()
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
                ft.Text("Lista de Exercícios da Ficha", size=14, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text("Toque em qualquer exercício para ir direto a ele:", size=11, color=SportColors.TEXT_SECONDARY),
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

    def _start_timer(self, seconds: int):
        self._stop_timer()
        self.rest_seconds_left = seconds
        self.timer_running = True

        def countdown():
            while self.timer_running and self.rest_seconds_left > 0:
                mins, secs = divmod(self.rest_seconds_left, 60)
                self.timer_text.value = f"{mins:02d}:{secs:02d}"
                if self.page:
                    try:
                        self.page.update()
                    except Exception:
                        pass
                time.sleep(1)
                self.rest_seconds_left -= 1

            if self.timer_running and self.rest_seconds_left <= 0:
                self.timer_text.value = "PRONTO!"
                if self.page:
                    try:
                        self.page.update()
                        UIHelper.show_toast(self.page, "Tempo de descanso encerrado! Próxima série!", color=SportColors.PRIMARY_NEON)
                    except Exception:
                        pass

        self.timer_thread = threading.Thread(target=countdown, daemon=True)
        self.timer_thread.start()

    def _add_rest_time(self, seconds: int):
        self.rest_seconds_left += seconds
        mins, secs = divmod(self.rest_seconds_left, 60)
        self.timer_text.value = f"{mins:02d}:{secs:02d}"
        if not self.timer_running:
            self._start_timer(self.rest_seconds_left)
        elif self.page:
            self.page.update()

    def _stop_timer(self):
        self.timer_running = False
        self.rest_seconds_left = 0
        self.timer_text.value = "00:00"
        if self.page:
            try:
                self.page.update()
            except Exception:
                pass

    def _finish_workout_session(self):
        """Finaliza o treino consolidando 100% de todas as séries de todos os exercícios da rotina."""
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

        # 3. Limpa estado
        self.completed_sets.clear()
        self.exercise_state.clear()
        self.current_exercise_index = 0
        self._initialize_exercise_state()
        self._stop_timer()
        self._render_boxed_card()

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
            self._render_boxed_card()
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
            self._render_boxed_card()
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
        self._render_boxed_card()
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
