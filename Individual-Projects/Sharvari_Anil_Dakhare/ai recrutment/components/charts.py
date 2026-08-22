import plotly.graph_objects as go
import plotly.express as px
from styles.theme import COLORS

CHART_FONT = "Inter, sans-serif"


def _base_layout(fig, height=320):
    fig.update_layout(
        font=dict(family=CHART_FONT, color=COLORS["text_primary"], size=13),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def hiring_trend_chart(months, applications, hires):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=applications, mode="lines", name="Applications",
        line=dict(color=COLORS["primary"], width=3, shape="spline"),
        fill="tozeroy", fillcolor="rgba(108, 99, 255, 0.08)",
    ))
    fig.add_trace(go.Scatter(
        x=months, y=hires, mode="lines", name="Hires",
        line=dict(color=COLORS["success"], width=3, shape="spline"),
    ))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=COLORS["border"])
    return _base_layout(fig)


def recruitment_funnel_chart(stages, values):
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        marker=dict(color=[COLORS["primary"], "#8B85FF", "#A9A4FF", "#C7C3FF", COLORS["success"]][:len(stages)]),
        textinfo="value+percent initial",
    ))
    return _base_layout(fig, height=340)


def gauge_chart(value, title="Score", max_value=100):
    color = COLORS["success"] if value >= 80 else COLORS["warning"] if value >= 60 else COLORS["danger"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14}},
        gauge={
            "axis": {"range": [0, max_value], "tickcolor": COLORS["text_secondary"]},
            "bar": {"color": color},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0, max_value * 0.6], "color": "#F1F5F9"},
                {"range": [max_value * 0.6, max_value * 0.8], "color": "#E2E8F0"},
            ],
        },
    ))
    return _base_layout(fig, height=220)


def monthly_report_chart(months, applications, offers, hires):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=applications, name="Applications", marker_color="#C7C3FF"))
    fig.add_trace(go.Bar(x=months, y=offers, name="Offers", marker_color=COLORS["primary"]))
    fig.add_trace(go.Bar(x=months, y=hires, name="Hires", marker_color=COLORS["success"]))
    fig.update_layout(barmode="group")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=COLORS["border"])
    return _base_layout(fig, height=320)


def department_hiring_chart(departments, counts):
    fig = px.bar(
        x=counts, y=departments, orientation="h",
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_xaxes(showgrid=True, gridcolor=COLORS["border"], title=None)
    fig.update_yaxes(showgrid=False, title=None)
    return _base_layout(fig, height=300)
