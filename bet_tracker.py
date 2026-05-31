import requests
from bs4 import BeautifulSoup
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date

# =============================
# BET TRACKER - STREAMLIT APP
# =============================

st.set_page_config(
    page_title="Bet Tracker",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = Path("bets_data.csv")

START_BANKROLL = 500.00

COLUMNS = [
    "Data",
    "Liga",
    "Selekcja",
    "Kurs",
    "Stawka",
    "Wynik",
    "Profit",
    "Profit skumulowany",
    "Bankroll",
    "Notatka"
]

RESULTS = ["WAIT", "WIN", "LOSS", "PUSH"]
SYSTEMS = ["FS TIPS", "Top Tipster", "Inny", "Value", "AKO", "Live"]

# =============================
# CSS
# =============================

def fetch_fstips_tip():
    url = "https://www.footballsuper.tips/football-accumulators-tips/football-tips-prediction-of-the-day/"

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text("\n", strip=True)

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    odd_index = None
    for i, line in enumerate(lines):
        if "Total Odd" in line:
            odd_index = i
            break

    if odd_index is None or odd_index < 5:
        return None

    odds_match = re.search(r"Total Odd[:\s]+([0-9]+(?:\.[0-9]+)?)", lines[odd_index])

    if not odds_match:
        return None

    odds = float(odds_match.group(1))

    tip_line = lines[odd_index - 4]
    match_line = lines[odd_index - 2]
    league_line = lines[odd_index - 1]

    selection = f"{match_line} - {tip_line}"

    return {
        "league": "FS TIPS",
        "selection": selection,
        "odds": odds,
        "note": f"Auto FSTips | {league_line}"
    }

st.markdown("""
<style>
div[data-testid="stTabs"] {
    background: rgba(15,23,42,0.55);
    padding: 10px;
    border-radius: 18px;
    border: 1px solid #334155;
}

button[data-baseweb="tab"] {
    background: #1E293B !important;
    border: 1px solid #475569 !important;
    border-radius: 14px 14px 0 0 !important;
    padding: 12px 22px !important;
    color: #E2E8F0 !important;
    font-weight: 800 !important;
    margin-right: 8px !important;
}

button[data-baseweb="tab"]:hover {
    background: #334155 !important;
    color: white !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(90deg, #22C55E, #16A34A) !important;
    color: white !important;
    border-bottom: 4px solid #EF4444 !important;
}
    .stApp {
        background: linear-gradient(135deg, #06121F 0%, #0B1F33 45%, #07111F 100%);
        color: #F8FAFC;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1600px;
    }

    h1, h2, h3 {
        color: #F8FAFC !important;
        font-weight: 900 !important;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(8, 47, 73, 0.95), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-left: 8px solid #06B6D4;
        border-radius: 26px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.45);
    }

    .metric-card {
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 14px 35px rgba(0,0,0,0.35);
    }

    .profit-positive {
        color: #22C55E;
        font-weight: 900;
    }

    .profit-negative {
        color: #EF4444;
        font-weight: 900;
    }

    .big-number {
        font-size: 42px;
        font-weight: 900;
        line-height: 1;
    }

    .subtitle {
        color: #94A3B8;
        font-size: 15px;
    }

    .stButton > button {
        background: linear-gradient(90deg, #0891B2, #06B6D4);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 10px 22px;
        font-weight: 900;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #0E7490, #0891B2);
        color: white;
    }

    textarea, input, select {
        border-radius: 14px !important;
    }
    .dashboard-pro-hero {
    background:
        linear-gradient(90deg, rgba(2,6,23,0.92) 0%, rgba(2,6,23,0.75) 45%, rgba(2,6,23,0.25) 100%),
        url("https://images.unsplash.com/photo-1508098682722-e99c643e7485");
    background-size: cover;
    background-position: center;
    border: 1px solid rgba(148,163,184,0.35);
    border-left: 8px solid #06B6D4;
    border-radius: 28px;
    padding: 34px;
    margin-bottom: 26px;
    box-shadow: 0 24px 60px rgba(0,0,0,0.55);
}

.dashboard-pro-grid {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 28px;
    align-items: center;
}

.dashboard-pro-title {
    font-size: 46px;
    font-weight: 900;
    color: white;
    margin-bottom: 8px;
}

.dashboard-pro-subtitle {
    color: #93C5FD;
    font-size: 17px;
    margin-bottom: 22px;
}

.dashboard-pro-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.dashboard-badge {
    background: rgba(15,23,42,0.75);
    border: 1px solid rgba(34,211,238,0.35);
    border-radius: 14px;
    padding: 10px 14px;
    color: #E2E8F0;
    font-weight: 800;
}

.dashboard-live-panel {
    background: rgba(15,23,42,0.78);
    border: 1px solid rgba(34,211,238,0.35);
    border-radius: 22px;
    padding: 22px;
    backdrop-filter: blur(6px);
}

.dashboard-live-row {
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid rgba(148,163,184,0.18);
    padding: 9px 0;
    color: #E2E8F0;
}

.dashboard-live-value-green {
    color: #22C55E;
    font-weight: 900;
}

.dashboard-live-value-white {
    color: #FFFFFF;
    font-weight: 900;
}
</style>
""", unsafe_allow_html=True)

# =============================
# DATA HELPERS
# =============================

def empty_df():
    return pd.DataFrame(columns=COLUMNS)


def load_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNS]
    return empty_df()


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


