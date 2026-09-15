"""
Cálculos e Fórmulas de Ciências do Esporte & Fisiologia do Exercício.
"""
from typing import Dict, Tuple

class HealthMath:
    @staticmethod
    def calculate_1rm_epley(weight: float, reps: int) -> float:
        """Fórmula de Epley para estimativa de 1RM (Repetição Máxima)."""
        if reps <= 1:
            return round(weight, 1)
        return round(weight * (1 + (reps / 30.0)), 1)
    
    @staticmethod
    def calculate_1rm_brzycki(weight: float, reps: int) -> float:
        """Fórmula de Brzycki para estimativa de 1RM."""
        if reps <= 1:
            return round(weight, 1)
        if reps >= 37:
            return round(weight * 1.5, 1)
        return round(weight / (1.0278 - (0.0278 * reps)), 1)

    @staticmethod
    def calculate_tmb_mifflin(weight_kg: float, height_cm: float, age: int, sex: str = "M") -> float:
        """Taxa Metabólica Basal (Fórmula de Mifflin-St Jeor)."""
        # Homens: 10*peso + 6.25*altura - 5*idade + 5
        # Mulheres: 10*peso + 6.25*altura - 5*idade - 161
        base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
        if sex.upper() == "M":
            return round(base + 5, 0)
        else:
            return round(base - 161, 0)

    @staticmethod
    def calculate_tdee(tmb: float, activity_level: str = "moderado") -> float:
        """Gasto Energético Total Diário (TDEE)."""
        factors = {
            "sedentario": 1.2,
            "leve": 1.375,
            "moderado": 1.55,
            "intenso": 1.725,
            "muito_intenso": 1.9,
        }
        factor = factors.get(activity_level.lower(), 1.55)
        return round(tmb * factor, 0)

    @staticmethod
    def calculate_macros_target(tdee: float, goal: str = "hipertrofia", weight_kg: float = 75.0) -> Dict[str, float]:
        """Calcula calorias alvo e distribuição de macronutrientes em gramas."""
        goal = goal.lower()
        if goal == "hipertrofia":
            target_kcal = tdee + 350
            protein_g = round(weight_kg * 2.2, 0) # 2.2g/kg
            fat_g = round(weight_kg * 0.9, 0)     # 0.9g/kg
        elif goal == "cutting":
            target_kcal = tdee - 500
            protein_g = round(weight_kg * 2.4, 0) # 2.4g/kg para preservar massa
            fat_g = round(weight_kg * 0.7, 0)     # 0.7g/kg
        else: # manutencao
            target_kcal = tdee
            protein_g = round(weight_kg * 2.0, 0)
            fat_g = round(weight_kg * 0.8, 0)

        # Calorias restantes viram carboidratos (1g prot = 4kcal, 1g fat = 9kcal, 1g carb = 4kcal)
        kcal_from_prot = protein_g * 4
        kcal_from_fat = fat_g * 9
        remaining_kcal = max(target_kcal - (kcal_from_prot + kcal_from_fat), 400)
        carbs_g = round(remaining_kcal / 4.0, 0)

        return {
            "target_calories": round(target_kcal, 0),
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "water_ml": round(weight_kg * 40, 0), # 40ml por kg para praticantes de musculação
        }

    @staticmethod
    def heart_rate_zones(age: int, resting_hr: int = 60) -> Dict[str, Tuple[int, int]]:
        """Calcula zonas de treino cardíaco pela fórmula de Karvonen."""
        max_hr = 220 - age
        hr_reserve = max_hr - resting_hr
        
        return {
            "Zona 1 (Recuperação Ativa 50-60%)": (
                int(resting_hr + (hr_reserve * 0.50)),
                int(resting_hr + (hr_reserve * 0.60)),
            ),
            "Zona 2 (Queima de Gordura / Base 60-70%)": (
                int(resting_hr + (hr_reserve * 0.60)),
                int(resting_hr + (hr_reserve * 0.70)),
            ),
            "Zona 3 (Aeróbico / Fôlego 70-80%)": (
                int(resting_hr + (hr_reserve * 0.70)),
                int(resting_hr + (hr_reserve * 0.80)),
            ),
            "Zona 4 (Limiar Anaeróbico 80-90%)": (
                int(resting_hr + (hr_reserve * 0.80)),
                int(resting_hr + (hr_reserve * 0.90)),
            ),
            "Zona 5 (Esforço Máximo / VO2 Max 90-100%)": (
                int(resting_hr + (hr_reserve * 0.90)),
                int(max_hr),
            ),
        }
