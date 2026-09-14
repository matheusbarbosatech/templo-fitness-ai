"""
Sistema de Design Oficial: 'Apple Fitness+ / Whoop Luxe Minimalist'
Paleta sóbria, elegante, sem excesso de cores berrantes, inspirada no design premium da Apple e Whoop.
"""
import flet as ft

# Fallback universal de componentes entre versões do Flet
Icons = getattr(ft, "Icons", getattr(ft, "icons", None))
Colors = getattr(ft, "Colors", getattr(ft, "colors", None))
NavigationDestination = getattr(ft, "NavigationBarDestination", getattr(ft, "NavigationDestination", None))

class SportColors:
    # Fundo e Superfícies (Grafite / Ardósia Nobre)
    BG_DARK = "#0B0F17"          # Deep Slate Obsidian
    BG_SURFACE = "#141C2E"       # Cartões em cinza ardósia acetinado
    BG_SURFACE_ALT = "#1C263D"   # Superfície de botões secundários / hover
    BG_INPUT = "#0F1624"         # Fundo discreto dos inputs
    
    # Cores de Acento Sofisticadas (Menta Suave, Gelo e Titânio)
    PRIMARY_NEON = "#10B981"     # Emerald / Mint Suave (Apple Fitness style)
    PRIMARY_NEON_DARK = "#059669"
    CYAN_ELECTRIC = "#38BDF8"    # Soft Ice Blue / Hidratação
    CRIMSON_NEON = "#E11D48"     # Ruby Rosewood discreto
    AMBER_GOLD = "#F59E0B"       # Warm Amber
    PURPLE_MIND = "#8B5CF6"      # Soft Iris
    TEAL_PHYSIO = "#14B8A6"      # Teal Suave
    
    # Textos de Alta Elegância
    TEXT_WHITE = "#FFFFFF"       # Branco Puro para títulos
    TEXT_PRIMARY = "#F8FAFC"     # Branco suave para leitura longa
    TEXT_SECONDARY = "#94A3B8"   # Cinza ardósia claro para legendas
    TEXT_MUTED = "#64748B"       # Cinza discreto para notas técnicas
    
    # Bordas Finas e Minimalistas (Subtle Glass)
    BORDER_DEFAULT = "#1E293B"   # Borda discreta padrão
    BORDER_NEON = "#10B981"      # Borda verde menta para seleção ativa
    BORDER_CYAN = "#38BDF8"
    BORDER_CRIMSON = "#E11D48"
    BORDER_GOLD = "#F59E0B"
    BORDER_PURPLE = "#8B5CF6"

class AppAlignment:
    CENTER = ft.Alignment(0, 0) if hasattr(ft, "Alignment") else getattr(ft.alignment, "center", None)
    TOP_LEFT = ft.Alignment(-1, -1) if hasattr(ft, "Alignment") else getattr(ft.alignment, "top_left", None)
    TOP_RIGHT = ft.Alignment(1, -1) if hasattr(ft, "Alignment") else getattr(ft.alignment, "top_right", None)
    BOTTOM_LEFT = ft.Alignment(-1, 1) if hasattr(ft, "Alignment") else getattr(ft.alignment, "bottom_left", None)
    BOTTOM_RIGHT = ft.Alignment(1, 1) if hasattr(ft, "Alignment") else getattr(ft.alignment, "bottom_right", None)

class AppPadding:
    @staticmethod
    def all(value: float):
        if hasattr(ft, "Padding"):
            return ft.Padding(left=value, top=value, right=value, bottom=value)
        return value

    @staticmethod
    def symmetric(horizontal: float = 0, vertical: float = 0):
        if hasattr(ft, "Padding"):
            return ft.Padding(left=horizontal, top=vertical, right=horizontal, bottom=vertical)
        return vertical

    @staticmethod
    def only(left: float = 0, top: float = 0, right: float = 0, bottom: float = 0):
        if hasattr(ft, "Padding"):
            return ft.Padding(left=left, top=top, right=right, bottom=bottom)
        return top

class AppBorder:
    @staticmethod
    def all(width: float = 1, color: str = "#1E293B"):
        try:
            if hasattr(ft.Border, "all"):
                return ft.Border.all(width, color)
        except Exception:
            pass
        try:
            side = ft.BorderSide(width, color)
            return ft.Border(top=side, right=side, bottom=side, left=side)
        except Exception:
            return None

class AppBorderRadius:
    @staticmethod
    def all(radius: float):
        if hasattr(ft, "BorderRadius"):
            return ft.BorderRadius(top_left=radius, top_right=radius, bottom_left=radius, bottom_right=radius)
        return radius

    @staticmethod
    def only(top_left: float = 0, top_right: float = 0, bottom_left: float = 0, bottom_right: float = 0):
        if hasattr(ft, "BorderRadius"):
            return ft.BorderRadius(top_left=top_left, top_right=top_right, bottom_left=bottom_left, bottom_right=bottom_right)
        return top_left

class SportStyles:
    @staticmethod
    def card_container(content, border_color=SportColors.BORDER_DEFAULT, padding=16, radius=14, on_click=None):
        pad = AppPadding.all(padding) if isinstance(padding, (int, float)) else padding
        return ft.Container(
            content=content,
            bgcolor=SportColors.BG_SURFACE,
            border_radius=radius,
            padding=pad,
            border=AppBorder.all(1, border_color),
            on_click=on_click,
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
        )

    @staticmethod
    def badge(text: str, color: str, bg_color: str = None, icon=None):
        if not bg_color:
            bg_color = f"{color}18"  # ~10% opacity sutil
        
        controls = []
        if icon:
            controls.append(ft.Icon(icon, size=13, color=color))
        controls.append(
            ft.Text(
                text,
                size=11,
                weight=ft.FontWeight.W_600,
                color=color,
            )
        )
        return ft.Container(
            content=ft.Row(controls, spacing=4, alignment=ft.MainAxisAlignment.CENTER, tight=True),
            padding=AppPadding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
            bgcolor=bg_color,
            border=AppBorder.all(1, f"{color}33"),
        )

    @staticmethod
    def section_header(title: str, subtitle: str = "", icon=None, action_button=None):
        title_row = []
        if icon:
            title_row.append(ft.Icon(icon, size=18, color=SportColors.PRIMARY_NEON))
        title_row.append(
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
        )
        
        left_col = [
            ft.Row(title_row, spacing=8, alignment=ft.MainAxisAlignment.START),
        ]
        if subtitle:
            left_col.append(
                ft.Text(subtitle, size=12, color=SportColors.TEXT_SECONDARY)
            )
        
        header_row = [
            ft.Column(left_col, spacing=2),
        ]
        if action_button:
            header_row.append(action_button)
            
        return ft.Row(header_row, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
