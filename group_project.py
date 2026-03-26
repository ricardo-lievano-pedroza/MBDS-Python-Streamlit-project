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



################################################################
# Jacek
################################################################
@st.cache_data(show_spinner=False)
def fetch_pokemon_json(q: str):
    url = f"https://pokeapi.co/api/v2/pokemon/{q.strip().lower()}"
    r = safe_get(url, timeout=10)
    if r is None:
        return None, 0  # network error

    if r.status_code != 200:
        return None, r.status_code

    try:
        return r.json(), 200
    except ValueError:
        return None, 0


@st.cache_data(show_spinner=False)
def fetch_move_details(move_url: str):
    r = safe_get(move_url, timeout=10)
    if r is None:
        return None

    if r.status_code != 200:
        return None

    try:
        m = r.json()
    except ValueError:
        return None

    return {
        "name": m["name"],
        "power": m["power"],
        "accuracy": m["accuracy"],
        "type": m["type"]["name"],
        "damage_class": m["damage_class"]["name"],
    }


@st.cache_data(show_spinner=False)
def fetch_type_data(type_name: str):
    url = f"https://pokeapi.co/api/v2/type/{type_name}"
    r = safe_get(url, timeout=10)
    if r is None:
        return None

    if r.status_code != 200:
        return None

    try:
        return r.json()
    except ValueError:
        return None


@st.cache_data(show_spinner=False)
def damaging_moves_for_pokemon(pokemon_id: int, pokemon_moves: list, limit: int = 12):
    moves = []
    for entry in pokemon_moves:
        d = fetch_move_details(entry["move"]["url"])
        if not d:
            continue
        if d["power"] is not None and d["power"] > 0:
            moves.append(d)
        if len(moves) >= limit:
            break
    return moves


def effectiveness_multiplier(move_type: str, defender_types: list[str]) -> float:
    type_data = fetch_type_data(move_type)
    if not type_data:
        return 1.0

    dr = type_data["damage_relations"]
    double_to = {t["name"] for t in dr["double_damage_to"]}
    half_to = {t["name"] for t in dr["half_damage_to"]}
    no_to = {t["name"] for t in dr["no_damage_to"]}

    eff = 1.0
    for dt in defender_types:
        if dt in double_to:
            eff *= 2.0
        elif dt in half_to:
            eff *= 0.5
        elif dt in no_to:
            eff *= 0.0
    return eff


def pick_atk_def(attacker_stats: dict, defender_stats: dict, damage_class: str) -> tuple[int, int]:
    if damage_class == "physical":
        return attacker_stats["attack"], defender_stats["defense"]
    return attacker_stats["special-attack"], defender_stats["special-defense"]

################################################################
# Alberto
################################################################
def run_battle(p1: dict, p2: dict, m1: dict, m2: dict) -> tuple[list[dict], list[dict], str]:
    s1 = stats_dict(p1)
    s2 = stats_dict(p2)

    p1_types = [t["type"]["name"] for t in p1["types"]]
    p2_types = [t["type"]["name"] for t in p2["types"]]

    hp1 = s1["hp"]
    hp2 = s2["hp"]

    log = []
    hp_hist = [
        {"round": 0, "pokemon": p1["name"].title(), "hp": hp1},
        {"round": 0, "pokemon": p2["name"].title(), "hp": hp2},
    ]

    def first_attacker() -> str:
        if s1["speed"] > s2["speed"]:
            return "p1"
        if s2["speed"] > s1["speed"]:
            return "p2"
        return random.choice(["p1", "p2"])

    for rnd in range(1, MAX_ROUNDS + 1):
        if hp1 <= 0 or hp2 <= 0:
            break

        first = first_attacker()
        order = [first, "p2" if first == "p1" else "p1"]

        for who in order:
            if hp1 <= 0 or hp2 <= 0:
                break

            if who == "p1":
                atk_p, def_p = p1, p2
                atk_stats, def_stats = s1, s2
                def_types = p2_types
                move = m1
                defender_hp = hp2
            else:
                atk_p, def_p = p2, p1
                atk_stats, def_stats = s2, s1
                def_types = p1_types
                move = m2
                defender_hp = hp1

            move_name = move["name"].replace("-", " ").title()
            power = int(move["power"]) if move["power"] is not None else 0
            acc = move["accuracy"]
            acc_val = 100 if acc is None else int(acc)
            dmg_class = move["damage_class"]
            mtype = move["type"]

            atk_stat, def_stat = pick_atk_def(atk_stats, def_stats, dmg_class)
            eff = effectiveness_multiplier(mtype, def_types)

            hit = random.random() < (acc_val / 100.0)
            if not hit:
                damage = 0
                result = "Missed"
            else:
                base_dmg = (2 * LEVEL / 5 + 2) * power
                stat_ratio = atk_stat / max(1, def_stat)
                damage = int((base_dmg * stat_ratio / 50 + 2) * eff)
                result = "Hit"

            defender_hp_after = max(0, defender_hp - damage)

            if who == "p1":
                hp2 = defender_hp_after
            else:
                hp1 = defender_hp_after

            log.append({
                "Round": rnd,
                "Attacker": atk_p["name"].title(),
                "Move": move_name,
                "Move Type": mtype,
                "Class": dmg_class,
                "Power": power,
                "Accuracy": acc_val,
                "Effectiveness": eff,
                "Damage": damage,
                "Defender": def_p["name"].title(),
                "Defender HP": defender_hp_after,
                "Result": result,
            })

        hp_hist.append({"round": rnd, "pokemon": p1["name"].title(), "hp": hp1})
        hp_hist.append({"round": rnd, "pokemon": p2["name"].title(), "hp": hp2})

    if hp1 <= 0 and hp2 <= 0:
        winner = "Draw (double KO)"
    elif hp2 <= 0:
        winner = p1["name"].title()
    elif hp1 <= 0:
        winner = p2["name"].title()
    else:
        winner = "Draw (100-round cap)"

    return log, hp_hist, winner
