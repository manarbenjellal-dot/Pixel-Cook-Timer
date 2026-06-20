# -*- coding: utf-8 -*-
"""
Pixel Cook Timer — app.py
A retro pixel-art Streamlit cooking timer.
Run: streamlit run app.py
"""

import time
import base64
import pathlib
import streamlit as st

# ── Page config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="Pixel Cook Timer",
    page_icon="🍳",
    layout="centered",
)

# ── Food / method catalogue ───────────────────────────────────────────────────
# Keys are plain ASCII — no emoji — to avoid Windows encoding issues.
# {food_key: {method: duration_seconds}}
FOODS: dict[str, dict[str, int]] = {
    "Rice":    {"Boiled": 30 * 60, "Smoked": 45 * 60},
    "Eggs":    {"Boiled": 10 * 60, "Fried in pan": 5 * 60,
                "Oven": 15 * 60,   "Smoked": 20 * 60},
    "Chicken": {"Fried in pan": 20 * 60, "Oven": 45 * 60, "Smoked": 90 * 60},
    "Beef":    {"Fried in pan": 15 * 60, "Oven": 40 * 60, "Smoked": 120 * 60},
    "Fish":    {"Fried in pan": 10 * 60, "Oven": 25 * 60, "Smoked": 60 * 60},
    "Bread":   {"Oven": 35 * 60, "Toasted": 5 * 60, "Smoked": 20 * 60},
    "Popcorn": {"Fried in pan": 5 * 60, "Microwave": 3 * 60},
    "Salmon":  {"Fried in pan": 8 * 60, "Oven": 20 * 60, "Smoked": 50 * 60},
    "Sausage": {"Fried in pan": 10 * 60, "Oven": 25 * 60,
                "Boiled": 15 * 60, "Smoked": 30 * 60},
    "Bacon":   {"Fried in pan": 8 * 60, "Oven": 15 * 60, "Smoked": 40 * 60},
    "Cookies": {"Oven": 12 * 60},
    "Noodles": {"Boiled": 8 * 60, "Fried in pan": 10 * 60},
}

# Display label shown in the dropdown (emoji + name)
FOOD_LABELS: dict[str, str] = {
    "Rice":    "Rice",
    "Eggs":    "Eggs",
    "Chicken": "Chicken",
    "Beef":    "Beef",
    "Fish":    "Fish",
    "Bread":   "Bread",
    "Popcorn": "Popcorn",
    "Salmon":  "Salmon",
    "Sausage": "Sausage",
    "Bacon":   "Bacon",
    "Cookies": "Cookies",
    "Noodles": "Noodles",
}

# Map food key -> image path
FOOD_IMAGES: dict[str, str] = {
    "Rice":    "assets/rice.png",
    "Eggs":    "assets/egg.png",
    "Chicken": "assets/chicken.png",
    "Beef":    "assets/beef.png",
    "Fish":    "assets/fish.png",
    "Bread":   "assets/bread.png",
    "Popcorn": "assets/popcorn.png",
    "Salmon":  "assets/salmon.png",
    "Sausage": "assets/sausage.png",
    "Bacon":   "assets/bacon.png",
    "Cookies": "assets/cookies.png",
    "Noodles": "assets/noodles.png",
}

DING_PATH = pathlib.Path("assets/ding.mp3")

