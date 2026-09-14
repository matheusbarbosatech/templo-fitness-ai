"""
Serviço de Inteligência Artificial Multidisciplinar conectado à API DevWorld.
Gerencia 4 Personas Especializadas nas Ciências do Esporte com injeção de Prontuário em Tempo Real.
"""
import os
import json
import requests
from typing import Dict, Any, List, Optional
from core.config import AppConfig
from services.db_service import DBService

PERSONA_CONFIGS = {
    "personal": {
        "name": "Treinador Márcio",
        "title": "Personal Trainer & Cinesiologista",
        "avatar_icon": "fitness_center",
        "color": "#FF3366", # Crimson Neon
        "system_prompt": """Você é o Treinador Márcio, um Personal Trainer de elite e especialista em Cinesiologia, Biomecânica e Hipertrofia/Força do app Apollo Fitness AI.
Seu tom é motivador, enérgico, técnico e direto ao ponto.
Seus pilares:
1. Sobrecarga progressiva, cadência de repetição (ex: 2s excêntrica, 1s concêntrica) e RPE/RIR (repetições na reserva).
2. Se o atleta disser que uma máquina está ocupada ou que sente dor, substitua imediatamente por uma variação biomecanicamente equivalente.
3. Use o contexto do atleta (peso, objetivo, sono e dores) para dar respostas precisas.
Responda de forma clara e visual com listas, tópicos e dicas de pegada/postura."""
    },
    "nutri": {
        "name": "Dra. Camila",
        "title": "Nutricionista Esportiva & Suplementação",
        "avatar_icon": "restaurant",
        "color": "#FFB800", # Amber Gold
        "system_prompt": """Você é a Dra. Camila, Nutricionista Esportiva especializada em timing de nutrientes, composição corporal (hipertrofia e cutting) e suplementação de alta performance no app Apollo Fitness AI.
Seu tom é científico, prático, acolhedor e focado em adesão sustentável.
Seus pilares:
1. Cálculo e distribuição de macronutrientes (Proteínas, Carboidratos, Gorduras e Hidratação).
2. Timing de refeições pré e pós-treino para síntese proteica e glicogênio muscular.
3. Uso seguro de suplementos comprovados (Creatina, Whey, Cafeína, Beta-Alanina, Eletrólitos).
Sugira ideias práticas de refeições rápidas e saborosas adaptadas ao objetivo do atleta."""
    },
    "mente": {
        "name": "Dr. Gabriel",
        "title": "Psicólogo do Esporte & Mindset",
        "avatar_icon": "psychology",
        "color": "#9D4EDD", # Purple Mind
        "system_prompt": """Você é o Dr. Gabriel, Psicólogo do Esporte e Neurocientista focado em disciplina, foco e conexão mente-músculo no app Apollo Fitness AI.
Seu tom é empático, inspirador, focado em alta performance e superação de limites.
Seus pilares:
1. Quebra de autosabotagem, preguiça e construção de hábitos inegociáveis.
2. Foco durante a série pesada e visualização do movimento.
3. Manejo de estresse, ansiedade pré-treino e autocuidado mental.
4. Uso de respiração diafragmática para regulação do sistema nervoso autônomo."""
    },
    "fisio": {
        "name": "Dr. Rafael",
        "title": "Fisioterapeuta Esportivo & Biomecânica",
        "avatar_icon": "healing",
        "color": "#06D6A0", # Teal Physio
        "system_prompt": """Você é o Dr. Rafael, Fisioterapeuta Esportivo especializado em prevenção de lesões, mobilidade articular e recovery no app Apollo Fitness AI.
Seu tom é técnico, cuidadoso, explicativo e focado em longevidade articular.
Seus pilares:
1. Mobilidade de tornozelos, quadril e coluna torácica para agachamentos e supinos seguros.
2. Estabilidade do manguito rotador e joelhos.
3. Protocolos de alívio para dores lombares, tendinites e contraturas.
4. Liberação miofascial e recuperação pós-treino."""
    }
}

class DevWorldAIService:
    @classmethod
    def get_athlete_context(cls) -> str:
        """Gera um resumo do prontuário do atleta para alimentar a IA."""
        profile = DBService.get_athlete_profile()
        nutrition = DBService.get_daily_nutrition()
        wellness = DBService.get_today_wellness()
        
        context = f"""
[PRONTUÁRIO ATUAL DO ATLETA]:
- Nome: {profile.get('name', 'Atleta')} | Idade: {profile.get('age', 26)} anos | Sexo: {profile.get('sex', 'M')}
- Peso Atual: {profile.get('weight_kg', 78.5)}kg | Altura: {profile.get('height_cm', 178)}cm
- Objetivo: {profile.get('goal', 'Hipertrofia').upper()} | Nível de Atividade: {profile.get('activity_level', 'Intenso')}
- Nutrição Hoje: {int(nutrition.get('total_calories', 0))} kcal ingeridas | {int(nutrition.get('total_protein', 0))}g Proteína | {int(nutrition.get('total_water_ml', 0))}ml Água
- Estado do Dia: Humor ({wellness.get('mood_score', 4)}/5) | Sono ({wellness.get('sleep_hours', 7.5)}h) | Nível de Estresse ({wellness.get('stress_score', 2)}/5)
- Notas de Dor / Físico: {wellness.get('soreness_notes', 'Nenhuma dor reportada')}
"""
        return context

    @classmethod
    def send_message(cls, persona_key: str, user_message: str) -> str:
        """Envia mensagem para a API DevWorld ou retorna resposta inteligente com base no contexto."""
        if persona_key not in PERSONA_CONFIGS:
            persona_key = "personal"

        persona_info = PERSONA_CONFIGS[persona_key]
        profile = DBService.get_athlete_profile()
        
        # Salva mensagem do usuário no banco
        DBService.add_chat_message(persona_key, "user", user_message)

        # Prepara contexto e histórico
        context_prompt = cls.get_athlete_context()
        history = DBService.get_chat_history(persona_key, limit=10)
        
        system_content = f"{persona_info['system_prompt']}\n\n{context_prompt}"
        
        messages = [{"role": "system", "content": system_content}]
        for h in history:
            messages.append({"role": h["role"], "content": h["content"]})

        api_key = profile.get("devworld_api_key") or AppConfig.DEVWORLD_API_KEY_ENV
        base_url = profile.get("devworld_base_url") or AppConfig.DEVWORLD_BASE_URL

        # Tentativa de chamada real à API DevWorld / OpenAI Compatible
        if api_key and api_key.strip():
            try:
                endpoint = f"{base_url.rstrip('/')}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key.strip()}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": AppConfig.DEFAULT_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 800
                }
                response = requests.post(endpoint, json=payload, headers=headers, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    bot_text = data["choices"][0]["message"]["content"]
                    DBService.add_chat_message(persona_key, "assistant", bot_text)
                    return bot_text
                else:
                    print(f"[DevWorld API Error]: Status {response.status_code} - {response.text}")
            except Exception as err:
                print(f"[DevWorld Connection Exception]: {err}")

        # Resposta de Motor Especialista Integrado (Fallback Inteligente)
        fallback_reply = cls._generate_smart_fallback(persona_key, user_message, profile, wellness=DBService.get_today_wellness())
        DBService.add_chat_message(persona_key, "assistant", fallback_reply)
        return fallback_reply

    @classmethod
    def _generate_smart_fallback(cls, persona: str, msg: str, profile: Dict[str, Any], wellness: Dict[str, Any]) -> str:
        """Gera respostas especializadas instantâneas de alta qualidade enquanto a chave de API não é inserida."""
        msg_lower = msg.lower()
        name = profile.get("name", "Atleta")
        goal = profile.get("goal", "hipertrofia")

        if persona == "personal":
            if "ocupada" in msg_lower or "trocar" in msg_lower or "substituir" in msg_lower:
                return (
                    f"Fala {name}! Se a máquina está ocupada, não perca o aquecimento muscular nem a intensidade!\n\n"
                    "🔄 **Substituições Imediatas de Alta Eficiência:**\n"
                    "• **Se for Cadeira Extensora:** Faça **Agachamento Búlgaro** com halteres ou **Sissy Squat** no solo.\n"
                    "• **Se for Puxada no Pulley:** Faça **Barra Fixa com elástico** ou **Puxada com Halteres unilateral**.\n"
                    "• **Se for Supino Reto:** Faça **Supino com Halteres** mantendo rotação neutra ou **Flexão de Braço com pés elevados**.\n\n"
                    "Mantenha 3 a 4 séries buscando 1 a 2 repetições antes da falha total (RPE 8-9)!"
                )
            elif "dor" in msg_lower or "ombro" in msg_lower or "joelho" in msg_lower:
                return (
                    f"Atenção {name}! Se estiver sentindo fisgadas ou desconforto articular, pare a carga imediatamente.\n\n"
                    "⚠️ **Ajuste de Segurança:**\n"
                    "1. Reduza a amplitude para a zona livre de dor.\n"
                    "2. Troque barras retas por halteres com pegada semi-neutra (alivia o impacto no manguito rotador).\n"
                    "3. Chame o Dr. Rafael (Fisioterapeuta) na aba ao lado para fazer 2 exercícios rápidos de mobilidade antes de continuar!"
                )
            else:
                return (
                    f"Fala {name}! Vamos com tudo para o objetivo de **{goal.upper()}**!\n\n"
                    "🔥 **Diretriz de Hoje:**\n"
                    "• Foque na **fase excêntrica** do movimento (desça o peso em 2 a 3 segundos controlados).\n"
                    "• Não esqueça de registrar cada série na aba de **Treino** para garantir que você está progredindo cargas semana a semana.\n\n"
                    "Qual exercício você está fazendo agora ou precisa de ajuste?"
                )

        elif persona == "nutri":
            if "pos treino" in msg_lower or "pós" in msg_lower:
                return (
                    f"Excelente pergunta, {name}! Para o seu objetivo de **{goal.upper()}**, a janela pós-treino é crucial para síntese proteica e reposição de glicogênio.\n\n"
                    "🥗 **Sugestão de Pós-Treino Rápido:**\n"
                    "• **Opção Líquida Rápida:** 30g de Whey Protein + 1 banana média batida com 30g de aveia + 5g de Creatina.\n"
                    "• **Opção Refeição Sólida:** 150g de peito de frango grelhado ou patinho moído + 180g de arroz branco ou batata inglesa + vegetais verdes escuros.\n\n"
                    "Não esqueça de manter a meta de água do dia que calculamos para você!"
                )
            elif "pre treino" in msg_lower or "pré" in msg_lower:
                return (
                    f"Para chegar com máxima energia no treino, {name}:\n\n"
                    "⚡ **Refeição Pré-Treino (60 a 90 min antes):**\n"
                    "• Carboidratos de fácil digestão (arroz, pão integral com geleia, banana com aveia ou tapioca).\n"
                    "• Uma porção moderada de proteína (ovos mexidos ou whey).\n"
                    "• Evite excesso de gorduras e fibras pesadas logo antes para não causar peso gástrico."
                )
            else:
                return (
                    f"Olá {name}! A alimentação é 70% do seu resultado estético e de força.\n\n"
                    f"Para você que pesa {profile.get('weight_kg')}kg com foco em {goal.upper()}:\n"
                    f"• Meta de Proteína: ~{round(float(profile.get('weight_kg', 75))*2.2, 0)}g por dia.\n"
                    f"• Meta de Água: ~{int(float(profile.get('weight_kg', 75))*40)}ml por dia.\n\n"
                    "Gostaria de calcular os macros de alguma receita específica ou tirar dúvidas sobre suplementos?"
                )

        elif persona == "mente":
            return (
                f"Olá {name}! Como está seu diálogo interno hoje?\n\n"
                "🧠 **Pílula de Mindset do Atleta:**\n"
                "A motivação te faz começar, mas apenas a **disciplina e a constância** te levam ao físico e à saúde que você deseja.\n"
                "Mesmo nos dias em que a energia parecer baixa, lembre-se: um treino 'nota 6' feito é infinitamente melhor do que um treino perfeito que não saiu do papel.\n\n"
                "Se estiver sentindo ansiedade ou agitação, recomendo fazer 2 minutos de **Box Breathing (4-4-4-4)** na aba de Saúde Mental antes de entrar na academia!"
            )

        else: # fisio
            return (
                f"Olá {name}! Cuidar das articulações e da postura é o que garante que você continue treinando forte por anos sem lesão.\n\n"
                "🦴 **Checklist Preventivo de Hoje:**\n"
                "1. Faça rotação externa de ombros com elástico leve antes de treinar peito/ombro.\n"
                "2. Mantenha os tornozelos móveis com alongamento de panturrilha na parede antes do agachamento.\n"
                "3. Ao trabalhar sentado no computador, faça pausas a cada 50 min para descompressão lombar.\n\n"
                "Está sentindo algum incômodo específico em alguma articulação ou músculo hoje?"
            )
