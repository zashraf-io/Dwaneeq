from __future__ import annotations
from arabic_reshaper import arabic_reshaper as ar
import os, sys
import json

# Light mode theme colors
LIGHT_THEME = {
    "sidebar_bg": "#f0f0f5",
    "main_bg": "grey90",
    "login_bg": "grey87",
    "text": "#222222",
    "heading": "#0a0a0a",
    "sidebar_btn": "grey20",
    "sidebar_btn_active": "#a3c9ff",
    "accent": "#3b82f6",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000",
    "button_text": "#ffffff",
    "border": "#dcdcdc"
}

Light_Blue = {
    "bg": "#f0f4ff",
    "fg": "#1c1c1c",
    "login_bg": "grey87",
    "sidebar_bg": "#e1ecff",
    "sidebar_btn": "#2196F3",
    "sidebar_btn_active": "#a3c9ff",
    "accent": "#3b82f6",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000"
}

Light_Yellow = {
    "bg": "#fffdf0",
    "fg": "#1c1c1c",
    "login_bg": "grey87",
    "sidebar_bg": "#fff8cc",
    "sidebar_btn": "#FFD54F",
    "sidebar_btn_active": "#ffe066",
    "accent": "#facc15",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000"
}

Light_Green = {
    "bg": "#f0fff5",
    "fg": "#1c1c1c",
    "login_bg": "grey87",
    "sidebar_bg": "#d1fae5",
    "sidebar_btn": "#4CAF50",
    "sidebar_btn_active": "#6ee7b7",
    "accent": "#10b981",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000"
}

Light_Red = {
    "bg": "#fff5f5",
    "fg": "#1c1c1c",
    "login_bg": "grey87",
    "sidebar_bg": "#ffe4e6",
    "sidebar_btn": "#e63946",
    "sidebar_btn_active": "#fca5a5",
    "accent": "#ef4444",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000"
}

Light_Blue = {
    "bg": "#f0f4ff",
    "fg": "#1c1c1c",
    "login_bg": "grey87",
    "sidebar_bg": "#e1ecff",
    "sidebar_btn": "#cce0ff",
    "sidebar_btn_active": "#a3c9ff",
    "accent": "#3b82f6",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000"
}

Light_Purple = {
    "bg": "#f6f0ff",              # general background
    "fg": "#1d1426",              # general text
    "login_bg": "#efe3fc",
    "sidebar_bg": "#e4d4f7",
    "sidebar_btn": "#B388EB",
    "sidebar_btn_active": "#be9ae8",
    "accent": "#a855f7",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000"
}

Light_Black = {
    "bg": "#f2f2f2",
    "fg": "#0d0d0d",
    "login_bg": "#e8e8e8",
    "sidebar_bg": "#d4d4d4",
    "sidebar_btn": "#333333",
    "sidebar_btn_active": "#a5a5a5",
    "accent": "#333333",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000"
}

Light_Grey = {
    "bg": "#f7f7f7",
    "fg": "#1e1e1e",
    "login_bg": "#eaeaea",
    "sidebar_bg": "#dedede",
    "sidebar_btn": "#B0B0B0",
    "sidebar_btn_active": "#b8b8b8",
    "accent": "#8a8a8a",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000"
}

# Dark mode theme colors
DARK_THEME = {
    "sidebar_bg": "#1e1e2f",
    "main_bg": "#121222",
    "login_bg": "#2a2a3b",
    "text": "#f5f5f5",
    "heading": "#ffffff",
    "button_bg": "#1a73e8",
    "button_text": "#ffffff",
    "border": "#444444"
}

Dark_Blue = {
    "bg": "#0f172a",
    "fg": "#e0f2fe",
    "login_bg": "#2a2a3b",
    "sidebar_bg": "#1e293b",
    "sidebar_btn": "#1565C0",
    "sidebar_btn_active": "#3b82f6",
    "accent": "#3b82f6",
    "entry_bg": "#1e293b",
    "entry_fg": "#ffffff"
}

