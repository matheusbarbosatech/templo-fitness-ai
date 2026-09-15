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
        """Abre um diálogo/modal de forma segura em qualquer versão do Flet (inclusive 0.86+)."""
        if not page or not dialog:
            return
        
        # 1. Método padrão Flet 0.86+ (show_dialog)
        if hasattr(page, "show_dialog") and callable(page.show_dialog):
            try:
                dialog.open = False  # show_dialog exige que ainda não esteja aberto
                page.show_dialog(dialog)
                return
            except Exception as e:
                print(f"[UIHelper.open_dialog] show_dialog error: {e}")

        # 2. Método Flet 0.25+ (page.open)
        if hasattr(page, "open") and callable(page.open):
            try:
                dialog.open = True
                page.open(dialog)
                return
            except Exception as e:
                print(f"[UIHelper.open_dialog] page.open error: {e}")
                
        # 3. Fallback legado
        try:
            dialog.open = True
            page.dialog = dialog
            page.update()
        except Exception as e:
            print(f"[UIHelper.open_dialog] page.dialog fallback error: {e}")

    @staticmethod
    def close_dialog(page: ft.Page, dialog: ft.AlertDialog):
        """Fecha um diálogo/modal de forma segura em qualquer versão do Flet (inclusive 0.86+)."""
        if not page:
            return
            
        # 1. Método padrão Flet 0.86+ (pop_dialog ou fechamento direto)
        if hasattr(page, "pop_dialog") and callable(page.pop_dialog):
            try:
                dialog.open = False
                page.pop_dialog()
                return
            except Exception as e:
                print(f"[UIHelper.close_dialog] pop_dialog error: {e}")
        
        # 2. Método Flet 0.25+ (page.close)
        if hasattr(page, "close") and callable(page.close):
            try:
                dialog.open = False
                page.close(dialog)
                return
            except Exception as e:
                print(f"[UIHelper.close_dialog] page.close error: {e}")
                
        # 3. Fallback legado
        try:
            dialog.open = False
            if hasattr(dialog, "update"):
                dialog.update()
            else:
                page.update()
        except Exception as e:
            print(f"[UIHelper.close_dialog] fallback error: {e}")

    @staticmethod
    def show_toast(page: ft.Page, message: str, color: str = SportColors.PRIMARY_NEON, text_color: str = SportColors.BG_DARK, duration_ms: int = 2500):
        """Exibe uma SnackBar moderna e estilizada em qualquer versão do Flet."""
        if not page:
            return
            
        snack = ft.SnackBar(
            content=ft.Row([
                ft.Icon(Icons.CHECK_CIRCLE, color=text_color, size=18),
                ft.Text(message, color=text_color, weight=ft.FontWeight.BOLD, size=13),
            ], spacing=8, alignment=ft.MainAxisAlignment.START),
            bgcolor=color,
            duration=ft.Duration(milliseconds=duration_ms) if hasattr(ft, "Duration") else duration_ms,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=AppPadding.all(12),
            shape=ft.RoundedRectangleBorder(radius=10) if hasattr(ft, "RoundedRectangleBorder") else None
        )
        
        # 1. Flet 0.86+ trata SnackBar como DialogControl
        if hasattr(page, "show_dialog") and callable(page.show_dialog):
            try:
                page.show_dialog(snack)
                return
            except Exception as e:
                print(f"[UIHelper.show_toast] show_dialog error: {e}")

        # 2. Flet 0.25+ (page.open)
        if hasattr(page, "open") and callable(page.open):
            try:
                page.open(snack)
                return
            except Exception:
                pass
                
        # 3. Fallback legado
        try:
            page.snack_bar = snack
            snack.open = True
            page.update()
        except Exception:
            pass