################################################################
# Shadi
################################################################

if "phase" not in st.session_state:
    st.session_state.phase = "input"


st.markdown("""
<style>
div[data-testid="stButton"] > button[kind="primary"]{
  width: 100%;
  height: 64px;
  border-radius: 14px;
  border: 2px solid rgba(255,255,255,0.35);
  background: linear-gradient(145deg, rgba(80,80,80,0.95),
             rgba(30,30,30,0.95));
  color: #fff;
  text-align: center;
  font-weight: 900;
  font-size: 16px;
  letter-spacing: 0.3px;
  line-height: 1.05;
  padding: 10px 14px;
  box-shadow:
    0 6px 0 rgba(0,0,0,0.55),
    inset 0 1px 0 rgba(255,255,255,0.25),
    inset 0 -2px 0 rgba(0,0,0,0.35);
  transition: transform 0.05s ease, box-shadow 0.05s ease, filter 0.08s ease;
}
div[data-testid="stButton"] > button[kind="primary"]:hover{ filter:
            brightness(1.08); }
div[data-testid="stButton"] > button[kind="primary"]:active{
  transform: translateY(4px);
  box-shadow:
    0 2px 0 rgba(0,0,0,0.55),
    inset 0 1px 0 rgba(255,255,255,0.20),
    inset 0 -2px 0 rgba(0,0,0,0.35);
}
</style>
""", unsafe_allow_html=True)


if st.session_state.phase == "input":
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.image("Poké_Ball_icon.svg.png", width=280)
    st.title("Pokémon Battle Dashboard (Gen 1–5)")

    name1 = st.text_input("Choose your first Pokémon! (Enter Pokémon name or Pokédex number.)", key="name1")
    if name1:
        p1, code = fetch_pokemon_json(name1)
        if code == 0:
            st.stop()
        if code == 404:
            st.error("First Pokémon not found.")
        elif p1 and p1["id"] > MAX_DEX:
            st.error(f"{p1['name'].title()} is #{p1['id']} (Gen 6+). Choose a Pokémon #649 or lower.")
        elif p1:
            st.session_state.p1 = p1

    show_p1_found = ("p1" in st.session_state) and ("p2" not in st.session_state) and (not st.session_state.get("name2"))
    if show_p1_found:
        st.success(f"Found {st.session_state.p1['name'].title()} (#{st.session_state.p1['id']})")

    if "p1" in st.session_state:
        name2 = st.text_input("Choose your second Pokémon! (Enter Pokémon name or Pokédex number.)", key="name2")
        if name2:
            p2, code = fetch_pokemon_json(name2)
            if code == 0:
                st.stop()
            if code == 404:
                st.error("Second Pokémon not found.")
            elif p2 and p2["id"] > MAX_DEX:
                st.error(f"{p2['name'].title()} is #{p2['id']} (Gen 6+). Choose a Pokémon #649 or lower.")
            elif p2:
                st.session_state.p2 = p2

        if "p2" in st.session_state:
            st.success(f"Found {st.session_state.p2['name'].title()} (#{st.session_state.p2['id']})")
            st.session_state.phase = "battle"
            st.rerun()

    if st.button("Reset"):
        reset_all()


elif st.session_state.phase == "battle":
    p1 = st.session_state.get("p1")
    p2 = st.session_state.get("p2")

    if not p1 or not p2:
        st.error("Missing Pokémon data. Please start over.")
        if st.button("Reset"):
            reset_all()
        st.stop()

    st.success("Ready for battle!")
    st.info("Commencing battle...")
    time.sleep(1.5)

    st.session_state.phase = "real_battle"
    st.rerun()


