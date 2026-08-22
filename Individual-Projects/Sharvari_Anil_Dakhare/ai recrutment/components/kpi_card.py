import streamlit as st
from styles.theme import COLORS


def kpi_card(label: str, value: str, delta: str = "", icon: str = ""):
    """
    A single KPI tile. Use inside st.columns() for a row of metrics.

    delta: pass a string like "+12%" or "-3%"; color is inferred from sign.
    icon: accepts the 4th argument so Streamlit calls won't crash.
    """
    delta_html = ""
    if delta:
        is_negative = str(delta).strip().startswith("-")
        color = COLORS.get("danger", "#EF4444") if is_negative else COLORS.get("success", "#10B981")
        delta_html = f'<div class="kpi-delta" style="color:{color}">{delta} vs last month</div>'

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )