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
        "title": "Guardião da Força & Personal Cinesiologista",
        "avatar_icon": "fitness_center",
        "color": "#FF3366", # Crimson Neon
        "system_prompt": """Você é o Treinador Márcio, Guardião da Força e Personal Trainer do app TEMPLO FITNESS AI.
Sua filosofia é a união da ciência biomecânica de ponta com a mordomia do corpo como Templo do Espírito Santo (1 Coríntios 6:19-20).
Seu tom é firme, motivador, bíblico, enérgico e focado em disciplina e domínio próprio (1 Coríntios 9:27) tanto para homens quanto para mulheres.
Seus pilares:
1. Treino com propósito: O corpo é um instrumento sagrado dado por Deus para servir a família e cumprir a vocação, não para culto à vaidade vazia.
2. Sobrecarga progressiva, cadência de repetição controlada e RPE/RIR.
3. Se o(a) atleta disser que uma máquina está ocupada ou sente dor articular, substitua imediatamente por uma variação biomecanicamente equivalente.
4. Lembre o(a) atleta: "O homem e a mulher sábios consolidam a sua força no Senhor (Provérbios 24:5)"."""
    },
    "nutri": {
        "name": "Dra. Camila",
        "title": "Nutrição da Criação & Mordomia",
        "avatar_icon": "restaurant",
        "color": "#FFB800", # Amber Gold
        "system_prompt": """Você é a Dra. Camila, Nutricionista Especialista em Composição Corporal e Mordomia Alimentar do app TEMPLO FITNESS AI.
Sua filosofia: "Quer comais, quer bebais ou façais qualquer outra coisa, fazei tudo para a glória de Deus (1 Coríntios 10:31)".
Seu tom é acolhedor, científico, prático e focado no domínio próprio contra a compulsão e o desleixo.
Seus pilares:
1. Nutrição com comida de verdade, alimentos naturais da criação divina e distribuição equilibrada de macros (Proteínas, Carboidratos e Gorduras).
2. Hidratação abundante e timing de refeições para manter o templo energizado e saudável.
3. Uso seguro e consciente de suplementos (Creatina, Whey, Minerais).
Ajude o(a) atleta a nutrir seu templo para ter vitalidade diária."""
    },
    "mente": {
        "name": "Dr. Gabriel",
        "title": "Mente, Disciplina & Fé",
        "avatar_icon": "psychology",
        "color": "#9D4EDD", # Purple Mind
        "system_prompt": """Você é o Dr. Gabriel, Mentor de Mindset Cristão, Foco e Disciplina do app TEMPLO FITNESS AI.
Sua missão é combater a preguiça, a procrastinação e a ansiedade através da renovação da mente (Romanos 12:2).
Seus pilares:
1. Quebra da autosabotagem: O corpo deve obedecer ao espírito fortalecido em Deus.
2. Paz e serenidade: Aplicar Filipenses 4:6-7 e respiração diafragmática para entrar no treino focado e calmo.
3. Constância como fruto espiritual: O resultado vem da fidelidade no pouco dia após dia.
Inspire o(a) atleta a levantar com a coragem dos justos e a perseverança da fé."""
    },
    "fisio": {
        "name": "Dr. Rafael",
        "title": "Restauração do Templo & Biomecânica",
        "avatar_icon": "healing",
        "color": "#06D6A0", # Teal Physio
        "system_prompt": """Você é o Dr. Rafael, Fisioterapeuta e Guardião Articular do Templo no app TEMPLO FITNESS AI.
Sua missão é a preservação e longevidade física do atleta para que desfrute de saúde e vigor por décadas (Josué 14:11 / 3 João 1:2).
Seus pilares:
1. Mobilidade articular e postura para agachamentos, supinos e movimentos do dia a dia.
2. Proteção de joelhos, manguito rotador e coluna.
3. Alívio de dores, descompressão e recuperação muscular pós-treino.
Ensine o(a) atleta a treinar com sabedoria sem sobrecarregar as articulações."""
    }
}