def calc_profit(row):
    result = str(row.get("Wynik", "")).strip().upper()

    try:
        stake = float(str(row.get("Stawka", 0)).replace(",", "."))
        odds = float(str(row.get("Kurs", 0)).replace(",", "."))
    except:
        return 0.0

    if result == "WIN":
        return round((odds * stake) - stake, 2)

    if result == "LOSS":
        return round(-stake, 2)

    if result == "PUSH":
        return 0.0

    return 0.0


def recalc(df):
    if df.empty:
        return df

    df = df.copy()
    df["Kurs"] = pd.to_numeric(df["Kurs"], errors="coerce").fillna(0)
    df["Stawka"] = pd.to_numeric(df["Stawka"], errors="coerce").fillna(0)

    df["Profit"] = df.apply(calc_profit, axis=1)
    df["Profit skumulowany"] = df["Profit"].cumsum().round(2)
    df["Bankroll"] = (START_BANKROLL + df["Profit skumulowany"]).round(2)

    return df


def summary_stats(df):
    if df.empty:
        return {
            "bankroll": START_BANKROLL,
            "profit": 0,
            "yield": 0,
            "win_rate": 0,
            "bets": 0,
            "wins": 0,
            "losses": 0,
            "avg_odds": 0,
            "total_stake": 0
        }

    settled = df[df["Wynik"].isin(["WIN", "LOSS", "PUSH"])]
    wins = len(settled[settled["Wynik"] == "WIN"])
    losses = len(settled[settled["Wynik"] == "LOSS"])
    bets = len(settled)
    total_stake = settled["Stawka"].sum()
    profit = settled["Profit"].sum()
    bankroll = START_BANKROLL + profit
    win_rate = (wins / bets * 100) if bets else 0
    yield_pct = (profit / total_stake * 100) if total_stake else 0
    avg_odds = settled["Kurs"].mean() if bets else 0

    return {
        "bankroll": bankroll,
        "profit": profit,
        "yield": yield_pct,
        "win_rate": win_rate,
        "bets": bets,
        "wins": wins,
        "losses": losses,
        "avg_odds": avg_odds,
        "total_stake": total_stake
    }


def profit_class(value):
    return "profit-positive" if value >= 0 else "profit-negative"

# =============================
# HEADER
# =============================

st.markdown("""
<div class="hero-card">
    <h1>⚽ Bet Tracker — Piłka Nożna</h1>
    <p class="subtitle">Bankroll · ROI/Yield · Win Rate · Profit skumulowany · Systemy typerskie</p>
</div>
""", unsafe_allow_html=True)

# =============================
# LOAD DATA
# =============================

df = load_data()
df = recalc(df)
save_data(df)
stats = summary_stats(df)

# =============================
# TABS
# =============================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "➕ Dodaj zakład",
    "📋 Historia",
    "📈 Statystyki",
    "🧮 Kalkulator"
])

# =============================
# DASHBOARD
# =============================

