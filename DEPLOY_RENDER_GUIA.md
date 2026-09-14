# 🚀 Guia de Deploy no Render & Envio para o GitHub — Apollo Fitness AI

Este guia passo a passo ensina exatamente como subir o código para o seu **GitHub** e colocá-lo no ar no **Render** em menos de 3 minutos, com suporte a acesso no celular (PWA) e no computador.

---

## 📋 Checklist de Prontidão

- [x] **Robô de Testes Automatizado:** 30/30 testes passaram (100% de cobertura funcional).
- [x] **Segurança do Repositório:** Arquivo `.gitignore` configurado (o arquivo `.apk` de 141MB está ignorado para não travar o limite do GitHub).
- [x] **Suporte a Nuvem:** Porta dinâmica `PORT` e host `0.0.0.0` configurados no `run_web.py`.
- [x] **Blueprint do Render:** Arquivo `render.yaml` gerado na raiz.
- [x] **Multi-Usuário & Metas:** Sistema completo para alternar atletas e calibrar treinos.

---

## 🐙 PASSO 1: Subir o Projeto para o seu GitHub

Abra o seu terminal (PowerShell ou Prompt de Comando) na pasta do projeto (`c:\Users\matheus\Desktop\app-treino-ia`) e execute os comandos abaixo:

### 1. Inicializar o Git e fazer o primeiro Commit
```bash
git init
git branch -M main
git add .
git commit -m "feat: Apollo Fitness AI - Multi-usuario, metas, IA e pronto para deploy"
```

> 💡 **Nota de Segurança:** O arquivo `apollo_fitness_ai.apk` não será enviado ao GitHub porque está no `.gitignore`. O GitHub não aceita arquivos maiores que 100MB sem Git LFS.

### 2. Conectar com o seu Repositório no GitHub
1. Acesse [github.com/new](https://github.com/new) e crie um novo repositório (ex: `apollo-fitness-ai`).
2. Copie o link do repositório (ex: `https://github.com/SEU_USUARIO/apollo-fitness-ai.git`).
3. Execute no terminal:
```bash
git remote add origin https://github.com/SEU_USUARIO/apollo-fitness-ai.git
git push -u origin main
```

---

## ☁️ PASSO 2: Fazer o Deploy no Render

O Render oferece hospedagem em nuvem gratuita para aplicações Web Python.

### Opção Recomendada: Pelo Painel do Render (3 Minutos)

1. Acesse [dashboard.render.com](https://dashboard.render.com/) e faça login (pode entrar com sua conta do GitHub).
2. Clique no botão azul **"New +"** no canto superior direito e selecione **"Web Service"**.
3. Selecione a opção **"Build and deploy from a Git repository"** e clique em **Next**.
4. Conecte o repositório que você acabou de subir: `apollo-fitness-ai` e clique em **Connect**.
5. Preencha as configurações conforme a tabela abaixo:

| Campo | Valor a preencher |
| :--- | :--- |
| **Name** | `apollo-fitness-ai` (ou o nome que preferir) |
| **Region** | Oregon (US West) ou Frankfurt |
| **Branch** | `main` |
| **Root Directory** | *(deixe em branco)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python run_web.py` |
| **Instance Type** | `Free` ($0/mês) |

6. Role até a seção **"Environment Variables"** (Variáveis de Ambiente) e adicione:
   - `PYTHON_VERSION` = `3.11.9`
   - `HOST` = `0.0.0.0`
   - `PORT` = `10000`
   - `DEVWORLD_BASE_URL` = `https://api.devworld.com.br/v1` *(opcional)*

7. Clique no botão inferior **"Create Web Service"**!

---

## ⏱️ O que acontece agora?

1. O Render vai clonar seu repositório no GitHub.
2. Vai instalar as dependências do `requirements.txt`.
3. Vai iniciar o servidor web do Apollo Fitness AI através do comando `python run_web.py`.
4. Em cerca de 1 a 2 minutos, o status mudará para **"Live"** (Verde).
5. O link público do seu app aparecerá no topo da tela, por exemplo:
   `https://apollo-fitness-ai.onrender.com`

---

## 📱 Como Acessar e Usar no Celular (Como App Nativo / PWA)

1. Abra o link gerado pelo Render no navegador do seu celular (Chrome no Android ou Safari no iPhone).
2. **No Android (Chrome):** Toque nos três pontinhos no canto superior direito e clique em **"Instalar aplicativo"** ou **"Adicionar à tela inicial"**.
3. **No iPhone (Safari):** Toque no botão de Compartilhar (quadrado com seta para cima) e selecione **"Adicionar à Tela de Início"**.
4. O ícone do **Apollo Fitness AI** ficará na tela do seu celular funcionando em tela cheia como se fosse baixado da Play Store/App Store!

---

## 🤖 Como rodar o Robô de Testes a qualquer momento

Se você fizer alterações no futuro e quiser garantir que tudo continue 1000% funcionando:
```bash
python test_robot_user.py
```
O robô executa a validação completa de banco, login multi-usuário, troca de exercícios, personal trainer, IA, fotos e nutrição em menos de 4 segundos.
