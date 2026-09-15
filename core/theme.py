"""
Sistema de Design Oficial: 'Nike Training / Whoop Carbon Volt'
Estética de altíssima performance: Preto Absoluto / Grafite Carbono, Tipografia Branca Nítida
e Acento Volt Neon (#CCFF00) para máxima energia, legibilidade e elegância esportiva.
"""
import flet as ft

# Fallback universal de componentes entre versões do Flet
Icons = getattr(ft, "Icons", getattr(ft, "icons", None))
Colors = getattr(ft, "Colors", getattr(ft, "colors", None))
NavigationDestination = getattr(ft, "NavigationBarDestination", getattr(ft, "NavigationDestination", None))

class SportColors:
    # Fundo e Superfícies (Carbon Dark / Obsidian Absoluto)
    BG_DARK = "#090A0C"             # Preto Puro Esportivo (OLED Friendly)
    BG_SURFACE = "#121316"          # Carbono Nobre Acetinado
    BG_SURFACE_ALT = "#1A1B1F"      # Cards Interativos & Hover
    BG_SURFACE_ELEVATED = "#222328" # Modais e Cabeçalhos em Destaque
    BG_INPUT = "#0E0F12"            # Fundo Limpo para Inputs
    
    # Acento de Alta Performance (Nike Volt / Whoop Acid Lime)
    PRIMARY_NEON = "#CCFF00"        # Volt Neon Eletrizante (Estilo Nike Pro / Whoop)
    PRIMARY_NEON_DARK = "#A3E635"   # Volt Suave
    PRIMARY_TEXT_ON_NEON = "#090A0C"# Texto preto de alto contraste sobre Volt
    
    # Cores de Apoio Funcionais
    CYAN_ELECTRIC = "#38BDF8"       # Azul Hidratação & Oxigenação
    CRIMSON_NEON = "#FF3366"        # Vermelho Frequência Cardíaca / Alerta
    AMBER_GOLD = "#F59E0B"          # Âmbar Calorias / Fogo Metabólico
    PURPLE_MIND = "#A855F7"         # Violeta Serenidade / Oração
    TEAL_PHYSIO = "#14B8A6"         # Cinesiologia & Fisioterapia
    
    # Textos de Altíssima Legibilidade
    TEXT_WHITE = "#FFFFFF"          # Branco Puro para Títulos
    TEXT_PRIMARY = "#F4F4F5"        # Branco Suave para Corpo de Texto
    TEXT_SECONDARY = "#A1A1AA"      # Cinza Claro para Métricas e Legendas
    TEXT_MUTED = "#52525B"          # Cinza Sóbrio para Detalhes Técnicos
    
    # Bordas Finas e Minimalistas
    BORDER_DEFAULT = "#222328"      # Borda sutil de divisão
    BORDER_FOCUS = "#3F3F46"        # Borda em foco
    BORDER_NEON = "#CCFF00"         # Borda de seleção ativa
    BORDER_CYAN = "#38BDF8"
    BORDER_CRIMSON = "#FF3366"
    BORDER_GOLD = "#F59E0B"

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
    def all(width: float = 1, color: str = "#222328"):
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
    def card_container(content, border_color=SportColors.BORDER_DEFAULT, padding=16, radius=16, on_click=None, bgcolor=SportColors.BG_SURFACE):
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
    def badge(text: str, color: str, bg_color: str = None, icon=None):
        if not bg_color:
            bg_color = f"{color}1F"
        
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
            border_radius=8,
            bgcolor=bg_color,
            border=AppBorder.all(1, f"{color}3D"),
        )

    @staticmethod
    def section_header(title: str, subtitle: str = "", icon=None, action_button=None):
        title_row = []
        if icon:
            title_row.append(ft.Icon(icon, size=18, color=SportColors.PRIMARY_NEON))
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
