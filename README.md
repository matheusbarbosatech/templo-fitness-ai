# 🏛️ TEMPLO FITNESS AI — Super-App Cristão de Treino, Força & Mordomia do Templo 360°

Aplicativo completo de musculação, performance esportiva, disciplina e saúde integral com fundamento bíblico (**1 Coríntios 6:19-20 — O corpo como Templo do Espírito Santo**). Desenvolvido em **Python + Flet**, com banco de dados **SQLite local (Offline-First)** e integração com a **API DevWorld**.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/matheusbarbosatech/templo-fitness-ai)

---

## 🌟 Principais Funcionalidades

### 1. 🏠 Dashboard 360° & Mordomia do Templo
- **Versículo Diário & Propósito:** Lembrete de que o treino é mordomia do corpo e instrumento de vocação divina.
- Visão holística: Treino ativo do dia, hidratação, calorias e balanço de macronutrientes.
- **Alternância Multi-Usuário:** Suporte a múltiplos usuários no mesmo aparelho com dados isolados.

### 2. 🏋️ Módulo de Execução de Treino & Prescrições do Personal
- Controle dinâmico de séries, repetições, cargas e RPE.
- **Troca Rápida de Exercício:** Substituições biomecanicamente equivalentes recomendadas pelo personal se a máquina estiver ocupada ou houver desconforto articular.
- **Prescrições Completas de Rotina:** Aplicação instantânea de treinos periodizados (Push/Pull/Legs, Upper/Lower, ABC Hipertrofia).
- **Cronômetro de descanso interativo** com contagem regressiva e alertas sonoros/visuais.
- Cálculo automático do **volume total de treino (tonelagem)** e registro no histórico.

### 3. 📖 Biblioteca Biomecânica & Máquinas
- 30+ exercícios com cinesiologia completa pré-cadastrados (Peito, Costas, Pernas, Ombros, Braços, Abdômen).
- Guia passo a passo de postura, ativação muscular e erros biomecânicos comuns.

### 4. 🤖 Sala da Junta Técnica de IA (DevWorld)
- Alternância em 1 clique entre 4 Especialistas das Ciências do Esporte e Mordomia Cristã:
  - 🏋️ **Treinador (Personal Trainer):** Sobrecarga progressiva, cadência de repetição e variações biomecânicas.
  - 🥗 **Nutricionista (Nutrição da Criação):** Alimentos naturais, distribuição de macros e domínio próprio contra a compulsão.
  - 🧠 **Dr. Gabriel (Mente, Disciplina & Fé):** Renovação da mente (Rm 12:2), foco, combate à ansiedade e perseverança diária.
  - 🦴 **Dr. Rafael (Fisioterapeuta do Templo):** Preservação articular, mobilidade e longevidade física.

### 5. 🥗 Módulo de Nutrição & Hidratação
- Calculadora de TMB, TDEE e distribuição de macros calculada automaticamente no Wizard de Metas.
- Contador interativo de água (+250ml, +500ml, +1L).
- Registro de refeições com presets rápidos e cálculo de calorias.

### 6. 🧠 Módulo de Saúde Mental, Sono & Oração
- **Oração do Templo & Consagração Pré-Treino:** Consagração do corpo e esforço físico a Deus.
- Check-in de humor, horas de sono e prontidão física.
- **Protocolo de Respiração Box Breathing (4-4-4-4)** guiado para foco e serenidade do sistema nervoso.

### 7. 📸 Galeria de Evolução Corporal & Antes & Depois
- Registro de fotos periódicas (Frente, Costas, Lado).
- **Comparativo Automático Antes & Depois** lado a lado com data e evolução de medidas.
- Histórico de peso e perímetros corporais.

### 8. ⚙️ Ajustes, Metas & API DevWorld
- Wizard de Anamnese & Metas 360° para recalibrar treinos a qualquer instante.
- Configuração de Chave de API DevWorld e parâmetros de modelo.

---

## 🚀 Como Executar

### Opção 1: Pelo arquivo executável (1 Clique)
Dê um duplo clique em:
- `1_RODAR_APP_NO_PC.bat` para abrir a janela nativa no Windows.
- `2_RODAR_APP_NAVEGADOR.bat` para abrir no seu navegador de internet ou celular na mesma rede Wi-Fi.

### Opção 2: Pelo Terminal
```bash
python run_local.py
```

### Opção 3: Servidor Web / Deploy
```bash
python run_web.py
```

---

## 🧪 Robô de Testes Automatizado
Para testar todas as funcionalidades do aplicativo simulando um usuário real:
```bash
python test_robot_user.py
```
*30/30 testes funcionais validados em menos de 4 segundos.*