Dark_Yellow = {
    "bg": "#1f1c0f",
    "fg": "#fff7cd",
    "login_bg": "#2a2a3b",
    "sidebar_bg": "#2c260f",
    "sidebar_btn": "#D4AC3F",
    "sidebar_btn_active": "#facc15",
    "accent": "#facc15",
    "entry_bg": "#2c260f",
    "entry_fg": "#ffffff"
}

Dark_Green = {
    "bg": "#0f2e1f",
    "fg": "#d1fae5",
    "login_bg": "#2a2a3b",
    "sidebar_bg": "#134e4a",
    "sidebar_btn": "#2e7d32",
    "sidebar_btn_active": "#10b981",
    "accent": "#10b981",
    "entry_bg": "#1f3f32",
    "entry_fg": "#ffffff"
}

Dark_Red = {
    "bg": "#2c0f0f",                              # general background
    "fg": "#fecaca",                              # general text
    "login_bg": "#3b1a1a",                        # login screen background
    "sidebar_bg": "#4b1e1e",                      # sidebar background
    "sidebar_btn": "#800000",                     # sidebar button normal
    "sidebar_btn_active": "#ef4444",              # sidebar button active
    "accent": "#ef4444",                          # main accent
    "entry_bg": "#3a1a1a",                        # entry background
    "entry_fg": "#ffffff",                        # entry text
}

Dark_Purple = {
    "bg": "#1e102b",
    "fg": "#f4f0fa",
    "login_bg": "#2e1c45",
    "sidebar_bg": "#321b4f",
    "sidebar_btn": "#7B61A8",
    "sidebar_btn_active": "#6d30a3",
    "accent": "#c084fc",
    "entry_bg": "#2a1e3d",
    "entry_fg": "#ffffff"
}

Dark_Black = {
    "bg": "#0d0d0d",
    "fg": "#f0f0f0",
    "login_bg": "#1a1a1a",
    "sidebar_bg": "#222222",
    "sidebar_btn": "#2D2D2D",
    "sidebar_btn_active": "#444444",
    "accent": "#ffffff",
    "entry_bg": "#1c1c1c",
    "entry_fg": "#ffffff"
}

Dark_Grey = {
    "bg": "#1f1f1f",
    "fg": "#f0f0f0",
    "login_bg": "#2c2c2c",
    "sidebar_bg": "#3a3a3a",
    "sidebar_btn": "#444444",
    "sidebar_btn_active": "#626262",
    "accent": "#b0b0b0",
    "entry_bg": "#2e2e2e",
    "entry_fg": "#ffffff"
}