elif st.session_state.phase == "real_battle":
    st.markdown("<h2 style='text-align:center;'>The Battleground</h2>", unsafe_allow_html=True)

    p1 = st.session_state.get("p1")
    p2 = st.session_state.get("p2")
    if not p1 or not p2:
        st.error("Missing Pokémon data. Please start over.")
        st.stop()

    p1_name = p1["name"].title()
    p2_name = p2["name"].title()

    p1_stats = stats_dict(p1)
    p2_stats = stats_dict(p2)

    p1_types = [t["type"]["name"] for t in p1["types"]]
    p2_types = [t["type"]["name"] for t in p2["types"]]
    p1_types_html = type_chips_html(p1_types)
    p2_types_html = type_chips_html(p2_types)
    type_css = "\n".join(f".type-{t}{{ background:{c}; }}" for t, c in TYPE_COLORS.items())

    p1_sprite = (p1["sprites"].get("back_default") or p1["sprites"].get("front_default"))
    p2_sprite = p2["sprites"].get("front_default")

    back_img = load_image(p1_sprite) if p1_sprite else None
    front_img = load_image(p2_sprite) if p2_sprite else None
    back_uri = pil_to_data_uri(back_img) if back_img else ""
    front_uri = pil_to_data_uri(front_img) if front_img else ""
    bg_uri = img_file_to_data_uri("battle_bg.png")

    ORDER = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
    LABEL = {"hp": "HP", "attack": "Atk", "defense": "Def", "special-attack": "SpA", "special-defense": "SpD", "speed": "Spe"}
    p1_stats_line = " &#8226; ".join(f"{LABEL[k]} {p1_stats.get(k, 0)}" for k in ORDER)
    p2_stats_line = " &#8226; ".join(f"{LABEL[k]} {p2_stats.get(k, 0)}" for k in ORDER)

    st.markdown(
        f"""
<style>
  .battlefield {{
    position: relative;
    width: 100%;
    max-width: 900px;
    height: 320px;
    margin: 0 auto;
    border-radius: 16px;
    border: 1px solid rgba(0,0,0,0.15);
    background-image: url("{bg_uri}");
    background-repeat: no-repeat;
    background-position: center;
    background-size: 100% 100%;
    image-rendering: pixelated;
    overflow: hidden;
  }}
  .sprite {{ position: absolute; image-rendering: pixelated; }}
  .opponent {{
    top: 55px; right: 105px;
    width: 83px;
    transform: scale(2.0);
    transform-origin: top right;
  }}
  .player {{
    bottom: -70px; left: 55px;
    transform: scale(2.5);
    transform-origin: bottom left;
  }}
  .info-box {{
    position: absolute;
    padding: 10px 12px;
    border-radius: 12px;
    background: rgba(0,0,0,0.55);
    color: white;
    font-weight: 700;
    font-size: 16px;
    line-height: 1.15;
    backdrop-filter: blur(2px);
    max-width: 420px;
  }}
  .info-types {{ font-weight: 500; font-size: 13px; opacity: 0.95; margin-top: 4px; }}
  .info-stats {{ font-weight: 500; font-size: 12.5px; opacity: 0.95; margin-top: 6px; }}
  .opp-info {{ top: 8px; left: 16px; }}
  .ply-info {{ bottom: 8px; right: 16px; }}

  .type-chip {{
    display:inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 12px;
    color: rgba(0,0,0,0.85);
    margin-right: 6px;
    border: 1px solid rgba(255,255,255,0.35);
  }}
  {type_css}
</style>

<div class="battlefield">
  <img class="sprite opponent" src="{front_uri}" />
  <img class="sprite player" src="{back_uri}" />

  <div class="info-box opp-info">
    <div>{p2_name}</div>
    <div class="info-types">{p2_types_html}</div>
    <div class="info-stats">{p2_stats_line}</div>
  </div>

  <div class="info-box ply-info">
    <div>{p1_name}</div>
    <div class="info-types">{p1_types_html}</div>
    <div class="info-stats">{p1_stats_line}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.divider()

    stat_df = pd.DataFrame([
        {"pokemon": p1_name, **{k: p1_stats[k] for k in ORDER}},
        {"pokemon": p2_name, **{k: p2_stats[k] for k in ORDER}},
    ])

    melted = stat_df.melt(id_vars="pokemon", var_name="stat", value_name="value")
    melted["stat"] = melted["stat"].map(STAT_LABELS).fillna(melted["stat"])

    st.subheader("Base Stat Comparison")
    fig_bar = px.bar(
        melted,
        x="stat",
        y="value",
        color="pokemon",
        barmode="group",
        labels={"stat": "Stat", "value": "Base Stat", "pokemon": "Pokémon"},
    )
    fig_bar.update_traces(hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y}<extra></extra>")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    st.markdown("<h2 style='text-align:center;'>Move Selection</h2>", unsafe_allow_html=True)


################################################################
# Mateus 
################################################################
p1_moves = damaging_moves_for_pokemon(p1["id"], p1["moves"], limit=8)
    p2_moves = damaging_moves_for_pokemon(p2["id"], p2["moves"], limit=8)

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown(f"### {p1_name}")
        for mv in p1_moves:
            move_name = mv["name"].replace("-", " ").title()
            c_btn, c_badge = st.columns([1, 1], gap="small")
            with c_btn:
                if st.button(move_name, key=f"p1_move_{mv['name']}", type="primary"):
                    st.session_state["p1_move"] = mv
            with c_badge:
                st.markdown(
                    f"<div style='display:flex; align-items:center; height:64px;'>"
                    f"{type_badge_html(mv['type'])}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        chosen = st.session_state.get("p1_move")
        if chosen:
            st.info(
                f"**Move Selected:** {chosen['name'].replace('-', ' ').title()}  \n"
                f"**Power:** {chosen['power']}  \n"
                f"**Accuracy:** {chosen['accuracy']}  \n"
                f"**Type:** {chosen['type'].title()}  \n"
                f"**Class:** {chosen['damage_class'].title()}"
            )

    with right:
        st.markdown(f"### {p2_name}")
        for mv in p2_moves:
            move_name = mv["name"].replace("-", " ").title()
            c_btn, c_badge = st.columns([1, 1], gap="small")
            with c_btn:
                if st.button(move_name, key=f"p2_move_{mv['name']}", type="primary"):
                    st.session_state["p2_move"] = mv
            with c_badge:
                st.markdown(
                    f"<div style='display:flex; align-items:center; height:64px;'>"
                    f"{type_badge_html(mv['type'])}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        chosen = st.session_state.get("p2_move")
        if chosen:
            st.info(
                f"**Move Selected:** {chosen['name'].replace('-', ' ').title()}  \n"
                f"**Power:** {chosen['power']}  \n"
                f"**Accuracy:** {chosen['accuracy']}  \n"
                f"**Type:** {chosen['type'].title()}  \n"
                f"**Class:** {chosen['damage_class'].title()}"
            )

    st.divider()

################################################################
# Blanca
################################################################
    st.subheader("Combat Simulation")

    m1 = st.session_state.get("p1_move")
    m2 = st.session_state.get("p2_move")

    if m1 and m2:
        st.success("Ready to battle!")

    battle_disabled = not (m1 and m2)
    if st.button("Battle!", type="primary", disabled=battle_disabled):
        log_rows, hp_hist, winner = run_battle(p1, p2, m1, m2)
        st.session_state["battle_log"] = log_rows
        st.session_state["hp_history"] = hp_hist
        st.session_state["battle_winner"] = winner

    if ("battle_log" in st.session_state and "battle_winner" in st.session_state):
        st.subheader("Battle Log Table")
        log_df = pd.DataFrame(st.session_state["battle_log"])
        for col in ["Move Type", "Class", "Result"]:
            if col in log_df.columns:
                log_df[col] = log_df[col].astype(str).str.replace("-", " ").str.title()
        log_df = log_df.rename(columns={"Class": "Damage Class"})
        st.dataframe(log_df, use_container_width=True, hide_index=True)

    if "hp_history" in st.session_state:
        st.subheader("HP Over Time")
        hp_df = pd.DataFrame(st.session_state["hp_history"])
        fig_line = px.line(
            hp_df,
            x="round",
            y="hp",
            color="pokemon",
            labels={"round": "Round", "hp": "HP", "pokemon": "Pokémon"},
        )
        fig_line.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Round: %{x}<br>HP: %{y}<extra></extra>"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    if "battle_winner" in st.session_state:
        st.subheader("And the winner is...")

        winner = st.session_state["battle_winner"]

        winner_sprite_url = None
        if winner == p1_name:
            winner_sprite_url = p1["sprites"].get("front_default")
        elif winner == p2_name:
            winner_sprite_url = p2["sprites"].get("front_default")

        if winner_sprite_url:
            img = load_sprite_scaled(winner_sprite_url, scale=5)
            if img is not None:
                c1, c2, c3 = st.columns([1, 1, 1])
                with c2:
                    st.image(img)

        st.success(f"🏆 {winner} wins the battle!")

    if st.button("Reset"):
        reset_all()