with tab1:
    st.markdown(f"""
    <div class="dashboard-pro-hero">
        <div class="dashboard-pro-grid">
            <div>
                <div class="dashboard-pro-title">⚽ Bet Tracker PRO</div>
                <div class="dashboard-pro-subtitle">
                    Live bankroll tracking · ROI/Yield · Win Rate · FS Tips automation
                </div>

                <div class="dashboard-pro-badges">
                    <div class="dashboard-badge">💼 Bankroll Management</div>
                    <div class="dashboard-badge">🎯 Value Bets</div>
                    <div class="dashboard-badge">📈 ROI / Yield</div>
                    <div class="dashboard-badge">🤖 Auto FS Tips</div>
                </div>
            </div>

            <div class="dashboard-live-panel">
                <div class="dashboard-live-row">
                    <span>Bankroll</span>
                    <span class="dashboard-live-value-green">CHF{stats['bankroll']:.2f}</span>
                </div>
                <div class="dashboard-live-row">
                    <span>Profit</span>
                    <span class="dashboard-live-value-green">CHF{stats['profit']:.2f}</span>
                </div>
                <div class="dashboard-live-row">
                    <span>Yield / ROI</span>
                    <span class="dashboard-live-value-white">{stats['yield']:.1f}%</span>
                </div>
                <div class="dashboard-live-row">
                    <span>Win Rate</span>
                    <span class="dashboard-live-value-white">{stats['win_rate']:.1f}%</span>
                </div>
                <div class="dashboard-live-row">
                    <span>Zakłady</span>
                    <span class="dashboard-live-value-white">{stats['bets']}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:38px;">💼</div>
            <p class="subtitle">Bankroll aktualny</p>
            <div class="big-number">CHF{stats['bankroll']:.2f}</div>
            <p class="subtitle">Start: CHF{START_BANKROLL:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:38px;">📈</div>
            <p class="subtitle">Profit</p>
            <div class="big-number {profit_class(stats['profit'])}">CHF{stats['profit']:.2f}</div>
            <p class="subtitle">Profit skumulowany</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:38px;">🎯</div>
            <p class="subtitle">Yield / ROI</p>
            <div class="big-number {profit_class(stats['yield'])}">{stats['yield']:.1f}%</div>
            <p class="subtitle">Zwrot z postawionych stawek</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:38px;">🏆</div>
            <p class="subtitle">Win Rate</p>
            <div class="big-number">{stats['win_rate']:.1f}%</div>
            <p class="subtitle">{stats['wins']} WIN / {stats['losses']} LOSS</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not df.empty:
        col_a, col_b = st.columns([1.25, 1])

        with col_a:
            fig = px.line(
                df,
                x=df.index,
                y="Bankroll",
                title="📈 Wzrost bankrolla",
                markers=True
            )
            fig.update_layout(
                template="plotly_dark",
                height=430,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.85)",
                font=dict(color="#E2E8F0"),
                title_font=dict(size=22),
            )
            fig.update_traces(line=dict(width=4))
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            settled = df[df["Wynik"].isin(["WIN", "LOSS", "PUSH", "WAIT"])]

            result_counts = settled["Wynik"].value_counts().reset_index()
            result_counts.columns = ["Wynik", "Liczba"]

            fig_pie = px.pie(
                result_counts,
                names="Wynik",
                values="Liczba",
                hole=0.55,
                title="🎯 Podsumowanie wyników"
            )
            fig_pie.update_layout(
                template="plotly_dark",
                height=430,
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E2E8F0"),
                title_font=dict(size=22),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("### 🧾 Ostatnie typy")

        last_bets = df.tail(8).copy()
        st.dataframe(
            last_bets[["Data", "Liga", "Selekcja", "Kurs", "Stawka", "Wynik", "Profit", "Bankroll"]],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.markdown("""
        <div class="metric-card">
            <h3>Brak danych</h3>
            <p class="subtitle">Dodaj pierwszy zakład albo pobierz typ z FS TIPS.</p>
        </div>
        """, unsafe_allow_html=True)

# =============================
# ADD BET
# =============================

with tab2:
    st.header("➕ Dodaj nowy zakład")

    if st.button("🌐 Pobierz typ z FS TIPS"):
        tip = fetch_fstips_tip()

        if tip:
            new_row = {
                "Data": date.today().strftime("%d.%m.%Y"),
                "Liga": tip["league"],
                "Selekcja": tip["selection"],
                "Kurs": tip["odds"],
                "Stawka": 100.00,
                "Wynik": "WAIT",
                "Profit": 0,
                "Profit skumulowany": 0,
                "Bankroll": START_BANKROLL,
                "Notatka": tip["note"]
            }

            df_new = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df_new = recalc(df_new)
            save_data(df_new)

            st.success(f"Dodano typ: {tip['selection']} @ {tip['odds']}")
        else:
            st.error("Nie udało się pobrać typu z FS TIPS.")

    with st.form("add_bet_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)

        with c1:
            bet_date = st.date_input("Data", value=date.today())
            league = st.selectbox("Liga / System", SYSTEMS)
            odds = st.number_input("Kurs", min_value=1.01, value=1.80, step=0.01)

        with c2:
            stake = st.number_input("Stawka", min_value=0.0, value=20.0, step=5.0)
            result = st.selectbox("Wynik", RESULTS)
            note = st.text_input("Notatka")

        with c3:
            selection = st.text_area("Selekcja", placeholder="Np. Roma - Fiorentina BTTS no")

        submitted = st.form_submit_button("Dodaj zakład")

        if submitted:
            new_row = {
                "Data": bet_date.strftime("%d.%m.%Y"),
                "Liga": league,
                "Selekcja": selection,
                "Kurs": odds,
                "Stawka": stake,
                "Wynik": result,
                "Profit": 0,
                "Profit skumulowany": 0,
                "Bankroll": START_BANKROLL,
                "Notatka": note
            }

            df_new = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df_new = recalc(df_new)
            save_data(df_new)
            st.success("Zakład dodany. Odśwież stronę albo przejdź do historii.")

# =============================
# HISTORY
# =============================

with tab3:
    st.header("📋 Historia zakładów")

    if df.empty:
        st.info("Brak danych.")
    else:
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="fixed",
            hide_index=True,
            key="bets_editor",
            column_config={
                "Wynik": st.column_config.SelectboxColumn("Wynik", options=RESULTS),
                "Liga": st.column_config.SelectboxColumn("Liga", options=SYSTEMS),
                "Kurs": st.column_config.NumberColumn("Kurs", format="%.2f"),
                "Stawka": st.column_config.NumberColumn("Stawka", format="%.2f"),
                "Profit": st.column_config.NumberColumn("Profit", format="%.2f", disabled=True),
                "Profit skumulowany": st.column_config.NumberColumn("Profit skumulowany", format="%.2f", disabled=True),
                "Bankroll": st.column_config.NumberColumn("Bankroll", format="%.2f", disabled=True),
            }
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Zapisz zmiany"):
                edited_df = edited_df.dropna(how="all")
                edited_df = recalc(edited_df)
                save_data(edited_df)
                st.success("Zapisano i przeliczono zakłady. Odśwież stronę.")

        with col2:
            row_to_delete = st.number_input(
                "Numer wiersza do usunięcia",
                min_value=0,
                max_value=max(len(df) - 1, 0),
                value=0,
                step=1
            )

            if st.button("🗑️ Usuń wybrany wiersz"):
                new_df = df.drop(df.index[int(row_to_delete)]).reset_index(drop=True)
                new_df = recalc(new_df)
                save_data(new_df)
                st.success(f"Usunięto wiersz {row_to_delete}. Odśwież stronę.")

        st.download_button(
            "📥 Pobierz CSV",
            df.to_csv(index=False).encode("utf-8"),
            "bet_tracker.csv",
            "text/csv"
        )

# =============================
# STATS
# =============================

with tab4:
    st.header("📈 Statystyki")

    if df.empty:
        st.info("Brak danych.")
    else:
        settled = df[df["Wynik"].isin(["WIN", "LOSS", "PUSH"])]

        by_system = settled.groupby("Liga").agg(
            Zaklady=("Liga", "count"),
            Profit=("Profit", "sum"),
            Stawki=("Stawka", "sum"),
            Sredni_kurs=("Kurs", "mean")
        ).reset_index()

        by_system["Yield %"] = (by_system["Profit"] / by_system["Stawki"] * 100).round(1)
        by_system["Profit"] = by_system["Profit"].round(2)
        by_system["Sredni_kurs"] = by_system["Sredni_kurs"].round(2)

        st.subheader("Podsumowanie systemów")
        st.dataframe(by_system, use_container_width=True)

        fig3 = px.bar(by_system, x="Liga", y="Profit", title="Profit według systemu")
        fig3.update_layout(template="plotly_dark", height=420)
        st.plotly_chart(fig3, use_container_width=True)

# =============================
# CALCULATOR
# =============================

with tab5:
    st.header("🧮 Kalkulator progresji +10%")

    c1, c2, c3 = st.columns(3)

    with c1:
        loss = st.number_input("Strata", value=28.0, step=1.0)
    with c2:
        odds_calc = st.number_input("Kurs", value=1.80, step=0.01)
    with c3:
        target_profit = st.number_input("Docelowy zysk", value=10.0, step=1.0)

    if odds_calc > 1:
        stake_needed = (loss + target_profit) / (odds_calc - 1)
    else:
        stake_needed = 0

    st.markdown(f"""
    <div class="metric-card">
        <p class="subtitle">Sugerowana stawka</p>
        <div class="big-number">CHF{stake_needed:.2f}</div>
    </div>
    """, unsafe_allow_html=True)