# ── Pastel pixel-art CSS ──────────────────────────────────────────────────────
PIXEL_CSS = """
<style>
  /* Import a pixel-art Google Font */
  @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

  /* ── global background & font ── */
  html, body, [data-testid="stAppViewContainer"] {
      background-color: #FFF5CC !important;
      font-family: 'Press Start 2P', monospace !important;
  }

  /* ── hide default Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }

  /* ── page title ── */
  h1 {
      font-family: 'Press Start 2P', monospace !important;
      color: #c0527a !important;
      text-align: center;
      font-size: 1.4rem !important;
      text-shadow: 3px 3px 0px #FFD6E0;
      letter-spacing: 2px;
  }

  /* ── section headers ── */
  h3 {
      font-family: 'Press Start 2P', monospace !important;
      color: #5a7abf !important;
      font-size: 0.65rem !important;
  }

  /* ── pixel selectbox label ── */
  label, .stSelectbox label {
      font-family: 'Press Start 2P', monospace !important;
      color: #5a7abf !important;
      font-size: 0.55rem !important;
  }

  /* ── selectbox control ── */
  [data-testid="stSelectbox"] > div > div {
      background-color: #D6F0FF !important;
      border: 3px solid #5a7abf !important;
      border-radius: 0px !important;
      image-rendering: pixelated;
      font-family: 'Press Start 2P', monospace !important;
      font-size: 0.6rem !important;
      color: #1a1a2e !important;
  }
  /* dropdown text items */
  [data-testid="stSelectbox"] span,
  [data-testid="stSelectbox"] p,
  [data-baseweb="select"] span,
  [data-baseweb="select"] div,
  [data-baseweb="menu"] li,
  [data-baseweb="menu"] div {
      font-family: 'Press Start 2P', monospace !important;
      font-size: 0.55rem !important;
      color: #1a1a2e !important;
  }

  /* ── food grid buttons ── */
  div[data-testid="stButton"] button[kind="secondary"] {
      font-family: 'Press Start 2P', monospace !important;
      font-size: 0.38rem !important;
      border-radius: 0px !important;
      border: 3px solid #aaa !important;
      border-top: none !important;
      box-shadow: 2px 2px 0px #aaa !important;
      background-color: #fff !important;
      color: #1a1a2e !important;
      padding: 4px 2px !important;
      margin-top: 0px !important;
  }

  /* ── pixel buttons ── */
  .stButton > button {
      font-family: 'Press Start 2P', monospace !important;
      font-size: 0.55rem !important;
      border-radius: 0px !important;
      border: 3px solid #444 !important;
      box-shadow: 4px 4px 0px #444 !important;
      transition: box-shadow 0.05s, transform 0.05s;
      cursor: pointer;
      padding: 10px 16px !important;
  }
  .stButton > button:active {
      box-shadow: 1px 1px 0px #444 !important;
      transform: translate(3px, 3px);
  }

  /* start button — pink */
  .start-btn .stButton > button {
      background-color: #FFD6E0 !important;
      color: #c0527a !important;
  }
  /* pause button — yellow */
  .pause-btn .stButton > button {
      background-color: #FFF5CC !important;
      color: #a07000 !important;
  }
  /* resume button — green */
  .resume-btn .stButton > button {
      background-color: #D9F7D6 !important;
      color: #3a7a35 !important;
  }
  /* reset button — blue */
  .reset-btn .stButton > button {
      background-color: #D6F0FF !important;
      color: #1a4a8a !important;
  }

  /* ── countdown display card ── */
  .timer-card {
      background-color: #1a1a2e;
      border: 4px solid #c0527a;
      box-shadow: 6px 6px 0px #c0527a;
      padding: 28px 20px;
      text-align: center;
      margin: 18px auto;
      max-width: 340px;
  }
  .timer-digits {
      font-family: 'Press Start 2P', monospace;
      font-size: 3.2rem;
      color: #FFD6E0;
      letter-spacing: 4px;
      text-shadow: 0 0 12px #FF6B9D, 0 0 24px #FF6B9D;
  }
  .timer-label {
      font-family: 'Press Start 2P', monospace;
      font-size: 0.5rem;
      color: #888;
      margin-top: 8px;
  }

  /* ── food image card ── */
  .food-card {
      background-color: #D9F7D6;
      border: 4px solid #5a9e55;
      box-shadow: 5px 5px 0px #5a9e55;
      padding: 16px;
      text-align: center;
      margin: 12px auto;
      max-width: 240px;
  }

  /* ── ready message ── */
  .ready-msg {
      font-family: 'Press Start 2P', monospace;
      font-size: 1.1rem;
      color: #c0527a;
      text-align: center;
      text-shadow: 3px 3px 0px #FFD6E0;
      animation: blink 0.8s step-end infinite;
      padding: 20px;
  }
  @keyframes blink {
      50% { opacity: 0; }
  }

  /* ── info line ── */
  .info-line {
      font-family: 'Press Start 2P', monospace;
      font-size: 0.5rem;
      color: #888;
      text-align: center;
      margin-top: -8px;
      margin-bottom: 12px;
  }
</style>
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_time(seconds: int) -> str:
    """Format seconds as MM:SS."""
    m, s = divmod(max(seconds, 0), 60)
    return f"{m:02d}:{s:02d}"


def img_to_b64(path: str) -> str | None:
    """Read an image file and return its base-64 data URI."""
    p = pathlib.Path(path)
    if not p.exists():
        return None
    data = p.read_bytes()
    b64  = base64.b64encode(data).decode()
    return f"data:image/png;base64,{b64}"


def audio_autoplay_html(path: pathlib.Path) -> str:
    """Return an HTML audio tag that autoplays once."""
    b64 = base64.b64encode(path.read_bytes()).decode()
    return (
        f'<audio autoplay="true" style="display:none">'
        f'<source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">'
        f'</audio>'
    )

# ── Session state initialisation ─────────────────────────────────────────────

def _init_state():
    defaults = {
        "running":       False,   # timer is actively counting down
        "paused":        False,   # timer is paused mid-countdown
        "remaining":     0,       # seconds left
        "total":         0,       # original duration in seconds
        "last_tick":     0.0,     # wall-clock time of last update
        "done":          False,   # reached zero
        "play_ding":     False,   # trigger the ding sound once
        "food":          list(FOODS.keys())[0],
        "method":        "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ── Inject CSS ────────────────────────────────────────────────────────────────
st.markdown(PIXEL_CSS, unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown("# &#127859; Pixel Cook Timer")
st.markdown(
    '<p class="info-line">select your food · choose a method · start cooking</p>',
    unsafe_allow_html=True,
)

# ── Food picker ───────────────────────────────────────────────────────────────
st.markdown("---")

food_keys = list(FOODS.keys())

# Guard: if stored food no longer valid, reset to first
if st.session_state["food"] not in food_keys:
    st.session_state["food"] = food_keys[0]

food_choice = st.session_state["food"]

# Label above the grid
st.markdown(
    '<p style="font-family:\'Press Start 2P\',monospace;font-size:0.6rem;'
    'color:#5a7abf;margin-bottom:6px;">Choose your food</p>',
    unsafe_allow_html=True,
)

# Render food grid: 6 columns × 2 rows
COLS_PER_ROW = 6
rows = [food_keys[i:i+COLS_PER_ROW] for i in range(0, len(food_keys), COLS_PER_ROW)]

for row in rows:
    cols = st.columns(len(row))
    for col, food in zip(cols, row):
        with col:
            img_src = img_to_b64(FOOD_IMAGES.get(food, ""))
            selected = (food == food_choice)
            # Card border changes when selected
            border_color = "#c0527a" if selected else "#aaa"
            bg_color     = "#FFD6E0" if selected else "#fff"
            shadow       = f"3px 3px 0px {border_color}"

            # Show the image as an HTML card above the button
            if img_src:
                st.markdown(
                    f'<div style="background:{bg_color};border:3px solid {border_color};'
                    f'box-shadow:{shadow};padding:6px;text-align:center;'
                    f'margin-bottom:-12px;">'
                    f'<img src="{img_src}" style="width:52px;height:52px;'
                    f'object-fit:contain;image-rendering:pixelated;display:block;margin:auto;"/>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            # Invisible-ish label button acts as the click target
            if st.button(
                food,
                key=f"food_btn_{food}",
                use_container_width=True,
            ):
                st.session_state["food"] = food
                st.rerun()

food_choice = st.session_state["food"]

st.markdown("---")

# ── Method selector + large food preview ──────────────────────────────────────
col_sel, col_img = st.columns([1, 1], gap="large")

with col_sel:
    # ── Dynamic method selector (only valid methods for chosen food) ───────
    methods = list(FOODS[food_choice].keys())
    if st.session_state["method"] not in methods:
        st.session_state["method"] = methods[0]

    method_choice = st.selectbox(
        "Cooking method",
        methods,
        index=methods.index(st.session_state["method"]),
        key="method_select",
    )
    st.session_state["method"] = method_choice

    duration_sec = FOODS[food_choice][method_choice]
    st.markdown(
        f'<p class="info-line">&#9201; {duration_sec // 60} min total</p>',
        unsafe_allow_html=True,
    )

with col_img:
    # ── Large food image ───────────────────────────────────────────────────
    img_path = FOOD_IMAGES.get(food_choice, "")
    img_src  = img_to_b64(img_path) if img_path else None
    if img_src:
        st.markdown(
            f'<div class="food-card">'
            f'<img src="{img_src}" style="width:140px;height:140px;'
            f'object-fit:contain;image-rendering:pixelated;" />'
            f'<div style="font-family:\'Press Start 2P\',monospace;font-size:0.5rem;'
            f'color:#3a7a35;margin-top:8px;">{food_choice}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="food-card" style="font-size:3rem;">&#127859;<br>'
            f'<span style="font-size:0.5rem;">{food_choice}</span></div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Timer tick logic ──────────────────────────────────────────────────────────
# Called on every rerun while the timer is running.
if st.session_state["running"] and not st.session_state["paused"]:
    now     = time.time()
    elapsed = now - st.session_state["last_tick"]
    st.session_state["last_tick"]  = now
    st.session_state["remaining"] -= int(elapsed)

    if st.session_state["remaining"] <= 0:
        st.session_state["remaining"] = 0
        st.session_state["running"]   = False
        st.session_state["done"]      = True
        st.session_state["play_ding"] = True

# ── Countdown display ─────────────────────────────────────────────────────────
if st.session_state["done"]:
    # Play ding once
    if st.session_state["play_ding"] and DING_PATH.exists():
        st.markdown(audio_autoplay_html(DING_PATH), unsafe_allow_html=True)
        st.session_state["play_ding"] = False

    st.markdown(
        '<div class="ready-msg">&#127869; Your food is ready!</div>',
        unsafe_allow_html=True,
    )
else:
    # Show the countdown card (00:00 when idle, ticking when running)
    display_secs = (
        st.session_state["remaining"]
        if (st.session_state["running"] or st.session_state["paused"])
        else duration_sec
    )
    st.markdown(
        f'<div class="timer-card">'
        f'<div class="timer-digits">{fmt_time(display_secs)}</div>'
        f'<div class="timer-label">MM : SS</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Control buttons ───────────────────────────────────────────────────────────
btn_cols = st.columns(4, gap="small")

with btn_cols[0]:
    st.markdown('<div class="start-btn">', unsafe_allow_html=True)
    start_clicked = st.button("▶ Start", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with btn_cols[1]:
    st.markdown('<div class="pause-btn">', unsafe_allow_html=True)
    pause_clicked = st.button("⏸ Pause", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with btn_cols[2]:
    st.markdown('<div class="resume-btn">', unsafe_allow_html=True)
    resume_clicked = st.button("▶▶ Resume", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with btn_cols[3]:
    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    reset_clicked = st.button("↺ Reset", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Button handlers ───────────────────────────────────────────────────────────

if start_clicked and not st.session_state["running"]:
    # Always (re)start from the full duration for the current selection
    st.session_state["remaining"] = FOODS[food_choice][method_choice]
    st.session_state["total"]     = st.session_state["remaining"]
    st.session_state["running"]   = True
    st.session_state["paused"]    = False
    st.session_state["done"]      = False
    st.session_state["play_ding"] = False
    st.session_state["last_tick"] = time.time()

if pause_clicked and st.session_state["running"] and not st.session_state["paused"]:
    st.session_state["paused"] = True

if resume_clicked and st.session_state["paused"]:
    st.session_state["paused"]    = False
    st.session_state["last_tick"] = time.time()  # reset tick so no phantom elapsed time

if reset_clicked:
    st.session_state["running"]   = False
    st.session_state["paused"]    = False
    st.session_state["done"]      = False
    st.session_state["play_ding"] = False
    st.session_state["remaining"] = 0

# ── Auto-rerun every second while counting down ───────────────────────────────
if st.session_state["running"] and not st.session_state["paused"]:
    time.sleep(1)
    st.rerun()
