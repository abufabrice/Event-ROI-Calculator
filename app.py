# app.py
import math
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ------------------------
# THEME & GLOBALS
# ------------------------
PRIMARY = "#0F6938"
ACCENT = "#111111"
BG = "#0B1A12"
CARD_BG = "rgba(255,255,255,0.85)"

st.set_page_config(
    page_title="Scino360 • Event ROI Calculator",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for ultra-modern look
st.markdown(f"""
<style>
/* Base */
html, body, [class*="css"]  {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
}}
/* Gradient header band */
.header {{
  background: linear-gradient(135deg, {PRIMARY} 0%, #0B3F22 60%, #062413 100%);
  padding: 28px 24px;
  border-radius: 18px;
  color: #FFFFFF;
  margin-bottom: 22px;
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 10px 28px rgba(0,0,0,0.18);
}}
.header h1 {{
  margin: 0 0 6px 0;
  font-weight: 750;
  letter-spacing: -0.2px;
}}
.header p {{
  margin: 0;
  opacity: 0.92;
}}
/* Metric cards */
.card {{
  background: {CARD_BG};
  backdrop-filter: blur(6px);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 16px;
  padding: 18px 18px 12px 18px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.08);
}}
.kpi-title {{
  font-size: 12px; 
  text-transform: uppercase; 
  letter-spacing: .12em; 
  color: #666; 
  margin-bottom: 4px;
}}
.kpi-value {{
  font-size: 28px; 
  font-weight: 800; 
  color: {ACCENT};
}}
.kpi-sub {{
  font-size: 12px; 
  color: #777; 
  margin-top: 4px;
}}
/* Section titles */
h3.section {{
  margin-top: 10px; 
  margin-bottom: 8px; 
  font-weight: 800;
}}
/* Inputs look */
.block-container {{
  padding-top: 18px;
}}
/* Hide deploy footer */
footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ------------------------
# HEADER
# ------------------------
st.markdown("""
<div class="header">
  <h1>Scino360 • Event ROI Calculator</h1>
  <p>From business card to big contract. Quantify the revenue you recover when every event lead is captured, assigned, and followed up with ROI‑backed messaging.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------
# SIDEBAR INPUTS
# ------------------------
with st.sidebar:
    st.markdown("### Inputs")
    leads = st.number_input("Leads collected at event", min_value=1, step=1, value=150)
    event_spend = st.number_input("Event spend (₣)", min_value=0.0, step=100000.0, value=1_800_000.0, format="%.0f")
    deal_value = st.number_input("Average deal value (₣)", min_value=1.0, step=500000.0, value=18_000_000.0, format="%.0f")

    st.markdown("---")
    st.markdown("#### Admin Access")
    admin_key = st.text_input("Admin key (optional)", type="password")
    is_admin = admin_key.strip() == st.secrets.get("ADMIN_KEY", "scino360")

# ------------------------
# DEFAULT / ADMIN SETTINGS
# ------------------------
# Baseline assumptions (typical without Scino360)
baseline_followup_rate = 0.30     # portion of leads actually worked
baseline_close_rate    = 0.05     # close rate on worked leads
lost_unassigned_rate   = 0.40     # never captured/assigned
dormant_rate           = 0.30     # captured but dormant

# With-Scino assumptions (admin-adjustable)
scino_followup_rate = 1.00        # all leads captured & worked
scino_close_rate    = 0.15        # improved close rate via ROI follow-ups
scino_cost          = 10_000_000  # default cost (₣) for an event program
resp_time_hours     = 24          # target response time

if is_admin:
    st.sidebar.markdown("### Admin Settings")
    cols = st.sidebar.columns(2)
    with cols[0]:
        baseline_followup_rate = st.slider("Baseline follow-up rate", 0.0, 1.0, baseline_followup_rate, 0.05)
        baseline_close_rate = st.slider("Baseline close rate", 0.0, 1.0, baseline_close_rate, 0.01)
        lost_unassigned_rate = st.slider("Lost/unassigned leads", 0.0, 1.0, lost_unassigned_rate, 0.05)
    with cols[1]:
        dormant_rate = st.slider("Dormant leads (captured, not worked)", 0.0, 1.0, dormant_rate, 0.05)
        scino_followup_rate = st.slider("Scino follow-up rate", 0.0, 1.0, scino_followup_rate, 0.01)
        scino_close_rate = st.slider("Scino close rate", 0.0, 1.0, scino_close_rate, 0.01)

    st.sidebar.markdown("#### Commercials")
    scino_cost = st.number_input("Scino360 program cost (₣)", min_value=0.0, step=500000.0, value=float(scino_cost), format="%.0f")
    resp_time_hours = st.slider("Target response time (hours)", 1, 72, resp_time_hours)

# ------------------------
# CALCULATIONS
# ------------------------
cost_per_lead = event_spend / leads

# Baseline (without Scino360)
worked_leads_base = round(leads * baseline_followup_rate)
closed_deals_base = round(worked_leads_base * baseline_close_rate)
revenue_base = closed_deals_base * deal_value

# With Scino360
worked_leads_scino = round(leads * scino_followup_rate)
closed_deals_scino = round(worked_leads_scino * scino_close_rate)
revenue_scino = closed_deals_scino * deal_value

incremental_gain = revenue_scino - revenue_base
roi_multiple = (incremental_gain - scino_cost) / scino_cost if scino_cost > 0 else np.nan

# Value recovered from "hidden" leads (simple illustration)
unassigned_leads = round(leads * lost_unassigned_rate)
recovered_lead_value = unassigned_leads * cost_per_lead

# ------------------------
# TOP KPI STRIP
# ------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="card"><div class="kpi-title">Cost per Lead</div>'
                f'<div class="kpi-value">₣{cost_per_lead:,.0f}</div>'
                '<div class="kpi-sub">Event spend / Leads</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="card"><div class="kpi-title">Baseline Revenue</div>'
                f'<div class="kpi-value">₣{revenue_base:,.0f}</div>'
                f'<div class="kpi-sub">{closed_deals_base} deals at baseline rates</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="card"><div class="kpi-title">With Scino360</div>'
                f'<div class="kpi-value">₣{revenue_scino:,.0f}</div>'
                f'<div class="kpi-sub">{closed_deals_scino} deals at improved rates</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="card"><div class="kpi-title">Incremental Gain</div>'
                f'<div class="kpi-value" style="color:{PRIMARY}">₣{incremental_gain:,.0f}</div>'
                f'<div class="kpi-sub">Recovered by value‑intelligent follow‑ups</div></div>', unsafe_allow_html=True)

st.markdown("")

# ------------------------
# FUNNEL COMPARISON
# ------------------------
def funnel_fig(leads_total, worked, closed, title):
    contacted = worked
    stages = ["Leads Collected", "Worked/Followed Up", "Closed Deals"]
    values = [leads_total, contacted, closed]
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent previous",
        marker={"color": [PRIMARY, "#2D9F6F", "#60B98C"]}
    ))
    fig.update_layout(
        title=title,
        height=420,
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Inter", size=13)
    )
    return fig

