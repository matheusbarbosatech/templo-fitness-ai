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
        "name": "Treinador",
        "title": "Guardião da Força & Personal Cinesiologista",
        "avatar_icon": "fitness_center",
        "color": "#FFFFFF", # Branco Puro Minimalista
        "system_prompt": """Você é o Treinador, Personal Trainer e Especialista em Cinesiologia do app TEMPLO FITNESS AI.
Sua filosofia é a união da ciência biomecânica de ponta com a mordomia do corpo como Templo do Espírito Santo (1 Coríntios 6:19-20).
Seu tom é firme, motivador, bíblico, enérgico e focado em disciplina e domínio próprio (1 Coríntios 9:27) tanto para homens quanto para mulheres.
Seus pilares:
1. Treino com propósito: O corpo é um instrumento sagrado dado por Deus para servir a família e cumprir a vocação, não para culto à vaidade vazia.
2. Sobrecarga progressiva, cadência de repetição controlada e RPE/RIR.
3. Se o(a) usuário(a) disser que uma máquina está ocupada ou sente dor articular, substitua imediatamente por uma variação biomecanicamente equivalente.
4. Lembre o(a) usuário(a): "O homem e a mulher sábios consolidam a sua força no Senhor (Provérbios 24:5)"."""
    },
    "nutri": {
        "name": "Nutricionista",
        "title": "Nutrição da Criação & Mordomia",
        "avatar_icon": "restaurant",
        "color": "#FFFFFF", # Branco Puro Minimalista
        "system_prompt": """Você é a Nutricionista Especialista em Composição Corporal e Alimentação do app TEMPLO FITNESS AI.
Sua filosofia: "Quer comais, quer bebais ou façais qualquer outra coisa, fazei tudo para a glória de Deus (1 Coríntios 10:31)".
Seu tom é acolhedor, científico, prático e focado no domínio próprio contra a compulsão e o desleixo.
Seus pilares:
1. Nutrição com comida de verdade, alimentos naturais da criação divina e distribuição equilibrada de macros (Proteínas, Carboidratos e Gorduras).
2. Hidratação abundante e timing de refeições para manter o templo energizado e saudável.
3. Uso seguro e consciente de suplementos (Creatina, Whey, Minerais).
Ajude o(a) usuário(a) a nutrir seu templo para ter vitalidade diária."""
    },
    "mente": {
        "name": "Dr. Gabriel",
        "title": "Mente, Disciplina & Fé",
        "avatar_icon": "psychology",
        "color": "#FFFFFF", # Branco Puro Minimalista
        "system_prompt": """Você é o Dr. Gabriel, Mentor de Mindset Cristão, Foco e Disciplina do app TEMPLO FITNESS AI.
Sua missão é combater a preguiça, a procrastinação e a ansiedade através da renovação da mente (Romanos 12:2).
Seus pilares:
1. Quebra da autosabotagem: O corpo deve obedecer ao espírito fortalecido em Deus.
2. Paz e serenidade: Aplicar Filipenses 4:6-7 e respiração diafragmática para entrar no treino focado e calmo.
3. Constância como fruto espiritual: O resultado vem da fidelidade no pouco dia após dia.
Inspire o(a) usuário(a) a levantar com a coragem dos justos e a perseverança da fé."""
    },
    "fisio": {
        "name": "Dr. Rafael",
        "title": "Restauração do Templo & Biomecânica",
        "avatar_icon": "healing",
        "color": "#FFFFFF", # Branco Puro Minimalista
        "system_prompt": """Você é o Dr. Rafael, Fisioterapeuta e Guardião Articular do Templo no app TEMPLO FITNESS AI.
Sua missão é a preservação e longevidade física do usuário para que desfrute de saúde e vigor por décadas (Josué 14:11 / 3 João 1:2).
Seus pilares:
1. Mobilidade articular e postura para agachamentos, supinos e movimentos do dia a dia.
2. Proteção de joelhos, manguito rotador e coluna.
3. Alívio de dores, descompressão e recuperação muscular pós-treino.
Ensine o(a) usuário(a) a treinar com sabedoria sem sobrecarregar as articulações."""
    }
}

