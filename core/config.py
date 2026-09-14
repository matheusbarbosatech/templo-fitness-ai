"""
Configurações Globais do Templo Fitness AI - Super-App Cristão de Treino, Força & Mordomia do Templo.
"""
import os
from pathlib import Path

# Diretórios base
ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
UPLOADS_DIR = ROOT_DIR / "uploads" / "evolution_photos"
DB_PATH = ROOT_DIR / "data" / "fitness_ai.db"

# Garante criação dos diretórios necessários
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

class AppConfig:
    APP_ICON = "🏛️"
    APP_NAME = "TEMPLO FITNESS AI"
    APP_SUBTITLE = "Mordomia do Templo, Disciplina & Força Integral"
    VERSION = "2.0.0"
    
    # Configuração da API DevWorld / LLM
    DEVWORLD_API_KEY_ENV = os.getenv("DEVWORLD_API_KEY", "")
    DEVWORLD_BASE_URL = os.getenv("DEVWORLD_BASE_URL", "https://api.devworld.com.br/v1")
    DEFAULT_MODEL = "devworld-gpt-4o-mini"
    
    # Configurações de Treino Padrão
    DEFAULT_REST_TIME_SECONDS = 90
    DEFAULT_WATER_GOAL_ML = 3000

    # Versículos Bíblicos de Força, Disciplina & Mordomia do Templo
    BIBLE_VERSES = [
        {
            "reference": "1 Coríntios 6:19-20",
            "text": "Acaso não sabem que o corpo de vocês é santuário do Espírito Santo que habita em vocês, que lhes foi dado por Deus? Vocês não são de si mesmos; foram comprados por alto preço. Portanto, glorifiquem a Deus com o seu próprio corpo."
        },
        {
            "reference": "1 Coríntios 9:26-27",
            "text": "Assim corro também eu, não sem meta; assim luto, não como desferindo golpes no ar. Mas esmurro o meu corpo e o reduzo à servidão, para que, tendo pregado a outros, não venha eu mesmo a ser desqualificado."
        },
        {
            "reference": "Provérbios 24:5",
            "text": "O homem sábio é forte, e o homem de conhecimento consolida a sua força."
        },
        {
            "reference": "Filipenses 4:13",
            "text": "Tudo posso naquele que me fortalece."
        },
        {
            "reference": "Isaías 40:29-31",
            "text": "Ele dá força ao cansado e multiplica o vigor ao que não tem nenhum... os que esperam no Senhor renovam as suas forças; voam alto como águias; correm e não se cansam, caminham e não se fatigam."
        },
        {
            "reference": "1 Timóteo 4:8",
            "text": "Pois o exercício físico tem valor; exercite seu corpo e sua fé com constância e sabedoria."
        },
        {
            "reference": "Romanos 12:1",
            "text": "Portanto, irmãos, rogo-lhes pelas misericórdias de Deus que se ofereçam em sacrifício vivo, santo e agradável a Deus; este é o culto racional de vocês."
        },
        {
            "reference": "Juízes 16:28",
            "text": "Então Sansão orou ao Senhor: 'Ó Soberano Senhor, lembra-te de mim! Ó Deus, peço-te que me fortaleças mais esta vez!'"
        }
    ]
