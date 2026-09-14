"""
Executador Web do Templo Fitness AI com suporte a deploy em nuvem (Render, Railway, Fly.io, etc.).
"""
import os
import sys
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

import flet as ft
from main import main

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8550))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("=" * 60)
    print("🌐 INICIANDO TEMPLO FITNESS AI - SERVIDOR WEB / PWA")
    print(f"👉 Porta: {port} | Host: {host}")
    print(f"👉 Local: http://localhost:{port}")
    print("=" * 60)
    
    app_view = getattr(ft.AppView, "WEB_BROWSER", getattr(ft, "WEB_BROWSER", None))
    ft.run(
        main,
        view=app_view,
        port=port,
        host=host,
        assets_dir="assets"
    )
