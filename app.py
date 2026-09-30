import html

import pandas as pd
import streamlit as st

st.set_page_config(page_title="UFC Fight Predictor", page_icon="🥊", layout="centered")

RED, BLUE = "#E5484D", "#3E8BFF"
ROLL_STATS = ["won", "SIG_STR_pct", "TD_pct", "CTRL", "SUB_ATT", "KD"]
LABELS = {
    "won": "Win rate",
    "SIG_STR_pct": "Striking accuracy",
    "TD_pct": "Takedown accuracy",
    "CTRL": "Control time",
    "SUB_ATT": "Submission attempts",
    "KD": "Knockdowns",
}


def fmt(stat, v):
    if pd.isna(v):
        return "–"
    if stat == "won":
        return f"{v * 100:.0f}%"
    if stat in ("SIG_STR_pct", "TD_pct"):
        return f"{v:.0f}%"
    if stat == "CTRL":
        return f"{int(v) // 60}:{int(v) % 60:02d}"
    return f"{v:.1f}"


st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Barlow:wght@400;500;600&display=swap');
html, body, [class*="css"], .stApp {{ font-family: 'Barlow', sans-serif; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ max-width: 820px; padding-top: 2.2rem; }}
.stApp {{ background: radial-gradient(1100px 500px at 50% -10%, #1B2D4D 0%, #0D1524 60%); }}

.hero h1 {{ font-family: 'Barlow Condensed', sans-serif; font-weight: 800; font-size: 3.4rem;
  letter-spacing: .5px; margin: 0; padding: 0; line-height: 1.1; }}
.hero p {{ color: #8FA0BC; margin: .9rem 0 2.2rem; line-height: 1.5; }}

.corner {{ font-family: 'Barlow Condensed', sans-serif; font-weight: 700; font-size: 1.05rem;
  letter-spacing: 1px; margin: 0 !important; padding: 0 0 .9rem !important; line-height: 1.2; }}
div[data-testid="stSelectbox"] {{ margin-top: .3rem !important; }}
.corner.red {{ color: {RED}; }} .corner.blue {{ color: {BLUE}; }}

div[data-testid="stElementContainer"]:has(.stButton), div[data-testid="stButton"] {{ width: 100% !important; }}
div.stButton {{ display: flex !important; justify-content: center !important; width: 100% !important;
  text-align: center; margin-top: 1.5rem; }}
div.stButton > button {{ margin: 0 auto !important; }}
div.stButton > button, div.stButton button[data-testid^="stBaseButton"] {{
  background: {RED} !important; color: #fff !important; border: 0 !important; border-radius: 4px !important;
  padding: 1rem 3.5rem !important; min-width: 260px; min-height: 3.6rem; width: auto !important;
  transition: filter .15s; }}
div.stButton button p, div.stButton button div {{
  font-family: 'Barlow Condensed', sans-serif !important; font-weight: 700 !important;
  font-size: 1.35rem !important; letter-spacing: 1.5px; margin: 0 !important; line-height: 1.3 !important; }}
div.stButton > button:hover {{ filter: brightness(1.12); color: #fff !important; }}
div.stButton > button:disabled {{ background: #2A3A57 !important; color: #7E8FAB !important; }}
div.stButton > button:focus-visible {{ outline: 2px solid #fff; outline-offset: 2px; }}

.matchup {{ display: grid; grid-template-columns: 1fr auto 1fr; align-items: end; gap: 1.5rem; margin-top: 2.5rem; }}
.side.right {{ text-align: right; }}
.fname {{ font-family: 'Barlow Condensed', sans-serif; font-weight: 700; font-size: 1.6rem; line-height: 1.2; margin-bottom: .7rem; }}
.pct {{ font-family: 'Barlow Condensed', sans-serif; font-weight: 800; font-size: 5rem; line-height: 1; }}
.side.left .pct, .side.left .fname {{ color: {RED}; }}
.side.right .pct, .side.right .fname {{ color: {BLUE}; }}
.vs {{ font-family: 'Barlow Condensed', sans-serif; font-weight: 700; color: #5F7191; font-size: 1.2rem; padding-bottom: 1rem; }}

.bar {{ display: flex; height: 14px; border-radius: 3px; overflow: hidden; margin: 1.6rem 0 1.2rem; background: #152238; }}
.bar .r {{ background: {RED}; }} .bar .b {{ background: {BLUE}; }}
.verdict {{ text-align: center; color: #8FA0BC; line-height: 1.6; }}
.verdict b {{ color: #EAF0FA; font-family: 'Barlow Condensed', sans-serif; font-size: 1.5rem; font-weight: 700; }}

.tape-title {{ font-family: 'Barlow Condensed', sans-serif; font-weight: 700; font-size: 1.5rem; line-height: 1.2; margin: 3rem 0 .6rem; }}
.tape-sub {{ color: #8FA0BC; font-size: .92rem; line-height: 1.6; margin-bottom: 1.4rem; }}
.row {{ display: grid; grid-template-columns: 1fr 1.5fr 1fr; align-items: center; gap: 1rem;
  padding: 1.2rem 0; border-top: 1px solid #22334F; }}
.row .v {{ font-family: 'Barlow Condensed', sans-serif; font-weight: 600; font-size: 1.7rem; line-height: 1.2; color: #7E8FAB; }}
.row .v.l {{ text-align: left; }} .row .v.rt {{ text-align: right; }}
.row .v.lead.l {{ color: {RED}; }} .row .v.lead.rt {{ color: {BLUE}; }}
.row .mid {{ text-align: center; font-size: .95rem; line-height: 1.3; color: #C5D1E6; }}
.impact {{ display: flex; height: 6px; margin-top: .7rem; }}
.impact .h {{ flex: 1; display: flex; background: #152238; }}
.impact .h.a {{ justify-content: flex-end; border-radius: 3px 0 0 3px; }}
.impact .h.c {{ border-radius: 0 3px 3px 0; }}
.impact .fr {{ background: {RED}; }} .impact .fb {{ background: {BLUE}; }}
.note {{ color: #6F809C; font-size: .82rem; line-height: 1.7; margin-top: 1.8rem; padding-bottom: 2rem; }}
</style>
<div class="hero"><h1>UFC Fight Predictor</h1>
<p>Pick two fighters and see who the model favours, and why.</p></div>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading data and training model...")
def load():
    from data_processing import long_df, diff_cols
    from model import log_reg_pipe

    fighters = sorted(long_df["fighter"].dropna().unique())
    return long_df, diff_cols, log_reg_pipe, fighters


long_df, diff_cols, model, fighters = load()


def get_form(name, n=5):
    hist = long_df[long_df["fighter"] == name].sort_values("date")
    return hist[ROLL_STATS].tail(n).mean(), hist["date"].max()


def compare(f1, f2):
    form1, last1 = get_form(f1)
    form2, last2 = get_form(f2)
    diff = {f"{s}_roll5_diff": form1[s] - form2[s] for s in ROLL_STATS}
    X = pd.DataFrame([diff])[diff_cols]
    p1 = float(model.predict_proba(X)[0][1])
    contrib = model[0].transform(X)[0] * model[-1].coef_[0]
    impact = {c.replace("_roll5_diff", ""): v for c, v in zip(diff_cols, contrib)}
    return form1, form2, last1, last2, p1, impact


c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="corner red">RED CORNER</div>', unsafe_allow_html=True)
    f1 = st.selectbox("Red corner", fighters, index=None, placeholder="Search a fighter",
                      label_visibility="collapsed")
with c2:
    st.markdown('<div class="corner blue">BLUE CORNER</div>', unsafe_allow_html=True)
    f2 = st.selectbox("Blue corner", fighters, index=None, placeholder="Search a fighter",
                      label_visibility="collapsed")

go = st.button("Predict fight", disabled=not (f1 and f2))

if go:
    if f1 == f2:
        st.warning("Pick two different fighters.")
        st.stop()

    form1, form2, last1, last2, p1, impact = compare(f1, f2)
    p2 = 1 - p1
    fav = f1 if p1 > p2 else f2
    n1, n2 = html.escape(f1), html.escape(f2)

    st.markdown(
        f"""
<div class="matchup">
  <div class="side left"><div class="fname">{n1}</div><div class="pct">{p1 * 100:.1f}%</div></div>
  <div class="vs">VS</div>
  <div class="side right"><div class="fname">{n2}</div><div class="pct">{p2 * 100:.1f}%</div></div>
</div>
<div class="bar"><div class="r" style="width:{p1 * 100:.1f}%"></div><div class="b" style="width:{p2 * 100:.1f}%"></div></div>
<div class="verdict">Favourite: <b>{html.escape(fav)}</b></div>
""",
        unsafe_allow_html=True,
    )

    max_imp = max(abs(v) for v in impact.values()) or 1
    rows = ""
    for s in ROLL_STATS:
        v1, v2 = form1[s], form2[s]
        l_lead = " lead" if v1 > v2 else ""
        r_lead = " lead" if v2 > v1 else ""
        w = abs(impact[s]) / max_imp * 100
        left = f'<div class="fr" style="width:{w:.0f}%"></div>' if impact[s] > 0 else ""
        right = f'<div class="fb" style="width:{w:.0f}%"></div>' if impact[s] < 0 else ""
        rows += f"""
<div class="row">
  <div class="v l{l_lead}">{fmt(s, v1)}</div>
  <div class="mid">{LABELS[s]}
    <div class="impact"><div class="h a">{left}</div><div class="h c">{right}</div></div></div>
  <div class="v rt{r_lead}">{fmt(s, v2)}</div>
</div>"""

    st.markdown(
        f"""
<div class="tape-title">Tale of the tape</div>
<div class="tape-sub">Average of each fighter's last 5 fights. The bar under each stat shows how far it pushed the
prediction toward the red or blue corner.</div>
{rows}
<div class="note">Last fight in dataset: {n1} on {last1.date()}, {n2} on {last2.date()}.
Older dates mean the form may be out of date. Data ends in 2023.</div>
""",
        unsafe_allow_html=True,
    )
