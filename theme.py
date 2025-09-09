# theme.py

class Theme:
    """
    Classe para centralizar as definições de estilo da aplicação.
    Isso garante uma aparência unificada e facilita a manutenção do design.
    """
    # Paleta de Cores Principal
    PRIMARY = "#3498db"      # Azul
    ACCENT = "#2ecc71"       # Verde (Sucesso)
    DANGER = "#e74c3c"       # Vermelho (Erro, Exclusão)
    WARNING = "#f1c40f"      # Amarelo (Aviso)
    PURPLE = "#9b59b6"      # Roxo
    ORANGE = "#e67e22"      # Laranja

    # Cores de UI (Interface do Usuário)
    BG_COLOR = "#f5f5f5"     # Fundo principal (Cinza muito claro)
    CARD_BG = "#ffffff"     # Fundo de cards e widgets (Branco)
    TEXT_COLOR = "#333333"   # Texto principal (Cinza escuro)
    LIGHT_TEXT = "#7f8c8d"  # Texto secundário (Cinza médio)
    DISABLED_BG = "#ecf0f1"  # Fundo para campos desabilitados
    SEPARATOR_COLOR = "#e0e0e0" # Cor para linhas separadoras

    # Fontes
    FONT_FAMILY = "Helvetica"
    FONT_DEFAULT = (FONT_FAMILY, 11)
    FONT_BOLD = (FONT_FAMILY, 11, "bold")
    FONT_TITLE = (FONT_FAMILY, 24, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 16, "bold")
    FONT_SMALL = (FONT_FAMILY, 9)

    # Estilos de Widgets (para serem usados com `**Theme.STYLE_NAME`)
    BUTTON_PRIMARY = {
        "bg": PRIMARY,
        "fg": "white",
        "font": (FONT_FAMILY, 11, "bold"),
        "padx": 15, "pady": 8,
        "relief": "flat",
        "cursor": "hand2"
    }

    BUTTON_SUCCESS = {
        "bg": ACCENT,
        "fg": "white",
        "font": (FONT_FAMILY, 12, "bold"),
        "relief": "flat",
        "cursor": "hand2",
        "padx": 15, "pady": 10
    }
    
    BUTTON_DANGER = {
        "bg": DANGER,
        "fg": "white",
        "font": (FONT_FAMILY, 10),
        "padx": 15, "pady": 6,
        "relief": "flat",
        "cursor": "hand2"
    }

    CARD_STYLE = {
        "bg": CARD_BG,
        "relief": "solid",
        "bd": 1,
        "highlightbackground": SEPARATOR_COLOR,
        "highlightthickness": 1
    }

    ENTRY_STYLE = {
        "bg": "white",
        "fg": TEXT_COLOR,
        "font": FONT_DEFAULT,
        "relief": "solid",
        "bd": 1
    }

    LABEL_FRAME_STYLE = {
        "bg": CARD_BG,
        "fg": TEXT_COLOR,
        "font": FONT_BOLD
    }