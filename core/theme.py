"""
Sistema de Design Oficial: 'Monochrome Stealth Minimalist (Cinza, Preto e Branco)'
Estética de altíssimo luxo minimalista: Preto Profundo (#0A0A0A), Superfícies em Grafite/Cinza
e Acentos em Branco Puro (#FFFFFF) e Prata Titânio para máxima sobriedade, foco e sofisticação.
"""
import flet as ft

# Fallback universal de componentes entre versões do Flet
Icons = getattr(ft, "Icons", getattr(ft, "icons", None))
Colors = getattr(ft, "Colors", getattr(ft, "colors", None))
NavigationDestination = getattr(ft, "NavigationBarDestination", getattr(ft, "NavigationDestination", None))

class SportColors:
    # Fundo e Superfícies (Preto Profundo & Cinzas Nobres)
    BG_DARK = "#0A0A0A"             # Preto Puro Minimalista (Matte Noir)
    BG_SURFACE = "#141414"          # Cinza Grafite Acetinado para Cards
    BG_SURFACE_ALT = "#1E1E1E"      # Cinza Carvão para Elementos Interativos / Hover
    BG_SURFACE_ELEVATED = "#282828" # Modais e Cabeçalhos Elevados
    BG_INPUT = "#121212"            # Fundo dos Campos de Entrada
    
    # Destaque Principal Minimalista (Branco Puro & Prata)
    PRIMARY_NEON = "#FFFFFF"        # Branco Puro para Destaques e Botões Principais
    PRIMARY_NEON_DARK = "#E5E5E5"   # Branco Prata
    PRIMARY_TEXT_ON_NEON = "#0A0A0A"# Preto Puro sobre o Branco para Contraste Máximo
    
    # Cores de Apoio Funcionais (Tons de Cinza / Titânio e Platina)
    CYAN_ELECTRIC = "#D4D4D8"       # Prata Titânio Claro
    CRIMSON_NEON = "#E4E4E7"        # Prata Suave
    AMBER_GOLD = "#A1A1AA"          # Cinza Médio Neutro
    PURPLE_MIND = "#A1A1AA"         # Cinza Médio Neutro
    TEAL_PHYSIO = "#A1A1AA"         # Cinza Médio Neutro
    
    # Textos de Altíssima Legibilidade (Monocromático Puro)
    TEXT_WHITE = "#FFFFFF"          # Branco Puro para Títulos e Destaques
    TEXT_PRIMARY = "#E5E5E5"        # Branco Suave para Leitura Longa
    TEXT_SECONDARY = "#A1A1AA"      # Cinza Neutro para Legendas e Métricas
    TEXT_MUTED = "#666666"          # Cinza Sóbrio para Notas Técnicas
    
    # Bordas Finas e Minimalistas (Grafite Suave)
    BORDER_DEFAULT = "#262626"      # Borda sutil grafite
    BORDER_FOCUS = "#444444"        # Borda em foco cinza claro
    BORDER_NEON = "#FFFFFF"         # Borda de seleção ativa em branco puro
    BORDER_CYAN = "#3F3F46"
    BORDER_CRIMSON = "#3F3F46"
    BORDER_GOLD = "#3F3F46"

class AppAlignment:
    CENTER = ft.Alignment(0, 0)
    TOP_LEFT = ft.Alignment(-1, -1)
    TOP_RIGHT = ft.Alignment(1, -1)
    BOTTOM_LEFT = ft.Alignment(-1, 1)
    BOTTOM_RIGHT = ft.Alignment(1, 1)

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
    def all(width: float = 1, color: str = "#262626"):
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
    def card_container(content, border_color=SportColors.BORDER_DEFAULT, padding=16, radius=14, on_click=None, bgcolor=SportColors.BG_SURFACE):
        pad = AppPadding.all(padding) if isinstance(padding, (int, float)) else padding
        return ft.Container(
            content=content,
            bgcolor=bgcolor,
            border_radius=radius,
            padding=pad,
            border=AppBorder.all(1, border_color),
            on_click=on_click,
            ink=True if on_click else False,
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
        )

    @staticmethod
    def badge(text: str, color: str = SportColors.TEXT_PRIMARY, bg_color: str = None, icon=None):
        if not bg_color:
            bg_color = SportColors.BG_SURFACE_ALT
        
        controls = []
        if icon:
            controls.append(ft.Icon(icon, size=12, color=color))
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
            border=AppBorder.all(1, SportColors.BORDER_DEFAULT),
        )

    @staticmethod
    def section_header(title: str, subtitle: str = "", icon=None, action_button=None):
        title_row = []
        if icon:
            title_row.append(ft.Icon(icon, size=18, color=SportColors.TEXT_WHITE))
        title_row.append(
            ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=SportColors.TEXT_WHITE)
        )
        
        left_col = [
            ft.Row(title_row, spacing=8, alignment=ft.MainAxisAlignment.START),
        ]
        if subtitle:
            left_col.append(
                ft.Text(subtitle, size=12, color=SportColors.TEXT_SECONDARY)
            )
        
        header_row = [
            ft.Column(left_col, spacing=2, expand=True if action_button else False),
        ]
        if action_button:
            header_row.append(action_button)
            
        return ft.Row(header_row, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
