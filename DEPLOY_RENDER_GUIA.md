# 🚀 Guia Definitivo de Deploy no Render & Envio para o GitHub — TEMPLO FITNESS AI

Este guia passo a passo ensina exatamente como subir o código para o seu **GitHub** (`matheusbarbosatech`) e colocá-lo no ar no **Render** em menos de 3 minutos, com suporte a acesso no celular (PWA) e no computador.

---

## 📋 Checklist de Prontidão

- [x] **Robôs de Testes & Estresse Extremo:** 71/71 testes passaram (30/30 testes funcionais + 41/41 testes de cenários extremos e concorrência).
- [x] **Segurança do Repositório:** Arquivo `.gitignore` configurado (o arquivo `.apk` de 141MB está ignorado para não travar o limite do GitHub).
- [x] **Suporte a Nuvem:** Porta dinâmica `PORT` e host `0.0.0.0` configurados no `run_web.py`.
- [x] **Blueprint do Render:** Arquivo `render.yaml` gerado na raiz (`templo-fitness-ai`).
- [x] **Multi-Usuário & Metas:** Sistema completo para alternar usuários e calibrar treinos.
- [x] **Identidade Bíblica Unissex:** Mordomia do Templo do Espírito Santo (1 Coríntios 6:19-20).

---

## 🐙 PASSO 1: Criar o Repositório no GitHub e Enviar o Código

### 1. Criar o Repositório no GitHub
1. Acesse **[github.com/new](https://github.com/new)** logado com sua conta `matheusbarbosatech`.
2. Nome do repositório: `templo-fitness-ai`.
3. Visibilidade: **Public** (Público) — *Recomendado para facilitar a conexão com qualquer conta do Render sem conflitos de permissão.*
4. **Não marque** as opções de adicionar README, .gitignore ou licença (pois já temos tudo pronto no projeto).
5. Clique em **"Create repository"**.

### 2. Enviar o Código pelo Terminal
Abra o seu terminal na pasta do projeto (`c:\Users\matheus\Desktop\templo-fitness-ai`) e execute os comandos:

```bash
git remote add origin https://github.com/matheusbarbosatech/templo-fitness-ai.git
git branch -M main
git push -u origin main
```

*(Se o comando `git remote add origin` disser que origin já existe, use `git remote set-url origin https://github.com/matheusbarbosatech/templo-fitness-ai.git` e depois rode o `git push -u origin main`).*

> 💡 **Nota de Segurança:** O arquivo `templo_fitness_ai.apk` (141MB) está protegido no `.gitignore` e não será enviado, evitando rejeição pelo limite de 100MB do GitHub.

---

## ☁️ PASSO 2: Deploy no Render (Segunda Conta)

Mesmo que sua nova conta do Render use outro e-mail, você pode conectar o repositório da conta `matheusbarbosatech` facilmente:

### Como fazer:
1. Acesse [dashboard.render.com](https://dashboard.render.com/) na sua nova conta do Render.
2. Clique no botão azul **"New +"** no canto superior direito e selecione **"Web Service"**.
3. Na tela seguinte:
   - Se o seu repositório for **Público**: role até o campo **"Public Git repository"**, cole o link:
     `https://github.com/matheusbarbosatech/templo-fitness-ai`
     e clique em **Continue**.
   - Ou clique em **"Connect account"** do GitHub para autorizar o Render a ler seus repositórios.
4. Preencha as opções conforme a tabela:

| Campo | Valor a preencher |
| :--- | :--- |
| **Name** | `templo-fitness-ai` |
| **Region** | Oregon (US West) ou Frankfurt |
| **Branch** | `main` |
| **Root Directory** | *(deixe em branco)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python run_web.py` |
| **Instance Type** | `Free` ($0/mês) |

5. Na seção **"Environment Variables"**, adicione:
   - `PYTHON_VERSION` = `3.11.9`
   - `HOST` = `0.0.0.0`
   - `PORT` = `10000`
   - `DEVWORLD_BASE_URL` = `https://api.devworld.com.br/v1` *(opcional)*

6. Clique no botão azul **"Deploy Web Service"**!

---

## ⏱️ O que acontece agora?

1. O Render vai clonar seu repositório no GitHub.
2. Vai instalar as dependências do `requirements.txt`.
3. Vai iniciar o servidor web do TEMPLO FITNESS AI através do comando `python run_web.py`.
4. Em cerca de 1 a 2 minutos, o status mudará para **"Live"** (Verde).
5. O link público do seu app aparecerá no topo da tela, por exemplo:
   `https://templo-fitness-ai.onrender.com`

---

## 📱 Como Acessar e Usar no Celular (Como App Nativo / PWA)

1. Abra o link gerado pelo Render no navegador do seu celular (Chrome no Android ou Safari no iPhone).
2. **No Android (Chrome):** Toque nos três pontinhos no canto superior direito e clique em **"Instalar aplicativo"** ou **"Adicionar à tela inicial"**.
3. **No iPhone (Safari):** Toque no botão de Compartilhar (quadrado com seta para cima) e selecione **"Adicionar à Tela de Início"**.
4. O ícone do **TEMPLO FITNESS AI** ficará na tela do seu celular funcionando em tela cheia como se fosse baixado da loja oficial!

---

## 🤖 Como rodar o Robô de Testes a qualquer momento

Se você fizer alterações no futuro e quiser garantir que tudo continue 1000% funcionando:
```bash
python test_robot_user.py
```
O robô executa a validação completa de banco, login multi-usuário, troca de exercícios, personal trainer, IA, fotos e nutrição em menos de 4 segundos.
