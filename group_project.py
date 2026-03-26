################################################################
# Ricardo
################################################################
import streamlit as st
import requests
import time
import base64
import random
import pandas as pd
import plotly.express as px
from PIL import Image
from io import BytesIO
from typing import Optional

MAX_DEX = 649
LEVEL = 50
MAX_ROUNDS = 100

TYPE_COLORS = {
    "normal": "#A8A77A",
    "fire": "#EE8130",
    "water": "#6390F0",
    "electric": "#F7D02C",
    "grass": "#7AC74C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "dark": "#705746",
    "steel": "#B7B7CE",
    "fairy": "#D685AD",
}

STAT_LABELS = {
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "special-attack": "Sp. Atk",
    "special-defense": "Sp. Def",
    "speed": "Speed",
}

def safe_get(url: str, timeout: int = 10) -> Optional[requests.Response]:
    try:
        return requests.get(url, timeout=timeout)
    except requests.exceptions.ConnectionError:
        st.error("Connection error: couldn't reach PokeAPI. Check your internet connection and try again.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out while contacting PokeAPI. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error while contacting PokeAPI: {e}")
        return None


def stats_dict(p: dict) -> dict:
    return {s["stat"]["name"]: s["base_stat"] for s in p["stats"]}


def img_file_to_data_uri(path: str) -> str:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def pil_to_data_uri(img: Image.Image, fmt="PNG") -> str:
    buf = BytesIO()
    img.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/{fmt.lower()};base64,{b64}"


def load_image(url: str) -> Optional[Image.Image]:
    r = safe_get(url, timeout=10)
    if r is None:
        return None
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        st.error("Failed to download a sprite image.")
        return None
    try:
        return Image.open(BytesIO(r.content))
    except Exception:
        st.error("Downloaded sprite image could not be opened.")
        return None


def load_sprite_scaled(url: str, scale: int = 3) -> Optional[Image.Image]:
    img = load_image(url)
    if img is None:
        return None
    img = img.convert("RGBA")
    w, h = img.size
    return img.resize((w * scale, h * scale), resample=Image.NEAREST)


def type_chips_html(types: list[str]) -> str:
    return " ".join(f'<span class="type-chip type-{t}">{t.upper()}</span>' for t in types)


def reset_all():
    for k in ("phase", "name1", "name2", "p1", "p2", "p1_move", "p2_move", "battle_log", "battle_winner", "hp_history"):
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


def type_badge_html(t: str) -> str:
    color = TYPE_COLORS.get(t, "#999999")
    return f"""
    <div style="
        width: 84px;
        height: 30px;
        border-radius: 999px;
        background: {color};
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 11px;
        line-height: 30px;
        color: rgba(0,0,0,0.85);
        border: 1px solid rgba(255,255,255,0.35);
    ">{t.upper()}</div>
    """

################################################################
# Jacek
################################################################


################################################################
# Alberto
################################################################


################################################################
# Shadi
################################################################


################################################################
# Mateus 
################################################################


################################################################
# Blanca
################################################################