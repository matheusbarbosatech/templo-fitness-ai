import sqlite3
import json

conn = sqlite3.connect('data/fitness_ai.db')
c = conn.cursor()

# Buscar o usuario Matheus
c.execute("SELECT id, name FROM users ORDER BY id")
users = c.fetchall()
# Pegar o primeiro usuário (geralmente Matheus)
matheus_id = users[0][0]
matheus_name = users[0][1]

# Buscar rotinas ÚNICAS de Matheus (pelo nome, pega o mais recente de cada nome)
c.execute("""
    SELECT id, name, category, description, color_hex
    FROM workout_routines
    WHERE user_id = ?
    GROUP BY name
    HAVING id = MAX(id)
    ORDER BY id
""", (matheus_id,))
routines = c.fetchall()

# Para cada rotina, buscar exercicios com GIF
routines_data = []
for r in routines:
    c.execute("""
        SELECT re.exercise_name, re.target_sets, re.target_reps, re.target_weight, re.rest_seconds,
               el.gif_url, el.primary_muscle, el.category, el.execution_guide, el.common_mistakes, el.id as ex_id
        FROM routine_exercises re
        LEFT JOIN exercise_library el ON el.name = re.exercise_name
        WHERE re.routine_id = ?
        ORDER BY re.id
    """, (r[0],))
    exercises = c.fetchall()
    
    exs = []
    for e in exercises:
        exs.append({
            "name": e[0],
            "sets": e[1],
            "reps": e[2],
            "weight": e[3],
            "rest": e[4],
            "gif_url": e[5] or "",
            "muscle": e[6] or "",
            "category": e[7] or "",
            "guide": e[8] or "",
            "mistakes": e[9] or "",
            "routine_id": r[0],
            "ex_id": e[10]
        })
    
    routines_data.append({
        "id": r[0],
        "name": r[1],
        "category": r[2],
        "description": r[3],
        "color": r[4] or "#6C63FF",
        "exercises": exs
    })

conn.close()

