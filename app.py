import os
import re
import csv
import json
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import requests
from openai import OpenAI
import streamlit as st

REQUESTS_SESSION = requests.Session()

st.set_option("client.toolbarMode", "minimal")

st.set_page_config(
    page_title="Scout",
    page_icon="🔧",
    layout="wide",
)

if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "Dark"

# ---------------------------------
# Technica-style UI
# ---------------------------------
def build_custom_css(theme: str):
    is_light = (theme or "Dark").lower() == "light"
    if is_light:
        palette = {
            "app_bg": "linear-gradient(180deg, #f7f4ec 0%, #f2eee3 100%)",
            "text": "#171717",
            "muted": "#5e5a52",
            "panel": "#fffdf8",
            "panel_2": "#f6f1e6",
            "line": "rgba(23,23,23,0.10)",
            "line_gold": "rgba(188,141,69,0.34)",
            "input_bg": "#fffdf8",
            "input_border": "#cfc6b4",
            "label": "#2a2722",
            "placeholder": "#847a6b",
            "sidebar_bg": "#f3eee2",
            "metric_bg": "#fbf8f1",
            "shadow": "0 12px 28px rgba(0,0,0,0.08)",
        }
    else:
        palette = {
            "app_bg": "radial-gradient(circle at top left, rgba(188,141,69,0.10), transparent 22%), radial-gradient(circle at top right, rgba(33,74,107,0.08), transparent 18%), linear-gradient(180deg, #090909 0%, #111111 42%, #141414 100%)",
            "text": "#F8F6EF",
            "muted": "#C9C1B3",
            "panel": "#141414",
            "panel_2": "#181818",
            "line": "rgba(255,255,255,0.08)",
            "line_gold": "rgba(188,141,69,0.28)",
            "input_bg": "#1A1A1A",
            "input_border": "#353535",
            "label": "#E6E0D4",
            "placeholder": "#8f8779",
            "sidebar_bg": "#111111",
            "metric_bg": "#181818",
            "shadow": "0 16px 40px rgba(0,0,0,0.32)",
        }

    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Montserrat:wght@400;500;600;700;800&display=swap');

    :root {{
        --technica-gold: #bc8d45;
        --technica-black: #000000;
        --technica-ivory: #F8F6EF;
        --technica-steel: #A3A3A3;
        --technica-blue: #214A6B;
        --technica-oxide: #5A1A12;
        --panel: {palette['panel']};
        --panel-2: {palette['panel_2']};
        --line: {palette['line']};
        --line-gold: {palette['line_gold']};
        --text: {palette['text']};
        --muted: {palette['muted']};
    }}

    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif;
    }}

    .stApp {{
        background: {palette['app_bg']};
        color: var(--text);
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }}

    h1, h2, h3, h4 {{
        color: var(--text);
        letter-spacing: 0.02em;
        font-family: 'Cinzel', serif;
    }}

    p, li, label, div, span {{
        color: var(--text);
    }}

    .hero-shell {{
        border: 1px solid var(--line-gold);
        border-radius: 20px;
        padding: 1.5rem 1.6rem;
        margin-bottom: 1.1rem;
        background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.015));
        box-shadow: {palette['shadow']};
    }}

    .hero-kicker, .section-kicker {{
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        color: var(--technica-gold);
        margin-bottom: 0.35rem;
        font-weight: 700;
    }}

    .hero-title {{
        font-family: 'Cinzel', serif;
        font-size: 2.35rem;
        line-height: 1.04;
        color: var(--text);
        margin: 0;
    }}

    .hero-subtitle {{
        margin-top: 0.65rem;
        font-size: 1rem;
        color: var(--muted);
        max-width: 48rem;
    }}

    .section-card, .mini-card {{
        background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
        border: 1px solid var(--line);
        border-radius: 16px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.10);
    }}

    .section-card {{
        padding: 1rem 1.1rem 1.15rem 1.1rem;
        margin-bottom: 1rem;
    }}

    .mini-card {{
        padding: 0.9rem 1rem;
        margin-bottom: 0.9rem;
    }}

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div {{
        background-color: {palette['input_bg']} !important;
        border: 1px solid {palette['input_border']} !important;
        border-radius: 12px !important;
        color: var(--text) !important;
    }}

    div[data-baseweb="select"] input,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    input, textarea {{
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        caret-color: var(--text) !important;
    }}

    div[data-baseweb="select"] svg {{
        fill: var(--text) !important;
        color: var(--text) !important;
    }}

    /* BaseWeb / Streamlit select dropdown portal styling */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] > div,
    div[role="listbox"],
    ul[role="listbox"] {{
        background: {palette['input_bg']} !important;
        background-color: {palette['input_bg']} !important;
        color: var(--text) !important;
        border: 1px solid {palette['input_border']} !important;
        box-shadow: 0 10px 28px rgba(0,0,0,0.12) !important;
    }}

    div[role="option"],
    li[role="option"],
    ul[role="listbox"] li,
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] div[role="option"] {{
        background: {palette['input_bg']} !important;
        background-color: {palette['input_bg']} !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }}

    div[role="option"] *,
    li[role="option"] *,
    ul[role="listbox"] li *,
    [data-baseweb="menu"] li *,
    [data-baseweb="menu"] div[role="option"] * {{
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }}

    div[role="option"]:hover,
    li[role="option"]:hover,
    div[role="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"] {{
        background: var(--panel-2) !important;
        background-color: var(--panel-2) !important;
    }}

    .stTextInput label, .stTextArea label, .stRadio label, .stSelectbox label, .stCheckbox label {{
        color: {palette['label']} !important;
        font-weight: 600 !important;
    }}

    .stButton > button {{
        background: linear-gradient(180deg, var(--technica-gold) 0%, #9F763A 100%);
        color: #111111;
        border: none;
        border-radius: 12px;
        font-weight: 800;
        padding: 0.82rem 1.25rem;
        box-shadow: 0 8px 18px rgba(0,0,0,0.18);
    }}

    .stButton > button:hover {{
        background: linear-gradient(180deg, #CA9950 0%, #AC8141 100%);
        color: #111111;
    }}

    .stTextInput input::placeholder,
    textarea::placeholder {{
        color: {palette['placeholder']} !important;
        opacity: 1 !important;
    }}

    section[data-testid="stSidebar"] {{
        border-right: 1px solid var(--line);
        background: {palette['sidebar_bg']};
    }}

    .streamlit-expanderHeader {{
        background-color: var(--panel-2);
        border: 1px solid var(--line);
        border-radius: 10px;
        color: var(--text);
        font-weight: 700;
    }}

    [data-testid="stMetric"] {{
        background: {palette['metric_bg']};
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1rem;
    }}

    [data-testid="stAlert"] {{
        border-radius: 14px;
    }}

    hr {{
        border-color: var(--line);
    }}

    a {{
        color: #D4AD6B !important;
    }}

    .small-note, .compact-caption {{
        color: var(--muted);
        font-size: 0.92rem;
    }}

    .logo-wrap {{
        display: flex;
        align-items: center;
        gap: 0.85rem;
        margin-bottom: 0.45rem;
    }}

    .logo-fallback {{
        width: 52px;
        height: 52px;
        border-radius: 12px;
        border: 1px solid rgba(188,141,69,0.28);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--technica-gold);
        font-family: 'Cinzel', serif;
        font-size: 1.2rem;
        font-weight: 700;
        background: rgba(255,255,255,0.02);
    }}

    @media (max-width: 900px) {{
        .block-container {{
            padding-top: 0.8rem;
        }}
    }}
</style>
"""

CUSTOM_CSS = build_custom_css(st.session_state.ui_theme)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------
# Branded hero
# ---------------------------------
logo_path = "technica_logo.png"

st.markdown('<div class="hero-shell">', unsafe_allow_html=True)
left, _ = st.columns([1.6, 1])

with left:
    st.markdown('<div class="logo-wrap">', unsafe_allow_html=True)
    if os.path.exists(logo_path):
        st.image(logo_path, width=74)
    else:
        st.markdown('<div class="logo-fallback">T</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="hero-kicker">Technica AI Diagnostic Layer</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Scout</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">A focused diagnostic planning tool for real-world technicians. Tight intake. Clear reasoning. Fast next-test guidance.</div>',
        unsafe_allow_html=True,
    )

st.markdown('</div>', unsafe_allow_html=True)

st.info(
    "Scout is a diagnostic aid only. Verify all findings with proper testing, service information, "
    "safety procedures, and manufacturer specifications."
)

# ---------------------------------
# Session state
# ---------------------------------
if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "latest_input" not in st.session_state:
    st.session_state.latest_input = None

if "latest_raw_output" not in st.session_state:
    st.session_state.latest_raw_output = None

if "latest_recalls" not in st.session_state:
    st.session_state.latest_recalls = []

if "vin_input" not in st.session_state:
    st.session_state.vin_input = ""

if "vehicle_year" not in st.session_state:
    st.session_state.vehicle_year = ""

if "vehicle_make" not in st.session_state:
    st.session_state.vehicle_make = ""

if "vehicle_model" not in st.session_state:
    st.session_state.vehicle_model = ""

if "vehicle_trim" not in st.session_state:
    st.session_state.vehicle_trim = ""

if "vehicle_engine" not in st.session_state:
    st.session_state.vehicle_engine = ""

if "vehicle_transmission" not in st.session_state:
    st.session_state.vehicle_transmission = ""

if "last_decoded_vin" not in st.session_state:
    st.session_state.last_decoded_vin = ""

if "show_recall_preview" not in st.session_state:
    st.session_state.show_recall_preview = False

if "latest_vehicle_label" not in st.session_state:
    st.session_state.latest_vehicle_label = ""

if "latest_service_refs" not in st.session_state:
    st.session_state.latest_service_refs = {}

if "show_service_preview" not in st.session_state:
    st.session_state.show_service_preview = False

with st.sidebar:
    st.markdown("### Scout System Status")
    st.radio("Theme", ["Dark", "Light"], key="ui_theme", horizontal=True)
    st.write("Build: V0.11 Beta")
    st.write("Mode: Diagnostic Planning Assistant")
    dataset_root = os.getenv("SCOUT_LOCAL_DATASET_DIR", str(Path("scout_database").resolve()))
    st.write("Local Dataset: " + ("Configured" if os.path.exists(dataset_root) else "Not found"))
    st.write("VIN Entered: " + ("Yes" if st.session_state.vin_input else "No"))
    st.write(
        "Vehicle Identified: " + (
            "Yes"
            if (
                st.session_state.vehicle_year
                and st.session_state.vehicle_make
                and st.session_state.vehicle_model
            )
            else "No"
        )
    )

# ---------------------------------
# Helpers
# ---------------------------------
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def normalize_vin(vin: str) -> str:
    return re.sub(r"[^A-HJ-NPR-Z0-9]", "", vin.upper().strip())

def safe_get(url: str, timeout: int = 12):
    try:
        r = REQUESTS_SESSION.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Scout/0.11"},
        )
        r.raise_for_status()
        return r
    except Exception:
        return None

def parse_fueleconomy_menu_items(response):
    if response is None:
        return []

    content_type = (response.headers.get("Content-Type") or "").lower()
    text = response.text.strip()

    if "json" in content_type or text.startswith("{"):
        try:
            payload = response.json()
            items = payload.get("menuItem", [])
            if isinstance(items, dict):
                items = [items]
            return items if isinstance(items, list) else []
        except Exception:
            pass

    try:
        root = ET.fromstring(text)
        items = []
        for item in root.findall(".//menuItem"):
            value = (item.findtext("value", default="") or "").strip()
            label = (item.findtext("text", default="") or "").strip()
            items.append({"value": value, "text": label})
        return items
    except Exception:
        return []

def parse_fueleconomy_vehicle_record(response):
    if response is None:
        return {}

    content_type = (response.headers.get("Content-Type") or "").lower()
    text = response.text.strip()

    if "json" in content_type or text.startswith("{"):
        try:
            payload = response.json()
            vehicle = payload.get("vehicle", payload)
            return vehicle if isinstance(vehicle, dict) else {}
        except Exception:
            pass

    try:
        root = ET.fromstring(text)
        vehicle_node = root.find(".//vehicle") if root.tag != "vehicle" else root
        if vehicle_node is None:
            return {}

        vehicle = {}
        for child in vehicle_node:
            tag = child.tag.split("}")[-1]
            vehicle[tag] = (child.text or "").strip()
        return vehicle
    except Exception:
        return {}

@st.cache_data(show_spinner=False, ttl=86400)
def get_year_options():
    url = "https://www.fueleconomy.gov/ws/rest/vehicle/menu/year"
    r = safe_get(url)
    if not r:
        current_year = datetime.now().year + 1
        return [str(y) for y in range(current_year, 1983, -1)]

    items = parse_fueleconomy_menu_items(r)
    years = []
    for item in items:
        year_value = clean_option(item.get("value") or item.get("text") or "")
        if year_value.isdigit():
            years.append(year_value)
    years = sorted(set(years), reverse=True)
    if years:
        return years
    current_year = datetime.now().year + 1
    return [str(y) for y in range(current_year, 1983, -1)]

@st.cache_data(show_spinner=False, ttl=86400)
def get_make_options(year: str = ""):
    year = clean_option(year)
    if not year:
        return []

    url = f"https://www.fueleconomy.gov/ws/rest/vehicle/menu/make?year={urllib.parse.quote(year)}"
    r = safe_get(url)
    if not r:
        return []

    items = parse_fueleconomy_menu_items(r)
    makes = []
    for item in items:
        make_name = clean_option(item.get("text") or item.get("value") or "")
        if make_name:
            makes.append(make_name)
    return sorted(set(makes), key=str.lower)

@st.cache_data(show_spinner=False, ttl=43200)
def get_model_options_for_year_make(year: str, make: str):
    year = clean_option(year)
    make = clean_option(make)
    if not year or not make:
        return []

    url = (
        "https://www.fueleconomy.gov/ws/rest/vehicle/menu/model"
        f"?year={urllib.parse.quote(year)}&make={urllib.parse.quote(make)}"
    )
    r = safe_get(url)
    if not r:
        return []

    items = parse_fueleconomy_menu_items(r)
    models = []
    for item in items:
        model_name = clean_option(item.get("text") or item.get("value") or "")
        if model_name:
            models.append(model_name)
    return sorted(set(models), key=str.lower)

@st.cache_data(show_spinner=False, ttl=43200)
def clean_option(value):
    value = (value or "").strip()
    if not value:
        return ""
    if value.lower() in {"not applicable", "unknown", "na", "n/a", "null", "none"}:
        return ""
    return value

def dedupe_options(values):
    seen = set()
    output = []
    for value in values:
        cleaned = clean_option(value)
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            output.append(cleaned)
    return output

def safe_select_index(options, current_value):
    current_value = current_value or ""
    try:
        return options.index(current_value)
    except ValueError:
        return 0

def apply_vin_decode_to_vehicle_state(vin_decode: dict):
    if not vin_decode.get("vin") or len(vin_decode.get("vin", "")) != 17:
        return

    st.session_state.vehicle_year = clean_option(vin_decode.get("year", ""))
    st.session_state.vehicle_make = clean_option(vin_decode.get("make", ""))
    st.session_state.vehicle_model = clean_option(vin_decode.get("model", ""))
    st.session_state.vehicle_trim = clean_option(vin_decode.get("trim", "")) or clean_option(vin_decode.get("series", ""))
    st.session_state.vehicle_engine = clean_option(vin_decode.get("engine_model", ""))
    st.session_state.vehicle_transmission = clean_option(vin_decode.get("transmission_style", ""))
    st.session_state.last_decoded_vin = vin_decode.get("vin", "")

def reset_vehicle_from_year():
    st.session_state.vehicle_make = ""
    st.session_state.vehicle_model = ""
    st.session_state.vehicle_trim = ""
    st.session_state.vehicle_engine = ""
    st.session_state.vehicle_transmission = ""

def reset_vehicle_from_make():
    st.session_state.vehicle_model = ""
    st.session_state.vehicle_trim = ""
    st.session_state.vehicle_engine = ""
    st.session_state.vehicle_transmission = ""

def reset_vehicle_from_model():
    st.session_state.vehicle_trim = ""
    st.session_state.vehicle_engine = ""
    st.session_state.vehicle_transmission = ""

@st.cache_data(show_spinner=False, ttl=86400)
def decode_vin_vpic(vin: str):
    vin = normalize_vin(vin)
    if not vin:
        return {
            "vin": "",
            "valid_length": False,
            "year": "",
            "make": "",
            "model": "",
            "trim": "",
            "engine_model": "",
            "engine_cylinders": "",
            "displacement_l": "",
            "drive_type": "",
            "transmission_style": "",
            "plant_country": "",
            "plant_company_name": "",
            "vehicle_type": "",
            "body_class": "",
            "series": "",
            "notes": [],
        }

    result = {
        "vin": vin,
        "valid_length": len(vin) == 17,
        "year": "",
        "make": "",
        "model": "",
        "trim": "",
        "engine_model": "",
        "engine_cylinders": "",
        "displacement_l": "",
        "drive_type": "",
        "transmission_style": "",
        "plant_country": "",
        "plant_company_name": "",
        "vehicle_type": "",
        "body_class": "",
        "series": "",
        "notes": [],
    }

    if len(vin) != 17:
        result["notes"].append("VIN is not 17 characters; full decode may be incomplete.")
        return result

    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
    r = safe_get(url)
    if not r:
        result["notes"].append("Unable to reach VIN decode service.")
        return result

    try:
        payload = r.json()
        rows = payload.get("Results", [])
        if not rows:
            result["notes"].append("VIN decode service returned no rows.")
            return result

        row = rows[0]
        result["year"] = row.get("ModelYear", "") or ""
        result["make"] = row.get("Make", "") or ""
        result["model"] = row.get("Model", "") or ""
        result["trim"] = row.get("Trim", "") or ""
        result["engine_model"] = row.get("EngineModel", "") or ""
        result["engine_cylinders"] = row.get("EngineCylinders", "") or ""
        result["displacement_l"] = row.get("DisplacementL", "") or ""
        result["drive_type"] = row.get("DriveType", "") or ""
        result["transmission_style"] = row.get("TransmissionStyle", "") or ""
        result["plant_country"] = row.get("PlantCountry", "") or ""
        result["plant_company_name"] = row.get("PlantCompanyName", "") or ""
        result["vehicle_type"] = row.get("VehicleType", "") or ""
        result["body_class"] = row.get("BodyClass", "") or ""
        result["series"] = row.get("Series", "") or ""

        if result["make"]:
            result["notes"].append(f"Manufacturer decoded as {result['make']}.")
        if result["year"]:
            result["notes"].append(f"Model year decoded as {result['year']}.")
        if result["engine_model"]:
            result["notes"].append(f"Engine model decoded as {result['engine_model']}.")
    except Exception:
        result["notes"].append("VIN decode response could not be parsed.")

    return result

@st.cache_data(show_spinner=False, ttl=43200)
def fetch_recalls(year: str, make: str, model: str):
    year = (year or "").strip()
    make = (make or "").strip()
    model = (model or "").strip()

    if not (year and make and model):
        return []

    url = (
        "https://api.nhtsa.gov/recalls/recallsByVehicle"
        f"?make={urllib.parse.quote(make)}"
        f"&model={urllib.parse.quote(model)}"
        f"&modelYear={urllib.parse.quote(year)}"
    )
    r = safe_get(url)
    if not r:
        return []

    try:
        payload = r.json()
        results = payload.get("results", [])
        cleaned = []
        for item in results[:10]:
            cleaned.append({
                "campaign_number": item.get("NHTSACampaignNumber", ""),
                "report_date": item.get("ReportReceivedDate", ""),
                "component": item.get("Component", ""),
                "summary": item.get("Summary", ""),
                "consequence": item.get("Consequence", ""),
                "remedy": item.get("Remedy", ""),
            })
        return cleaned
    except Exception:
        return []

def build_tsb_links(year: str, make: str, model: str, vin: str):
    y = (year or "").strip()
    mk = (make or "").strip()
    md = (model or "").strip()
    vin = normalize_vin(vin)

    query_main = " ".join([x for x in [y, mk, md, "TSB manufacturer communications NHTSA"] if x])
    query_recall = " ".join([x for x in [y, mk, md, "recall NHTSA"] if x])
    query_vin = " ".join([x for x in [vin, "NHTSA recall"] if x])

    return {
        "manufacturer_communications_search": (
            "https://www.google.com/search?q=" + urllib.parse.quote(query_main)
        ),
        "recall_search": (
            "https://www.google.com/search?q=" + urllib.parse.quote(query_recall)
        ),
        "vin_recall_search": (
            "https://www.google.com/search?q=" + urllib.parse.quote(query_vin)
            if vin else ""
        ),
        "nhtsa_recalls_home": "https://www.nhtsa.gov/recalls",
        "nhtsa_vin_decoder": (
            f"https://vpic.nhtsa.dot.gov/decoder/Decoder?VIN={urllib.parse.quote(vin)}"
            if vin else "https://vpic.nhtsa.dot.gov/decoder/"
        ),
        "manufacturer_communications_home": "https://www.nhtsa.gov/vehicle-manufacturers/manufacturer-communications",
    }

def summarize_recalls_for_prompt(recalls: list):
    if not recalls:
        return "No recalls were returned from the recall search."

    lines = []
    for r in recalls[:5]:
        lines.append(
            f"- Campaign {r.get('campaign_number', '')}: "
            f"Component: {r.get('component', '')}. "
            f"Summary: {r.get('summary', '')[:260]}"
        )
    return "\n".join(lines)

def summarize_tsb_links_for_prompt(year: str, make: str, model: str):
    parts = [p for p in [year, make, model] if p]
    if not parts:
        return "No TSB/manufacturer communication search context available."
    return (
        f"Use manufacturer communications / TSB awareness for {' '.join(parts)} where relevant. "
        "If known bulletin-type issues would materially affect the likely system or next tests, mention that."
    )

def get_local_dataset_root() -> Path:
    return Path(os.getenv("SCOUT_LOCAL_DATASET_DIR", "scout_database")).expanduser().resolve()

def slugify_value(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")

def build_vehicle_tokens(year: str, make: str, model: str, engine: str, complaint: str, codes: str):
    raw_tokens = [year, make, model, engine]
    raw_tokens.extend(re.findall(r"[A-Za-z0-9\-\.]{3,}", complaint or ""))
    raw_tokens.extend(re.findall(r"[A-Za-z0-9\-\.]{3,}", codes or ""))
    cleaned = []
    seen = set()
    for token in raw_tokens:
        token = (token or "").strip()
        if not token:
            continue
        lowered = token.lower()
        if lowered not in seen:
            seen.add(lowered)
            cleaned.append(token)
    return cleaned[:14]

@st.cache_data(show_spinner=False, ttl=1800)
def scan_local_service_dataset(year: str, make: str, model: str, engine: str, complaint: str, codes: str):
    root = get_local_dataset_root()
    if not root.exists():
        return {
            "root": str(root),
            "exists": False,
            "scanned_files": 0,
            "matches": [],
            "vehicle_folder": "",
        }

    vehicle_folder = root / "service_manuals" / slugify_value(make) / f"{slugify_value(year)}_{slugify_value(model)}"
    search_roots = [vehicle_folder] if vehicle_folder.exists() else [root]

    tokens = [t.lower() for t in build_vehicle_tokens(year, make, model, engine, complaint, codes)]
    matches = []
    scanned_files = 0

    for search_root in search_roots:
        for file_path in search_root.rglob("*"):
            if not file_path.is_file():
                continue
            scanned_files += 1
            path_text = str(file_path.relative_to(root)).lower()
            score = sum(1 for token in tokens if token and token in path_text)
            if score > 0:
                matches.append({
                    "path": str(file_path.relative_to(root)),
                    "name": file_path.name,
                    "score": score,
                    "suffix": file_path.suffix.lower(),
                })
            if scanned_files >= 4000:
                break
        if scanned_files >= 4000:
            break

    matches.sort(key=lambda item: (-item["score"], item["path"]))
    return {
        "root": str(root),
        "exists": True,
        "scanned_files": scanned_files,
        "matches": matches[:12],
        "vehicle_folder": str(vehicle_folder.relative_to(root)) if vehicle_folder.exists() else "",
    }

def build_charm_links(year: str, make: str, model: str, engine: str):
    base_terms = " ".join([x for x in [year, make, model, engine] if x]).strip()
    if not base_terms:
        return {}
    site_query = urllib.parse.quote(f'site:charm.li {base_terms}')
    exploded_query = urllib.parse.quote(f'site:charm.li {base_terms} exploded view OR removal OR installation')
    wiring_query = urllib.parse.quote(f'site:charm.li {base_terms} wiring diagram')
    specs_query = urllib.parse.quote(f'site:charm.li {base_terms} specifications torque')
    return {
        "search": f"https://www.google.com/search?q={site_query}",
        "exploded": f"https://www.google.com/search?q={exploded_query}",
        "wiring": f"https://www.google.com/search?q={wiring_query}",
        "specs": f"https://www.google.com/search?q={specs_query}",
    }

def summarize_service_references_for_prompt(service_refs: dict):
    if not service_refs:
        return "No service reference bundle was prepared."

    lines = []
    local_dataset = service_refs.get("local_dataset", {})
    charm_links = service_refs.get("charm_links", {})

    if local_dataset.get("exists"):
        lines.append(f"Local dataset root: {local_dataset.get('root', '')}")
        if local_dataset.get("vehicle_folder"):
            lines.append(f"Vehicle folder candidate: {local_dataset.get('vehicle_folder')}")
        matches = local_dataset.get("matches", [])
        if matches:
            lines.append("Local file candidates:")
            for item in matches[:6]:
                lines.append(f"- {item.get('path', '')} (score {item.get('score', 0)})")
        else:
            lines.append("Local dataset exists, but no matching files were found yet.")
    else:
        lines.append("Local dataset root was not found.")

    if charm_links:
        lines.append("Charm / web reference links were prepared for procedures, exploded views, wiring, and specs.")

    return "\n".join(lines)

def render_service_reference_panel(service_refs: dict):
    st.markdown('<div class="mini-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Service Information Layer</div>', unsafe_allow_html=True)
    st.subheader("Service References")

    if not service_refs:
        st.write("No service references prepared yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    local_dataset = service_refs.get("local_dataset", {})
    charm_links = service_refs.get("charm_links", {})

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("**Local dataset**")
        if local_dataset.get("exists"):
            st.caption(f"Dataset root: {local_dataset.get('root', '')}")
            if local_dataset.get("vehicle_folder"):
                st.write(f"Vehicle folder: `{local_dataset.get('vehicle_folder')}`")
            matches = local_dataset.get("matches", [])
            if matches:
                for item in matches[:8]:
                    st.markdown(f"- `{item.get('path', '')}`")
            else:
                st.write("Dataset found, but there are no matching files for this vehicle yet.")
        else:
            st.write("No local dataset folder found yet.")
            st.caption("Create a folder named `scout_database` beside the app, or set SCOUT_LOCAL_DATASET_DIR to your manual library.")

    with right:
        st.markdown("**External reference links**")
        if charm_links:
            st.markdown(f"[Charm / manual search]({charm_links['search']})")
            st.markdown(f"[Exploded views / removal]({charm_links['exploded']})")
            st.markdown(f"[Wiring diagrams]({charm_links['wiring']})")
            st.markdown(f"[Specs / torque search]({charm_links['specs']})")
        else:
            st.write("Vehicle details are not complete enough to build reference links yet.")

    st.markdown("</div>", unsafe_allow_html=True)

def append_case_log(row: dict, filename: str = "scout_case_log.csv"):
    file_exists = os.path.exists(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def parse_model_json(raw_text: str):
    raw_text = (raw_text or "").strip()
    if not raw_text:
        raise json.JSONDecodeError("Empty response", raw_text, 0)

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise

def build_prompt(data: dict, vin_decode: dict, recalls: list, service_refs: dict | None = None) -> str:
    vin_context = f"""
VIN:
- Raw VIN: {vin_decode.get("vin", "")}
- Valid length: {vin_decode.get("valid_length", False)}
- Decoded year: {vin_decode.get("year", "")}
- Decoded make: {vin_decode.get("make", "")}
- Decoded model: {vin_decode.get("model", "")}
- Trim: {vin_decode.get("trim", "")}
- Engine model: {vin_decode.get("engine_model", "")}
- Engine cylinders: {vin_decode.get("engine_cylinders", "")}
- Displacement (L): {vin_decode.get("displacement_l", "")}
- Drive type: {vin_decode.get("drive_type", "")}
- Transmission style: {vin_decode.get("transmission_style", "")}
- Plant country: {vin_decode.get("plant_country", "")}
- Plant company name: {vin_decode.get("plant_company_name", "")}
- Vehicle type: {vin_decode.get("vehicle_type", "")}
- Body class: {vin_decode.get("body_class", "")}
- Series: {vin_decode.get("series", "")}
- VIN notes: {", ".join(vin_decode.get("notes", []))}
"""

    recall_context = summarize_recalls_for_prompt(recalls)
    tsb_context = summarize_tsb_links_for_prompt(data["year"], data["make"], data["model"])
    service_context = summarize_service_references_for_prompt(service_refs or {})

    return f"""
You are an expert automotive diagnostic technician helping a professional technician.

Your purpose:
Help determine the most logical diagnostic path for the issue described.

Diagnostic reasoning framework:
1. Frame the complaint clearly.
2. Identify the most likely system involved.
3. Consider known/common platform failures.
4. Consider useful VIN-derived context if relevant.
5. Consider recall or manufacturer communication relevance if relevant.
6. Rank likely causes.
7. Choose the next best high-information diagnostic test.
8. Explain why that test comes next.
9. Keep the plan practical, efficient, and technician-friendly.

Rules:
- Do not recommend blind parts replacement.
- Prioritize verification and high-information tests first.
- Use known/common platform failures when relevant.
- Use VIN-derived context only when genuinely helpful.
- Use recalls / manufacturer communication context only when genuinely relevant.
- Keep the language concise, practical, and shop-friendly.
- Think like a strong diagnostician, not like a generic chatbot.
- Focus on the next best test, not a full repair manual.
- Where a service-information reference is relevant, mention the kind of reference the technician should open next (wiring, removal, specs, exploded view, etc.).
- If evidence is weak, say so.
- Do not leave required fields blank.

Vehicle Information:
- Year: {data["year"]}
- Make: {data["make"]}
- Model: {data["model"]}
- Trim: {data["trim"]}
- Engine / Platform: {data["platform"]}
- Transmission: {data["transmission"]}
- Mileage: {data["mileage"]}

{vin_context}

Recall Search Context:
{recall_context}

Manufacturer Communication / TSB Context:
{tsb_context}

Service Information Context:
{service_context}

Primary Complaint:
{data["complaint"]}

Fault Codes:
{data["codes"]}

Symptoms / Observations:
{data["symptoms"]}

Recent Repairs:
{data["recent_repairs"]}

Additional Notes:
{data["notes"]}

Return ONLY valid JSON in this exact structure:

{{
  "complaint_framing": [
    "short bullet",
    "short bullet"
  ],
  "system_analysis": "short paragraph identifying the most likely system involved",
  "vin_relevance": "short note on whether VIN-derived information materially changes diagnostic thinking",
  "recall_tsb_relevance": "short note on whether any recall or manufacturer communication context may materially affect diagnosis",
  "known_failure_patterns": [
    "pattern 1",
    "pattern 2"
  ],
  "probable_causes": [
    {{
      "cause": "short cause name",
      "why_likely": "1-2 sentence explanation"
    }}
  ],
  "diagnostic_steps": [
    {{
      "step_number": 1,
      "title": "short step title",
      "why_next": "why this step comes next",
      "component": "specific component or subsystem",
      "tools_required": [
        "scan tool",
        "tool 2",
        "tool 3"
      ],
      "procedure": [
        "procedure step 1",
        "procedure step 2"
      ]
    }}
  ],
  "service_references": [
    {{
      "reference_type": "wiring diagram or exploded view or procedure or spec",
      "title": "short title",
      "why_it_matters": "one short explanation"
    }}
  ],
  "tech_notes": [
    "note 1",
    "note 2"
  ],
  "confidence": {{
    "level": "Low or Medium or High",
    "reason": "one short explanation"
  }}
}}

Requirements:
- Include at least 3 diagnostic steps whenever realistically possible.
- Every diagnostic step must include:
  - step_number
  - title
  - why_next
  - component
  - tools_required
  - procedure
- Every diagnostic step must include at least 3 tools_required entries whenever realistically possible.
- Do not leave tools_required empty.
- If only basic tools are needed, list them.
- Every diagnostic step must identify a component or subsystem.
- Include 1-4 service_references whenever enough context exists.
- Output JSON only. No markdown outside JSON.
"""

def render_exploded_view_link(vehicle_label: str, component: str, title: str):
    search_term = component if component and component.strip() else title
    query = f"{vehicle_label} {search_term} exploded view diagram"
    url = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(query)}"
    st.markdown(f"[Search exploded view / diagram for **{search_term}**]({url})")

def render_vin_decode(vin_decode: dict):
    st.markdown('<div class="mini-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Vehicle Intelligence</div>', unsafe_allow_html=True)
    st.subheader("VIN Decode Preview")

    if not vin_decode.get("vin"):
        st.write("No VIN entered.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Make:** {vin_decode.get('make', '') or 'Unknown'}")
        st.write(f"**Model:** {vin_decode.get('model', '') or 'Unknown'}")
        st.write(f"**Year:** {vin_decode.get('year', '') or 'Unknown'}")
    with col2:
        st.write(f"**Trim:** {vin_decode.get('trim', '') or 'Unknown'}")
        st.write(f"**Engine model:** {vin_decode.get('engine_model', '') or 'Unknown'}")
        st.write(f"**Vehicle type:** {vin_decode.get('vehicle_type', '') or 'Unknown'}")
    with col3:
        st.write(f"**Drive type:** {vin_decode.get('drive_type', '') or 'Unknown'}")
        st.write(f"**Transmission:** {vin_decode.get('transmission_style', '') or 'Unknown'}")
        st.write(f"**Body class:** {vin_decode.get('body_class', '') or 'Unknown'}")

    notes = vin_decode.get("notes", [])
    if notes:
        st.markdown("**VIN Notes**")
        for note in notes:
            st.markdown(f"- {note}")

    st.markdown("</div>", unsafe_allow_html=True)

def render_vehicle_header(year, make, model, trim, engine, trans, mileage):
    parts = [p for p in [year, make, model] if p]

    if not parts:
        return

    st.markdown('<div class="mini-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Active Vehicle</div>', unsafe_allow_html=True)
    st.markdown(f"### {' '.join(parts)}")

    secondary = " | ".join([x for x in [trim, engine, trans, mileage] if x])
    if secondary:
        st.write(secondary)

    st.markdown("</div>", unsafe_allow_html=True)

def render_recall_tsb_panel(recalls: list, links: dict):
    st.markdown('<div class="mini-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Manufacturer Intelligence</div>', unsafe_allow_html=True)
    st.subheader("Recalls + TSB / Manufacturer Communications")

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("**Open recalls found**")
        if recalls:
            for r in recalls[:5]:
                st.markdown(
                    f"- **{r.get('campaign_number', 'Campaign')}** | "
                    f"{r.get('component', 'Component not listed')}"
                )
                if r.get("summary"):
                    st.caption(r["summary"][:220] + ("..." if len(r["summary"]) > 220 else ""))
        else:
            st.write("No recalls returned from the current year/make/model search.")

    with right:
        st.markdown("**Quick links**")
        st.markdown(f"[NHTSA recalls home]({links['nhtsa_recalls_home']})")
        st.markdown(f"[VIN decoder]({links['nhtsa_vin_decoder']})")
        st.markdown(f"[Manufacturer communications / TSB info]({links['manufacturer_communications_home']})")
        st.markdown(f"[Search TSB / manufacturer communications]({links['manufacturer_communications_search']})")
        st.markdown(f"[Search recalls by vehicle]({links['recall_search']})")
        if links.get("vin_recall_search"):
            st.markdown(f"[Search recalls by VIN]({links['vin_recall_search']})")

    st.markdown("</div>", unsafe_allow_html=True)

def render_results(result: dict, vehicle_label: str):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Scout Output</div>', unsafe_allow_html=True)
    st.header("Diagnostic Path")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("Complaint Framing")
        complaint_items = result.get("complaint_framing", [])
        if complaint_items:
            for item in complaint_items:
                st.markdown(f"- {item}")
        else:
            st.write("No complaint framing returned.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("System Analysis")
        st.write(result.get("system_analysis", "No system analysis returned."))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("VIN Impact")
        st.write(result.get("vin_relevance", "No VIN-specific relevance returned."))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("Manufacturer Guidance")
        st.write(result.get("recall_tsb_relevance", "No recall or TSB relevance returned."))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("Known Pattern Failures")
        patterns = result.get("known_failure_patterns", [])
        if patterns:
            for item in patterns:
                st.markdown(f"- {item}")
        else:
            st.write("No clear platform-specific patterns identified.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("Confidence")
        confidence = result.get("confidence", {})
        st.metric("Level", confidence.get("level", "Unknown"))
        st.write(confidence.get("reason", ""))
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="mini-card">', unsafe_allow_html=True)
    st.subheader("Probable Causes")
    causes = result.get("probable_causes", [])
    if causes:
        for i, cause in enumerate(causes, start=1):
            st.markdown(f"**{i}. {cause.get('cause', 'Unknown cause')}**")
            st.write(cause.get("why_likely", ""))
    else:
        st.write("No probable causes returned.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="mini-card">', unsafe_allow_html=True)
    st.subheader("Diagnostic Path")
    steps = result.get("diagnostic_steps", [])
    if steps:
        for idx, step in enumerate(steps, start=1):
            step_num = step.get("step_number", idx)
            title = step.get("title", "Untitled step")
            component = step.get("component") or title
            tools = step.get("tools_required", [])
            procedure = step.get("procedure", [])

            with st.expander(f"Step {step_num} — {title}", expanded=(idx == 1)):
                st.markdown("**Why this step comes next**")
                st.write(step.get("why_next", ""))

                st.markdown("**Component / Area**")
                st.write(component)

                st.markdown("**Tools Required**")
                if tools:
                    for tool in tools:
                        st.markdown(f"- {tool}")
                else:
                    for tool in ["scan tool", "basic hand tools", "flashlight"]:
                        st.markdown(f"- {tool}")

                st.markdown("**Procedure**")
                if procedure:
                    for p in procedure:
                        st.markdown(f"- {p}")
                else:
                    st.write("No procedure returned.")

                st.markdown("**Exploded View / Diagram**")
                render_exploded_view_link(vehicle_label, component, title)
    else:
        st.write("No diagnostic steps returned.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="mini-card">', unsafe_allow_html=True)
    st.subheader("Service References to Open Next")
    service_references = result.get("service_references", [])
    if service_references:
        for item in service_references:
            st.markdown(f"**{item.get('reference_type', 'Reference').title()}** — {item.get('title', 'Untitled reference')}")
            st.write(item.get("why_it_matters", ""))
    else:
        st.write("No explicit service references were returned.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="mini-card">', unsafe_allow_html=True)
    st.subheader("Tech Notes")
    notes = result.get("tech_notes", [])
    if notes:
        for note in notes:
            st.markdown(f"- {note}")
    else:
        st.write("No additional tech notes returned.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------
# Intake UI
# ---------------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-kicker">Technica AI Intake</div>', unsafe_allow_html=True)
st.markdown("## Vehicle Intake")

vin_col_left, vin_col_mid, vin_col_right = st.columns([2, 1, 1])

with vin_col_left:
    vin = st.text_input(
        "VIN",
        key="vin_input",
        placeholder="1FTFW1ET5FKE12345",
    )

with vin_col_mid:
    st.write("")
    st.write("")
    decode_vin_clicked = st.button("Decode VIN")

with vin_col_right:
    st.write("")
    st.write("")
    if st.button("Clear Vehicle"):
        st.session_state.vin_input = ""
        st.session_state.vehicle_year = ""
        st.session_state.vehicle_make = ""
        st.session_state.vehicle_model = ""
        st.session_state.vehicle_trim = ""
        st.session_state.vehicle_engine = ""
        st.session_state.vehicle_transmission = ""
        st.session_state.last_decoded_vin = ""
        st.session_state.latest_result = None
        st.session_state.latest_input = None
        st.session_state.latest_raw_output = None
        st.session_state.latest_recalls = []
        st.session_state.latest_service_refs = {}
        st.session_state.show_recall_preview = False
        st.session_state.show_service_preview = False
        st.session_state.latest_vehicle_label = ""
        st.rerun()

st.markdown('<div class="compact-caption">Fast path: decode VIN for year/make/model, then confirm trim, engine, and transmission manually.</div>', unsafe_allow_html=True)

vin_clean = normalize_vin(st.session_state.vin_input)
vin_decode = decode_vin_vpic(vin_clean) if (vin_clean and (len(vin_clean) == 17 or st.session_state.last_decoded_vin == vin_clean)) else {}

if decode_vin_clicked:
    if not vin_clean:
        st.warning("Enter a VIN first.")
    elif vin_clean == st.session_state.last_decoded_vin:
        st.info("This VIN has already been decoded in this session.")
    else:
        apply_vin_decode_to_vehicle_state(vin_decode)
        st.session_state.show_recall_preview = False
        st.session_state.show_service_preview = False
        if vin_decode.get("valid_length"):
            st.success("VIN decoded. Core vehicle fields updated.")
        else:
            st.warning("VIN was captured, but it is not 17 characters. Some fields may be incomplete.")

year_options = [""] + get_year_options()
make_options = [""] + get_make_options(st.session_state.vehicle_year)

if st.session_state.vehicle_year not in year_options:
    st.session_state.vehicle_year = ""

if st.session_state.vehicle_make not in make_options:
    st.session_state.vehicle_make = ""

model_options = [""]
if st.session_state.vehicle_year and st.session_state.vehicle_make:
    model_options = [""] + get_model_options_for_year_make(
        st.session_state.vehicle_year,
        st.session_state.vehicle_make,
    )

if st.session_state.vehicle_model not in model_options:
    st.session_state.vehicle_model = ""

col_a, col_b, col_c = st.columns(3)

with col_a:
    selected_year = st.selectbox(
        "Year",
        options=year_options,
        index=safe_select_index(year_options, st.session_state.vehicle_year),
        key="vehicle_year",
        on_change=reset_vehicle_from_year,
    )

with col_b:
    selected_make = st.selectbox(
        "Make",
        options=make_options,
        index=safe_select_index(make_options, st.session_state.vehicle_make),
        key="vehicle_make",
        on_change=reset_vehicle_from_make,
    )

with col_c:
    selected_model = st.selectbox(
        "Model",
        options=model_options,
        index=safe_select_index(model_options, st.session_state.vehicle_model),
        key="vehicle_model",
        on_change=reset_vehicle_from_model,
    )

identity_col_1, identity_col_2, identity_col_3 = st.columns(3)
with identity_col_1:
    selected_trim = st.text_input(
        "Trim Level",
        key="vehicle_trim",
        placeholder="XLT / Lariat / Touring / Sport / Base",
    ).strip()
with identity_col_2:
    selected_engine = st.text_input(
        "Engine / Platform",
        key="vehicle_engine",
        placeholder="Manual entry only — 3.5L EcoBoost / FA20DIT / 2AR-FE",
    ).strip()
with identity_col_3:
    selected_transmission = st.text_input(
        "Transmission",
        key="vehicle_transmission",
        placeholder="Manual entry only — 6AT / 8HP / CVT / 6MT",
    ).strip()

mileage = st.text_input("Mileage", placeholder="185000")

render_vehicle_header(
    selected_year,
    selected_make,
    selected_model,
    selected_trim,
    selected_engine,
    selected_transmission,
    mileage,
)

st.caption(
    "VIN decoding can still populate what NHTSA returns, but engine and transmission are now manual-entry fields so the intake stays accurate and technician-controlled."
)

complaint = st.text_area(
    "Customer Complaint / Primary Concern",
    placeholder="Rough idle on cold start, clears after 30 seconds",
    height=132,
)

codes = st.text_area(
    "Fault Codes",
    placeholder="P0016, P0018",
    height=100,
)

symptoms = st.text_area(
    "Symptoms / Technician Observations",
    placeholder="Cold start rattle, rough idle, poor acceleration, intermittent misfire",
    height=120,
)

recent_repairs = st.text_area(
    "Recent Repairs",
    placeholder="Spark plugs replaced 2 months ago",
    height=100,
)

notes = st.text_area(
    "Additional Notes",
    placeholder="Operating conditions, prior diagnostic work, fuel quality, warning lights, etc.",
    height=100,
)

show_raw_output = st.checkbox("Show raw AI output for debugging", value=False)

render_vin_decode(vin_decode)

resolved_year_preview = selected_year.strip() or vin_decode.get("year", "")
resolved_make_preview = selected_make.strip() or vin_decode.get("make", "")
resolved_model_preview = selected_model.strip() or vin_decode.get("model", "")

preview_ready = bool(resolved_year_preview and resolved_make_preview and resolved_model_preview)
preview_button_label = "Hide recalls + TSB links" if st.session_state.show_recall_preview else "Load recalls + TSB links"
if preview_ready and st.button(preview_button_label):
    st.session_state.show_recall_preview = not st.session_state.show_recall_preview

if preview_ready and st.session_state.show_recall_preview:
    recalls_preview = fetch_recalls(
        resolved_year_preview,
        resolved_make_preview,
        resolved_model_preview,
    )
    tsb_links_preview = build_tsb_links(
        resolved_year_preview,
        resolved_make_preview,
        resolved_model_preview,
        vin_clean,
    )
    render_recall_tsb_panel(recalls_preview, tsb_links_preview)

service_preview_label = "Hide service references" if st.session_state.show_service_preview else "Load service references"
if preview_ready and st.button(service_preview_label):
    st.session_state.show_service_preview = not st.session_state.show_service_preview

if preview_ready and st.session_state.show_service_preview:
    preview_service_refs = {
        "local_dataset": scan_local_service_dataset(
            resolved_year_preview,
            resolved_make_preview,
            resolved_model_preview,
            selected_engine.strip(),
            complaint.strip(),
            codes.strip(),
        ),
        "charm_links": build_charm_links(
            resolved_year_preview,
            resolved_make_preview,
            resolved_model_preview,
            selected_engine.strip(),
        ),
    }
    st.session_state.latest_service_refs = preview_service_refs
    render_service_reference_panel(preview_service_refs)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------
# Run AI
# ---------------------------------
if st.button("Generate Diagnostic Path", type="primary"):
    required_fields = {
        "Primary Complaint": complaint,
        "Symptoms / Technician Observations": symptoms,
    }

    has_manual_identity = (
        selected_year.strip()
        and selected_make.strip()
        and selected_model.strip()
    )
    has_vin = bool(vin_clean)

    if not has_manual_identity and not has_vin:
        st.error("Please provide either a VIN or the Year / Make / Model.")
    else:
        missing = [field for field, value in required_fields.items() if not value.strip()]
        if missing:
            st.error(f"Please fill in these fields: {', '.join(missing)}")
        else:
            client = get_openai_client()
            if not client:
                st.error("OPENAI_API_KEY is missing. Add it to your terminal environment before running the app.")
            else:
                resolved_year = selected_year.strip() or vin_decode.get("year", "")
                resolved_make = selected_make.strip() or vin_decode.get("make", "")
                resolved_model = selected_model.strip() or vin_decode.get("model", "")
                resolved_trim = selected_trim.strip() or vin_decode.get("trim", "") or vin_decode.get("series", "")
                resolved_engine = selected_engine.strip() or vin_decode.get("engine_model", "")
                resolved_transmission = selected_transmission.strip() or vin_decode.get("transmission_style", "")

                input_data = {
                    "vin": vin_clean,
                    "year": resolved_year,
                    "make": resolved_make,
                    "model": resolved_model,
                    "trim": resolved_trim,
                    "platform": resolved_engine,
                    "transmission": resolved_transmission,
                    "mileage": mileage.strip(),
                    "complaint": complaint.strip(),
                    "codes": codes.strip(),
                    "symptoms": symptoms.strip(),
                    "recent_repairs": recent_repairs.strip(),
                    "notes": notes.strip(),
                }

                recalls = fetch_recalls(input_data["year"], input_data["make"], input_data["model"])
                st.session_state.latest_recalls = recalls

                service_refs = {
                    "local_dataset": scan_local_service_dataset(
                        input_data["year"],
                        input_data["make"],
                        input_data["model"],
                        input_data["platform"],
                        input_data["complaint"],
                        input_data["codes"],
                    ),
                    "charm_links": build_charm_links(
                        input_data["year"],
                        input_data["make"],
                        input_data["model"],
                        input_data["platform"],
                    ),
                }
                st.session_state.latest_service_refs = service_refs

                vehicle_label = (
                    f"{input_data['year']} "
                    f"{input_data['make']} "
                    f"{input_data['model']} "
                    f"{input_data['trim']} "
                    f"{input_data['platform']} "
                    f"{input_data['transmission']}"
                ).strip()

                try:
                    with st.spinner("Building a diagnostic plan..."):
                        response = client.responses.create(
                            model="gpt-5-mini",
                            input=build_prompt(input_data, vin_decode, recalls, service_refs),
                            reasoning={"effort": "low"},
                        )

                    raw_text = getattr(response, "output_text", "").strip()
                    st.session_state.latest_raw_output = raw_text

                    if not raw_text:
                        st.error("No output returned from the model.")
                    else:
                        if show_raw_output:
                            st.markdown('<div class="section-card">', unsafe_allow_html=True)
                            st.markdown("### Raw AI Output")
                            st.code(raw_text, language="json")
                            st.markdown("</div>", unsafe_allow_html=True)

                        try:
                            result = parse_model_json(raw_text)
                            st.session_state.latest_result = result
                            st.session_state.latest_input = input_data
                            st.session_state.latest_vehicle_label = vehicle_label
                        except json.JSONDecodeError:
                            st.error("The AI returned an unexpected format.")
                            st.markdown("### Raw Output")
                            st.code(raw_text)

                except Exception as e:
                    st.error(f"Something went wrong: {e}")

if st.session_state.latest_result and isinstance(st.session_state.latest_result, dict):
    render_results(
        st.session_state.latest_result,
        st.session_state.latest_vehicle_label or " ".join(
            [
                st.session_state.get("vehicle_year", ""),
                st.session_state.get("vehicle_make", ""),
                st.session_state.get("vehicle_model", ""),
                st.session_state.get("vehicle_trim", ""),
                st.session_state.get("vehicle_engine", ""),
                st.session_state.get("vehicle_transmission", ""),
            ]
        ).strip(),
    )

if st.session_state.latest_service_refs:
    render_service_reference_panel(st.session_state.latest_service_refs)

# ---------------------------------
# Feedback / repair tracking
# ---------------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-kicker">Repair Intelligence Capture</div>', unsafe_allow_html=True)
st.header("Technician Feedback + Repair Tracking")

feedback_col1, feedback_col2 = st.columns(2)

with feedback_col1:
    helpful = st.radio(
        "Was this output helpful?",
        ["Yes", "No"],
        horizontal=True,
    )

with feedback_col2:
    use_again = st.radio(
        "Would you use this again?",
        ["Yes", "No", "Maybe"],
        horizontal=True,
    )

solved_options = ["Not yet / no solution confirmed"]

if st.session_state.latest_result and isinstance(st.session_state.latest_result, dict):
    for step in st.session_state.latest_result.get("diagnostic_steps", []):
        step_num = step.get("step_number", "?")
        title = step.get("title", "Untitled step")
        solved_options.append(f"Step {step_num} — {title}")

solved_step = st.selectbox(
    "Which diagnostic step yielded the solution?",
    solved_options
)

final_fix = st.text_area(
    "Final Repair / Final Fix",
    placeholder="Example: replaced left intake cam phaser and timing chain set",
    height=100,
)

missing_info = st.text_area(
    "What was missing or wrong? (optional)",
    placeholder="Example: should have suggested checking oil pressure before recommending chain inspection",
    height=100,
)

log_case = st.checkbox("Log this case to the Scout dataset", value=True)

if st.button("Save Feedback / Log Case"):
    if not st.session_state.latest_input or not st.session_state.latest_result:
        st.error("Generate a diagnostic path first before saving feedback.")
    else:
        solved_step_number = ""
        solved_step_title = ""

        if solved_step != "Not yet / no solution confirmed":
            match = re.match(r"Step\s+(\d+)\s+—\s+(.*)", solved_step)
            if match:
                solved_step_number = match.group(1)
                solved_step_title = match.group(2)

        row = {
            "timestamp_utc": datetime.utcnow().isoformat(),
            "vin": st.session_state.latest_input.get("vin", ""),
            "year": st.session_state.latest_input.get("year", ""),
            "make": st.session_state.latest_input.get("make", ""),
            "model": st.session_state.latest_input.get("model", ""),
            "trim": st.session_state.latest_input.get("trim", ""),
            "platform": st.session_state.latest_input.get("platform", ""),
            "transmission": st.session_state.latest_input.get("transmission", ""),
            "mileage": st.session_state.latest_input.get("mileage", ""),
            "complaint": st.session_state.latest_input.get("complaint", ""),
            "codes": st.session_state.latest_input.get("codes", ""),
            "symptoms": st.session_state.latest_input.get("symptoms", ""),
            "recent_repairs": st.session_state.latest_input.get("recent_repairs", ""),
            "notes": st.session_state.latest_input.get("notes", ""),
            "helpful": helpful,
            "use_again": use_again,
            "solved_step_number": solved_step_number,
            "solved_step_title": solved_step_title,
            "final_fix": final_fix.strip(),
            "missing_info": missing_info.strip(),
            "recalls_json": json.dumps(st.session_state.latest_recalls, ensure_ascii=False),
            "raw_ai_output": st.session_state.latest_raw_output or "",
            "structured_ai_output": json.dumps(st.session_state.latest_result, ensure_ascii=False),
            "service_refs_json": json.dumps(st.session_state.latest_service_refs, ensure_ascii=False),
        }

        if log_case:
            append_case_log(row)
            st.success("Feedback saved and case logged to scout_case_log.csv")
        else:
            st.success("Feedback captured in the session. Case logging was not selected.")

st.caption(
    "This version logs cases locally to scout_case_log.csv. Later versions can push this into "
    "a database, analytics dashboard, and shop-level workflow layer."
)
st.markdown("</div>", unsafe_allow_html=True)