# Language loading
def load_language(lang_code):
    lang_file = os.path.join(os.path.dirname(__file__), "lang", f"{lang_code}.json")
    try:
        with open(lang_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if lang_code == "ar":
                # Reshape string values
                for k, v in data.items():
                    if isinstance(v, str):
                        data[k] = ar.reshape(v)
                    elif isinstance(v, list):
                        data[k] = [ar.reshape(item) if isinstance(item, str) else item for item in v]
                    elif isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            if isinstance(sub_v, str):
                                data[k][sub_k] = ar.reshape(sub_v)
            return data
    except Exception as e:
        print(f"Error loading {lang_code}.json: {e}")
        return {}

LANG = {
    "en": load_language("en"),
    "ar": load_language("ar")
}

# align
align = {
    "add_transaction" : {
        "ltr": {
            "amount_labl": {"column": 0, "sticky": "w"},
            "amount_entry": {"column": 0, "sticky": "e"},
            "currency": {"column": 1, "sticky": "w"},
            "note_labl": {"column": 0, "sticky": "w"},
            "note_text_box": {"column": 1, "sticky": "e"},
            "date_frame" : {"column": 0, "sticky": "w"},
            "date_labl" : {"column": 0, "sticky": "e"},
            "open_cal_btn" : {"column": 2, "sticky": "w"},
            
        },
        "rtl": {
            "amount_labl": {"column": 1, "sticky": "e"},
            "amount_entry": {"column": 1, "sticky": "w"},
            "currency": {"column": 0, "sticky": "e"},
            "note_labl": {"column": 1, "sticky": "e"},
            "note_text_box": {"column": 0, "sticky": "w"},
            "date_frame" : {"column": 1, "sticky": "e"},
            "date_labl" : {"column": 2, "sticky": "e"},
            "open_cal_btn" : {"column": 0, "sticky": "e"},

    }
        },

    "budget" : {
        "ltr": {
            "total_budget_lbl" : {"column": 0, "sticky": "w"},
            "total_budget_amount" : {"column": 1, "sticky": "w"},
            "spent_lbl" : {"column": 0, "sticky": "w"},
            "spent_amount" : {"column": 1, "sticky": "w"},
            "remaining_lbl" : {"column": 0, "sticky": "w"},
            "remaining_amount" : {"column": 1, "sticky": "w"},
            "currency" : {"column": 2, "sticky": "w"}

        },
        "rtl": {
            "total_budget_lbl" : {"column": 2, "sticky": "e"},
            "total_budget_amount" : {"column": 1, "sticky": "e"},
            "spent_lbl" : {"column": 2, "sticky": "e"},
            "spent_amount" : {"column": 1, "sticky": "e"},
            "remaining_lbl" : {"column": 2, "sticky": "e"},
            "remaining_amount" : {"column": 1, "sticky": "e"},
            "currency" : {"column": 0, "sticky": "e"}

        }
    },
}

currency = "EGP"
current_user_id = "not defined"
choosed_mode = "dark"
choosed_theme = "black"
choosed_colors = Dark_Black
lang_name = "en"
choosed_lang = LANG[lang_name]
direction = "rtl"

def set_mode(mode: str) -> None:
    "set the app choosed mode ['light', 'dark']"
    global choosed_mode
    if mode == 'light':
        choosed_mode = 'light'
    elif mode == 'dark':
        choosed_mode = 'dark'

    set_theme(choosed_theme)

def set_theme(theme: str) -> None:
    """sets the theme used in the app into the choosed theme by passing dictionary name
    ['blue' - 'yellow' - 'green' - 'red']
    default value will use the current theme"""
    global choosed_colors, choosed_mode, choosed_theme
    choosed_theme = theme
    if choosed_mode == 'light':
        if theme == 'blue':
            choosed_colors = Light_Blue
        elif theme == 'yellow':
            choosed_colors  = Light_Yellow
        elif theme == 'green':
            choosed_colors = Light_Green
        elif theme == 'red':
            choosed_colors = Light_Red
        elif theme == 'purple':
            choosed_colors = Light_Purple
        elif theme == 'grey':
            choosed_colors = Light_Grey
        elif theme == 'black':
            choosed_colors = Light_Black
    elif choosed_mode == 'dark':
        if theme == 'blue':
            choosed_colors = Dark_Blue
        elif theme == 'yellow':
            choosed_colors  = Dark_Yellow
        elif theme == 'green':
            choosed_colors = Dark_Green
        elif theme == 'red':
            choosed_colors = Dark_Red
        elif theme == 'purple':
            choosed_colors = Dark_Purple
        elif theme == 'grey':
            choosed_colors = Dark_Grey
        elif theme == 'black':
            choosed_colors = Dark_Black


def set_lang(lang: str) -> None:
    "sets the language used in the app by passing the dictionary name ['AR' - 'EN']"
    global choosed_lang, lang_name, direction
    if lang == "ar":
        lang_name = "ar"
        direction = "rtl"
    elif lang == "en":
        lang_name = "en"
        direction = "ltr"
    
    choosed_lang = LANG[lang_name]
        

def get_current_lang() -> str:
    "returns the curent choosed language"
    global lang_name
    return lang_name


def set_current_user_id(user_id) -> None:
    "sets the global user id used in the whole app during the session"
    global current_user_id
    current_user_id = str(user_id)

def get_current_user_id() -> int | str:
    "returns the global user id used in the session"
    if current_user_id != 'not defined':
        return int(current_user_id)
    else:
        return 0

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