# Gerar HTML
html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🏋️ Treinos de {matheus_name} - Templo Fitness AI</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
  
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  
  :root {{
    --bg: #0a0a0f;
    --surface: #13131a;
    --surface2: #1c1c27;
    --border: rgba(255,255,255,0.07);
    --accent: #6C63FF;
    --accent2: #ff6584;
    --text: #e8e8f0;
    --text-muted: #7878a0;
    --success: #00e5a0;
    --warning: #ffbe00;
  }}
  
  body {{
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }}
  
  /* BG Gradient */
  body::before {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: 
      radial-gradient(ellipse 80% 50% at 20% -10%, rgba(108,99,255,0.15) 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 80% 100%, rgba(255,101,132,0.1) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
  }}
  
  .container {{ position: relative; z-index: 1; max-width: 1400px; margin: 0 auto; padding: 0 24px; }}
  
  /* HEADER */
  header {{
    padding: 48px 0 32px;
    text-align: center;
  }}
  
  .header-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(108,99,255,0.15);
    border: 1px solid rgba(108,99,255,0.3);
    border-radius: 100px;
    padding: 6px 16px;
    font-size: 13px;
    color: var(--accent);
    margin-bottom: 20px;
    font-weight: 500;
  }}
  
  h1 {{
    font-size: clamp(32px, 5vw, 56px);
    font-weight: 900;
    background: linear-gradient(135deg, #fff 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    margin-bottom: 12px;
  }}
  
  .subtitle {{
    color: var(--text-muted);
    font-size: 16px;
  }}
  
  /* TABS */
  .tabs {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: center;
    margin: 40px 0 32px;
  }}
  
  .tab-btn {{
    padding: 10px 20px;
    border-radius: 100px;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text-muted);
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s;
    font-family: 'Inter', sans-serif;
  }}
  
  .tab-btn:hover, .tab-btn.active {{
    background: var(--accent);
    border-color: var(--accent);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(108,99,255,0.4);
  }}
  
  /* ROUTINE SECTION */
  .routine-section {{ display: none; animation: fadeIn 0.3s ease; }}
  .routine-section.active {{ display: block; }}
  
  @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(16px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  
  .routine-header {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
  }}
  
  .routine-icon {{
    width: 60px;
    height: 60px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    flex-shrink: 0;
  }}
  
  .routine-header h2 {{ font-size: 24px; font-weight: 700; margin-bottom: 4px; }}
  .routine-header p {{ color: var(--text-muted); font-size: 14px; }}
  
  .routine-stats {{
    margin-left: auto;
    display: flex;
    gap: 24px;
  }}
  
  .stat {{ text-align: center; }}
  .stat-value {{ font-size: 28px; font-weight: 800; color: var(--accent); }}
  .stat-label {{ font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
  
  /* EXERCISE GRID */
  .exercises-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 20px;
  }}
  
  /* EXERCISE CARD */
  .exercise-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    overflow: hidden;
    transition: all 0.3s;
    position: relative;
  }}
  
  .exercise-card:hover {{
    transform: translateY(-4px);
    border-color: rgba(108,99,255,0.4);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(108,99,255,0.2);
  }}
  
  .gif-container {{
    position: relative;
    background: #0d0d14;
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }}
  
  .gif-container img {{
    width: 100%;
    height: 100%;
    object-fit: contain;
    transition: transform 0.3s;
  }}
  
  .exercise-card:hover .gif-container img {{ transform: scale(1.05); }}
  
  .gif-placeholder {{
    font-size: 48px;
    opacity: 0.3;
  }}
  
  .muscle-badge {{
    position: absolute;
    top: 12px;
    right: 12px;
    background: rgba(0,0,0,0.7);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 100px;
    padding: 4px 10px;
    font-size: 11px;
    color: var(--text-muted);
    backdrop-filter: blur(8px);
  }}
  
  .card-body {{ padding: 20px; }}
  
  .exercise-name {{
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 12px;
    line-height: 1.3;
  }}
  
  .exercise-metrics {{
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }}
  
  .metric {{
    background: var(--surface2);
    border-radius: 10px;
    padding: 8px 12px;
    text-align: center;
    flex: 1;
    min-width: 70px;
  }}
  
  .metric-value {{
    font-size: 18px;
    font-weight: 800;
    color: var(--accent);
    display: block;
    line-height: 1;
  }}
  
  .metric-label {{
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
    display: block;
  }}
  
  .rest-info {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 16px;
  }}
  
  /* EDIT FORM */
  .edit-toggle {{
    width: 100%;
    padding: 10px;
    background: rgba(108,99,255,0.1);
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 10px;
    color: var(--accent);
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }}
  
  .edit-toggle:hover {{
    background: rgba(108,99,255,0.2);
    border-color: var(--accent);
  }}
  
  .edit-form {{
    display: none;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
  }}
  
  .edit-form.open {{ display: block; }}
  
  .form-row {{
    display: flex;
    gap: 8px;
    margin-bottom: 10px;
  }}
  
  .form-group {{ flex: 1; }}
  
  .form-group label {{
    display: block;
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 5px;
  }}
  
  .form-group input {{
    width: 100%;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 10px;
    color: var(--text);
    font-size: 14px;
    font-family: 'Inter', sans-serif;
    transition: border-color 0.2s;
  }}
  
  .form-group input:focus {{
    outline: none;
    border-color: var(--accent);
  }}
  
  .save-btn {{
    width: 100%;
    padding: 10px;
    background: linear-gradient(135deg, var(--accent), #a78bfa);
    border: none;
    border-radius: 10px;
    color: white;
    font-size: 14px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    cursor: pointer;
    transition: all 0.2s;
    margin-top: 4px;
  }}
  
  .save-btn:hover {{ transform: translateY(-1px); box-shadow: 0 8px 20px rgba(108,99,255,0.5); }}
  
  /* TOAST */
  .toast {{
    position: fixed;
    bottom: 32px;
    left: 50%;
    transform: translateX(-50%) translateY(100px);
    background: var(--success);
    color: #000;
    padding: 14px 28px;
    border-radius: 100px;
    font-weight: 700;
    font-size: 14px;
    z-index: 999;
    transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  }}
  
  .toast.show {{ transform: translateX(-50%) translateY(0); }}
  
  /* TIPS SECTION */
  .tips-box {{
    background: rgba(108,99,255,0.08);
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 32px;
    display: flex;
    align-items: flex-start;
    gap: 16px;
  }}
  
  .tips-box .icon {{ font-size: 24px; flex-shrink: 0; }}
  .tips-box p {{ color: var(--text-muted); font-size: 14px; line-height: 1.6; }}
  .tips-box strong {{ color: var(--text); }}

  @media (max-width: 768px) {{
    .exercises-grid {{ grid-template-columns: 1fr; }}
    .routine-stats {{ display: none; }}
    .routine-header {{ flex-direction: column; text-align: center; }}
  }}
</style>
</head>
<body>

<div class="container">
  <header>
    <div class="header-badge">🏋️ Templo Fitness AI</div>
    <h1>Seus Treinos,<br>{matheus_name}</h1>
    <p class="subtitle">Visualize, edite séries, reps e cargas direto aqui</p>
  </header>
  
  <div class="tips-box">
    <div class="icon">💡</div>
    <p><strong>Como usar:</strong> Clique em "✏️ Editar Exercício" em qualquer card para alterar séries, reps, carga e descanso. As alterações são salvas no banco de dados do app. Para ver os GIFs animados, precisa de conexão com a internet.</p>
  </div>
  
  <div class="tabs">
"""

# Gerar tabs
icons = ["💪","🦵","🏃","⚡","🔥","💥","🎯","🏆"]
for i, r in enumerate(routines_data):
    icon = icons[i % len(icons)]
    active = "active" if i == 0 else ""
    html += f'    <button class="tab-btn {active}" onclick="showTab({r["id"]})" id="tab-{r["id"]}">{icon} {r["name"]}</button>\n'

html += "  </div>\n\n"

# Gerar seções
for i, r in enumerate(routines_data):
    active = "active" if i == 0 else ""
    total_sets = sum(e["sets"] for e in r["exercises"] if e["sets"])
    total_vol = sum((e["sets"] or 0) * (e["weight"] or 0) for e in r["exercises"])
    icon = icons[i % len(icons)]
    
    color = r["color"] if r["color"].startswith("#") else f"#{r['color']}"
    
    html += f"""  <div class="routine-section {active}" id="section-{r['id']}">
    <div class="routine-header">
      <div class="routine-icon" style="background: {color}22; color: {color};">{icon}</div>
      <div>
        <h2>{r['name']}</h2>
        <p>{r['description'] or r['category']}</p>
      </div>
      <div class="routine-stats">
        <div class="stat">
          <div class="stat-value">{len(r['exercises'])}</div>
          <div class="stat-label">Exercícios</div>
        </div>
        <div class="stat">
          <div class="stat-value">{total_sets}</div>
          <div class="stat-label">Total Séries</div>
        </div>
        <div class="stat">
          <div class="stat-value">{int(total_vol)}kg</div>
          <div class="stat-label">Volume Total</div>
        </div>
      </div>
    </div>
    
    <div class="exercises-grid">
"""
    
    for e in r["exercises"]:
        weight_display = f"{e['weight']:.0f}kg" if e['weight'] else "Livre"
        rest_display = f"{e['rest']}s" if e['rest'] else "-"
        
        gif_html = ""
        if e["gif_url"]:
            gif_html = f'<img src="{e["gif_url"]}" alt="{e["name"]}" loading="lazy">'
        else:
            gif_html = '<div class="gif-placeholder">🏋️</div>'
        
        muscle_short = e["muscle"][:25] + "..." if len(e["muscle"]) > 25 else e["muscle"]
        
        # Gerar form de edição
        ex_key = f"ex_{r['id']}_{e['name'].replace(' ', '_').replace('/', '_')}"
        
        ex_name_escaped = e['name'].replace("'", "\\'")
        html += f"""      <div class="exercise-card" id="{ex_key}">
        <div class="gif-container">
          {gif_html}
          {"<div class='muscle-badge'>" + muscle_short + "</div>" if muscle_short else ""}
        </div>
        <div class="card-body">
          <div class="exercise-name">{e['name']}</div>
          <div class="exercise-metrics">
            <div class="metric">
              <span class="metric-value">{e['sets']}</span>
              <span class="metric-label">Séries</span>
            </div>
            <div class="metric">
              <span class="metric-value" style="font-size:14px">{e['reps']}</span>
              <span class="metric-label">Reps</span>
            </div>
            <div class="metric">
              <span class="metric-value" style="color:#ff6584">{weight_display}</span>
              <span class="metric-label">Carga</span>
            </div>
          </div>
          <div class="rest-info">⏱️ Descanso: {rest_display}</div>
          
          <button class="edit-toggle" onclick="toggleEdit('{ex_key}')">
            ✏️ Editar Exercício
          </button>
          
          <div class="edit-form" id="form-{ex_key}">
            <div class="form-row">
              <div class="form-group">
                <label>Séries</label>
                <input type="number" id="sets-{ex_key}" value="{e['sets']}" min="1" max="20">
              </div>
              <div class="form-group">
                <label>Reps</label>
                <input type="text" id="reps-{ex_key}" value="{e['reps']}">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Carga (kg)</label>
                <input type="number" id="weight-{ex_key}" value="{e['weight']}" step="0.5">
              </div>
              <div class="form-group">
                <label>Descanso (s)</label>
                <input type="number" id="rest-{ex_key}" value="{e['rest']}">
              </div>
            </div>
            <button class="save-btn" onclick="saveExercise('{ex_key}', {r['id']}, '{ex_name_escaped}')">
              💾 Salvar Alteração
            </button>
          </div>
        </div>
      </div>
"""
    
    html += "    </div>\n  </div>\n\n"

html += """</div>

<div class="toast" id="toast">✅ Alteração salva com sucesso!</div>

<script>
function showTab(routineId) {
  document.querySelectorAll('.routine-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('section-' + routineId).classList.add('active');
  document.getElementById('tab-' + routineId).classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function toggleEdit(key) {
  const form = document.getElementById('form-' + key);
  form.classList.toggle('open');
  const btn = document.querySelector('#' + key + ' .edit-toggle');
  btn.textContent = form.classList.contains('open') ? '✖ Fechar' : '✏️ Editar Exercício';
}

function saveExercise(key, routineId, exerciseName) {
  const sets = document.getElementById('sets-' + key).value;
  const reps = document.getElementById('reps-' + key).value;
  const weight = document.getElementById('weight-' + key).value;
  const rest = document.getElementById('rest-' + key).value;
  
  // Atualizar visualmente os métricas
  const card = document.getElementById(key);
  const metrics = card.querySelectorAll('.metric-value');
  metrics[0].textContent = sets;
  metrics[1].textContent = reps;
  metrics[2].textContent = weight + 'kg';
  card.querySelector('.rest-info').textContent = '⏱️ Descanso: ' + rest + 's';
  
  // Chamar API para salvar no banco
  fetch('/api/update_exercise', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      routine_id: routineId,
      exercise_name: exerciseName,
      target_sets: parseInt(sets),
      target_reps: reps,
      target_weight: parseFloat(weight),
      rest_seconds: parseInt(rest)
    })
  })
  .then(r => r.json())
  .then(data => {
    showToast(data.success ? '✅ Salvo no banco de dados!' : '⚠️ ' + (data.error || 'Erro ao salvar'));
  })
  .catch(() => {
    // Se não tiver API rodando, mostra mensagem de visualização
    showToast('👁️ Visualização salva! Abra o app para confirmar no banco.');
  });
  
  toggleEdit(key);
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3500);
}
</script>

</body>
</html>
"""

with open('meus_treinos.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML gerado com sucesso!")
print("   Arquivo: meus_treinos.html")
print(f"   Rotinas: {len(routines_data)}")
total_ex = sum(len(r['exercises']) for r in routines_data)
print(f"   Total de exercicios: {total_ex}")