class DevWorldAIService:
    @classmethod
    def get_athlete_context(cls, user_id: Optional[int] = None) -> str:
        """Gera um resumo dos dados do usuário para alimentar a IA."""
        target_uid = user_id or DBService.get_active_user_id()
        profile = DBService.get_athlete_profile(user_id=target_uid)
        nutrition = DBService.get_daily_nutrition(user_id=target_uid)
        wellness = DBService.get_today_wellness(user_id=target_uid)
        
        context = f"""
[DADOS ATUAIS DO USUÁRIO]:
- Nome: {profile.get('name', 'Usuário')} | Idade: {profile.get('age', 26)} anos | Sexo: {profile.get('sex', 'M')}
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

        # Tentativa de chamada real à API DevWorld
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
                    "max_tokens": 850
                }
                response = requests.post(endpoint, json=payload, headers=headers, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    bot_text = data["choices"][0]["message"]["content"]
                    DBService.add_chat_message(persona_key, "assistant", bot_text, user_id=target_uid)
                    return bot_text
                elif response.status_code == 401:
                    print(f"[DevWorld API 401]: Chave inválida ou expirada.")
                    fallback_reply = (
                        "⚠️ **Aviso de Conexão DevWorld:** Sua chave de API não foi autorizada (erro 401). "
                        "Por favor, clique no botão de configurações (⚙️) no topo para atualizar sua chave da DevWorld.\n\n"
                        + cls._generate_smart_fallback(persona_key, user_message, profile, wellness=DBService.get_today_wellness(user_id=target_uid))
                    )
                    DBService.add_chat_message(persona_key, "assistant", fallback_reply, user_id=target_uid)
                    return fallback_reply
                else:
                    print(f"[DevWorld API Error]: Status {response.status_code} - {response.text}")
            except Exception as err:
                print(f"[DevWorld Connection Exception]: {err}")

        # Resposta do Motor Cinesiológico Inteligente (Sem repetições estáticas)
        fallback_reply = cls._generate_smart_fallback(persona_key, user_message, profile, wellness=DBService.get_today_wellness(user_id=target_uid))
        DBService.add_chat_message(persona_key, "assistant", fallback_reply, user_id=target_uid)
        return fallback_reply

    @classmethod
    def _generate_smart_fallback(cls, persona: str, msg: str, profile: Dict[str, Any], wellness: Dict[str, Any]) -> str:
        """Gera respostas especializadas instantâneas de alta qualidade com ampla cobertura contextual sem repetições."""
        msg_lower = msg.lower().strip()
        name = profile.get("name", "Guerreiro").split()[0]
        goal = (profile.get("goal") or "hipertrofia").lower()
        weight = float(profile.get("weight_kg") or 78.5)
        routine = profile.get("recommended_routine") or "PPL"
        days_week = profile.get("training_days_week") or 5

        # =========================================================================
        # 1. PERSONA: PERSONAL TRAINER / TREINADOR
        # =========================================================================
        if persona == "personal":
            # REFAZER AVALIAÇÃO / METAS / ANAMNESE
            if any(w in msg_lower for w in ["avaliação", "avaliacao", "refazer", "anamnese", "metas", "recalibrar", "mudar objetivo"]):
                return (
                    f"Fala {name}! Você pode **refazer sua Avaliação Física & Anamnese 360°** a qualquer momento!\n\n"
                    "📋 **Como refazer agora mesmo:**\n"
                    "1. Clique no botão **📋 (ícone de prancheta)** localizado no topo desta tela (ao lado do nome) ou na barra superior do app.\n"
                    "2. Atualize seus dados: Peso Alvo, Prazo, Frequência Semanal (atualmente {days_week} dias) e Foco Muscular.\n"
                    "3. Clique em **'Calibrar Meu Treino & Metas'**.\n\n"
                    "⚡ A IA do Templo recalcula na hora seu TMB, TDEE, divisão recomendada (ex: {routine}) e aplica a ficha direto no seu Treino do Dia!"
                )

            # SAUDAÇÃO / INÍCIO DE CONVERSA
            elif any(msg_lower.startswith(w) for w in ["ola", "olá", "oi", "bom dia", "boa tarde", "boa noite", "e ai", "e aí", "opa", "salve", "fala"]):
                return (
                    f"Fala {name}! Paz e vigor! Pronto para honrar o Templo hoje com foco em **{goal.upper()}**?\n\n"
                    f"Estou com sua periodização ativa ({routine} - {days_week}x na semana) e peso atual de {weight}kg na tela.\n\n"
                    "Em que posso te orientar agora?\n"
                    "• Dúvidas de execução de exercícios (supino, agachamento, terra...)\n"
                    "• Ajuste de séries, repetições, cargas ou descanso\n"
                    "• Substituição de máquina ocupada na academia\n"
                    "• Refazer sua avaliação física ou mudar o foco muscular"
                )

            # CONFIGURAR API / CHAVE DEVWORLD
            elif any(w in msg_lower for w in ["chave", "api", "devworld", "conectar", "configurar", "token"]):
                return (
                    f"Para ativar o modelo de linguagem em tempo real da **DevWorld**:\n\n"
                    "🔑 **Passo a passo rápido:**\n"
                    "1. Clique no botão de engrenagem **(⚙️)** na barra superior do app ou no cabeçalho aqui do chat.\n"
                    "2. Cole sua chave de API DevWorld no campo correspondente.\n"
                    "3. Clique em **'Testar Conexão'** para validar e depois em **'Salvar'**.\n\n"
                    "Enquanto isso, eu continuo te prestando consultoria completa com base nos seus dados salvos!"
                )

            # SUBSTITUIÇÃO DE EXERCÍCIOS / MÁQUINA OCUPADA
            elif any(w in msg_lower for w in ["ocupada", "ocupado", "trocar", "substituir", "alternativa", "lotada", "lotado"]):
                return (
                    f"Sem perder o aquecimento, {name}! 'O homem prudente constrói a sua força (Provérbios 24:5)'.\n\n"
                    "🔄 **Substituições Biomecânicas Rápidas:**\n"
                    "• **Se for Cadeira Extensora:** Faça **Agachamento Búlgaro** com halteres ou **Passada com Halteres**.\n"
                    "• **Se for Puxador / Pulley:** Faça **Barra Fixa (com elástico se necessário)** ou **Remada Curvada com Barra**.\n"
                    "• **Se for Supino Reto:** Faça **Supino Reto com Halteres** ou **Flexões com carga no solo**.\n"
                    "• **Se for Leg Press:** Faça **Agachamento Goblet** pesado ou **Agachamento no Hack**.\n"
                    "• **Se for Elevação Lateral na Máquina:** Use **Halteres** no plano escapular (30° à frente).\n\n"
                    "Qual máquina específica está ocupada agora para eu te passar a substituição exata?"
                )

            # DORES / LESÕES / PREVENÇÃO
            elif any(w in msg_lower for w in ["dor", "ombro", "joelho", "lombar", "cotovelo", "lesão", "lesao", "machucou", "estalo"]):
                return (
                    f"Atenção total, {name}! Seu corpo é o Templo do Espírito Santo (1 Coríntios 6:19); treinar com dor lesiva é negligência, não bravura.\n\n"
                    "🛡️ **Protocolo Imediato de Segurança Articular:**\n"
                    "1. **Interrompa a carga no ângulo da dor:** Reduza a amplitude até a zona confortável e segura.\n"
                    "2. **Ombro no Supino:** Reduza a abdução dos cotovelos (mantenha em 45° a 60° em relação ao tronco) e use pegada neutra com halteres.\n"
                    "3. **Joelho no Agachamento:** Garanta que os joelhos apontem na mesma direção da ponta dos pés e não faça valgo dinâmico (joelho caindo para dentro).\n"
                    "4. **Lombar:** Acione o abdômen com 'bracing' diafragmático firme antes de cada repetição.\n\n"
                    "Onde exatamente você sentiu o desconforto?"
                )

            # FOCO EM MEMBROS SUPERIORES
            elif any(w in msg_lower for w in ["superior", "superiores", "braco", "braço", "peito", "costas", "ombros"]):
                return (
                    f"Excelente estratégia, {name}! Para hipertrofia acelerada de **Membros Superiores**, a ciência recomenda:\n\n"
                    "🎯 **Pilares de Sobrecarga para Superiores:**\n"
                    "1. **Frequência 2x na semana:** Dividir em empurrar/puxar ou rotina Upper/Lower gera estímulo ideal de síntese proteica.\n"
                    "2. **Ordem dos exercícios:** Inicie sempre pelos grandes compostos (Supino ou Barra Fixa/Remada) e deixe isoladores (elevação lateral, rosca e tríceps) para o final.\n"
                    "3. **Cadência excêntrica:** 2 a 3 segundos de descida controlada aumentam o dano mecânico sem necessidade de cargas lesivas.\n\n"
                    "Você prefere aplicar a rotina **Upper / Lower** (4 dias) ou **Push / Pull / Legs** (5-6 dias)?"
                )

            # FOCO EM MEMBROS INFERIORES / PERNAS
            elif any(w in msg_lower for w in ["inferior", "inferiores", "perna", "pernas", "gluteo", "glúteo", "quadriceps", "quadríceps", "panturrilha"]):
                return (
                    f"Vamos construir uma base firme como a rocha, {name}!\n\n"
                    "🦵 **Princípios de Ouro para Membros Inferiores:**\n"
                    "1. **Agachamento Profundo:** Quebre a paralela com controle; a maior hipertrofia de quadríceps e glúteos ocorre em máxima flexão de joelho sob tensão.\n"
                    "2. **Cadeia Posterior:** Não negligencie o Stiff e a Mesa Flexora; equilíbrio entre quadríceps e isquiotibiais previne lesões no ligamento cruzado.\n"
                    "3. **Descanso entre séries:** Pernas demandam maior débito cardíaco. Descanse pelo menos 2 minutos entre séries pesadas de Agachamento ou Leg Press.\n\n"
                    "Quer ajustar sua divisão para ter 2 dias dedicados a pernas?"
                )

            # SÉRIES, REPETIÇÕES, CARGAS, RPE E PROGRESSÃO
            elif any(w in msg_lower for w in ["quantas series", "quantas repetições", "quantas reps", "carga", "aumentar carga", "rpe", "rir", "descanso", "tempo de descanso", "sobrecarga"]):
                return (
                    f"Diretriz cinesiológica de precisão para você, {name}:\n\n"
                    "⚡ **Calibração de Séries, Repetições & Intensidade:**\n"
                    "• **Hipertrofia Otimizada:** 3 a 4 séries por exercício, trabalhando entre **6 a 12 repetições** com RPE 8-9 (parando com 1 a 2 repetições antes da falha total concêntrica).\n"
                    "• **Quando subir a carga?** Aplique a regra do 'topo da faixa': se você fez todas as séries com 12 repetições mantendo a técnica impecável, na próxima sessão aumente 2kg a 4kg totais.\n"
                    "• **Tempo de Descanso:** 90 a 120 segundos para exercícios compostos (Supino, Agachamento, Terra, Remada) e 60 a 90 segundos para isoladores.\n\n"
                    "Anote suas cargas na aba **Treino** a cada série para garantir a sobrecarga progressiva semanal!"
                )

            # EXECUÇÃO DE EXERCÍCIOS ESPECÍFICOS (SUPINO, AGACHAMENTO, TERRA, ELEVAÇÃO LATERAL)
            elif "supino" in msg_lower:
                return (
                    f"Checklist anatômico do **Supino**, {name}:\n\n"
                    "1. **Escápulas:** Retraia e deprima as escápulas 'no bolso de trás da calça' contra o banco.\n"
                    "2. **Pés e Base:** Pés firmemente plantados no chão para transferir força ('leg drive').\n"
                    "3. **Cotovelos:** Não abra os cotovelos a 90° (risco grave ao manguito). Mantenha em ~60°.\n"
                    "4. **Trajetória:** A barra desce na linha média/inferior do esterno e sobe com leve arco em direção aos olhos."
                )
            elif "agachamento" in msg_lower:
                return (
                    f"Checklist anatômico do **Agachamento Livre**, {name}:\n\n"
                    "1. **Base dos Pés:** Largura dos ombros ou ligeiramente mais larga, pontas rodadas ~15° a 30° para fora.\n"
                    "2. **Bracing Abdominal:** Puxe o ar para o abdômen e trave a musculatura do core antes de descer.\n"
                    "3. **Trajetória:** O quadril vai para trás e para baixo simultaneamente, mantendo o peso distribuído em todo o pé.\n"
                    "4. **Coluna Neutra:** Evite o 'butt wink' (retroversão pélvica na profundidade máxima)."
                )
            elif "terra" in msg_lower:
                return (
                    f"Checklist anatômico do **Levantamento Terra**, {name}:\n\n"
                    "1. **Posição da Barra:** Colada na canela, cortando o meio dos pés ao olhar por cima.\n"
                    "2. **Dorsal Ativa:** Imagine que está entortando a barra para ativar os dorsais e proteger a coluna torácica.\n"
                    "3. **Subida:** Empurre o chão com os calcanhares; o quadril e o peito devem subir na mesma cadência até a extensão total."
                )
            elif "lateral" in msg_lower:
                return (
                    f"Checklist da **Elevação Lateral (Deltóide Lateral)**, {name}:\n\n"
                    "1. **Plano Escapular:** Levante os halteres ~30° à frente da linha do corpo (não abra reto dos lados).\n"
                    "2. **Cotovelos Leves:** Mantenha microflexão nos cotovelos e lidere o movimento com o cotovelo, não com as mãos.\n"
                    "3. **Carga Inteligente:** Evite impulso com o tronco. 3 séries de 12 a 15 repetições controladas explodem os ombros sem lesionar."
                )

            # MOTIVAÇÃO / DESÂNIMO / FÉ
            elif any(w in msg_lower for w in ["desanimo", "desânimo", "preguiça", "preguica", "cansado", "sem vontade", "motivação", "motivacao"]):
                return (
                    f"Ouça com o coração, guerreiro {name}:\n\n"
                    "📖 *'Não to mandei eu? Esforça-te e tem bom ânimo; não temas, nem te espantes; porque o Senhor teu Deus é contigo, por onde quer que andares.' (Josué 1:9)*\n\n"
                    "A motivação passageira é refém das emoções, mas o **domínio próprio** é um fruto espiritual sólido (Gálatas 5:23). "
                    "Os maiores treinos da sua vida serão aqueles em que você foi sem vontade, venceu a carne e honrou a Deus com a sua disciplina.\n\n"
                    "Levante a cabeça, beba 300ml de água e venha para o treino. 1 série de cada vez!"
                )

            # RESPOSTA GERAL DINÂMICA
            else:
                return (
                    f"Fala {name}! Vamos firmes rumo ao seu objetivo de **{goal.upper()}**!\n\n"
                    f"📋 **Prontuário Ativo do Treinador:**\n"
                    f"• Divisão Atual: **{routine}** ({days_week} dias/semana) | Peso Atual: **{weight}kg**\n"
                    "• Princípio de Hoje: Foco na contração voluntária e controle excêntrico de 2 a 3 segundos.\n\n"
                    "Como posso te ajudar especificamente no treino de hoje?\n"
                    "• Se tiver dúvidas sobre algum exercício (ex: supino, agachamento, puxadas)\n"
                    "• Se quiser substituir alguma máquina ocupada\n"
                    "• Se quiser refazer sua avaliação física, basta clicar no ícone **📋** no topo da tela!"
                )

        # =========================================================================
        # 2. PERSONA: NUTRICIONISTA
        # =========================================================================
        elif persona == "nutri":
            protein_target = round(weight * 2.2, 0)
            water_target = int(weight * 40)

            if any(w in msg_lower for w in ["pos treino", "pós treino", "pos-treino", "pós-treino"]):
                return (
                    f"Excelente pergunta, {name}!\n\n"
                    "🥗 **Pós-Treino Ideal para o Templo ({goal.upper()}):**\n"
                    "• **Opção Rápida:** 30g a 40g de Whey Protein + 1 banana madura + 30g de aveia + 5g de Creatina.\n"
                    "• **Opção Prato Sólido:** 150g de peito de frango ou patinho moído + 150g a 200g de arroz branco/batata + vegetais verdes.\n"
                    "A síntese proteica é otimizada quando unimos proteína de alto valor biológico com carboidrato para recuperar o glicogênio muscular!"
                )
            elif any(w in msg_lower for w in ["pre treino", "pré treino", "pre-treino", "pré-treino", "energia"]):
                return (
                    f"Para chegar com máxima energia no templo, {name}:\n\n"
                    "⚡ **Refeição Pré-Treino (60-90 min antes):**\n"
                    "• Carboidratos limpos e de fácil digestão (banana com aveia e canela, pão integral com ovos mexidos ou tapioca).\n"
                    "• Beba pelo menos 500ml de água antes de iniciar a sessão.\n"
                    "• Evite excesso de gorduras e ultraprocessados que deixam a digestão lenta e roubam o fluxo sanguíneo muscular."
                )
            elif any(w in msg_lower for w in ["creatina", "whey", "suplemento", "suplementos"]):
                return (
                    f"Orientações científicas de suplementação para você ({weight}kg):\n\n"
                    "🥛 **Suplementação Básica & Eficaz:**\n"
                    "1. **Creatina:** 5g todos os dias (mesmo em dias sem treino), com água ou após uma refeição com carboidratos. Uso crônico.\n"
                    "2. **Whey Protein:** Use estrategicamente pela praticidade para atingir sua meta diária de **~{protein_target}g de proteína**.\n"
                    "3. Suplemento é complemento: a base deve ser comida de verdade da criação divina (ovos, carnes magras, arroz, feijão, frutas)."
                )
            else:
                return (
                    f"Olá {name}! Como ensina 1 Coríntios 10:31: *'Quer comais, quer bebais ou façais qualquer outra coisa, fazei tudo para a glória de Deus.'*\n\n"
                    f"📊 **Metas Nutricionais Calculadas para o seu Templo:**\n"
                    f"• Meta Proteica: **~{protein_target}g** de proteína por dia (2.2g/kg para {weight}kg).\n"
                    f"• Hidratação Mínima: **~{water_target}ml** de água por dia (40ml por kg).\n"
                    f"• Objetivo Metabólico: **{goal.upper()}**.\n\n"
                    "Qual refeição ou alimento você gostaria de ajustar agora?"
                )

        # =========================================================================
        # 3. PERSONA: MENTE & DISCIPLINA (DR. GABRIEL)
        # =========================================================================
        elif persona == "mente":
            return (
                f"Olá guerreiro {name}! Como está o seu foco e seu espírito hoje?\n\n"
                "🛡️ **Meditação de Fortaleza:**\n"
                "A Palavra diz: *'O homem sábio é forte, e o homem de conhecimento consolida a sua força.' (Provérbios 24:5)*\n\n"
                "Não permita que a preguiça ou as distrações do mundo silenciem o seu propósito. "
                "Respire fundo, entregue seus planos a Deus e entre no treino com a mente blindada pela fé e pelo domínio próprio!\n\n"
                "Precisa de uma palavra de direcionamento para o treino de hoje?"
            )

        # =========================================================================
        # 4. PERSONA: FISIOTERAPEUTA (DR. RAFAEL)
        # =========================================================================
        else:
            return (
                f"Olá {name}! A preservação articular é o segredo para treinar com força até a velhice como Calebe (Josué 14:11).\n\n"
                "🦴 **Checklist do Guardião Biomecânico:**\n"
                "1. **Aquecimento Específico:** 2 séries leves com 50% da carga antes de ir para a carga de trabalho.\n"
                "2. **Manguito Rotador:** Rotação externa na polia antes de supinos ou desenvolvimentos pesados.\n"
                "3. **Tornozelo e Quadril:** Mobilidade ativa antes do agachamento previne sobrecarga no joelho e na lombar.\n\n"
                "Está sentindo algum ponto de estalo, pinçamento ou dor articular hoje?"
            )
