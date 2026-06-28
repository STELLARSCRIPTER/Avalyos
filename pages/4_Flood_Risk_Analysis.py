"""
AVALYOS — Flood Risk Analysis Page  (with interactive dropdowns)
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings, os

warnings.filterwarnings("ignore")

# ── Path config ───────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR     = os.path.join(BASE_DIR, "dataset")
RAINFALL_CSV = os.path.join(DATA_DIR, "district wise rainfall normal.csv")
EMDAT_CSV    = os.path.join(DATA_DIR, "public_emdat_project.csv")

ELNINO_YEARS = [1982,1983,1987,1991,1992,1994,1997,1998, 
                2002,2004,2006,2009,2010,2015,2016,2018,2019,2023]
MONTHS       = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

AFFECTED_COUNTRIES = [
    "India","Bangladesh","China","Indonesia","Philippines",
    "Pakistan","Myanmar","Vietnam","Thailand","Nepal",
    "Peru","Ecuador","Colombia","Brazil","Bolivia",
    "Mozambique","Zimbabwe","South Africa",
]

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Flood Risk Analysis | AVALYOS",
    page_icon="🌊", layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
:root {
  --primary:#0066ff; --bg:#ffffff; --card:#f0f2f6;
  --text:#262730; --muted:#666666; --border:#e6e9ee;
  --success:#00a86b; --error:#d32f2f;
}
body,.stApp{background-color:var(--bg)!important;color:var(--text)!important;}
.hero{background:var(--card);border:1px solid var(--border);border-radius:12px;
      padding:2rem 2.5rem;margin-bottom:1.5rem;}
.filter-bar{background:var(--card);border:1px solid var(--border);border-radius:8px;
            padding:0.8rem 1.2rem;margin-bottom:1rem;}
.tag-high{background:#fde8e8;color:var(--error);border-radius:4px;
          padding:2px 8px;font-size:0.8rem;font-weight:600;}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def load_rainfall(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df["STATE_UT_NAME"] = df["STATE_UT_NAME"].str.strip().str.title()
    df["DISTRICT"]      = df["DISTRICT"].str.strip().str.title()
    for col in MONTHS + ["ANNUAL"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

@st.cache_data(show_spinner=False)
def load_emdat(path):
    df = pd.read_csv(path, encoding="latin-1", low_memory=False)
    df.columns = df.columns.str.strip()
    df["Year"]     = pd.to_numeric(df["Start Year"], errors="coerce")
    df["Damage_M"] = pd.to_numeric(
        df.get("Total Damage, Adjusted ('000 US$)", pd.Series(dtype=float)),
        errors="coerce") / 1000
    for col in ["Total Deaths","Total Affected"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["ElNino"] = df["Year"].isin(ELNINO_YEARS)
    return df

@st.cache_data(show_spinner=False)
def build_annual(india):
    a = india.groupby("Year").agg(
        Events  =("DisNo.","count"),
        Deaths  =("Total Deaths","sum"),
        Affected=("Total Affected","sum"),
        Damage  =("Damage_M","sum"),
    ).reset_index()
    a["ElNino"]     = a["Year"].isin(ELNINO_YEARS)
    dmean, dstd     = a["Damage"].mean(), a["Damage"].std()
    a["HighImpact"] = a["Damage"] > (dmean + 0.5*dstd)
    return a

# ── guard missing files ───────────────────────────────────────────────────────
missing = [p for p in [RAINFALL_CSV, EMDAT_CSV] if not os.path.exists(p)]
if missing:
    st.error(f"**Missing:** {', '.join(missing)}\nPlace CSVs in `{DATA_DIR}/`")
    st.stop()

with st.spinner("Loading datasets…"):
    rain   = load_rainfall(RAINFALL_CSV)
    emdat  = load_emdat(EMDAT_CSV)
    india  = emdat[(emdat["Country"]=="India") & (emdat["Disaster Type"]=="Flood")].copy()
    annual = build_annual(india)

# global derived stats (used in KPIs)
state_rain           = rain.groupby("STATE_UT_NAME")[MONTHS+["ANNUAL"]].mean()
state_rain["NOV_DEC"]= state_rain["NOV"]+state_rain["DEC"]
threshold            = state_rain["NOV_DEC"].mean()+state_rain["NOV_DEC"].std()
high_rain_states     = state_rain[state_rain["NOV_DEC"]>threshold].index.tolist()
national_avg         = rain[MONTHS].mean()

overlap      = annual[annual["ElNino"] & annual["HighImpact"]]
elnino_in    = annual[annual["ElNino"]]
match_pct    = len(overlap)/len(elnino_in)*100 if len(elnino_in) else 0
elnino_avg   = annual[annual["ElNino"]].mean(numeric_only=True)
normal_avg_s = annual[~annual["ElNino"]].mean(numeric_only=True)
damage_mult  = (elnino_avg["Damage"]/normal_avg_s["Damage"]
                if normal_avg_s["Damage"]>0 else 1.0)
c1s = min(match_pct/100,1.0)
c2s = min((damage_mult-1)/4,1.0) if normal_avg_s["Damage"]>0 else 0
c3s = min(len(india)/150,1.0)
confidence = (c1s*0.4+c2s*0.4+c3s*0.2)*100


# ════════════════════════════════════════════════════════════════════════════
# HERO + KPIs
# ════════════════════════════════════════════════════════════════════════════

st.markdown(
    '<div class="hero">'
    '<h1 style="color:var(--primary);">🌊 FLOOD RISK ANALYSIS</h1>'
    '<p style="color:var(--muted);">India flood patterns — district rainfall normals & EMDAT disaster database.</p>'
    '</div>', unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Districts",         f"{rain['DISTRICT'].nunique():,}")
k2.metric("Flood Events",      f"{len(india):,}", "2000–2023")
k3.metric("Total Deaths",      f"{int(india['Total Deaths'].sum()):,}")
k4.metric("Total Damage",      f"${india['Damage_M'].sum():,.0f}M")
k5.metric("El Niño Match %",   f"{match_pct:.0f}%")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════

tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "☔ Rainfall Patterns",
    "📊 EMDAT Flood Impact",
    "🌀 El Niño Correlation",
    "⏱ Time-Lag Analysis",
    "🌍 Global Comparison",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — RAINFALL  |  dropdowns: State → District
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Rainfall Pattern Analysis")

    # ── filter bar ────────────────────────────────────────────────────────────
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([2, 2, 1])
    all_states  = sorted(rain["STATE_UT_NAME"].unique().tolist())
    sel_state   = f1.selectbox("Select State", ["All States"] + all_states, key="t1_state")

    dist_options = (["All Districts"] +
                    sorted(rain[rain["STATE_UT_NAME"]==sel_state]["DISTRICT"].unique().tolist())
                    if sel_state != "All States" else ["All Districts"])
    sel_district = f2.selectbox("Select District", dist_options, key="t1_dist")

    view_mode = f3.radio("View", ["Monthly", "Seasonal"], key="t1_view", horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── filter data ───────────────────────────────────────────────────────────
    if sel_state == "All States":
        filtered_rain = rain
        chart_label   = "National Average"
        plot_vals     = national_avg[MONTHS].values
    elif sel_district == "All Districts":
        filtered_rain = rain[rain["STATE_UT_NAME"]==sel_state]
        chart_label   = sel_state
        plot_vals     = filtered_rain[MONTHS].mean().values
    else:
        filtered_rain = rain[(rain["STATE_UT_NAME"]==sel_state) &
                             (rain["DISTRICT"]==sel_district)]
        chart_label   = f"{sel_district}, {sel_state}"
        plot_vals     = filtered_rain[MONTHS].mean().values

    # ── KPIs ──────────────────────────────────────────────────────────────────
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Districts in view", len(filtered_rain))
    annual_val = filtered_rain["ANNUAL"].mean()
    m2.metric("Avg Annual Rainfall", f"{annual_val:.0f} mm")
    nov_dec = filtered_rain[["NOV","DEC"]].mean().sum()
    m3.metric("Nov+Dec Rainfall",    f"{nov_dec:.0f} mm")
    peak_m = MONTH_LABELS[int(np.nanargmax(plot_vals))]
    m4.metric("Peak Month", peak_m)

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        if view_mode == "Monthly":
            st.markdown(f"**Monthly Rainfall — {chart_label}**")
            fig, ax = plt.subplots(figsize=(6,3.5))
            colors = ["#d62728" if m in ["NOV","DEC"] else "#1f77b4" for m in MONTHS]
            ax.bar(MONTH_LABELS, plot_vals, color=colors)
            ax.set_ylabel("Avg Rainfall (mm)")
            ax.grid(axis="y", alpha=0.3)
            fig.tight_layout(); st.pyplot(fig); plt.close(fig)
        else:
            st.markdown(f"**Seasonal Rainfall — {chart_label}**")
            seasons = {
                "Jan–Feb": filtered_rain[["JAN","FEB"]].mean().sum(),
                "Mar–May": filtered_rain[["MAR","APR","MAY"]].mean().sum(),
                "Jun–Sep": filtered_rain[["JUN","JUL","AUG","SEP"]].mean().sum(),
                "Oct–Dec": filtered_rain[["OCT","NOV","DEC"]].mean().sum(),
            }
            fig, ax = plt.subplots(figsize=(6,3.5))
            ax.bar(seasons.keys(), seasons.values(),
                   color=["#aec7e8","#ffbb78","#1f77b4","#d62728"])
            ax.set_ylabel("Avg Rainfall (mm)")
            ax.grid(axis="y", alpha=0.3)
            fig.tight_layout(); st.pyplot(fig); plt.close(fig)

    with col_r:
        st.markdown("**Top 10 States — Nov + Dec Rainfall**")
        top10 = state_rain.nlargest(10,"NOV_DEC")["NOV_DEC"].sort_values()
        colors_bar = ["#d62728" if s in high_rain_states else "steelblue" for s in top10.index]
        fig2, ax2 = plt.subplots(figsize=(6,3.5))
        ax2.barh(top10.index, top10.values, color=colors_bar)
        ax2.set_xlabel("Rainfall (mm)")
        ax2.grid(axis="x", alpha=0.3)
        fig2.tight_layout(); st.pyplot(fig2); plt.close(fig2)

    if sel_state != "All States":
        st.markdown("---")
        with st.expander("📋 District-level table for selected state"):
            cols_show = ["DISTRICT","ANNUAL","JUN","JUL","AUG","SEP","NOV","DEC"]
            st.dataframe(
                filtered_rain[cols_show].sort_values("ANNUAL",ascending=False).round(1),
                use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — EMDAT IMPACT  |  dropdowns: Year range + metric
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("India Flood Impacts — EMDAT Database")

    # ── filter bar ────────────────────────────────────────────────────────────
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([2, 2, 1])
    yr_min, yr_max = int(annual["Year"].min()), int(annual["Year"].max())
    year_range = f1.slider("Year Range", yr_min, yr_max, (yr_min, yr_max), key="t2_yr")
    metric_sel = f2.selectbox("Primary Metric",
                              ["Events","Deaths","Affected","Damage"], key="t2_metric")
    show_elnino = f3.checkbox("Highlight El Niño", value=True, key="t2_en")
    st.markdown('</div>', unsafe_allow_html=True)

    ann_f = annual[(annual["Year"]>=year_range[0]) & (annual["Year"]<=year_range[1])]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Flood Events",    f"{int(ann_f['Events'].sum()):,}")
    m2.metric("Total Deaths",    f"{int(ann_f['Deaths'].sum()):,}")
    m3.metric("Total Affected",  f"{int(ann_f['Affected'].sum()):,}")
    m4.metric("Total Damage",    f"${ann_f['Damage'].sum():,.0f}M")

    metric_labels = {"Events":"Flood Events","Deaths":"Total Deaths",
                     "Affected":"Total Affected","Damage":"Damage (M USD)"}
    metric_colors = {"Events":"steelblue","Deaths":"crimson",
                     "Affected":"darkorange","Damage":"green"}

    fig, ax = plt.subplots(figsize=(12,4))
    ax.bar(ann_f["Year"], ann_f[metric_sel],
           color=metric_colors[metric_sel], alpha=0.75, width=0.8)
    if show_elnino:
        for yr in ann_f[ann_f["ElNino"]]["Year"]:
            ax.axvline(yr, color="purple", alpha=0.25, linewidth=6)
        from matplotlib.patches import Patch
        ax.legend(handles=[Patch(color="purple",alpha=0.4,label="El Niño year")], fontsize=9)
    ax.set_title(f"{metric_labels[metric_sel]} — {year_range[0]}–{year_range[1]}")
    ax.set_xlabel("Year"); ax.tick_params(axis="x",rotation=45)
    ax.grid(axis="y",alpha=0.3)
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

    with st.expander("📋 Annual data table"):
        disp = ann_f.copy()
        disp["ElNino"]     = disp["ElNino"].map({True:"✅",False:""})
        disp["HighImpact"] = disp["HighImpact"].map({True:"⚠️",False:""})
        disp["Damage"]     = disp["Damage"].round(1)
        disp["Year"]       = disp["Year"].astype(int)
        st.dataframe(disp.rename(columns={
            "Events":"Flood Events","Deaths":"Total Deaths",
            "Affected":"Total Affected","Damage":"Damage (M USD)",
            "ElNino":"El Niño","HighImpact":"High Impact"}),
            use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — EL NIÑO CORRELATION  |  dropdown: compare metric
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("El Niño vs Normal Years — Flood Comparison")

    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2 = st.columns([2, 2])
    compare_metric = f1.selectbox("Compare by",
        ["All metrics","Events","Deaths","Damage"], key="t3_metric")
    yr_subset = f2.multiselect("Focus El Niño Years (optional)",
        [int(y) for y in elnino_in["Year"].tolist()],
        default=[], key="t3_yrs")
    st.markdown('</div>', unsafe_allow_html=True)

    # optionally filter to subset of El Niño years
    if yr_subset:
        sub_annual = annual[annual["Year"].isin(yr_subset) | ~annual["ElNino"]]
    else:
        sub_annual = annual

    sub_elnino_avg  = sub_annual[sub_annual["ElNino"]].mean(numeric_only=True)
    sub_normal_avg  = sub_annual[~sub_annual["ElNino"]].mean(numeric_only=True)
    sub_overlap     = sub_annual[sub_annual["ElNino"] & sub_annual["HighImpact"]]
    sub_match_pct   = (len(sub_overlap)/len(sub_annual[sub_annual["ElNino"]])*100
                       if len(sub_annual[sub_annual["ElNino"]])>0 else 0)

    m1,m2,m3 = st.columns(3)
    m1.metric("El Niño Years",        len(sub_annual[sub_annual["ElNino"]]))
    m2.metric("High-Impact Overlaps", len(sub_overlap))
    m3.metric("Overlap %",            f"{sub_match_pct:.1f}%")

    metrics_to_plot = (["Events","Deaths","Damage"]
                       if compare_metric=="All metrics" else [compare_metric])
    labels_map = {"Events":"Flood Events/yr","Deaths":"Deaths/yr","Damage":"Damage (M USD)/yr"}

    fig, axes = plt.subplots(1, len(metrics_to_plot),
                             figsize=(5*len(metrics_to_plot), 4))
    if len(metrics_to_plot)==1:
        axes = [axes]
    for ax, col in zip(axes, metrics_to_plot):
        vals = [sub_elnino_avg[col], sub_normal_avg[col]]
        bars = ax.bar(["El Niño","Normal"], vals,
                      color=["#7b2d8b","steelblue"], alpha=0.85, edgecolor="white")
        ax.set_title(labels_map[col])
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.02,
                    f"{v:,.0f}", ha="center", fontsize=10, fontweight="bold")
        ax.grid(axis="y",alpha=0.3)
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

    st.markdown("**Overlapping high-impact El Niño years:**")
    if len(sub_overlap):
        st.write(", ".join(str(int(y)) for y in sub_overlap["Year"].tolist()))
    else:
        st.write("No overlap in selection.")

    st.markdown("**Confidence Score**")
    sc_df = pd.DataFrame({
        "Component": ["El Niño–Flood overlap (40%)","Damage amplification (40%)",
                       "Sample size (20%)","OVERALL"],
        "Score":     [f"{c1s*100:.1f}%", f"{c2s*100:.1f}%",
                      f"{c3s*100:.1f}%", f"{confidence:.1f} / 100"],
    })
    st.dataframe(sc_df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — TIME-LAG  |  dropdown: select specific El Niño year
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Time-Lag Analysis — El Niño Year vs Following Year")

    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2 = st.columns([2, 2])
    lag_years_available = [int(y) for y in ELNINO_YEARS
                           if annual[(annual["Year"]==y)|(annual["Year"]==y+1)]["Damage"].sum()>0]
    sel_lag_yr = f1.selectbox("Highlight El Niño Year",
                              ["All"] + [str(y) for y in lag_years_available], key="t4_yr")
    lag_metric = f2.selectbox("Metric", ["Damage","Deaths","Events"], key="t4_metric")
    st.markdown('</div>', unsafe_allow_html=True)

    lag_rows = []
    for yr in ELNINO_YEARS:
        same = annual[annual["Year"]==yr][lag_metric].sum()
        nxt  = annual[annual["Year"]==yr+1][lag_metric].sum()
        lag_rows.append({"El Niño Year":int(yr), "Same Year (Y)":same, "Next Year (Y+1)":nxt})
    lag_df = pd.DataFrame(lag_rows)
    lag_df = lag_df[(lag_df["Same Year (Y)"]>0)|(lag_df["Next Year (Y+1)"]>0)]

    avg_same = lag_df["Same Year (Y)"].mean()
    avg_next = lag_df["Next Year (Y+1)"].mean()

    lag_unit = {"Damage":"M USD","Deaths":"deaths","Events":"events"}[lag_metric]
    m1,m2 = st.columns(2)
    m1.metric(f"Avg {lag_metric} — El Niño Year (Y)",    f"{avg_same:,.1f} {lag_unit}")
    m2.metric(f"Avg {lag_metric} — Following Year (Y+1)", f"{avg_next:,.1f} {lag_unit}")

    if avg_same > avg_next:
        st.info("📌 **Impact is IMMEDIATE** — strikes in the same year as El Niño.")
    else:
        st.warning("📌 **Impact is DELAYED** — greater effect appears the year after El Niño.")

    fig, ax = plt.subplots(figsize=(11, 4))
    x = np.arange(len(lag_df)); w = 0.35
    bar_colors_same = []
    bar_colors_next = []
    for _, row in lag_df.iterrows():
        hi = (sel_lag_yr != "All" and str(int(row["El Niño Year"]))==sel_lag_yr)
        bar_colors_same.append("#ff0080" if hi else "#7b2d8b")
        bar_colors_next.append("#ff8c00" if hi else "steelblue")

    for i, (cs, cn, row) in enumerate(zip(bar_colors_same, bar_colors_next, lag_df.itertuples())):
        ax.bar(i-w/2, row[2], w, color=cs, alpha=0.9)   # Same Year  (col index 1=El Niño Year, 2=Same Year (Y))
        ax.bar(i+w/2, row[3], w, color=cn, alpha=0.9)   # Next Year  (col index 3=Next Year (Y+1))

    ax.set_xticks(x)
    ax.set_xticklabels(lag_df["El Niño Year"].astype(int), rotation=45)
    ax.set_ylabel(f"{lag_metric} ({lag_unit})")
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(color="#7b2d8b", label="El Niño Year (Y)"),
        Patch(color="steelblue", label="Following Year (Y+1)"),
    ])
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

    if sel_lag_yr != "All":
        yr_int = int(sel_lag_yr)
        row_sel = lag_df[lag_df["El Niño Year"]==yr_int]
        if not row_sel.empty:
            st.markdown(f"**Selected year {yr_int} detail:**")
            d1, d2, d3 = st.columns(3)
            d1.metric("El Niño Year", yr_int)
            d2.metric(f"Same Year {lag_metric}", f"{row_sel['Same Year (Y)'].values[0]:,.1f}")
            d3.metric(f"Next Year {lag_metric}", f"{row_sel['Next Year (Y+1)'].values[0]:,.1f}")

    with st.expander("📋 Full lag table"):
        st.dataframe(lag_df.set_index("El Niño Year").round(1), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — GLOBAL  |  dropdown: select country/countries
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.subheader("El Niño Flood Pattern — Multi-Country View")

    @st.cache_data(show_spinner=False)
    def load_global(path):
        df = pd.read_csv(path, encoding="latin-1", low_memory=False)
        df.columns = df.columns.str.strip()
        df["Year"]     = pd.to_numeric(df["Start Year"], errors="coerce")
        df["Damage_M"] = pd.to_numeric(
            df.get("Total Damage, Adjusted ('000 US$)", pd.Series(dtype=float)),
            errors="coerce") / 1000
        df["Total Deaths"] = pd.to_numeric(df["Total Deaths"], errors="coerce")
        floods = df[df["Country"].isin(AFFECTED_COUNTRIES) &
                    (df["Disaster Type"]=="Flood")].copy()
        floods["ElNino"] = floods["Year"].isin(ELNINO_YEARS)
        return floods

    global_floods = load_global(EMDAT_CSV)

    # ── filter bar ────────────────────────────────────────────────────────────
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([3, 2, 1])
    sel_countries = f1.multiselect(
        "Select Countries", AFFECTED_COUNTRIES,
        default=AFFECTED_COUNTRIES, key="t5_countries")
    global_metric = f2.selectbox("Compare by",
        ["Damage_Ratio","Deaths_Ratio","Events_ElNino"], key="t5_metric")
    global_yr_range = f3.slider("Year filter",
        int(global_floods["Year"].min()), int(global_floods["Year"].max()),
        (int(global_floods["Year"].min()), int(global_floods["Year"].max())),
        key="t5_yr")
    st.markdown('</div>', unsafe_allow_html=True)

    if not sel_countries:
        st.warning("Select at least one country.")
        st.stop()

    gf_f = global_floods[
        global_floods["Country"].isin(sel_countries) &
        (global_floods["Year"]>=global_yr_range[0]) &
        (global_floods["Year"]<=global_yr_range[1])
    ]

    summary = gf_f.groupby(["Country","ElNino"]).agg(
        Events=("DisNo.","count"),
        Deaths=("Total Deaths","sum"),
        Damage=("Damage_M","sum"),
    ).reset_index()

    pivot = summary.pivot(index="Country", columns="ElNino",
                          values=["Events","Deaths","Damage"])
    pivot.columns = ["Events_Normal","Events_ElNino",
                     "Deaths_Normal","Deaths_ElNino",
                     "Damage_Normal","Damage_ElNino"]
    pivot = pivot.fillna(0)
    pivot["Damage_Ratio"] = (pivot["Damage_ElNino"] /
                              pivot["Damage_Normal"].replace(0,np.nan)).round(2)
    pivot["Deaths_Ratio"] = (pivot["Deaths_ElNino"] /
                              pivot["Deaths_Normal"].replace(0,np.nan)).round(2)
    pivot = pivot.sort_values(global_metric, ascending=False)

    metric_label_map = {
        "Damage_Ratio":    "Damage Ratio (El Niño / Normal)",
        "Deaths_Ratio":    "Deaths Ratio (El Niño / Normal)",
        "Events_ElNino":   "Flood Events during El Niño Years",
    }

    # ── KPIs for selected countries ───────────────────────────────────────────
    m1,m2,m3 = st.columns(3)
    m1.metric("Countries Selected",   len(sel_countries))
    m2.metric("Total Flood Events",   int(gf_f.shape[0]))
    m3.metric("Total Deaths",         f"{int(gf_f['Total Deaths'].sum()):,}")

    col_l, col_r = st.columns([1,1])

    with col_l:
        st.markdown(f"**{metric_label_map[global_metric]}**")
        valid = pivot[pivot[global_metric].notna()]
        fig, ax = plt.subplots(figsize=(6,max(3, len(valid)*0.45)))
        vals   = valid[global_metric].sort_values()
        colors = ["#d62728" if v>1 else "steelblue" for v in vals]
        ax.barh(vals.index, vals.values, color=colors, alpha=0.85)
        if "Ratio" in global_metric:
            ax.axvline(1, color="red", ls="--", lw=1.2, label="Ratio = 1")
            ax.legend(fontsize=8)
        ax.set_xlabel(metric_label_map[global_metric])
        ax.grid(axis="x", alpha=0.3)
        fig.tight_layout(); st.pyplot(fig); plt.close(fig)

    with col_r:
        st.markdown("**Country Detail Table**")
        show = pivot[["Events_Normal","Events_ElNino",
                      "Deaths_Normal","Deaths_ElNino",
                      "Damage_Normal","Damage_ElNino",
                      "Deaths_Ratio","Damage_Ratio"]].copy()
        show.columns = ["Events(N)","Events(EN)","Deaths(N)","Deaths(EN)",
                        "Damage(N) M$","Damage(EN) M$","Deaths Ratio","Damage Ratio"]
        st.dataframe(show.round(2), use_container_width=True)

    # ── single country deep-dive ──────────────────────────────────────────────
    st.markdown("---")
    dive_country = st.selectbox("🔍 Deep-dive into one country",
                                sel_countries, key="t5_dive")
    dive_df = gf_f[gf_f["Country"]==dive_country].groupby("Year").agg(
        Events=("DisNo.","count"),
        Deaths=("Total Deaths","sum"),
        Damage=("Damage_M","sum"),
    ).reset_index()
    dive_df["ElNino"] = dive_df["Year"].isin(ELNINO_YEARS)

    fig2, ax2 = plt.subplots(figsize=(11,3.5))
    ax2.bar(dive_df["Year"], dive_df["Damage"], color="steelblue", alpha=0.75, width=0.8)
    for yr in dive_df[dive_df["ElNino"]]["Year"]:
        ax2.axvline(yr, color="purple", alpha=0.25, linewidth=6)
    ax2.set_title(f"{dive_country} — Annual Flood Damage (M USD)  |  purple = El Niño")
    ax2.set_ylabel("Damage (M USD)")
    ax2.tick_params(axis="x",rotation=45)
    ax2.grid(axis="y",alpha=0.3)
    fig2.tight_layout(); st.pyplot(fig2); plt.close(fig2)


# ════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    "**AVALYOS Flood Risk Analysis** &nbsp;|&nbsp; "
    "Data: IMD District Rainfall Normals • EMDAT Global Disaster Database &nbsp;|&nbsp; "
    "Built with Streamlit")

    