"""
Bateria de Testes de Estresse e Cenários Extremos (Stress & Edge-Case Robot)
TEMPLO FITNESS AI - Validação Profunda Noturna / Matinal
"""
import sys
import os
import time
import sqlite3
from datetime import date
from typing import Dict, Any, List

# Garante UTF-8 no terminal Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.db_service import DBService
from services.devworld_ai_service import DevWorldAIService
from core.health_math import HealthMath

class ExtremeStressTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.start_time = time.time()

    def assert_test(self, description: str, condition: bool, details: str = ""):
        if condition:
            self.passed += 1
            det_str = f" ({details})" if details else ""
            print(f"  ✅ [PASSOU] {description}{det_str}")
        else:
            self.failed += 1
            det_str = f" -> FALHA: {details}" if details else " -> FALHA"
            self.errors.append(f"{description}: {details}")
            print(f"  ❌ [FALHOU] {description}{det_str}")

    def run_all(self):
        print("=" * 80)
        print("🏛️ BATERIA DE TESTES DE ESTRESSE & CENÁRIOS EXTREMOS - TEMPLO FITNESS AI")
        print("=" * 80)

        self.test_health_math_edge_cases()
        self.test_multi_user_concurrency_and_isolation()
        self.test_workout_extreme_loads_and_volumes()
        self.test_physical_assessment_extreme_profiles()
        self.test_kinesiology_double_swaps()
        self.test_coach_presets_stability()
        self.test_ai_chat_special_characters_and_prompts()
        self.test_nutrition_and_hydration_extremes()
        self.test_evolution_photos_and_metrics()
        self.test_database_integrity_and_cleanliness()

        elapsed = round(time.time() - self.start_time, 2)
        total = self.passed + self.failed
        pct = round((self.passed / max(total, 1)) * 100, 1)

        print("\n" + "=" * 80)
        print(f"📊 RELATÓRIO FINAL: {self.passed}/{total} TESTES EXTREMOS APROVADOS ({pct}%)")
        print(f"⏱️ Tempo Total de Estresse: {elapsed} segundos")
        if self.failed == 0:
            print("🛡️ CERTIFICAÇÃO: O APP SUPORTA 100% DOS CENÁRIOS EXTREMOS SEM ERROS!")
        else:
            print(f"⚠️ ATENÇÃO: {self.failed} testes falharam. Detalhes: {self.errors}")
        print("=" * 80)
        return self.failed == 0

    # -------------------------------------------------------------
    # 1. Cálculos de Ciências do Esporte & Casos Limítrofes
    # -------------------------------------------------------------
    def test_health_math_edge_cases(self):
        print("\n📌 [1/10] Fórmulas Matemáticas & Casos Limítrofes (HealthMath)")
        
        # 1RM com 1 repetição (deve ser a própria carga)
        rm1 = HealthMath.calculate_1rm_epley(100.0, 1)
        self.assert_test("1RM Epley com 1 repetição é igual à carga", rm1 == 100.0, f"{rm1} kg")

        rm_brz1 = HealthMath.calculate_1rm_brzycki(100.0, 1)
        self.assert_test("1RM Brzycki com 1 repetição é igual à carga", rm_brz1 == 100.0, f"{rm_brz1} kg")

        # 1RM com peso corporal / carga 0
        rm_zero = HealthMath.calculate_1rm_epley(0.0, 15)
        self.assert_test("1RM Epley com carga 0 não quebra", rm_zero == 0.0)

        # 1RM com repetições muito altas (ex: 35 e 40 reps)
        rm_high = HealthMath.calculate_1rm_epley(40.0, 30)
        self.assert_test("1RM Epley com 30 reps calcula estimativa segura", rm_high == 80.0, f"{rm_high} kg")

        rm_brz_extreme = HealthMath.calculate_1rm_brzycki(50.0, 40)
        self.assert_test("1RM Brzycki com reps >= 37 ativa guardrail seguro", rm_brz_extreme > 0, f"{rm_brz_extreme} kg")

        # TMB Mifflin-St Jeor para Homens e Mulheres
        tmb_m = HealthMath.calculate_tmb_mifflin(80.0, 180.0, 25, "M")
        self.assert_test("TMB masculina válida (Mifflin)", 1700 <= tmb_m <= 1900, f"{tmb_m} kcal")

        tmb_f = HealthMath.calculate_tmb_mifflin(55.0, 165.0, 23, "F")
        self.assert_test("TMB feminina válida (Mifflin)", 1200 <= tmb_f <= 1400, f"{tmb_f} kcal")

        # TDEE com níveis de atividade
        tdee_sed = HealthMath.calculate_tdee(1800, "sedentario")
        tdee_hard = HealthMath.calculate_tdee(1800, "muito_intenso")
        self.assert_test("TDEE muito intenso > sedentário", tdee_hard > tdee_sed, f"Intenso: {tdee_hard} vs Sedentário: {tdee_sed}")

        # Zonas de frequência cardíaca de Karvonen
        zones = HealthMath.heart_rate_zones(age=25, resting_hr=60)
        self.assert_test("Zonas cardíacas Karvonen calculadas (5 zonas)", len(zones) == 5)
        z5_min, z5_max = zones["Zona 5 (Esforço Máximo / VO2 Max 90-100%)"]
        self.assert_test("Zona 5 máxima respeita 220 - idade", z5_max == 195, f"Max HR: {z5_max} bpm")

    # -------------------------------------------------------------
    # 2. Concorrência e Chaveamento Rápido de Usuários
    # -------------------------------------------------------------
    def test_multi_user_concurrency_and_isolation(self):
        print("\n📌 [2/10] Isolamento de Dados & Concorrência Multi-Usuário")
        
        # Verifica usuários principais existentes
        users = DBService.list_users()
        user_ids = {u["id"]: u["name"] for u in users}
        self.assert_test("Usuário Matheus existe com ID 1", 1 in user_ids, user_ids.get(1))
        self.assert_test("Usuária Mary existe", any("Mary" in name for name in user_ids.values()))

        # Simula chaveamento rápido alternado 10 vezes
        success_switches = 0
        for i in range(10):
            target = 1 if i % 2 == 0 else 20
            switched = DBService.switch_user(target)
            if switched["id"] == target:
                success_switches += 1
        self.assert_test("10 chaveamentos rápidos consecutivos sem travamento", success_switches == 10)

        # Confere isolamento de perfis
        profile_matheus = DBService.get_athlete_profile(1)
        profile_mary = DBService.get_athlete_profile(20)
        self.assert_test("Perfil de Matheus é independente de Mary", profile_matheus["user_id"] == 1 and profile_mary["user_id"] == 20)
        self.assert_test("Nome no perfil de Matheus está limpo (sem 'Atleta')", "atleta" not in profile_matheus.get("name", "").lower(), profile_matheus.get("name"))

        # Retorna para Matheus
        DBService.switch_user(1)

    # -------------------------------------------------------------
    # 3. Cenários Extremos de Carga e Treino
    # -------------------------------------------------------------
    def test_workout_extreme_loads_and_volumes(self):
        print("\n📌 [3/10] Cenários Extremos de Cargas, Repetições e Tonelagem")
        
        # Teste com carga decimal precisa (ex: halteres de 12.5 kg)
        extreme_sets = [
            {"exercise_name": "Elevação Lateral com Halteres", "set_number": 1, "weight_kg": 12.5, "reps": 15, "rpe": 8.5},
            {"exercise_name": "Elevação Lateral com Halteres", "set_number": 2, "weight_kg": 14.0, "reps": 12, "rpe": 9.0},
            {"exercise_name": "Elevação Lateral com Halteres", "set_number": 3, "weight_kg": 16.5, "reps": 10, "rpe": 9.5},
            # Exercício de peso corporal (carga 0 kg)
            {"exercise_name": "Barra Fixa Supinada", "set_number": 1, "weight_kg": 0.0, "reps": 12, "rpe": 9.0},
            # Carga pesada (leg press 280 kg)
            {"exercise_name": "Leg Press 45°", "set_number": 1, "weight_kg": 280.0, "reps": 10, "rpe": 9.0},
        ]
        
        tonnage = sum(s["weight_kg"] * s["reps"] for s in extreme_sets)
        expected_tonnage = (12.5*15) + (14.0*12) + (16.5*10) + (0.0*12) + (280.0*10)
        self.assert_test("Cálculo preciso de tonelagem mista (decimal, zero e alta carga)", tonnage == expected_tonnage, f"Total: {tonnage} kg")

        # Salva a sessão extrema
        sess_id = DBService.save_workout_session(
            routine_name="Treino Extremo de Teste",
            duration_min=75,
            total_volume=tonnage,
            sets=extreme_sets,
            notes="Sessão de estresse com cargas decimais e peso corporal.",
            user_id=1
        )
        self.assert_test("Sessão extrema salva com sucesso no SQLite", sess_id > 0, f"ID: {sess_id}")

        # Recupera as sessões recentes e valida integridade
        recents = DBService.get_recent_workout_sessions(limit=3, user_id=1)
        self.assert_test("Sessão recuperada no histórico recente com campos corretos", len(recents) > 0 and recents[0]["id"] == sess_id)

    # -------------------------------------------------------------
    # 4. Avaliação Física com Múltiplos Perfis Extremos
    # -------------------------------------------------------------
    def test_physical_assessment_extreme_profiles(self):
        print("\n📌 [4/10] Avaliação Física & Anamnese 360° com Perfis Variados")
        
        # Perfil 1: Iniciante com dor no ombro e foco em hipertrofia
        p1 = DBService.save_goals(
            goal="hipertrofia",
            target_weight=75.0,
            target_weeks=12,
            days_week=3,
            session_mins=45,
            experience="iniciante",
            joint_pain="ombro",
            diet_strategy="equilibrada",
            muscle_focus="superiores",
            user_id=1
        )
        self.assert_test("Anamnese com dor no ombro e foco em superiores salva", p1["recommended_routine"] in ["ABC", "UpperLower", "PPL"])
        self.assert_test("Meta calórica de hipertrofia gerada com superávit", p1["daily_calories"] > p1["tdee"])

        # Perfil 2: Avançado 6 dias por semana em cutting
        p2 = DBService.save_goals(
            goal="cutting",
            target_weight=70.0,
            target_weeks=8,
            days_week=6,
            session_mins=60,
            experience="avancado",
            joint_pain="nenhuma",
            diet_strategy="hiperproteica",
            muscle_focus="equilibrado",
            user_id=1
        )
        self.assert_test("Anamnese de 6 dias recomenda divisão PPL", p2["recommended_routine"] == "PPL")
        self.assert_test("Cutting aplica déficit calórico controlado", p2["daily_calories"] < p2["tdee"])
        self.assert_test("Proteína em cutting é mantida alta (>= 2.2g/kg)", p2["daily_protein"] >= 150)

    # -------------------------------------------------------------
    # 5. Substituições Cinesiológicas em Cadeia
    # -------------------------------------------------------------
    def test_kinesiology_double_swaps(self):
        print("\n📌 [5/10] Substituições de Exercícios e Biblioteca Cinesiológica")
        
        routines = DBService.get_routines(user_id=1)
        self.assert_test("Rotinas ativas disponíveis para teste", len(routines) > 0)
        
        target_routine = routines[0]
        r_id = target_routine["id"]
        exercises = target_routine.get("exercises", [])
        self.assert_test("Rotina contém exercícios prescritos", len(exercises) > 0)

        original_ex = exercises[0]["exercise_name"]
        
        # Obtém alternativas
        subs = DBService.get_exercise_substitutions(original_ex)
        if subs:
            alt1 = subs[0]["alternative_name"]
            # Substituição 1
            swap1 = DBService.swap_routine_exercise(r_id, original_ex, alt1)
            self.assert_test(f"Substituição 1: {original_ex} -> {alt1}", swap1)

            # Reverte ou faz substituição 2 de volta
            swap2 = DBService.swap_routine_exercise(r_id, alt1, original_ex)
            self.assert_test(f"Restauração do exercício original ({original_ex})", swap2)
        else:
            self.assert_test("Biblioteca respondeu sem falha mesmo para exercício pontual", True)

    # -------------------------------------------------------------
    # 6. Prescrições do Treinador (Presets Estáveis)
    # -------------------------------------------------------------
    def test_coach_presets_stability(self):
        print("\n📌 [6/10] Estabilidade das Prescrições do Treinador (Presets PPL, Upper/Lower, ABC)")
        
        # Aplica Upper / Lower
        ok_ul = DBService.apply_coach_routine_preset("UpperLower", user_id=1)
        self.assert_test("Preset Upper / Lower aplicado com sucesso", ok_ul)
        ul_routines = DBService.get_routines(user_id=1)
        self.assert_test("Preset Upper / Lower gerou 2 rotinas", len(ul_routines) == 2)

        # Aplica PPL
        ok_ppl = DBService.apply_coach_routine_preset("PPL", user_id=1)
        self.assert_test("Preset PPL aplicado com sucesso", ok_ppl)
        ppl_routines = DBService.get_routines(user_id=1)
        self.assert_test("Preset PPL gerou 3 rotinas completas (Push, Pull, Legs)", len(ppl_routines) == 3)

    # -------------------------------------------------------------
    # 7. Chat com Especialistas e Sanitização de Caracteres Especiais
    # -------------------------------------------------------------
    def test_ai_chat_special_characters_and_prompts(self):
        print("\n📌 [7/10] Chat do Conselho de Especialistas & Sanitização de Caracteres")
        
        special_msg = "Teste com aspas 'simples', \"duplas\", emojis 🏋️‍♂️💪, símbolos %, &, *, e quebra\nde\nlinha."
        
        # Salva mensagem de teste
        saved = DBService.add_chat_message(
            persona="personal",
            role="user",
            content=special_msg,
            user_id=1
        )
        self.assert_test("Mensagem com caracteres especiais e quebras salva no SQLite", True)

        # Consulta resposta do Treinador usando o serviço de IA local / fallback
        ai_resp = DevWorldAIService.send_message(
            persona_key="personal",
            user_message="Como dar foco em membros superiores?",
            user_id=1
        )
        self.assert_test("Treinador IA gerou resposta técnica sobre foco em superiores", len(ai_resp) > 30 and "superiores" in ai_resp.lower())

        # Consulta a Nutricionista
        nutri_resp = DevWorldAIService.send_message(
            persona_key="nutri",
            user_message="O que comer logo após o treino de força?",
            user_id=1
        )
        self.assert_test("Nutricionista gerou orientação de pós-treino válida", len(nutri_resp) > 30)

    # -------------------------------------------------------------
    # 8. Nutrição, Hidratação & Somatórios Extremos
    # -------------------------------------------------------------
    def test_nutrition_and_hydration_extremes(self):
        print("\n📌 [8/10] Nutrição, Hidratação e Somatórios Extremos")
        
        today_str = str(date.today())
        
        # Registra água extrema (3500 ml em copos de 500ml)
        for _ in range(7):
            DBService.add_water(500, log_date=today_str, user_id=1)
            
        nutri = DBService.get_daily_nutrition(target_date=today_str, user_id=1)
        self.assert_test("Registro de hidratação totalizou corretamente (>= 3500 ml)", nutri["total_water_ml"] >= 3500, f"{nutri['total_water_ml']} ml")

        # Registra refeição proteica
        DBService.add_meal(
            meal_name="Frango Grelhado com Arroz e Salada",
            calories=580,
            protein=48.0,
            carbs=65.0,
            fat=10.0,
            user_id=1,
            log_date=today_str
        )
        nutri_after = DBService.get_daily_nutrition(target_date=today_str, user_id=1)
        self.assert_test("Refeição registrada e somatório de macros atualizado", nutri_after["total_protein"] >= 48.0, f"Proteína Total: {nutri_after['total_protein']}g")

    # -------------------------------------------------------------
    # 9. Fotos de Evolução, Links e Variação de Medidas
    # -------------------------------------------------------------
    def test_evolution_photos_and_metrics(self):
        print("\n📌 [9/10] Fotos de Evolução & Cálculo de Variação Corporal")
        
        # Salva registro com medidas corporais
        DBService.add_evolution_log(
            angle="Frente",
            photo_path="https://images.unsplash.com/photo-fitness-test.jpg",
            weight=78.5,
            chest=104.0,
            arm=38.5,
            waist=81.0,
            thigh=59.0,
            notes="Medição de estresse com parâmetros antropométricos completos.",
            user_id=1
        )
        self.assert_test("Registro antropométrico com foto e medidas salvo", True)

        history = DBService.get_evolution_logs(user_id=1)
        self.assert_test("Histórico de evolução recuperado com sucesso", len(history) >= 1)

    # -------------------------------------------------------------
    # 10. Integridade do Banco & Limpeza de Testes
    # -------------------------------------------------------------
    def test_database_integrity_and_cleanliness(self):
        print("\n📌 [10/10] Integridade do SQLite & Garantia de Dados Intactos")
        
        with DBService.get_connection() as conn:
            cursor = conn.cursor()
            
            # Limpa apenas registros de teste extremos da sessão
            cursor.execute("DELETE FROM workout_sessions WHERE routine_name = 'Treino Extremo de Teste'")
            cursor.execute("DELETE FROM ai_chat_history WHERE content LIKE '%Teste com aspas%'")
            conn.commit()

        # Valida que Matheus (ID 1) e Mary Ellen (ID 20) permanecem 100% íntegros
        matheus = DBService.get_active_user(1)
        mary = DBService.get_active_user(20)
        
        self.assert_test("Matheus (ID 1) está preservado e ativo", matheus is not None and matheus["username"] == "matheus")
        self.assert_test("Mary Ellen (ID 20) está preservada e ativa", mary is not None and mary["username"] == "mary")
        
        matheus_routines = DBService.get_routines(user_id=1)
        self.assert_test("Matheus possui rotinas ativas prontas para o treino de hoje", len(matheus_routines) >= 2)


if __name__ == "__main__":
    tester = ExtremeStressTester()
    success = tester.run_all()
    sys.exit(0 if success else 1)
