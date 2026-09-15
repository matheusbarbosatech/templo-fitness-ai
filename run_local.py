"""
Executador Local do Super-App Templo Fitness AI para Teste Instantâneo no PC.
"""
import os
import sys
import time
from pathlib import Path

# Configura UTF-8 no terminal Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Cria diretório de logs
LOGS_DIR = ROOT_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def main():
    print("=" * 60)
    print("🚀 INICIANDO TEMPLO FITNESS AI - SUPER-APP CRISTÃO 360°")
    print("=" * 60)
    print(f"📁 Diretório: {ROOT_DIR}")
    print("🧠 Conselho de IA: Treinador, Nutricionista, Dr. Gabriel, Dr. Rafael")
    print("⚡ Abrindo janela Flet...")
    print("=" * 60)

    import flet as ft
    from main import main as app_main
    
    ft.run(app_main)

if __name__ == "__main__":
    main()
