"""
Utilitário de Interface e Diálogos Universal - Templo Fitness AI.
Compatível de forma transparente com Flet moderno (0.25+, 0.86+) e legados.
Garante que modais, bottom sheets e snackbars abram e fechem sem erros em qualquer plataforma.
"""
import flet as ft
from typing import Optional
from core.theme import SportColors, Icons, AppPadding, AppBorder

class UIHelper:
    @staticmethod
    def open_dialog(page: ft.Page, dialog: ft.AlertDialog):
        """Abre um diálogo/modal de forma segura em qualquer versão do Flet."""
        if not page:
            return
        
        dialog.open = True
        
        # 1. Método padrão Flet 0.25+ / 0.86+
        if hasattr(page, "open") and callable(page.open):
            try:
                page.open(dialog)
                return
            except Exception as e:
                print(f"[UIHelper.open_dialog] page.open error: {e}")
                
        # 2. Fallback legado
        try:
            page.dialog = dialog
            page.update()
        except Exception as e:
            print(f"[UIHelper.open_dialog] page.dialog fallback error: {e}")

    @staticmethod
    def close_dialog(page: ft.Page, dialog: ft.AlertDialog):
        """Fecha um diálogo/modal de forma segura em qualquer versão do Flet."""
        if not page:
            return
            
        dialog.open = False
        
        # 1. Método padrão Flet 0.25+ / 0.86+
        if hasattr(page, "close") and callable(page.close):
            try:
                page.close(dialog)
                return
            except Exception as e:
                print(f"[UIHelper.close_dialog] page.close error: {e}")
                
        # 2. Fallback legado
        try:
            page.update()
        except Exception as e:
            print(f"[UIHelper.close_dialog] fallback error: {e}")

    @staticmethod
    def show_toast(page: ft.Page, message: str, color: str = SportColors.PRIMARY_NEON, text_color: str = SportColors.BG_DARK, duration_ms: int = 2200):
        """Exibe uma SnackBar moderna e estilizada."""
        if not page:
            return
            
        snack = ft.SnackBar(
            content=ft.Row([
                ft.Icon(Icons.CHECK_CIRCLE, color=text_color, size=18),
                ft.Text(message, color=text_color, weight=ft.FontWeight.BOLD, size=13),
            ], spacing=8, alignment=ft.MainAxisAlignment.START),
            bgcolor=color,
            duration=duration_ms,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=AppPadding.all(12),
            shape=ft.RoundedRectangleBorder(radius=10) if hasattr(ft, "RoundedRectangleBorder") else None
        )
        
        if hasattr(page, "open") and callable(page.open):
            try:
                page.open(snack)
                return
            except Exception:
                pass
                
        page.snack_bar = snack
        snack.open = True
        try:
            page.update()
        except Exception:
            pass
