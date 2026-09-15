"""
Módulo Oficial de Execução de Treino - Templo Fitness AI.
Padrão Nike Training / Whoop Carbon Volt.
Apresenta:
1. Alternância fluida e instantânea de treinos (Treino A, B, C, etc.).
2. Demonstração visual animada (GIF / Cinesiologia) para cada exercício.
3. Descrição Completa: O QUE FAZER, POR QUE FAZER, COMO FAZER & ERROS.
4. Controle dinâmico de séries, cargas, repetições e cronômetro de descanso.
"""
import flet as ft
import time
import threading
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
        
        self.completed_sets: List[Dict[str, Any]] = []
        self.session_start_time = time.time()
        
        # Cronômetro de descanso
        self.rest_seconds_left = 0
        self.timer_running = False
        self.timer_thread = None
        self.timer_text = ft.Text("00:00", size=24, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON)
        self.timer_progress = ft.ProgressBar(value=0.0, color=SportColors.PRIMARY_NEON, bgcolor=SportColors.BG_SURFACE_ALT, height=4)
        
        # Elementos reativos da interface
        self.routine_selector_row = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
        self.routine_header_title = ft.Text("", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
        self.routine_header_desc = ft.Text("", size=12, color=SportColors.TEXT_SECONDARY)
        self.exercise_cards_column = ft.Column(spacing=14)

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

        # Atualiza a barra de seleção e a lista de exercícios
        self._update_routine_selector_ui()
        self._render_current_routine_exercises()

        # Barra de Prescrições Rápidas
        top_action_bar = ft.Row([
            ft.Row([
                ft.Icon(Icons.FLASH_ON, color=SportColors.PRIMARY_NEON, size=18),
                ft.Text("PROGRAMA ATIVO", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY),
            ], spacing=6),
            ft.ElevatedButton(
                "Prescrições do Treinador",
                icon=Icons.AUTO_FIX_HIGH,
                style=ft.ButtonStyle(
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    color=SportColors.PRIMARY_NEON,
                    text_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD),
                    shape=ft.RoundedRectangleBorder(radius=8) if hasattr(ft, "RoundedRectangleBorder") else None
                ),
                height=32,
                on_click=lambda _: self._show_coach_presets_dialog()
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Card do Cronômetro de Descanso
        timer_card = SportStyles.card_container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(Icons.TIMER_OUTLINED, color=SportColors.PRIMARY_NEON, size=18),
                        ft.Text("CRONÔMETRO DE RECUPERAÇÃO", size=11, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY),
                    ], spacing=6),
                    ft.Row([
                        self._timer_preset_chip(45),
                        self._timer_preset_chip(60),
                        self._timer_preset_chip(90),
                        self._timer_preset_chip(120),
                        ft.IconButton(
                            icon=Icons.STOP_CIRCLE_OUTLINED,
                            icon_color=SportColors.TEXT_MUTED,
                            icon_size=18,
                            tooltip="Zerar cronômetro",
                            on_click=lambda _: self._stop_timer()
                        )
                    ], spacing=4)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                self.timer_progress,
                ft.Row([
                    self.timer_text,
                    ft.Text("Descanso ativo entre séries", size=11, color=SportColors.TEXT_MUTED)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ], spacing=8),
            border_color=SportColors.BORDER_DEFAULT,
            padding=12
        )

        # Cabeçalho da Rotina Selecionada
        routine_info_card = SportStyles.card_container(
            content=ft.Column([
                self.routine_header_title,
                self.routine_header_desc,
            ], spacing=3),
            bgcolor=SportColors.BG_SURFACE_ALT,
            border_color=SportColors.BORDER_DEFAULT,
            padding=12
        )

        # Botão Finalizar Treino
        finish_bar = ft.Container(
            content=ft.ElevatedButton(
                "FINALIZAR TREINO & COMPUTAR TONELAGEM",
                icon=Icons.CHECK_CIRCLE,
                style=ft.ButtonStyle(
                    bgcolor=SportColors.PRIMARY_NEON,
                    color=SportColors.PRIMARY_TEXT_ON_NEON,
                    text_style=ft.TextStyle(size=13, weight=ft.FontWeight.BOLD),
                    shape=ft.RoundedRectangleBorder(radius=12) if hasattr(ft, "RoundedRectangleBorder") else None
                ),
                height=48,
                on_click=lambda _: self._finish_workout_session()
            ),
            padding=AppPadding.symmetric(vertical=8)
        )

        return ft.Container(
            content=ft.ListView([
                top_action_bar,
                self.routine_selector_row,
                timer_card,
                routine_info_card,
                self.exercise_cards_column,
                finish_bar,
                ft.Container(height=80)
            ], spacing=10, padding=AppPadding.all(14)),
            bgcolor=SportColors.BG_DARK,
            expand=True
        )

    def _timer_preset_chip(self, seconds: int):
        return ft.Container(
            content=ft.Text(f"{seconds}s", size=10, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_PRIMARY),
            bgcolor=SportColors.BG_SURFACE,
            padding=AppPadding.symmetric(horizontal=6, vertical=3),
            border_radius=6,
            border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
            on_click=lambda _, s=seconds: self._start_timer(s)
        )

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
                            size=14,
                            color=SportColors.PRIMARY_TEXT_ON_NEON if is_selected else SportColors.PRIMARY_NEON
                        ),
                        ft.Text(
                            r_label,
                            size=12,
                            weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.W_500,
                            color=SportColors.PRIMARY_TEXT_ON_NEON if is_selected else SportColors.TEXT_WHITE
                        )
                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=SportColors.PRIMARY_NEON if is_selected else SportColors.BG_SURFACE_ALT,
                    border_radius=10,
                    padding=AppPadding.symmetric(horizontal=14, vertical=10),
                    border=AppBorder.all(1, SportColors.PRIMARY_NEON if is_selected else SportColors.BORDER_DEFAULT),
                    on_click=lambda _, i=idx: self._select_routine(i),
                    ink=True
                )
            )

        if self.routines and self.selected_routine_index < len(self.routines):
            current = self.routines[self.selected_routine_index]
            self.routine_header_title.value = f"🔥 {current.get('name', 'Treino')}"
            self.routine_header_desc.value = f"🎯 {current.get('description', 'Foco de hipertrofia muscular')}"

    def _select_routine(self, index: int):
        """Alterna a rotina em 1 clique e reconstrói os exercícios na tela instantaneamente."""
        self.selected_routine_index = index
        self._update_routine_selector_ui()
        self._render_current_routine_exercises()
        if self.page:
            self.page.update()

    def _render_current_routine_exercises(self):
        """Renderiza os cards completos de cada exercício com visual animado e guias detalhados."""
        self.exercise_cards_column.controls.clear()
        
        if not self.routines or self.selected_routine_index >= len(self.routines):
            return

        current_routine = self.routines[self.selected_routine_index]
        exercises = current_routine.get("exercises", [])

        if not exercises:
            self.exercise_cards_column.controls.append(
                ft.Container(
                    content=ft.Text("Nenhum exercício configurado nesta rotina.", color=SportColors.TEXT_MUTED),
                    padding=AppPadding.all(16)
                )
            )
            return

        for ex_idx, ex in enumerate(exercises):
            ex_name = ex.get("exercise_name", "Exercício")
            target_sets = ex.get("target_sets", 4)
            target_reps = ex.get("target_reps", "8-12")
            target_weight = ex.get("target_weight", 20.0)
            rest_sec = ex.get("rest_seconds", 90)
            
            p_muscle = ex.get("primary_muscle") or "Músculo Alvo"
            equipment = ex.get("equipment") or "Aparelho"
            why_do_it = ex.get("why_do_it") or "Exercício fundamental para hipertrofia, tensão mecânica e recrutamento de fibras motoras."
            guide = ex.get("execution_guide") or "1. Ajuste a postura e faça retração escapular. 2. Realize o movimento na amplitude completa sem impulsos. 3. Controle a descida excêntrica por 2 a 3 segundos."
            mistakes = ex.get("common_mistakes") or "Usar carga excessiva prejudicando a amplitude; soltar o peso na fase excêntrica; balançar o corpo."
            gif_url = ex.get("gif_url") or DBService.get_exercise_gif(ex_name)

            # 1. Demonstração Visual / Animação (GIF do Exercício)
            visual_media = ft.Container(
                content=ft.Stack([
                    ft.Image(
                        src=gif_url,
                        height=160,
                        width=None,
                        fit="contain",
                        border_radius=10,
                        repeat=ft.ImageRepeat.NO_REPEAT,
                        error_content=ft.Container(
                            content=ft.Column([
                                ft.Icon(Icons.FITNESS_CENTER, size=36, color=SportColors.PRIMARY_NEON),
                                ft.Text(f"Demonstração: {ex_name}", size=11, color=SportColors.TEXT_SECONDARY)
                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            height=140,
                            alignment=AppAlignment.CENTER,
                            bgcolor=SportColors.BG_SURFACE_ALT
                        )
                    ),
                    ft.Container(
                        content=ft.Row([
                            SportStyles.badge("CINESIOLOGIA & MOVIMENTO", SportColors.PRIMARY_NEON),
                        ]),
                        top=8,
                        left=8
                    )
                ]),
                border_radius=10,
                border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
                bgcolor=SportColors.BG_SURFACE_ALT,
                padding=AppPadding.all(4)
            )

            # 2. Descrição Completa do Exercício na Ficha
            description_box = ft.Container(
                content=ft.Column([
                    # O QUE FAZER
                    ft.Column([
                        ft.Row([
                            ft.Icon(Icons.FITNESS_CENTER, size=13, color=SportColors.PRIMARY_NEON),
                            ft.Text("O QUE FAZER (POSTURA & MOVIMENTO)", size=11, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON),
                        ], spacing=4),
                        ft.Text(guide, size=11, color=SportColors.TEXT_PRIMARY),
                    ], spacing=2),
                    
                    # POR QUE FAZER
                    ft.Column([
                        ft.Row([
                            ft.Icon(Icons.PSYCHOLOGY, size=13, color=SportColors.CYAN_ELECTRIC),
                            ft.Text("POR QUE FAZER (CINESIOLOGIA)", size=11, weight=ft.FontWeight.BOLD, color=SportColors.CYAN_ELECTRIC),
                        ], spacing=4),
                        ft.Text(why_do_it, size=11, color=SportColors.TEXT_SECONDARY),
                    ], spacing=2),

                    # COMO FAZER & ERROS
                    ft.Column([
                        ft.Row([
                            ft.Icon(Icons.WARNING_AMBER_ROUNDED, size=13, color=SportColors.AMBER_GOLD),
                            ft.Text("COMO FAZER & O QUE EVITAR", size=11, weight=ft.FontWeight.BOLD, color=SportColors.AMBER_GOLD),
                        ], spacing=4),
                        ft.Text(mistakes, size=11, color=SportColors.TEXT_MUTED),
                    ], spacing=2),
                ], spacing=8),
                bgcolor=SportColors.BG_SURFACE_ALT,
                padding=AppPadding.all(10),
                border_radius=10,
                border=AppBorder.all(1, SportColors.BORDER_DEFAULT)
            )

            # 3. Tabela de Séries
            sets_rows = []
            for s_num in range(1, target_sets + 1):
                w_input = ft.TextField(
                    value=str(int(target_weight)),
                    width=55,
                    height=34,
                    text_size=12,
                    text_align=ft.TextAlign.CENTER,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    bgcolor=SportColors.BG_INPUT,
                    border_color=SportColors.BORDER_DEFAULT,
                    color=SportColors.TEXT_WHITE,
                    content_padding=AppPadding.all(2)
                )
                r_input = ft.TextField(
                    value="10",
                    width=45,
                    height=34,
                    text_size=12,
                    text_align=ft.TextAlign.CENTER,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    bgcolor=SportColors.BG_INPUT,
                    border_color=SportColors.BORDER_DEFAULT,
                    color=SportColors.TEXT_WHITE,
                    content_padding=AppPadding.all(2)
                )
                
                check_btn = ft.IconButton(
                    icon=Icons.CHECK_BOX_OUTLINE_BLANK,
                    icon_color=SportColors.TEXT_MUTED,
                    icon_size=22,
                    tooltip="Concluir série e iniciar descanso",
                    on_click=None
                )

                def make_on_check(btn=check_btn, w_inp=w_input, r_inp=r_input, s=s_num, name=ex_name, r_time=rest_sec):
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
                        
                        UIHelper.show_toast(self.page, f"Série #{s} de {name} registrada! Descanso iniciado ({r_time}s).", color=SportColors.PRIMARY_NEON)
                        self._start_timer(r_time)
                        if self.page:
                            self.page.update()
                    return handler

                check_btn.on_click = make_on_check()

                sets_rows.append(
                    ft.Row([
                        ft.Text(f"Série {s_num}", size=12, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY, width=50),
                        w_input,
                        ft.Text("kg", size=11, color=SportColors.TEXT_MUTED),
                        r_input,
                        ft.Text("reps", size=11, color=SportColors.TEXT_MUTED),
                        check_btn
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                )

            # Montagem do Card Completo do Exercício
            card = SportStyles.card_container(
                content=ft.Column([
                    # Cabeçalho do Card
                    ft.Row([
                        ft.Column([
                            ft.Text(f"{ex_idx + 1}. {ex_name}", size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                            ft.Row([
                                SportStyles.badge(p_muscle, SportColors.PRIMARY_NEON),
                                SportStyles.badge(equipment, SportColors.TEXT_SECONDARY),
                                SportStyles.badge(f"{target_sets} séries × {target_reps}", SportColors.AMBER_GOLD),
                            ], spacing=4),
                        ], spacing=3, expand=True),
                        ft.ElevatedButton(
                            "Substituir",
                            icon=Icons.SWAP_HORIZ,
                            style=ft.ButtonStyle(
                                bgcolor=SportColors.BG_SURFACE_ALT,
                                color=SportColors.CYAN_ELECTRIC,
                                text_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD),
                                shape=ft.RoundedRectangleBorder(radius=8) if hasattr(ft, "RoundedRectangleBorder") else None
                            ),
                            height=30,
                            on_click=lambda _, name=ex_name, rid=current_routine["id"]: self._show_swap_exercise_dialog(rid, name)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START),
                    
                    # Imagem/GIF Animado
                    visual_media,
                    
                    # Descrição Completa (O que fazer, Por que fazer, Como fazer)
                    description_box,
                    
                    # Tabela de Séries
                    ft.Divider(color=SportColors.BORDER_DEFAULT, height=8),
                    ft.Text("REGISTRO DE CARGAS & REPETIÇÕES:", size=11, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_SECONDARY),
                    ft.Column(sets_rows, spacing=4),
                ], spacing=10),
                border_color=SportColors.BORDER_DEFAULT,
                padding=14
            )

            self.exercise_cards_column.controls.append(card)

    def _start_timer(self, seconds: int):
        self.rest_seconds_left = seconds
        total_time = max(seconds, 1)

        def countdown():
            while self.rest_seconds_left > 0 and self.timer_running:
                mins, secs = divmod(self.rest_seconds_left, 60)
                self.timer_text.value = f"{mins:02d}:{secs:02d}"
                self.timer_progress.value = self.rest_seconds_left / total_time
                if self.page:
                    try:
                        self.page.update()
                    except Exception:
                        pass
                time.sleep(1)
                self.rest_seconds_left -= 1
            
            if self.rest_seconds_left <= 0 and self.timer_running:
                self.timer_text.value = "✓ Próxima Série!"
                self.timer_progress.value = 0.0
                if self.page:
                    try:
                        UIHelper.show_toast(self.page, "Descanso finalizado! Inicie a próxima série.", color=SportColors.PRIMARY_NEON)
                    except Exception:
                        pass

        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_running = False
            time.sleep(0.1)
        
        self.timer_running = True
        self.timer_thread = threading.Thread(target=countdown, daemon=True)
        self.timer_thread.start()

    def _stop_timer(self):
        self.timer_running = False
        self.rest_seconds_left = 0
        self.timer_text.value = "00:00"
        self.timer_progress.value = 0.0
        if self.page:
            self.page.update()

    def _finish_workout_session(self):
        if not self.completed_sets:
            UIHelper.show_toast(self.page, "Complete pelo menos 1 série antes de finalizar o treino!", color=SportColors.AMBER_GOLD)
            return

        total_vol = sum(s["weight_kg"] * s["reps"] for s in self.completed_sets)
        uid = self.user_id or DBService.get_active_user_id()
        current_routine = self.routines[self.selected_routine_index]
        r_name = current_routine.get("name", "Treino Concluído")

        DBService.save_workout_session(
            routine_name=r_name,
            duration_min=int((time.time() - self.session_start_time) / 60) or 45,
            total_volume=total_vol,
            sets=self.completed_sets,
            notes="Treino executado com postura exemplar e descrição biomecânica aplicada.",
            user_id=uid
        )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(Icons.CHECK_CIRCLE, color=SportColors.PRIMARY_NEON, size=24),
                ft.Text("Treino Concluído com Glória!", size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
            ], spacing=8),
            content=ft.Column([
                ft.Text(f"Excelente esforço! Você finalizou o {r_name}.", size=13, color=SportColors.TEXT_PRIMARY),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Séries Concluídas:", size=12, color=SportColors.TEXT_SECONDARY),
                            ft.Text(f"{len(self.completed_sets)} séries", size=12, weight=ft.FontWeight.BOLD, color=SportColors.PRIMARY_NEON)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Text("Tonelagem Levantada:", size=12, color=SportColors.TEXT_SECONDARY),
                            ft.Text(f"{int(total_vol)} kg", size=14, weight=ft.FontWeight.BOLD, color=SportColors.AMBER_GOLD)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=4),
                    bgcolor=SportColors.BG_SURFACE_ALT,
                    padding=AppPadding.all(12),
                    border_radius=10
                ),
            ], tight=True, spacing=10),
            actions=[
                ft.ElevatedButton(
                    "Concluir e Salvar",
                    style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.PRIMARY_TEXT_ON_NEON),
                    on_click=lambda _: self._close_dialog_and_reset(dialog)
                )
            ]
        )
        UIHelper.open_dialog(self.page, dialog)

    def _close_dialog_and_reset(self, dialog):
        UIHelper.close_dialog(self.page, dialog)
        self.completed_sets.clear()
        self._stop_timer()
        UIHelper.show_toast(self.page, "Treino registrado no seu histórico com sucesso!", color=SportColors.PRIMARY_NEON)

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
                tips = s.get("execution_tips", "")

                card = SportStyles.card_container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(alt_name, size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                            SportStyles.badge(muscle, SportColors.PRIMARY_NEON)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        SportStyles.badge(f"Equipamento: {equip}", SportColors.TEXT_SECONDARY),
                        ft.Text(f"💡 Dica do Treinador: {reason}", size=11, color=SportColors.CYAN_ELECTRIC),
                        ft.Text(f"🎯 Execução: {tips}", size=11, color=SportColors.TEXT_MUTED),
                        ft.ElevatedButton(
                            f"Substituir por {alt_name}",
                            icon=Icons.CHECK,
                            style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.PRIMARY_TEXT_ON_NEON),
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
                ft.Text("Trocar Exercício", size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text(f"Exercício atual: {current_exercise}\nMáquina ocupada ou dor? Escolha uma alternativa biomecanicamente equivalente:", size=11, color=SportColors.TEXT_SECONDARY),
                    ft.Column(sub_cards, spacing=8)
                ], spacing=10),
                width=340,
                height=420
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
            self._update_routine_selector_ui()
            self._render_current_routine_exercises()
            if self.page:
                self.page.update()

    def _show_coach_presets_dialog(self):
        """Abre modal com prescrições completas da periodização."""
        presets = [
            ("PPL", "Push / Pull / Legs (Hipertrofia Avançada)", "3 treinos com frequência ideal e recuperação neural profunda.", Icons.FITNESS_CENTER),
            ("UpperLower", "Upper / Lower (Força & Performance)", "2 treinos divididos entre membros superiores e inferiores.", Icons.SPORTS_GYMNASTICS),
            ("ABC", "ABC Clássico (Peito/Tríceps, Costas/Bíceps, Pernas)", "A divisão tradicional favorita das academias.", Icons.FITNESS_CENTER),
        ]

        preset_cards = []
        for key, title, desc, icon in presets:
            card = SportStyles.card_container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=SportColors.PRIMARY_NEON, size=18),
                        ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE),
                    ], spacing=6),
                    ft.Text(desc, size=11, color=SportColors.TEXT_SECONDARY),
                    ft.ElevatedButton(
                        f"Aplicar Prescrição {key}",
                        icon=Icons.CHECK,
                        style=ft.ButtonStyle(bgcolor=SportColors.PRIMARY_NEON, color=SportColors.PRIMARY_TEXT_ON_NEON),
                        height=32,
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
                ft.Text("Prescrições do Treinador", size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
            ], spacing=6),
            content=ft.Container(
                content=ft.ListView([
                    ft.Text("Selecione uma divisão científica para reconfigurar todo o seu programa:", size=11, color=SportColors.TEXT_SECONDARY),
                    ft.Column(preset_cards, spacing=8)
                ], spacing=10),
                width=340,
                height=400
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
        UIHelper.show_toast(self.page, f"Prescrição {preset_key} aplicada com sucesso!", color=SportColors.PRIMARY_NEON)
        self._update_routine_selector_ui()
        self._render_current_routine_exercises()
        if self.page:
            self.page.update()

    def _apply_default_routine(self):
        uid = self.user_id or DBService.get_active_user_id()
        DBService.apply_coach_routine_preset("ABC", user_id=uid)
        self.routines = DBService.get_routines(user_id=uid)
        self.selected_routine_index = 0
        self.build()
        if self.page:
            self.page.update()
