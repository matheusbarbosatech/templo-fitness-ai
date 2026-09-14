"""
Configurações Globais do Super-App de Saúde e Musculação com IA (DevWorld).
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
    APP_NAME = "APOLLO FITNESS AI"
    APP_SUBTITLE = "Super-App de Saúde Esportiva & Musculação 360°"
    VERSION = "1.0.0"
    
    # Configuração da API DevWorld / LLM
    DEVWORLD_API_KEY_ENV = os.getenv("DEVWORLD_API_KEY", "")
    DEVWORLD_BASE_URL = os.getenv("DEVWORLD_BASE_URL", "https://api.devworld.com.br/v1")
    DEFAULT_MODEL = "devworld-gpt-4o-mini"
    
    # Configurações de Treino Padrão
    DEFAULT_REST_TIME_SECONDS = 90
    DEFAULT_WATER_GOAL_ML = 3000
