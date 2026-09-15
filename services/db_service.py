"""
Serviço de Banco de Dados Local SQLite (Offline-First) - Templo Fitness AI.
Gerencia o armazenamento persistente de perfis, treinos, biblioteca de 50+ exercícios,
nutrição, saúde mental, fotos de evolução e histórico das IAs.
"""
import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from core.config import DB_PATH

class DBService:
    _active_user_id: int = 1

    @classmethod
    def get_active_user_id(cls) -> int:
        return cls._active_user_id

    @classmethod
    def set_active_user_id(cls, user_id: int):
        cls._active_user_id = user_id

    @staticmethod
    def get_connection():
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
        """Inicializa as tabelas do banco de dados relacional e migrações multi-usuário."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()

            # 0. Tabela de Múltiplos Usuários (Alunos & Personal)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT 'aluno',
                avatar_icon TEXT DEFAULT 'person',
                color_hex TEXT DEFAULT '#00FFA3',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 1. Perfil do Usuário
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS athlete_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                name TEXT DEFAULT 'Matheus',
                age INTEGER DEFAULT 26,
                sex TEXT DEFAULT 'M',
                height_cm REAL DEFAULT 178.0,
                weight_kg REAL DEFAULT 78.5,
                goal TEXT DEFAULT 'hipertrofia',
                activity_level TEXT DEFAULT 'intenso',
                target_weight_kg REAL DEFAULT 75.0,
                target_weeks INTEGER DEFAULT 12,
                training_days_week INTEGER DEFAULT 4,
                session_minutes INTEGER DEFAULT 60,
                experience_level TEXT DEFAULT 'intermediario',
                joint_pain TEXT DEFAULT 'nenhuma',
                diet_strategy TEXT DEFAULT 'equilibrada',
                daily_calories_target REAL DEFAULT 2400,
                daily_protein_target REAL DEFAULT 160,
                daily_water_target_ml INTEGER DEFAULT 3000,
                recommended_routine TEXT DEFAULT 'ABC',
                devworld_api_key TEXT DEFAULT '',
                devworld_base_url TEXT DEFAULT 'https://api.devworld.com.br/v1',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 2. Catálogo de Exercícios & Biomecânica
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                primary_muscle TEXT NOT NULL,
                secondary_muscles TEXT,
                equipment TEXT NOT NULL,
                execution_guide TEXT NOT NULL,
                why_do_it TEXT NOT NULL,
                common_mistakes TEXT NOT NULL,
                icon_name TEXT DEFAULT 'fitness_center'
            )
            """)

            # 3. Rotinas de Treino (Fichas)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_routines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                color_hex TEXT DEFAULT '#00FFA3'
            )
            """)

            # 4. Exercícios da Rotina
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS routine_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                routine_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                target_sets INTEGER DEFAULT 4,
                target_reps TEXT DEFAULT '8-12',
                target_weight REAL DEFAULT 20.0,
                rest_seconds INTEGER DEFAULT 90,
                FOREIGN KEY (routine_id) REFERENCES workout_routines(id)
            )
            """)

            # 5. Histórico de Sessões de Treino
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                routine_name TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_minutes INTEGER DEFAULT 0,
                total_volume_kg REAL DEFAULT 0,
                notes TEXT
            )
            """)

            # 6. Registro de Séries Executadas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                set_number INTEGER NOT NULL,
                weight_kg REAL NOT NULL,
                reps INTEGER NOT NULL,
                rpe REAL DEFAULT 8.0,
                completed INTEGER DEFAULT 1,
                FOREIGN KEY (session_id) REFERENCES workout_sessions(id)
            )
            """)

            # 7. Nutrição e Refeições
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                log_date DATE NOT NULL,
                meal_name TEXT NOT NULL,
                meal_time TEXT,
                calories REAL DEFAULT 0,
                protein_g REAL DEFAULT 0,
                carbs_g REAL DEFAULT 0,
                fat_g REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 8. Hidratação (Água)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS water_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                log_date DATE NOT NULL,
                amount_ml INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 9. Saúde Mental, Sono & Recuperação (Wellness)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_wellness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                log_date DATE NOT NULL,
                mood_score INTEGER DEFAULT 4,
                stress_score INTEGER DEFAULT 2,
                sleep_hours REAL DEFAULT 7.5,
                energy_score INTEGER DEFAULT 4,
                soreness_notes TEXT DEFAULT '',
                reflection_text TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 10. Evolução Corporal (Fotos & Medidas)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS body_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                log_date DATE NOT NULL,
                photo_path TEXT,
                angle TEXT DEFAULT 'Frente',
                weight_kg REAL,
                chest_cm REAL,
                arm_cm REAL,
                waist_cm REAL,
                thigh_cm REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 11. Histórico de Chat da IA (Memória Multidisciplinar)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                persona TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            conn.commit()

        # Executa migrações de colunas caso o banco já existisse
        cls._run_schema_migrations()

        # Garante usuários iniciais, exercícios e dados padrão
        cls._ensure_initial_users()
        cls._ensure_initial_profile()
        cls._seed_exercises_if_empty()
        cls._seed_default_routines_if_empty()
        cls._seed_evolution_if_empty()

    @classmethod
    def _run_schema_migrations(cls):
        """Adiciona colunas novas de forma segura se tabelas antigas existirem."""
        migrations = [
            ("users", "password", "TEXT DEFAULT '123456'"),
            ("athlete_profile", "priority_muscle_focus", "TEXT DEFAULT 'equilibrado'"),
            ("athlete_profile", "user_id", "INTEGER DEFAULT 1"),
            ("athlete_profile", "target_weight_kg", "REAL DEFAULT 75.0"),
            ("athlete_profile", "target_weeks", "INTEGER DEFAULT 12"),
            ("athlete_profile", "training_days_week", "INTEGER DEFAULT 4"),
            ("athlete_profile", "session_minutes", "INTEGER DEFAULT 60"),
            ("athlete_profile", "experience_level", "TEXT DEFAULT 'intermediario'"),
            ("athlete_profile", "joint_pain", "TEXT DEFAULT 'nenhuma'"),
            ("athlete_profile", "diet_strategy", "TEXT DEFAULT 'equilibrada'"),
            ("athlete_profile", "daily_calories_target", "REAL DEFAULT 2400"),
            ("athlete_profile", "daily_protein_target", "REAL DEFAULT 160"),
            ("athlete_profile", "daily_water_target_ml", "INTEGER DEFAULT 3000"),
            ("athlete_profile", "recommended_routine", "TEXT DEFAULT 'ABC'"),
            ("workout_routines", "user_id", "INTEGER DEFAULT 1"),
            ("workout_sessions", "user_id", "INTEGER DEFAULT 1"),
            ("nutrition_logs", "user_id", "INTEGER DEFAULT 1"),
            ("water_logs", "user_id", "INTEGER DEFAULT 1"),
            ("daily_wellness", "user_id", "INTEGER DEFAULT 1"),
            ("body_evolution", "user_id", "INTEGER DEFAULT 1"),
            ("ai_chat_history", "user_id", "INTEGER DEFAULT 1"),
        ]
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            for table, col, col_type in migrations:
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
                except Exception:
                    pass

            # Migração de índice antigo do daily_wellness (para permitir multi-usuário)
            try:
                cursor.execute("PRAGMA index_list(daily_wellness)")
                idx_list = cursor.fetchall()
                has_autoindex = any("autoindex" in str(idx[1]).lower() for idx in idx_list)
                if has_autoindex:
                    cursor.execute("""
                    CREATE TABLE daily_wellness_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER DEFAULT 1,
                        log_date DATE NOT NULL,
                        mood_score INTEGER DEFAULT 4,
                        stress_score INTEGER DEFAULT 2,
                        sleep_hours REAL DEFAULT 7.5,
                        energy_score INTEGER DEFAULT 4,
                        soreness_notes TEXT DEFAULT '',
                        reflection_text TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """)
                    cursor.execute("""
                    INSERT INTO daily_wellness_new (id, user_id, log_date, mood_score, stress_score, sleep_hours, energy_score, soreness_notes, reflection_text, created_at)
                    SELECT id, COALESCE(user_id, 1), log_date, mood_score, stress_score, sleep_hours, energy_score, soreness_notes, reflection_text, created_at
                    FROM daily_wellness
                    """)
                    cursor.execute("DROP TABLE daily_wellness")
                    cursor.execute("ALTER TABLE daily_wellness_new RENAME TO daily_wellness")
            except Exception:
                pass

            conn.commit()

    @classmethod
    def _ensure_initial_users(cls):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = 'matheus'")
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO users (id, name, username, role, avatar_icon, color_hex, password)
                VALUES (1, 'Matheus', 'matheus', 'aluno', 'fitness_center', '#FFFFFF', '123456')
                """)
                conn.commit()

            cursor.execute("SELECT id FROM users WHERE username = 'mary'")
            mary_row = cursor.fetchone()
            if not mary_row:
                cursor.execute("""
                INSERT INTO users (name, username, role, avatar_icon, color_hex, password)
                VALUES ('Mary Ellen da Silva Alves Barbosa', 'mary', 'aluno', 'person', '#FFFFFF', '123456')
                """)
                mary_id = cursor.lastrowid
                conn.commit()
                cls._seed_mary_profile_and_routines(mary_id)
            else:
                cls._seed_mary_profile_and_routines(mary_row["id"])

    # ==================== GERENCIAMENTO MULTI-USUÁRIO ====================
    @classmethod
    def list_users(cls) -> List[Dict[str, Any]]:
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY id ASC")
            return [dict(r) for r in cursor.fetchall()]

    @classmethod
    def get_active_user(cls, user_id: Optional[int] = None) -> Dict[str, Any]:
        target_uid = user_id or cls.get_active_user_id()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (target_uid,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            cursor.execute("SELECT * FROM users ORDER BY id ASC LIMIT 1")
            first = cursor.fetchone()
            if first:
                cls.set_active_user_id(first["id"])
                return dict(first)
            return {"id": 1, "name": "Matheus", "username": "matheus", "role": "aluno", "color_hex": "#FFFFFF"}

    @classmethod
    def switch_user(cls, user_id: int) -> Dict[str, Any]:
        cls.set_active_user_id(user_id)
        # Garante perfil criado para o usuário
        cls._ensure_profile_for_user(user_id)
        # Garante rotinas criadas para o usuário
        cls._ensure_routines_for_user(user_id)
        return cls.get_active_user()

    @classmethod
    def create_user(cls, name: str, username: str, role: str = "aluno", avatar_icon: str = "person", color_hex: str = "#00FFA3") -> int:
        clean_user = username.strip().lower().replace(" ", "_")
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO users (name, username, role, avatar_icon, color_hex)
            VALUES (?, ?, ?, ?, ?)
            """, (name.strip(), clean_user, role, avatar_icon, color_hex))
            user_id = cursor.lastrowid
            conn.commit()
        cls._ensure_profile_for_user(user_id, name=name.strip())
        cls._ensure_routines_for_user(user_id)
        return user_id

    @classmethod
    def _ensure_profile_for_user(cls, user_id: int, name: str = ""):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM athlete_profile WHERE user_id = ?", (user_id,))
            if cursor.fetchone()[0] == 0:
                user_name = name or f"Usuário #{user_id}"
                cursor.execute("""
                INSERT INTO athlete_profile (user_id, name, age, sex, height_cm, weight_kg, goal, activity_level)
                VALUES (?, ?, 26, 'M', 178.0, 78.5, 'hipertrofia', 'intenso')
                """, (user_id, user_name))
                conn.commit()

    @classmethod
    def _seed_mary_profile_and_routines(cls, mary_id: int):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            # 1. Perfil
            cursor.execute("SELECT COUNT(*) FROM athlete_profile WHERE user_id = ?", (mary_id,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                INSERT INTO athlete_profile (
                    user_id, name, age, sex, height_cm, weight_kg, goal, activity_level,
                    target_weight_kg, target_weeks, training_days_week, session_minutes,
                    experience_level, joint_pain, diet_strategy, daily_calories_target,
                    daily_protein_target, daily_water_target_ml, recommended_routine,
                    priority_muscle_focus
                )
                VALUES (?, 'Mary Ellen da Silva Alves Barbosa', 28, 'F', 160.0, 62.0, 'hipertrofia', 'intenso',
                        60.0, 12, 3, 60, 'iniciante', 'nenhuma', 'equilibrada', 1850.0, 135.0, 2500, 'ABC Feminino', 'Inferiores e Glúteos')
                """, (mary_id,))

            # 2. Biblioteca de Exercícios da Ficha
            mary_exercises_lib = [
                ("Bicicleta Ergométrica (Aquecimento)", "Aquecimento", "Cardiorrespiratório e Membros Inferiores", "Panturrilhas, Quadríceps", "Bicicleta Estacionária",
                 "Ajuste o selim na altura da crista ilíaca. Pedale em cadência moderada e constante para elevar a temperatura corporal e lubrificar as articulações dos joelhos e quadris.",
                 "Aquecimento cardiovascular prévio aumenta o fluxo sanguíneo muscular, previne lesões articulares e prepara o sistema neuromuscular.",
                 "Usar carga excessiva antes do treino principal; pedalar com joelhos desalinhados ou postura encurvada.", "directions_bike"),
                ("Leg Press Horizontal", "Pernas", "Quadríceps e Glúteos", "Adutores, Isquiotibiais", "Máquina Leg Press Horizontal",
                 "Apoie os pés na largura dos ombros no meio da plataforma. Destrave com segurança e desça controladamente até formar um ângulo de 90° nos joelhos sem tirar a lombar do encosto. Empurre pelos calcanhares sem travar os joelhos em hiperextensão.",
                 "Constrói volume e tônus muscular nas coxas e glúteos em cadeia cinética fechada com estabilização total da coluna.",
                 "Tirar a lombar ou glúteos do assento na descida máxima; estalar os joelhos no topo; colocar pés muito baixos gerando sobrecarga patelar.", "fitness_center"),
                ("Cadeira Adutora", "Pernas", "Adutores da Coxa", "Grácil, Pectíneo", "Cadeira Adutora",
                 "Sente-se com a coluna totalmente apoiada no encosto. Abra as pernas na amplitude confortável e feche com força controlada aproximando os joelhos no centro. Segure 1 segundo no pico de contração.",
                 "Fortalece a parte interna da coxa, melhorando o desenho muscular, a estabilidade pélvica e a harmonia dos membros inferiores.",
                 "Soltar o peso batendo as placas no retorno; arquear a coluna para frente; amplitude insuficiente.", "fitness_center"),
                ("Panturrilha em Pé Livre", "Pernas", "Panturrilha (Gastrocnêmio e Sóleo)", "Tibial Posterior", "Solo / Step",
                 "Apoie a ponta dos pés em um degrau ou step. Desça os calcanhares para alongar a fáscia e empurre o solo até a ponta máxima dos pés, esmagando a panturrilha por 1 a 2 segundos no topo.",
                 "Desenvolve a firmeza e vascularização da batata da perna, essencial para circulação venosa e suporte na pisada.",
                 "Fazer movimentos rápidos e saltitantes usando elasticidade de tendão em vez de força muscular; flexionar os joelhos durante a subida.", "accessibility"),
                ("Puxada Alta pela Frente (Polia)", "Costas", "Grande Dorsal", "Bíceps, Deltoide Posterior, Romboides", "Polia / Pulley Alto",
                 "Pegada aberta pronada. Faça a retração escapular puxando a barra em direção à parte superior do peitoral, mantendo o peito estufado e cotovelos apontando para baixo e para trás. Retorne controlando o peso.",
                 "Alarga a silhueta das costas criando a linha em V (cintura visualmente mais fina) e melhora a postura dos ombros.",
                 "Balançar o tronco para trás pegando impulso; puxar a barra na nuca; encolher os ombros.", "fitness_center"),
                ("Remada na Máquina", "Costas", "Romboides e Dorsal", "Trapézio Médio, Bíceps", "Máquina de Remada Sentada",
                 "Apoie o peito no apoio acolchoado. Puxe os pegadores retraindo as escápulas e apertando o meio das costas. Não deixe os ombros subirem em direção às orelhas.",
                 "Desenvolve densidade e espessura das costas, corrigindo desvios posturais causados pelo uso excessivo de celular e computadores.",
                 "Descolar o peito do apoio; hiperestender a coluna lombar; puxar com o punho em vez das costas.", "fitness_center"),
                ("Supino Reto com Halteres", "Peito", "Peitoral Maior", "Deltoide Anterior, Tríceps", "Halteres e Banco Reto",
                 "Deite no banco com escápulas travadas e pés firmes no chão. Desça os halteres de forma controlada até a linha do peito mantendo os cotovelos a 45-60° do tronco. Empurre convergindo levemente sem bater os halteres.",
                 "Permite liberdade articular total para os ombros e punhos, garantindo hipertrofia peitoral com máxima segurança.",
                 "Abrir demais os cotovelos a 90° estressando os ombros; tirar os pés do chão; descer de forma descontrolada.", "fitness_center"),
                ("Elevação Frontal + Lateral (Bi-set)", "Ombros", "Deltoide Lateral e Anterior", "Trapézio Superior", "Halteres",
                 "Execute primeiro a elevação lateral elevando os halteres até a linha dos ombros com cotovelos levemente flexionados. Em seguida, sem descanso, execute a elevação frontal elevando os braços à frente até a altura dos olhos.",
                 "Bi-set de alta intensidade para desenho e definição 3D dos ombros, lapidando as porções anterior e medial.",
                 "Jogar o quadril e balançar a coluna lombar; subir acima da linha dos ombros comprimindo o manguito.", "fitness_center"),
                ("Tríceps na Polia (Corda)", "Braços", "Tríceps Braquial", "Antebraço", "Polia Alta com Corda",
                 "Cotovelos colados ao lado das costelas. Estenda os braços para baixo até o travamento e abra as pontas da corda para fora no final do movimento para contração máxima da cabeça lateral do tríceps.",
                 "Tonifica e elimina a flacidez na região posterior do braço ('músculo do tchauzinho'), conferindo firmeza e definição.",
                 "Abrir os cotovelos durante o movimento; jogar os ombros para frente; usar peso que impeça a extensão completa.", "fitness_center"),
                ("Stiff (Barra Livre ou Halteres)", "Pernas", "Glúteos e Posteriores de Coxa", "Eretores da Espinha", "Barra Livre ou Halteres",
                 "Pés na largura dos quadris, joelhos semi-flexionados e travados nesse ângulo. Empurre o quadril para trás enquanto desce a carga rente às pernas mantendo a coluna 100% reta e peito aberto. Suba contraindo fortemente os glúteos.",
                 "Exercício de ouro para empinar os glúteos e alongar sob tensão os isquiotibiais, gerando hipertrofia de alto nível.",
                 "Arredondar a coluna lombar; flexionar os joelhos como se fosse um agachamento; afastar o peso do corpo.", "fitness_center"),
                ("Agachamento Sumô", "Pernas", "Glúteos e Adutores", "Quadríceps", "Halter ou Barra Smith",
                 "Pés afastados além da linha dos ombros com pontas viradas para fora a 45°. Agache direcionando os joelhos na mesma direção dos pés, mantendo o tronco ereto e o abdômen travado. Empurre pelo chão ativando glúteos e adutores.",
                 "Recruta intensamente o glúteo máximo e a face medial das coxas, desenhando a musculatura inferior com conforto articular.",
                 "Deixar os joelhos desabarem para dentro (valgo dinâmico); curvar a coluna lombar para frente.", "fitness_center"),
                ("Cadeira Abdutora", "Pernas", "Glúteo Médio e Mínimo", "Tensor da Fáscia Lata", "Cadeira Abdutora",
                 "Sente-se com o tronco ereto ou levemente inclinado para frente para maior ativação do glúteo superior. Abra as pernas com força máxima contra a resistência e segure 1 segundo no pico antes de retornar devagar.",
                 "Proporciona o preenchimento lateral dos glúteos ('efeito ampulheta') e fortalece os estabilizadores da pelve.",
                 "Usar peso excessivo sem abrir a amplitude total; bater os pesos no retorno perdendo a tensão contínua.", "fitness_center")
            ]
            for ex in mary_exercises_lib:
                cursor.execute("""
                INSERT OR IGNORE INTO exercise_library (name, category, primary_muscle, secondary_muscles, equipment, execution_guide, why_do_it, common_mistakes, icon_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, ex)

            # 3. Rotinas de Mary
            cursor.execute("SELECT COUNT(*) FROM workout_routines WHERE user_id = ?", (mary_id,))
            if cursor.fetchone()[0] == 0:
                mary_routines = [
                    ("Treino A - Inferiores 1 (Quadríceps e Adutores)", "Inferiores", "Foco em quadríceps, adutores e panturrilha com pré-aquecimento", "#FFFFFF", [
                        ("Bicicleta Ergométrica (Aquecimento)", 1, "5-10 min", 0.0, 0),
                        ("Leg Press Horizontal", 3, "10-12", 40.0, 90),
                        ("Cadeira Extensora", 3, "12-15", 25.0, 60),
                        ("Cadeira Adutora", 3, "12-15", 30.0, 60),
                        ("Panturrilha em Pé Livre", 3, "15-20", 0.0, 45),
                    ]),
                    ("Treino B - Superiores (Costas, Peito, Ombros e Braços)", "Superiores", "Foco em postura, tronco definido, tônus nos braços e deltoides", "#FFFFFF", [
                        ("Puxada Alta pela Frente (Polia)", 3, "10-12", 25.0, 60),
                        ("Remada na Máquina", 3, "10-12", 20.0, 60),
                        ("Supino Reto com Halteres", 3, "10-12", 6.0, 60),
                        ("Elevação Frontal + Lateral (Bi-set)", 3, "10-12", 4.0, 60),
                        ("Tríceps na Polia (Corda)", 3, "12-15", 15.0, 45),
                    ]),
                    ("Treino C - Inferiores 2 (Posteriores e Glúteos)", "Glúteos & Posteriores", "Foco em cadeia posterior, glúteo médio e máximo, e isquiotibiais", "#FFFFFF", [
                        ("Bicicleta Ergométrica (Aquecimento)", 1, "5-10 min", 0.0, 0),
                        ("Stiff (Barra Livre ou Halteres)", 3, "10-12", 20.0, 90),
                        ("Agachamento Sumô", 3, "10-12", 16.0, 90),
                        ("Cadeira Flexora", 3, "12-15", 25.0, 60),
                        ("Cadeira Abdutora", 3, "12-15", 35.0, 60),
                    ])
                ]
                for r_name, r_cat, r_desc, r_col, ex_list in mary_routines:
                    cursor.execute("""
                    INSERT INTO workout_routines (user_id, name, category, description, color_hex)
                    VALUES (?, ?, ?, ?, ?)
                    """, (mary_id, r_name, r_cat, r_desc, r_col))
                    rid = cursor.lastrowid
                    for ex_name, s, r, w, rest in ex_list:
                        cursor.execute("""
                        INSERT INTO routine_exercises (routine_id, exercise_name, target_sets, target_reps, target_weight, rest_seconds)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, (rid, ex_name, s, r, w, rest))

            conn.commit()

    @classmethod
    def _ensure_routines_for_user(cls, user_id: int):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM workout_routines WHERE user_id = ?", (user_id,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
                user_row = cursor.fetchone()
                if user_row and user_row["username"] == "mary":
                    cls._seed_mary_profile_and_routines(user_id)
                else:
                    cls.apply_coach_routine_preset("ABC", user_id=user_id)

    @classmethod
    def _ensure_initial_profile(cls):
        cls._ensure_profile_for_user(1, name="Matheus")

    @classmethod
    def get_athlete_profile(cls, user_id: Optional[int] = None) -> Dict[str, Any]:
        target_uid = user_id or cls.get_active_user_id()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM athlete_profile WHERE user_id = ? ORDER BY id ASC LIMIT 1", (target_uid,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            # Fallback para primeiro perfil
            cursor.execute("SELECT * FROM athlete_profile ORDER BY id ASC LIMIT 1")
            first = cursor.fetchone()
            if first:
                return dict(first)
            return {
                "name": "Matheus", "age": 26, "sex": "M",
                "height_cm": 178.0, "weight_kg": 78.5, "goal": "hipertrofia",
                "activity_level": "intenso", "devworld_api_key": "", "devworld_base_url": "https://api.devworld.com.br/v1",
                "target_weight_kg": 75.0, "target_weeks": 12, "training_days_week": 4,
                "daily_calories_target": 2400, "daily_protein_target": 160, "daily_water_target_ml": 3000
            }

    @classmethod
    def update_athlete_profile(cls, name: str, age: int, sex: str, height: float, weight: float, goal: str, activity: str, api_key: str = None, base_url: str = None, user_id: Optional[int] = None):
        target_uid = user_id or cls.get_active_user_id()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE athlete_profile
            SET name = ?, age = ?, sex = ?, height_cm = ?, weight_kg = ?, goal = ?, activity_level = ?,
                devworld_api_key = COALESCE(?, devworld_api_key),
                devworld_base_url = COALESCE(?, devworld_base_url)
            WHERE user_id = ?
            """, (name, age, sex, height, weight, goal, activity, api_key, base_url, target_uid))
            conn.commit()

    @classmethod
    def save_goals(cls, goal: str, target_weight: float, target_weeks: int, days_week: int, session_mins: int, experience: str, joint_pain: str, diet_strategy: str, user_id: Optional[int] = None, muscle_focus: str = "equilibrado") -> Dict[str, Any]:
        """Calcula metas nutricionais e rotina recomendada a partir do formulário de objetivos e persiste no perfil."""
        target_uid = user_id or cls.get_active_user_id()
        profile = cls.get_athlete_profile(target_uid)
        
        weight = float(profile.get("weight_kg", 78.5))
        height = float(profile.get("height_cm", 178.0))
        age = int(profile.get("age", 26))
        sex = profile.get("sex", "M").upper()

        # Fórmula de Mifflin-St Jeor
        if sex == "M":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        activity_factors = {
            "sedentario": 1.2,
            "leve": 1.375,
            "moderado": 1.55,
            "intenso": 1.725,
            "muito_intenso": 1.9
        }
        activity = profile.get("activity_level", "intenso")
        tdee = bmr * activity_factors.get(activity, 1.55)

        # Ajustes por objetivo e foco muscular
        goal_lower = goal.lower()
        focus_lower = (muscle_focus or "").lower()

        if "hipertrofia" in goal_lower:
            target_calories = round(tdee + 350, 0)
            protein_g = round(weight * 2.2, 0)
        elif "cutting" in goal_lower or "emagrecimento" in goal_lower or "definicao" in goal_lower:
            target_calories = round(max(1400, tdee - 450), 0)
            protein_g = round(weight * 2.4, 0)
        elif "forca" in goal_lower:
            target_calories = round(tdee + 200, 0)
            protein_g = round(weight * 2.0, 0)
        else: # Recomposição / Manutenção
            target_calories = round(tdee, 0)
            protein_g = round(weight * 2.2, 0)

        # Calibração da rotina ideal com base no foco e frequência
        if "superior" in focus_lower or "upper" in focus_lower:
            recommended_routine = "UpperLower" if days_week <= 4 else "PPL"
        elif "inferior" in focus_lower:
            recommended_routine = "ABC"
        elif "forca" in goal_lower or days_week == 4:
            recommended_routine = "UpperLower"
        elif days_week >= 5:
            recommended_routine = "PPL"
        else:
            recommended_routine = "ABC"

        water_ml = int(weight * 40)

        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE athlete_profile
            SET goal = ?, target_weight_kg = ?, target_weeks = ?, training_days_week = ?,
                session_minutes = ?, experience_level = ?, joint_pain = ?, diet_strategy = ?,
                daily_calories_target = ?, daily_protein_target = ?, daily_water_target_ml = ?,
                recommended_routine = ?
            WHERE user_id = ?
            """, (goal, target_weight, target_weeks, days_week, session_mins, experience, joint_pain, diet_strategy, target_calories, protein_g, water_ml, recommended_routine, target_uid))
            conn.commit()

        return {
            "goal": goal,
            "bmr": round(bmr, 0),
            "tdee": round(tdee, 0),
            "daily_calories": target_calories,
            "daily_protein": protein_g,
            "daily_water_ml": water_ml,
            "recommended_routine": recommended_routine
        }

    # ==================== EXERCÍCIOS ====================
    @classmethod
    def get_exercises(cls, category: Optional[str] = None, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM exercise_library WHERE 1=1"
            params = []
            if category and category != "Todos":
                query += " AND category = ?"
                params.append(category)
            if search_query:
                query += " AND (name LIKE ? OR primary_muscle LIKE ?)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])
            query += " ORDER BY category, name ASC"
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

    @classmethod
    def get_exercise_by_name(cls, name: str) -> Optional[Dict[str, Any]]:
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM exercise_library WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # ==================== ROTINAS DE TREINO & PERSONAL ====================
    EXERCISE_SUBSTITUTIONS = {
        "Supino Reto com Barra": [
            {
                "alternative_name": "Supino Inclinado com Halteres",
                "reason": "Barra Ocupada: Permite maior amplitude de movimento e rotação natural dos punhos.",
                "equipment": "Halteres / Banco",
                "primary_muscle": "Peitoral Maior",
                "execution_tips": "Mantenha a pegada semi-neutra (45°) para aliviar o manguito rotador."
            },
            {
                "alternative_name": "Crucifixo na Polia (Crossover)",
                "reason": "Dor no Ombro / Isolamento: Elimina o estresse nos tríceps e foca na tensão contínua do peito.",
                "equipment": "Polia Dupla",
                "primary_muscle": "Peitoral Maior",
                "execution_tips": "Feche apertando o meio do peito no pico de contração."
            },
            {
                "alternative_name": "Voador / Peck Deck",
                "reason": "Segurança / Isolamento: Ideal para buscar a falha muscular sem risco de prender a barra no peito.",
                "equipment": "Máquina Peck Deck",
                "primary_muscle": "Peitoral Maior",
                "execution_tips": "Mantenha escápulas retraídas e cotovelos na linha média do peito."
            }
        ],
        "Supino Inclinado com Halteres": [
            {
                "alternative_name": "Crossover Polia Baixa",
                "reason": "Halteres Ocupados: Mesma linha de tração ascendente com tensão contínua nas fibras claviculares.",
                "equipment": "Polia Baixa",
                "primary_muscle": "Peitoral Superior",
                "execution_tips": "Traga as mãos convergindo na altura dos olhos."
            },
            {
                "alternative_name": "Supino Reto com Barra",
                "reason": "Sobrecarga Progressiva: Permite elevar cargas com controle escapular rígido.",
                "equipment": "Barra Olímpica",
                "primary_muscle": "Peitoral Maior",
                "execution_tips": "Desça no terço inferior do esterno mantendo os pés firmes."
            }
        ],
        "Cadeira Extensora": [
            {
                "alternative_name": "Leg Press 45°",
                "reason": "Máquina Ocupada: Distribui a sobrecarga em cadeia cinética fechada com segurança patelar.",
                "equipment": "Máquina Leg Press",
                "primary_muscle": "Quadríceps e Glúteos",
                "execution_tips": "Pés na linha média, amplitude de 90° sem desgrudar a pelve do encosto."
            },
            {
                "alternative_name": "Agachamento Livre com Barra",
                "reason": "Construção de Força: Exercício composto funcional com máximo recrutamento sistêmico.",
                "equipment": "Barra / Gaiola",
                "primary_muscle": "Quadríceps, Glúteos e Core",
                "execution_tips": "Foque no controle de descida (excêntrica de 3 segundos)."
            }
        ],
        "Agachamento Livre com Barra": [
            {
                "alternative_name": "Leg Press 45°",
                "reason": "Gaiola Ocupada / Desconforto Lombar: Elimina compressão axial direta na coluna vertebral.",
                "equipment": "Máquina Leg Press",
                "primary_muscle": "Quadríceps e Glúteos",
                "execution_tips": "Não descole a lombar do encosto no ponto mais baixo."
            },
            {
                "alternative_name": "Cadeira Extensora",
                "reason": "Isolamento Específico: Foco total no reto femoral sem fadiga cardiorrespiratória.",
                "equipment": "Máquina Extensora",
                "primary_muscle": "Quadríceps",
                "execution_tips": "Segure 1 segundo na contração máxima no topo."
            }
        ],
        "Puxada Frontal na Polia (Pulley)": [
            {
                "alternative_name": "Pull Down na Polia Alta",
                "reason": "Pulley Ocupado / Fadiga no Bíceps: Isola a grande dorsal sem usar a flexão dos braços.",
                "equipment": "Polia Alta / Corda",
                "primary_muscle": "Latíssimo do Dorso",
                "execution_tips": "Cotovelos travados em leve flexão durante todo o arco do movimento."
            },
            {
                "alternative_name": "Remada Curvada com Barra",
                "reason": "Densidade / Sobrecarga: Constrói espessura lombar e dorsal completa.",
                "equipment": "Barra Livre",
                "primary_muscle": "Latíssimo e Romboides",
                "execution_tips": "Tronco a 45°, puxe em direção ao umbigo esmagando as costas."
            }
        ],
        "Remada Curvada com Barra": [
            {
                "alternative_name": "Remada Cavalinho (Barra T)",
                "reason": "Desconforto Lombar: Apoio fixo que protege eretores da espinha e foca na espessura dorsal.",
                "equipment": "Máquina Barra T",
                "primary_muscle": "Dorsal e Romboides",
                "execution_tips": "Puxe em direção ao abdômen esmagando as escápulas."
            },
            {
                "alternative_name": "Remada Baixa no Triângulo",
                "reason": "Máquina Livre / Controle: Estabilidade sentada para focar na retração escapular pura.",
                "equipment": "Polia Baixa / Triângulo",
                "primary_muscle": "Latíssimo Médio",
                "execution_tips": "Alongue na volta sem jogar o tronco para a frente."
            }
        ],
        "Desenvolvimento com Halteres": [
            {
                "alternative_name": "Elevação Lateral com Halteres",
                "reason": "Desconforto Articular / Foco Lateral: Enfatiza a largura visual dos ombros sem compressão no tríceps.",
                "equipment": "Halteres",
                "primary_muscle": "Deltoide Lateral",
                "execution_tips": "Cotovelos lideram a subida até a altura do ombro."
            },
            {
                "alternative_name": "Elevação Lateral na Polia",
                "reason": "Tensão Constante: O cabo não perde tensão no início do movimento como os halteres.",
                "equipment": "Polia Baixa",
                "primary_muscle": "Deltoide Lateral",
                "execution_tips": "Incline ligeiramente o tronco para manter tração contínua."
            }
        ],
        "Mesa Flexora": [
            {
                "alternative_name": "Stiff com Barra / Halteres",
                "reason": "Máquina Ocupada: Foco na cadeia posterior em posição de estiramento profundo do quadril.",
                "equipment": "Halteres ou Barra",
                "primary_muscle": "Isquiotibiais e Glúteo",
                "execution_tips": "Mantenha coluna neutra e jogue o quadril para trás."
            }
        ],
        "Tríceps Corda na Polia Alta": [
            {
                "alternative_name": "Tríceps Testa com Barra W",
                "reason": "Polia Ocupada: Construtor clássico de força e espessura para a cabeça longa do tríceps.",
                "equipment": "Barra W / Banco",
                "primary_muscle": "Tríceps",
                "execution_tips": "Braços levemente inclinados para trás em 75°."
            },
            {
                "alternative_name": "Tríceps Francês Unilateral",
                "reason": "Estiramento Máximo: Trabalha o tríceps em máxima flexão de ombro gerando alta tensão mecânica.",
                "equipment": "Halter",
                "primary_muscle": "Tríceps Cabeça Longa",
                "execution_tips": "Desça o halter atrás da nuca sentindo o alongamento do tendão."
            }
        ],
        "Rosca Direta com Barra W": [
            {
                "alternative_name": "Rosca Martelo com Halteres",
                "reason": "Dor no Punho: Pegada neutra anatômica que alivia o antebraço e desenvolve o músculo braquial.",
                "equipment": "Halteres",
                "primary_muscle": "Braquial e Bíceps",
                "execution_tips": "Cotovelos colados ao lado do tronco sem balanço."
            },
            {
                "alternative_name": "Rosca Scott na Máquina / Banco",
                "reason": "Isolamento Estrito: Elimina qualquer trapaça ou impulso lombar.",
                "equipment": "Banco Scott",
                "primary_muscle": "Bíceps Cabeça Curta",
                "execution_tips": "Controle a fase excêntrica até a extensão quase total."
            }
        ]
    }

    @classmethod
    def get_exercise_substitutions(cls, exercise_name: str) -> List[Dict[str, Any]]:
        """Retorna alternativas biomecanicamente validadas para o exercício selecionado."""
        if exercise_name in cls.EXERCISE_SUBSTITUTIONS:
            return cls.EXERCISE_SUBSTITUTIONS[exercise_name]
        
        # Fallback inteligente se o exercício não tiver preset manual: busca por grupo muscular
        ex = cls.get_exercise_by_name(exercise_name)
        if ex:
            cat = ex.get("category", "")
            others = cls.get_exercises(category=cat)
            results = []
            for o in others:
                if o["name"] != exercise_name and len(results) < 3:
                    results.append({
                        "alternative_name": o["name"],
                        "reason": f"Mesmo grupo muscular ({cat}): Excelente substituição biomecânica para manter a intensidade do treino.",
                        "equipment": o.get("equipment", "Equipamento Padrão"),
                        "primary_muscle": o.get("primary_muscle", cat),
                        "execution_tips": "Execute com 3 a 4 séries buscando 8 a 12 repetições."
                    })
            return results
        return []

    @classmethod
    def swap_routine_exercise(cls, routine_id: int, old_exercise_name: str, new_exercise_name: str) -> bool:
        """Troca um exercício de uma rotina por uma recomendação do personal."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE routine_exercises
            SET exercise_name = ?
            WHERE routine_id = ? AND exercise_name = ?
            """, (new_exercise_name, routine_id, old_exercise_name))
            conn.commit()
            return cursor.rowcount > 0

    @classmethod
    def apply_coach_routine_preset(cls, preset_name: str, user_id: Optional[int] = None) -> bool:
        """Aplica uma prescrição completa do Treinador para o usuário ativo."""
        target_uid = user_id or cls.get_active_user_id()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            # Deleta rotinas antigas do usuário
            cursor.execute("SELECT id FROM workout_routines WHERE user_id = ?", (target_uid,))
            old_ids = [r["id"] for r in cursor.fetchall()]
            for oid in old_ids:
                cursor.execute("DELETE FROM routine_exercises WHERE routine_id = ?", (oid,))
            cursor.execute("DELETE FROM workout_routines WHERE user_id = ?", (target_uid,))

            if preset_name.upper() == "PPL":
                routines = [
                    ("Treino 1 - Push (Peito, Ombros e Tríceps)", "Push", "Prescrição Treinador: Hipertrofia de Empurrar", "#FFFFFF", [
                        ("Supino Reto com Barra", 4, "8-10", 60.0, 90),
                        ("Supino Inclinado com Halteres", 4, "10-12", 24.0, 90),
                        ("Crucifixo na Polia (Crossover)", 3, "12-15", 15.0, 60),
                        ("Desenvolvimento com Halteres", 4, "8-10", 18.0, 90),
                        ("Elevação Lateral com Halteres", 4, "12-15", 10.0, 60),
                        ("Tríceps Corda na Polia Alta", 4, "10-12", 25.0, 60),
                    ]),
                    ("Treino 2 - Pull (Costas, Bíceps e Trapézio)", "Pull", "Prescrição Treinador: Densidade e Asa de Costas", "#FFFFFF", [
                        ("Puxada Frontal na Polia (Pulley)", 4, "8-10", 55.0, 90),
                        ("Remada Curvada com Barra", 4, "8-10", 50.0, 90),
                        ("Remada Baixa no Triângulo", 3, "10-12", 45.0, 60),
                        ("Crucifixo Invertido no Peck Deck", 4, "12-15", 35.0, 60),
                        ("Rosca Direta com Barra W", 4, "8-10", 25.0, 60),
                        ("Rosca Martelo com Halteres", 3, "10-12", 14.0, 60),
                    ]),
                    ("Treino 3 - Legs (Pernas Completas & Abdômen)", "Legs", "Prescrição Treinador: Força Máxima de Inferiores", "#FFFFFF", [
                        ("Agachamento Livre com Barra", 4, "6-8", 80.0, 120),
                        ("Leg Press 45°", 4, "10-12", 160.0, 90),
                        ("Cadeira Extensora", 3, "12-15", 40.0, 60),
                        ("Stiff com Barra / Halteres", 4, "8-10", 50.0, 90),
                        ("Mesa Flexora", 4, "10-12", 35.0, 60),
                        ("Panturrilha em Pé na Máquina", 5, "15-20", 50.0, 45),
                        ("Abdominal na Polia Alta (Crunch)", 4, "15-20", 30.0, 60),
                    ])
                ]
            elif preset_name.upper() == "UPPERLOWER":
                routines = [
                    ("Treino 1 - Upper (Membros Superiores)", "Upper", "Prescrição Treinador: Peito, Costas, Braços e Ombros", "#FFFFFF", [
                        ("Supino Reto com Barra", 4, "8-10", 60.0, 90),
                        ("Remada Curvada com Barra", 4, "8-10", 50.0, 90),
                        ("Desenvolvimento com Halteres", 3, "10-12", 18.0, 90),
                        ("Puxada Frontal na Polia (Pulley)", 3, "10-12", 50.0, 60),
                        ("Rosca Direta com Barra W", 3, "10-12", 24.0, 60),
                        ("Tríceps Testa com Barra W", 3, "10-12", 22.0, 60),
                    ]),
                    ("Treino 2 - Lower (Membros Inferiores & Core)", "Lower", "Prescrição Treinador: Coxas, Glúteos e Abdômen", "#FFFFFF", [
                        ("Agachamento Livre com Barra", 4, "8-10", 75.0, 120),
                        ("Leg Press 45°", 4, "10-12", 150.0, 90),
                        ("Stiff com Barra / Halteres", 4, "10-12", 45.0, 90),
                        ("Mesa Flexora", 3, "12-15", 35.0, 60),
                        ("Panturrilha em Pé na Máquina", 4, "15-20", 45.0, 45),
                        ("Prancha Abdominal Isométrica", 3, "60s", 0.0, 45),
                    ])
                ]
            else: # Padrão ABC
                routines = [
                    ("Treino A - Peito, Tríceps e Deltoide Anterior", "Push", "Foco em empurrar e densidade peitoral", "#FFFFFF", [
                        ("Supino Reto com Barra", 4, "8-10", 60.0, 90),
                        ("Supino Inclinado com Halteres", 4, "10-12", 24.0, 90),
                        ("Crucifixo na Polia (Crossover)", 3, "12-15", 15.0, 60),
                        ("Desenvolvimento com Halteres", 4, "8-10", 18.0, 90),
                        ("Tríceps Corda na Polia Alta", 4, "10-12", 25.0, 60),
                    ]),
                    ("Treino B - Costas, Bíceps e Trapézio", "Pull", "Foco em puxadas e largura dorsal", "#FFFFFF", [
                        ("Puxada Frontal na Polia (Pulley)", 4, "8-10", 55.0, 90),
                        ("Remada Curvada com Barra", 4, "8-10", 50.0, 90),
                        ("Remada Baixa no Triângulo", 3, "10-12", 45.0, 60),
                        ("Crucifixo Invertido no Peck Deck", 4, "12-15", 35.0, 60),
                        ("Rosca Direta com Barra W", 4, "8-10", 25.0, 60),
                    ]),
                    ("Treino C - Pernas, Ombros Lateral/Posterior & Abdômen", "Legs", "Foco em membros inferiores e deltoides", "#FFFFFF", [
                        ("Agachamento Livre com Barra", 4, "8-10", 80.0, 120),
                        ("Leg Press 45°", 4, "10-12", 160.0, 90),
                        ("Cadeira Extensora", 3, "12-15", 40.0, 60),
                        ("Stiff com Barra / Halteres", 4, "8-10", 50.0, 90),
                        ("Elevação Lateral com Halteres", 4, "12-15", 10.0, 60),
                        ("Abdominal na Polia Alta (Crunch)", 4, "15-20", 30.0, 60),
                    ])
                ]

            for r_name, r_cat, r_desc, r_col, ex_list in routines:
                cursor.execute("""
                INSERT INTO workout_routines (user_id, name, category, description, color_hex)
                VALUES (?, ?, ?, ?, ?)
                """, (target_uid, r_name, r_cat, r_desc, r_col))
                rid = cursor.lastrowid
                for ex_name, s, r, w, rest in ex_list:
                    cursor.execute("""
                    INSERT INTO routine_exercises (routine_id, exercise_name, target_sets, target_reps, target_weight, rest_seconds)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (rid, ex_name, s, r, w, rest))

            conn.commit()
            return True

    @classmethod
    def get_exercise_gif(cls, name: str) -> str:
        """Retorna a URL do GIF ou demonstração animada do exercício."""
        visuals = {
            # Exercícios Gerais & Masculino
            "Supino Reto com Barra": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/pectorals/barbell-bench-press.gif",
            "Supino Inclinado com Halteres": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/pectorals/dumbbell-incline-bench-press.gif",
            "Crucifixo na Polia (Crossover)": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/pectorals/cable-standing-fly.gif",
            "Crossover Polia Baixa": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/pectorals/cable-low-fly.gif",
            "Voador / Peck Deck": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/pectorals/lever-seated-fly.gif",
            "Paralelas (Dips) com Foco em Peitoral": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/pectorals/chest-dip-on-straight-bar.gif",
            "Desenvolvimento com Halteres": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/delts/dumbbell-seated-shoulder-press-parallel-grip.gif",
            "Elevação Lateral com Halteres": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/delts/dumbbell-lateral-raise.gif",
            "Elevação Lateral na Polia": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/delts/cable-lateral-raise.gif",
            "Desenvolvimento Militar com Barra": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/delts/barbell-seated-overhead-press.gif",
            "Crucifixo Invertido no Peck Deck": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/delts/lever-seated-reverse-fly.gif",
            "Tríceps Corda na Polia Alta": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/triceps/cable-pushdown-with-rope-attachment.gif",
            "Tríceps Testa com Barra W": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/triceps/barbell-lying-triceps-extension-skull-crusher.gif",
            "Tríceps Francês Unilateral": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/triceps/dumbbell-standing-triceps-extension.gif",
            "Puxada Frontal na Polia (Pulley)": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/lats/cable-lat-pulldown-full-range-of-motion.gif",
            "Pull Down na Polia Alta": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/lats/cable-pushdown-straight-arm-v-2.gif",
            "Remada Curvada com Barra": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/upper-back/barbell-bent-over-row.gif",
            "Remada Baixa no Triângulo": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/upper-back/cable-seated-row.gif",
            "Remada Cavalinho (Barra T)": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/upper-back/lever-t-bar-row.gif",
            "Remada Unilateral com Halter (Serrote)": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/upper-back/dumbbell-row.gif",
            "Rosca Direta com Barra W": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/biceps/barbell-curl.gif",
            "Rosca Martelo com Halteres": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/biceps/dumbbell-hammer-curl.gif",
            "Rosca Scott na Máquina / Banco": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/biceps/barbell-preacher-curl.gif",
            "Agachamento Livre com Barra": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/glutes/barbell-full-squat-back-pov.gif",
            "Leg Press 45°": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/glutes/sled-45-leg-press.gif",
            "Cadeira Extensora": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/quads/lever-leg-extension.gif",
            "Agachamento Búlgaro": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/quads/dumbbell-single-leg-split-squat.gif",
            "Stiff com Barra / Halteres": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/hamstrings/barbell-straight-leg-deadlift.gif",
            "Mesa Flexora": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/hamstrings/lever-lying-leg-curl.gif",
            "Cadeira Flexora": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/hamstrings/lever-seated-leg-curl.gif",
            "Elevação Pélvica com Barra": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/glutes/barbell-hip-thrust.gif",
            "Panturrilha em Pé na Máquina": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/calves/lever-standing-calf-raise.gif",
            "Abdominal na Polia Alta (Crunch)": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/abs/cable-kneeling-crunch.gif",
            "Elevação de Pernas na Barra Fixa": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/abs/hanging-leg-raise.gif",
            "Prancha Abdominal Isométrica": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/abs/bodyweight-incline-side-plank.gif",
            
            # Ficha de Treinos Mary Ellen & Feminino (Foto)
            "Bicicleta Ergométrica (Aquecimento)": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/cardio/stationary-bike-run-v-3.gif",
            "Leg Press Horizontal": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/glutes/lever-horizontal-one-leg-press.gif",
            "Cadeira Adutora": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/adductors/lever-seated-hip-adduction.gif",
            "Panturrilha em Pé Livre": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/calves/barbell-floor-calf-raise.gif",
            "Puxada Alta pela Frente (Polia)": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/lats/cable-pulldown.gif",
            "Remada na Máquina": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/upper-back/cable-low-seated-row.gif",
            "Supino Reto com Halteres": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/pectorals/dumbbell-bench-press.gif",
            "Elevação Frontal + Lateral (Bi-set)": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/delts/band-front-lateral-raise.gif",
            "Tríceps na Polia (Corda)": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/triceps/cable-pushdown-with-rope-attachment.gif",
            "Stiff (Barra Livre ou Halteres)": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/glutes/dumbbell-stiff-leg-deadlift.gif",
            "Agachamento Sumô": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/glutes/smith-sumo-squat.gif",
            "Cadeira Abdutora": "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/abductors/lever-seated-hip-abduction.gif",
        }
        return visuals.get(name, "https://raw.githubusercontent.com/JahelCuadrado/ExerciseGymGifsDB/main/pectorals/barbell-bench-press.gif")

    @classmethod
    def get_routines(cls, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        target_uid = user_id or cls.get_active_user_id()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workout_routines WHERE user_id = ? ORDER BY id ASC", (target_uid,))
            routines = [dict(r) for r in cursor.fetchall()]
            if not routines:
                # Se não houver rotinas ainda para o usuário, gera o preset padrão
                cls.apply_coach_routine_preset("ABC", user_id=target_uid)
                cursor.execute("SELECT * FROM workout_routines WHERE user_id = ? ORDER BY id ASC", (target_uid,))
                routines = [dict(r) for r in cursor.fetchall()]

            for r in routines:
                cursor.execute("""
                SELECT re.*, 
                       el.category as muscle_category,
                       el.primary_muscle,
                       el.secondary_muscles,
                       el.equipment,
                       el.execution_guide,
                       el.why_do_it,
                       el.common_mistakes
                FROM routine_exercises re
                LEFT JOIN exercise_library el ON re.exercise_name = el.name
                WHERE re.routine_id = ?
                ORDER BY re.id ASC
                """, (r["id"],))
                
                ex_list = []
                for row in cursor.fetchall():
                    item = dict(row)
                    item["gif_url"] = cls.get_exercise_gif(item["exercise_name"])
                    ex_list.append(item)
                r["exercises"] = ex_list

            return routines

    @classmethod
    def save_workout_session(cls, routine_name: str, duration_min: int, total_volume: float, sets: List[Dict[str, Any]], notes: str = "", user_id: Optional[int] = None) -> int:
        target_uid = user_id or cls.get_active_user_id()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO workout_sessions (user_id, routine_name, duration_minutes, total_volume_kg, notes)
            VALUES (?, ?, ?, ?, ?)
            """, (target_uid, routine_name, duration_min, total_volume, notes))
            session_id = cursor.lastrowid
            
            for s in sets:
                cursor.execute("""
                INSERT INTO session_sets (session_id, exercise_name, set_number, weight_kg, reps, rpe, completed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (session_id, s.get("exercise_name"), s.get("set_number", 1), s.get("weight_kg", 0), s.get("reps", 10), s.get("rpe", 8.0), 1))
            
            conn.commit()
            return session_id

    @classmethod
    def get_recent_workout_sessions(cls, limit: int = 10, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        target_uid = user_id or cls.get_active_user_id()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workout_sessions WHERE user_id = ? ORDER BY id DESC LIMIT ?", (target_uid, limit))
            return [dict(r) for r in cursor.fetchall()]

    # ==================== NUTRIÇÃO & ÁGUA ====================
    @classmethod
    def get_daily_nutrition(cls, target_date: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        target_uid = user_id or cls.get_active_user_id()
        if not target_date:
            target_date = str(date.today())
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT SUM(calories) as total_calories,
                   SUM(protein_g) as total_protein,
                   SUM(carbs_g) as total_carbs,
                   SUM(fat_g) as total_fat
            FROM nutrition_logs WHERE user_id = ? AND log_date = ?
            """, (target_uid, target_date))
            totals = cursor.fetchone()
            
            cursor.execute("SELECT * FROM nutrition_logs WHERE user_id = ? AND log_date = ? ORDER BY id ASC", (target_uid, target_date))
            meals = [dict(r) for r in cursor.fetchall()]

            cursor.execute("SELECT SUM(amount_ml) as total_water FROM water_logs WHERE user_id = ? AND log_date = ?", (target_uid, target_date))
            water_row = cursor.fetchone()
            total_water = water_row["total_water"] if water_row and water_row["total_water"] else 0

            return {
                "date": target_date,
                "total_calories": totals["total_calories"] or 0,
                "total_protein": totals["total_protein"] or 0,
                "total_carbs": totals["total_carbs"] or 0,
                "total_fat": totals["total_fat"] or 0,
                "total_water_ml": total_water,
                "meals": meals
            }

    @classmethod
    def add_meal(cls, meal_name: str, calories: float, protein: float, carbs: float, fat: float, log_date: Optional[str] = None, user_id: Optional[int] = None):
        target_uid = user_id or cls.get_active_user_id()
        if not log_date:
            log_date = str(date.today())
        meal_time = datetime.now().strftime("%H:%M")
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO nutrition_logs (user_id, log_date, meal_name, meal_time, calories, protein_g, carbs_g, fat_g)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (target_uid, log_date, meal_name, meal_time, calories, protein, carbs, fat))
            conn.commit()

    @classmethod
    def add_water(cls, amount_ml: int, log_date: Optional[str] = None, user_id: Optional[int] = None):
        target_uid = user_id or cls.get_active_user_id()
        if not log_date:
            log_date = str(date.today())
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO water_logs (user_id, log_date, amount_ml) VALUES (?, ?, ?)", (target_uid, log_date, amount_ml))
            conn.commit()

    # ==================== SAÚDE MENTAL & WELLNESS ====================
    @classmethod
    def get_today_wellness(cls, target_date: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        target_uid = user_id or cls.get_active_user_id()
        if not target_date:
            target_date = str(date.today())
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM daily_wellness WHERE user_id = ? AND log_date = ?", (target_uid, target_date))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {
                "log_date": target_date,
                "mood_score": 4,
                "stress_score": 2,
                "sleep_hours": 7.5,
                "energy_score": 4,
                "soreness_notes": "Sem dores articulares",
                "reflection_text": ""
            }

    @classmethod
    def save_wellness_log(cls, mood: int, stress: int, sleep: float, energy: int, soreness: str, reflection: str, target_date: Optional[str] = None, user_id: Optional[int] = None):
        target_uid = user_id or cls.get_active_user_id()
        if not target_date:
            target_date = str(date.today())
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM daily_wellness WHERE user_id = ? AND log_date = ?", (target_uid, target_date))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("""
                UPDATE daily_wellness
                SET mood_score = ?, stress_score = ?, sleep_hours = ?, energy_score = ?, soreness_notes = ?, reflection_text = ?
                WHERE id = ?
                """, (mood, stress, sleep, energy, soreness, reflection, existing["id"]))
            else:
                cursor.execute("""
                INSERT INTO daily_wellness (user_id, log_date, mood_score, stress_score, sleep_hours, energy_score, soreness_notes, reflection_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (target_uid, target_date, mood, stress, sleep, energy, soreness, reflection))
            conn.commit()

    # ==================== EVOLUÇÃO CORPORAL ====================
    @classmethod
    def get_evolution_logs(cls, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        target_uid = user_id or cls.get_active_user_id()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM body_evolution WHERE user_id = ? ORDER BY log_date DESC, id DESC", (target_uid,))
            return [dict(r) for r in cursor.fetchall()]

    @classmethod
    def add_evolution_log(cls, angle: str, photo_path: str, weight: float, chest: float = 0, arm: float = 0, waist: float = 0, thigh: float = 0, notes: str = "", user_id: Optional[int] = None):
        target_uid = user_id or cls.get_active_user_id()
        today_str = str(date.today())
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO body_evolution (user_id, log_date, photo_path, angle, weight_kg, chest_cm, arm_cm, waist_cm, thigh_cm, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (target_uid, today_str, photo_path, angle, weight, chest, arm, waist, thigh, notes))
            conn.commit()

    # ==================== IA CHAT MEMORY ====================
    @classmethod
    def get_chat_history(cls, persona: str, limit: int = 30, user_id: Optional[int] = None) -> List[Dict[str, str]]:
        target_uid = user_id or cls.get_active_user_id()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT role, content FROM ai_chat_history
            WHERE user_id = ? AND persona = ? ORDER BY id ASC LIMIT ?
            """, (target_uid, persona, limit))
            return [{"role": r["role"], "content": r["content"]} for r in cursor.fetchall()]

    @classmethod
    def add_chat_message(cls, persona: str, role: str, content: str, user_id: Optional[int] = None):
        target_uid = user_id or cls.get_active_user_id()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO ai_chat_history (user_id, persona, role, content)
            VALUES (?, ?, ?, ?)
            """, (target_uid, persona, role, content))
            conn.commit()

    # ==================== SEEDING INICIAL ====================
    @classmethod
    def _seed_exercises_if_empty(cls):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM exercise_library")
            if cursor.fetchone()[0] > 0:
                return

            exercises = [
                # PEITO
                (
                    "Supino Reto com Barra", "Peito", "Peitoral Maior", "Tríceps, Deltoide Anterior", "Barra / Banco Reto",
                    "1. Deite no banco com os olhos sob a barra. 2. Pés firmes no chão, faça a retração escapular (junte as escápulas). 3. Pegada ligeiramente mais larga que os ombros. 4. Desça a barra controladamente até o terço inferior do peito. 5. Empurre explosivamente sem perder a retração das escápulas.",
                    "Construtor primordial de força e espessura do peitoral, gerando alta tensão mecânica.",
                    "Deixar os cotovelos abertos a 90° (risco para os ombros); perder a estabilidade escapular; rebater a barra no osso esterno.",
                    "fitness_center"
                ),
                (
                    "Supino Inclinado com Halteres", "Peito", "Peitoral Superior (Clavicular)", "Deltoide Anterior, Tríceps", "Halteres / Banco 30-45°",
                    "1. Ajuste o banco em 30° a 45°. 2. Suba os halteres até a linha dos ombros. 3. Desça abrindo os cotovelos a ~60° em relação ao tronco. 4. Suba em arco suave convergente sem bater os halteres no topo.",
                    "Foco no preenchimento da porção clavicular do peito (peito alto), conferindo aspecto denso.",
                    "Banco inclinado demais (acima de 45° vira treino de ombro); bater os halteres no topo perdendo tensão.",
                    "fitness_center"
                ),
                (
                    "Crucifixo na Polia (Crossover)", "Peito", "Peitoral Maior (Esterno-Costal)", "Deltoide Anterior", "Polia Dupla",
                    "1. Posicione as polias na altura do peito ou acima. 2. Dê um passo à frente com o tronco ligeiramente inclinado. 3. Abra os braços com cotovelos semiflexionados sentindo o alongamento. 4. Feche abraçando um barril imaginário e esprema o peito por 1 segundo.",
                    "Tensão contínua do início ao fim do movimento com pico de contração no ponto de fechamento.",
                    "Flexionar e estender os braços como se fosse um supino; usar impulso do tronco.",
                    "cable"
                ),
                (
                    "Crossover Polia Baixa", "Peito", "Peitoral Superior", "Deltoide Anterior", "Polia Baixa",
                    "1. Polias na posição mais baixa. 2. Traga os cabos de baixo para cima convergindo na altura do queixo/olhos. 3. Mantenha os cotovelos levemente flexionados.",
                    "Excelente ativação das fibras ascendentes da porção superior do peito.",
                    "Jogar o tronco para trás no final da repetição.",
                    "cable"
                ),
                (
                    "Voador / Peck Deck", "Peito", "Peitoral Maior", "Deltoide Anterior", "Máquina Peck Deck",
                    "1. Ajuste o banco para que a pegada fique na linha do meio do peito. 2. Mantenha o peito estufado e escápulas travadas. 3. Feche aproximando os punhos e segure a contração por 1 segundo.",
                    "Isolamento puro sem sobrecarga nos estabilizadores, ideal para falha muscular segura.",
                    "Projetar os ombros para frente no fechamento perdendo o trabalho do peito.",
                    "crop_free"
                ),

                # COSTAS
                (
                    "Puxada Frontal na Polia (Pulley)", "Costas", "Latíssimo do Dorso", "Bíceps, Redondo Maior, Romboides", "Polia Alta",
                    "1. Sente-se e trave as coxas no apoio. 2. Pegada pronada um pouco além da largura dos ombros. 3. Inicie puxando com as escápulas para baixo (depressão escapular). 4. Traga a barra em direção à fúrcula clavicular com o peito alto.",
                    "Principal exercício para desenvolvimento da largura dorsal (formato em V).",
                    "Puxar atrás da nuca (risco cervical); balançar excessivamente o tronco para trás.",
                    "format_align_center"
                ),
                (
                    "Remada Curvada com Barra", "Costas", "Latíssimo, Romboides, Trapézio", "Bíceps, Eretor da Espinha", "Barra Livre",
                    "1. Pés na largura do quadril, joelhos levemente flexionados. 2. Incline o tronco a 45° mantendo a coluna neutra. 3. Puxe a barra em direção ao umbigo, cotovelos rentes ao tronco. 4. Aperte as costas no topo e desça controlando.",
                    "Constrói densidade, espessura e força global da cadeia posterior e core.",
                    "Arredondar a lombar (risco grave de hérnia); ficar muito ereto e virar encolhimento.",
                    "fitness_center"
                ),
                (
                    "Remada Baixa no Triângulo", "Costas", "Latíssimo Médio e Romboides", "Bíceps, Trapézio", "Máquina / Cabo",
                    "1. Pés apoiados com joelhos ligeiramente flexionados. 2. Coluna ereta e peito aberto. 3. Puxe o triângulo contra o abdômen inferior esmagando as costas. 4. Alongue na volta sem jogar a coluna para a frente.",
                    "Excelente controle motor para espessura dorsal e adução de escápulas.",
                    "Balançar o tronco para frente e para trás feito remo de barco.",
                    "cable"
                ),
                (
                    "Remada Cavalinho (Barra T)", "Costas", "Dorsal e Trapézio Médio", "Bíceps, Antebraço", "Máquina Barra T",
                    "1. Apoie o peito ou fique inclinado na base. 2. Puxe com pegada neutra direcionando a força para os cotovelos. 3. Foque em fechar as asas das costas.",
                    "Permite alta sobrecarga progressiva com suporte estável de pegada.",
                    "Tirar o peito do apoio para roubar impulso.",
                    "fitness_center"
                ),
                (
                    "Pull Down na Polia Alta", "Costas", "Latíssimo do Dorso", "Tríceps Porção Longa, Abdômen", "Polia Alta / Barra Reta ou Corda",
                    "1. Afaste-se da polia com o tronco a 30°. 2. Braços estendidos e cotovelos travados em leve flexão. 3. Traga a barra até as coxas em arco, apertando a dorsal.",
                    "Isola a grande dorsal sem usar a flexão de bíceps, perfeito para pré/pós-exaustão.",
                    "Flexionar os cotovelos transformando em tríceps testa.",
                    "cable"
                ),

                # PERNAS (QUADRÍCEPS, POSTERIORES, GLÚTEOS)
                (
                    "Agachamento Livre com Barra", "Pernas", "Quadríceps, Glúteos", "Posteriores, Adutores, Core", "Barra Olímpica / Gaiola",
                    "1. Barra repousada no trapézio (high bar) ou deltoide posterior (low bar). 2. Pés na largura dos ombros com pontas levemente para fora. 3. Respire fundo travando o abdômen (manobra de Valsalva). 4. Desça até pelo menos 90° mantendo os joelhos alinhados aos pés. 5. Suba empurrando o chão.",
                    "O rei dos exercícios de pernas: estimula hipertrofia, força sistêmica e liberação hormonal.",
                    "Valgo dinâmico (joelhos caindo para dentro); descolar calcanhares do chão; flexionar a coluna (buttwink severo).",
                    "accessibility_new"
                ),
                (
                    "Leg Press 45°", "Pernas", "Quadríceps, Glúteo Máximo", "Adutores, Isquiotibiais", "Máquina Leg Press 45°",
                    "1. Apoie totalmente as costas e a cabeça no encosto. 2. Pés no meio da plataforma na largura dos ombros. 3. Destrave e desça até os joelhos formarem 90° sem desgrudar o quadril do banco. 4. Empurre sem hiperextender os joelhos no topo.",
                    "Permite trabalhar cargas altíssimas com total estabilização lombar.",
                    "Tirar o quadril/glúteo do assento na descida (esmagamento lombar); travar os joelhos estalando a articulação.",
                    "crop_free"
                ),
                (
                    "Cadeira Extensora", "Pernas", "Quadríceps (Reto Femoral e Vastos)", "Nenhum", "Máquina Extensora",
                    "1. Regule o encosto para que o joelho coincida com o eixo de rotação da máquina. 2. Rolete sobre a canela acima do tornozelo. 3. Estenda as pernas até a contração máxima e segure 1 segundo no topo.",
                    "Isolamento máximo do quadríceps e ativação seletiva do reto femoral.",
                    "Ponto do rolete muito alto ou desregulado; chutar a carga com impulso sem controle excêntrico.",
                    "airline_seat_recline_extra"
                ),
                (
                    "Mesa Flexora", "Pernas", "Isquiotibiais (Posterior de Coxa)", "Gastrocnêmio", "Máquina Mesa Flexora",
                    "1. Deite de bruços e segure nos apoios. 2. Rolete apoiado acima do tendão de Aquiles. 3. Flexione os joelhos trazendo o calcanhar ao glúteo mantendo a pelve colada no banco.",
                    "Trabalha o comprimento total dos isquiotibiais na flexão do joelho.",
                    "Levantar o quadril da mesa na subida para roubar com a lombar.",
                    "airline_seat_flat"
                ),
                (
                    "Stiff com Barra / Halteres", "Pernas", "Isquiotibiais e Glúteo", "Eretor da Espinha, Trapézio", "Barra ou Halteres",
                    "1. Pés na largura do quadril, joelhos quase estendidos (micro-flexionados). 2. Empurre o quadril para trás como se fosse fechar uma porta com o bumbum. 3. Desça a barra rente às pernas até sentir o alongamento máximo dos posteriores. 4. Suba contraindo os glúteos.",
                    "Excelente estímulo de hipertrofia por estiramento com alta tensão passiva e ativa.",
                    "Curvar a coluna torácica/lombar; agachar em vez de empurrar o quadril para trás (hinge).",
                    "fitness_center"
                ),
                (
                    "Elevação Pélvica com Barra", "Pernas", "Glúteo Máximo", "Isquiotibiais, Core", "Banco e Barra com Espuma",
                    "1. Apoie a parte inferior das escápulas na borda do banco. 2. Barra sobre o quadril com acolchoamento. 3. Pés firmes com joelhos a 90° no topo. 4. Eleve o quadril até alinhar tronco e coxas, apertando o glúteo no pico.",
                    "Maior ativação eletromiográfica do glúteo máximo em posição encurtada.",
                    "Hiperestender a coluna lombar no topo em vez de fazer retroversão pélvica.",
                    "airline_seat_legroom_extra"
                ),
                (
                    "Panturrilha em Pé na Máquina", "Pernas", "Gastrocnêmio", "Sóleo", "Máquina de Panturrilha",
                    "1. Ombros sob os apoios, ponta dos pés na borda da plataforma. 2. Desça ao máximo sentindo o alongamento do tendão. 3. Suba na ponta dos dedos ao máximo e segure 2 segundos no topo.",
                    "Desenvolve a porção visual e volumosa das panturrilhas.",
                    "Fazer repetições rápidas 'quicando' no tendão de Aquiles sem pausa.",
                    "accessibility"
                ),

                # OMBROS (DELTOIDES)
                (
                    "Desenvolvimento com Halteres", "Ombros", "Deltoide Anterior e Lateral", "Tríceps, Trapézio Superior", "Halteres / Banco 80-90°",
                    "1. Banco quase a 90°. 2. Halteres na altura das orelhas com cotovelos a ~45° (plano escapular). 3. Empurre para cima até quase tocar os halteres. 4. Desça de forma controlada até a altura do queixo.",
                    "Construtor essencial de volume e força nos ombros e tríceps.",
                    "Abrir demais os cotovelos a 90° (atrito no manguito rotador); arquear a lombar.",
                    "fitness_center"
                ),
                (
                    "Elevação Lateral com Halteres", "Ombros", "Deltoide Lateral", "Trapézio", "Halteres",
                    "1. Pés firmes, tronco levemente inclinado para frente (5°). 2. Suba os halteres até a linha dos ombros com os cotovelos liderando o movimento. 3. Polegares levemente apontados para frente/baixo. 4. Desça em 2 segundos.",
                    "O exercício chave para criar o aspecto de 'ombros em coco' (largura visual).",
                    "Elevar acima da linha dos ombros jogando a tensão no trapézio; dar impulso com o tronco.",
                    "fitness_center"
                ),
                (
                    "Elevação Lateral na Polia", "Ombros", "Deltoide Lateral", "Trapézio", "Polia Baixa",
                    "1. Posicione o cabo atrás ou na frente do corpo. 2. Segure no apoio da máquina e incline o tronco ligeiramente para o lado da polia. 3. Eleve o braço mantendo tensão constante desde o início.",
                    "Garante tensão mecânica uniforme ao longo de toda a curva de resistência.",
                    "Puxar com o punho ou girar o ombro para trás.",
                    "cable"
                ),
                (
                    "Crucifixo Invertido no Peck Deck", "Ombros", "Deltoide Posterior", "Romboides, Trapézio Médio", "Máquina Peck Deck",
                    "1. Peito apoiado no encosto, braços alinhados aos ombros. 2. Abra os braços para trás com foco na porção posterior do ombro. 3. Segure a contração e retorne devagar.",
                    "Fundamental para postura, estabilidade de ombro e simetria lateral 3D.",
                    "Juntar as escápulas demais usando as costas em vez do deltoide posterior.",
                    "crop_free"
                ),

                # BRAÇOS (BÍCEPS, TRÍCEPS, ANTEBRAÇO)
                (
                    "Rosca Direta com Barra W", "Braços", "Bíceps Braquial", "Braquiorradial, Antebraço", "Barra W",
                    "1. Em pé, pegada na curva da barra W (mais ergonômica para os punhos). 2. Cotovelos colados ao lado do tronco. 3. Flexione os antebraços até a contração máxima do bíceps sem mover os cotovelos para frente. 4. Desça estendendo quase tudo.",
                    "Exercício base para pico de contração e força de flexão de cotovelo.",
                    "Jogar os cotovelos para trás ou balançar as costas para subir o peso.",
                    "fitness_center"
                ),
                (
                    "Rosca Martelo com Halteres", "Braços", "Braquial e Braquiorradial", "Bíceps", "Halteres",
                    "1. Pegada neutra (palmas viradas uma para a outra). 2. Suba os halteres mantendo a pegada firme. 3. Desça controlando o peso.",
                    "Aumenta a espessura do braço e destaca o músculo braquial que empurra o bíceps para cima.",
                    "Girar o punho durante o movimento perdendo a pegada neutra.",
                    "fitness_center"
                ),
                (
                    "Rosca Scott na Máquina / Banco", "Braços", "Bíceps (Cabeça Curta)", "Braquial", "Banco Scott / Barra W",
                    "1. Axilas apoiadas firmemente no topo do estofado. 2. Desça a barra até estender os braços com cuidado. 3. Suba até a contração máxima sem perder a tensão na vertical.",
                    "Isolamento brutal do bíceps eliminando qualquer possibilidade de trapaça com os ombros.",
                    "Despencar a barra no final da descida correndo risco de estiramento do tendão distal.",
                    "airline_seat_recline_normal"
                ),
                (
                    "Tríceps Corda na Polia Alta", "Braços", "Tríceps (Cabeça Lateral)", "Ancôneo", "Polia Alta / Corda",
                    "1. Cotovelos fixos ao lado do corpo. 2. Puxe a corda para baixo e, no final da extensão, afaste as pontas da corda abrindo os punhos. 3. Retorne até 90° mantendo os cotovelos imóveis.",
                    "Excelente para definição e pico de contração da cabeça lateral do tríceps.",
                    "Abrir os cotovelos ou movimentar os ombros para ajudar na empurrada.",
                    "cable"
                ),
                (
                    "Tríceps Testa com Barra W", "Braços", "Tríceps (Cabeça Longa e Média)", "Nenhum", "Barra W / Banco Reto",
                    "1. Deitado no banco, braços levemente inclinados para trás em relação à vertical (75°). 2. Flexione apenas os cotovelos descendo a barra até a testa/topo da cabeça. 3. Estenda os antebraços mantendo os braços firmes.",
                    "Melhor exercício para recrutar a cabeça longa do tríceps que dá volume ao braço.",
                    "Abrir os cotovelos para os lados; bater a barra na testa.",
                    "fitness_center"
                ),
                (
                    "Tríceps Francês Unilateral", "Braços", "Tríceps Cabeça Longa", "Nenhum", "Halter / Polia",
                    "1. Braço estendido acima da cabeça. 2. Desça o halter atrás da nuca sentindo o alongamento profundo do tríceps. 3. Estenda de volta.",
                    "Trabalha o tríceps em posição de estiramento máximo.",
                    "Deixar o cotovelo oscilar excessivamente durante a subida.",
                    "fitness_center"
                ),

                # ABDÔMEN & CORE
                (
                    "Abdominal na Polia Alta (Crunch)", "Abdômen", "Reto Abdominal", "Oblíquos", "Polia Alta / Corda",
                    "1. Ajoelhe-se de frente ou costas para a polia segurando a corda na nuca. 2. Flexione a coluna aproximando as costelas do quadril como uma concha. 3. Desça apertando o abdômen e retorne controlando.",
                    "Permite sobrecarga progressiva com placas para hipertrofia dos gomos abdominais.",
                    "Flexionar o quadril em vez de enrolar a coluna; puxar a corda com os braços.",
                    "cable"
                ),
                (
                    "Elevação de Pernas na Barra Fixa", "Abdômen", "Reto Abdominal Inferior", "Flexores do Quadril", "Barra Fixa",
                    "1. Pendure-se na barra com pegada pronada. 2. Eleve os joelhos ou pernas estendidas até que a pelve gire para cima. 3. Desça sem balançar o corpo.",
                    "Trabalho intenso da porção infra-abdominal e força de pegada.",
                    "Balançar como pêndulo usando inércia.",
                    "accessibility"
                ),
                (
                    "Prancha Abdominal Isométrica", "Abdômen", "Transverso do Abdômen, Core", "Glúteos, Ombros", "Colchonete",
                    "1. Apoie os antebraços e pontas dos pés no chão. 2. Mantenha o corpo em linha reta da cabeça aos calcanhares. 3. Contraia o abdômen como se fosse levar um soco e aperte os glúteos.",
                    "Fortalecimento da cinta natural do abdômen, estabilização da coluna e prevenção de dores lombares.",
                    "Deixar a lombar cair (arcar para baixo) ou elevar o quadril feito montanha.",
                    "crop_landscape"
                ),
            ]

            cursor.executemany("""
            INSERT INTO exercise_library (name, category, primary_muscle, secondary_muscles, equipment, execution_guide, why_do_it, common_mistakes, icon_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, exercises)
            conn.commit()

    @classmethod
    def _seed_default_routines_if_empty(cls):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM workout_routines")
            if cursor.fetchone()[0] > 0:
                return

            # Cria Treinos A (Push), B (Pull), C (Legs)
            routines = [
                ("Treino A - Push (Peito, Ombros e Tríceps)", "Push", "Foco em empurrar, densidade peitoral e deltoides", "#FFFFFF"),
                ("Treino B - Pull (Costas, Bíceps e Trapézio)", "Pull", "Foco em puxadas, dorsal em V e pico de bíceps", "#FFFFFF"),
                ("Treino C - Legs (Pernas Completas e Core)", "Legs", "Foco em quadríceps, posteriores, glúteos e abdômen", "#FFFFFF"),
            ]

            for r_name, r_cat, r_desc, r_col in routines:
                cursor.execute("""
                INSERT INTO workout_routines (name, category, description, color_hex)
                VALUES (?, ?, ?, ?)
                """, (r_name, r_cat, r_desc, r_col))
                r_id = cursor.lastrowid

                if r_cat == "Push":
                    ex_list = [
                        ("Supino Reto com Barra", 4, "8-10", 60.0, 90),
                        ("Supino Inclinado com Halteres", 4, "10-12", 24.0, 90),
                        ("Crucifixo na Polia (Crossover)", 3, "12-15", 15.0, 60),
                        ("Desenvolvimento com Halteres", 4, "8-10", 18.0, 90),
                        ("Elevação Lateral com Halteres", 4, "12-15", 10.0, 60),
                        ("Tríceps Corda na Polia Alta", 4, "10-12", 25.0, 60),
                    ]
                elif r_cat == "Pull":
                    ex_list = [
                        ("Puxada Frontal na Polia (Pulley)", 4, "8-10", 55.0, 90),
                        ("Remada Curvada com Barra", 4, "8-10", 50.0, 90),
                        ("Remada Baixa no Triângulo", 3, "10-12", 45.0, 60),
                        ("Crucifixo Invertido no Peck Deck", 4, "12-15", 35.0, 60),
                        ("Rosca Direta com Barra W", 4, "8-10", 25.0, 60),
                        ("Rosca Martelo com Halteres", 3, "10-12", 14.0, 60),
                    ]
                else: # Legs
                    ex_list = [
                        ("Agachamento Livre com Barra", 4, "6-8", 80.0, 120),
                        ("Leg Press 45°", 4, "10-12", 160.0, 90),
                        ("Cadeira Extensora", 3, "12-15", 40.0, 60),
                        ("Stiff com Barra / Halteres", 4, "8-10", 50.0, 90),
                        ("Mesa Flexora", 4, "10-12", 35.0, 60),
                        ("Panturrilha em Pé na Máquina", 5, "15-20", 50.0, 45),
                        ("Abdominal na Polia Alta (Crunch)", 4, "15-20", 30.0, 60),
                    ]

                for ex_name, sets, reps, weight, rest in ex_list:
                    cursor.execute("""
                    INSERT INTO routine_exercises (routine_id, exercise_name, target_sets, target_reps, target_weight, rest_seconds)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (r_id, ex_name, sets, reps, weight, rest))

            conn.commit()

    @classmethod
    def _seed_evolution_if_empty(cls):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM body_evolution")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                INSERT INTO body_evolution (log_date, photo_path, angle, weight_kg, chest_cm, arm_cm, waist_cm, thigh_cm, notes)
                VALUES ('2026-09-01', '', 'Frente', 80.2, 100.0, 37.0, 84.5, 58.0, 'Início do protocolo de hipertrofia limpa.')
                """)
                cursor.execute("""
                INSERT INTO body_evolution (log_date, photo_path, angle, weight_kg, chest_cm, arm_cm, waist_cm, thigh_cm, notes)
                VALUES ('2026-09-13', '', 'Frente', 78.5, 102.0, 38.0, 82.0, 59.0, 'Mais densidade nos deltoides e redução na cintura.')
                """)
                conn.commit()