class DevWorldAIService:
    @classmethod
    def get_athlete_context(cls, user_id: Optional[int] = None) -> str:
        """Gera um resumo do prontuário do atleta para alimentar a IA."""
        target_uid = user_id or DBService.get_active_user_id()
        profile = DBService.get_athlete_profile(user_id=target_uid)
        nutrition = DBService.get_daily_nutrition(user_id=target_uid)
        wellness = DBService.get_today_wellness(user_id=target_uid)
        
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
    def send_message(cls, persona_key: str, user_message: str, user_id: Optional[int] = None) -> str:
        """Envia mensagem para a API DevWorld ou retorna resposta inteligente com base no contexto."""
        if persona_key not in PERSONA_CONFIGS:
            persona_key = "personal"

        target_uid = user_id or DBService.get_active_user_id()
        persona_info = PERSONA_CONFIGS[persona_key]
        profile = DBService.get_athlete_profile(user_id=target_uid)
        
        # Salva mensagem do usuário no banco
        DBService.add_chat_message(persona_key, "user", user_message, user_id=target_uid)

        # Prepara contexto e histórico
        context_prompt = cls.get_athlete_context(user_id=target_uid)
        history = DBService.get_chat_history(persona_key, limit=10, user_id=target_uid)
        
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
                    DBService.add_chat_message(persona_key, "assistant", bot_text, user_id=target_uid)
                    return bot_text
                else:
                    print(f"[DevWorld API Error]: Status {response.status_code} - {response.text}")
            except Exception as err:
                print(f"[DevWorld Connection Exception]: {err}")

        # Resposta de Motor Especialista Integrado (Fallback Inteligente)
        fallback_reply = cls._generate_smart_fallback(persona_key, user_message, profile, wellness=DBService.get_today_wellness(user_id=target_uid))
        DBService.add_chat_message(persona_key, "assistant", fallback_reply, user_id=target_uid)
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
                    f"Fala guerreiro {name}! 'O homem sábio é forte e consolida a sua força (Provérbios 24:5)'.\n"
                    "Se a máquina está ocupada, não perca o fogo nem o aquecimento muscular!\n\n"
                    "🔄 **Substituições Cinesiológicas dos Valentes:**\n"
                    "• **Se for Cadeira Extensora:** Faça **Agachamento Búlgaro** com halteres ou **Sissy Squat** no solo.\n"
                    "• **Se for Puxada no Pulley:** Faça **Barra Fixa com elástico** ou **Remada Unilateral com Halter**.\n"
                    "• **Se for Supino Reto:** Faça **Supino com Halteres** mantendo rotação neutra ou **Flexão de Braço no Solo**.\n\n"
                    "Domine o seu corpo com 3 a 4 séries firmes (1 Coríntios 9:27)!"
                )
            elif "dor" in msg_lower or "ombro" in msg_lower or "joelho" in msg_lower:
                return (
                    f"Atenção {name}! Seu corpo é o Templo do Espírito Santo (1 Coríntios 6:19-20); cuide dele com sabedoria.\n\n"
                    "⚠️ **Ajuste Preventivo Imediato:**\n"
                    "1. Reduza a amplitude para a zona livre de desconforto.\n"
                    "2. Troque barras rígidas por halteres com pegada neutra para preservar os tendões.\n"
                    "3. Chame o Dr. Rafael (Fisioterapeuta) para calibrar sua mobilidade antes de voltar às cargas pesadas!"
                )
            else:
                return (
                    f"Fala guerreiro {name}! Vamos com vigor para o objetivo de **{goal.upper()}**!\n\n"
                    "⚔️ **Diretriz de Hoje:**\n"
                    "• 'Tudo posso naquele que me fortalece (Filipenses 4:13)'. Não treine por vaidade passageira, mas para ser forte e pronto para toda boa obra.\n"
                    "• Controle a fase excêntrica da repetição (2 a 3 segundos de descida controlada).\n"
                    "• Registre suas séries e cargas na aba de **Treino** com disciplina inegociável!\n\n"
                    "Qual exercício você está executando agora ou precisa de substituição?"
                )

        elif persona == "nutri":
            if "pos treino" in msg_lower or "pós" in msg_lower:
                return (
                    f"Excelente pergunta, {name}! Como diz a Palavra: 'Quer comais, quer bebais ou façais qualquer outra coisa, fazei tudo para a glória de Deus (1 Coríntios 10:31)'.\n\n"
                    "🥗 **Sugestão de Pós-Treino Rápido & Nutritivo:**\n"
                    "• **Opção Líquida:** 30g de Whey Protein + 1 banana madura + 30g de aveia batida com água + 5g de Creatina.\n"
                    "• **Opção Refeição Sólida da Criação:** 150g de peito de frango grelhado ou ovos cozidos + 180g de arroz branco ou batata inglesa + legumes da terra.\n\n"
                    "Honre seu templo mantendo também a meta diária de água!"
                )
            elif "pre treino" in msg_lower or "pré" in msg_lower:
                return (
                    f"Para chegar com máxima energia e foco no templo, {name}:\n\n"
                    "⚡ **Refeição Pré-Treino (60 a 90 min antes):**\n"
                    "• Carboidratos limpos e energéticos (banana com aveia e canela, pão integral com ovos ou tapioca).\n"
                    "• Boa hidratação prévia (pelo menos 500ml de água antes de começar).\n"
                    "• Evite gorduras pesadas e excesso de ultraprocessados logo antes do treino."
                )
            else:
                return (
                    f"Olá {name}! A alimentação é um dos maiores pilares da mordomia do seu corpo.\n\n"
                    f"Para você que pesa {profile.get('weight_kg')}kg com foco em {goal.upper()}:\n"
                    f"• Meta de Proteína: ~{round(float(profile.get('weight_kg', 75))*2.2, 0)}g por dia.\n"
                    f"• Meta de Hidratação: ~{int(float(profile.get('weight_kg', 75))*40)}ml de água por dia.\n\n"
                    "Alimente seu corpo com respeito à criação divina e fuja da gula e do desleixo!"
                )

        elif persona == "mente":
            return (
                f"Olá guerreiro {name}! Como está seu espírito e sua mente hoje?\n\n"
                "🛡️ **Meditação de Fé & Foco:**\n"
                "A Bíblia diz: 'Não te mandei eu? Sê forte e corajoso; não temas, nem te espantes, porque o Senhor teu Deus é contigo por onde quer que andares (Josué 1:9)'.\n\n"
                "A preguiça e o desânimo são armadilhas da carne. Quando faltar motivação, acione o **domínio próprio** (Gálatas 5:23). Faça uma oração rápida de 1 minuto e consagre seu treino a Deus!\n\n"
                "Precisa de foco para a sessão de hoje?"
            )

        else: # fisio
            return (
                f"Olá {name}! Lembre-se sempre: 'O corpo de vocês é o santuário do Espírito Santo (1 Coríntios 6:19)'.\n\n"
                "🦴 **Checklist do Guardião do Templo:**\n"
                "1. Faça aquecimento com rotação externa leve de ombros antes de treinar peito/ombro.\n"
                "2. Mantenha os tornozelos móveis antes de agachar para preservar o joelho e a coluna.\n"
                "3. Treine com cadência inteligente: quem destrói as articulações por ego para de treinar cedo; quem cuida da biomecânica treina forte até a velhice como Calebe (Josué 14:11).\n\n"
                "Está sentindo algum ponto de dor ou desconforto hoje?"
            )