l, r = st.columns(2)
with l:
    st.markdown("### Baseline Funnel")
    st.plotly_chart(
        funnel_fig(leads, worked_leads_base, closed_deals_base, "Without Scino360"),
        use_container_width=True
    )
with r:
    st.markdown("### Scino360 Funnel")
    st.plotly_chart(
        funnel_fig(leads, worked_leads_scino, closed_deals_scino, "With Scino360"),
        use_container_width=True
    )

# ------------------------
# VALUE HIGHLIGHTS
# ------------------------
st.markdown("### Value Highlights")
vh1, vh2, vh3 = st.columns(3)
with vh1:
    st.markdown(f'<div class="card"><div class="kpi-title">Hidden Leads Recovered</div>'
                f'<div class="kpi-value">{unassigned_leads:,}</div>'
                f'<div class="kpi-sub">Worth ₣{recovered_lead_value:,.0f} in 48 hours</div></div>', unsafe_allow_html=True)
with vh2:
    st.markdown(f'<div class="card"><div class="kpi-title">Response Time Target</div>'
                f'<div class="kpi-value">{resp_time_hours} hrs</div>'
                f'<div class="kpi-sub">Faster follow‑ups protect conversion</div></div>', unsafe_allow_html=True)
with vh3:
    roi_txt = "—" if math.isnan(roi_multiple) else f"{roi_multiple:,.2f}×"
    st.markdown(f'<div class="card"><div class="kpi-title">ROI Multiple (after cost)</div>'
                f'<div class="kpi-value">{roi_txt}</div>'
                f'<div class="kpi-sub">Incremental gain minus cost / cost</div></div>', unsafe_allow_html=True)

# ------------------------
# TABLE SUMMARY
# ------------------------
st.markdown("### Summary")
df = pd.DataFrame({
    "Metric": ["Leads", "Event Spend (₣)", "Avg Deal Value (₣)",
               "Worked Leads (Baseline)", "Closed Deals (Baseline)", "Revenue (Baseline)",
               "Worked Leads (Scino360)", "Closed Deals (Scino360)", "Revenue (Scino360)",
               "Incremental Gain", "Hidden Leads Recovered", "Recovered Lead Value (₣)"],
    "Value": [leads, event_spend, deal_value,
              worked_leads_base, closed_deals_base, revenue_base,
              worked_leads_scino, closed_deals_scino, revenue_scino,
              incremental_gain, unassigned_leads, recovered_lead_value]
})
st.dataframe(df, use_container_width=True)

st.markdown("---")
st.caption("Assumptions are illustrative. Adjust in Admin Settings to match your market and vertical playbooks.")
