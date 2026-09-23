"""Morning charts use measured values, explicit units and unfilled date gaps."""
from datetime import date
from html import escape
import plotly.graph_objects as go
from analytics.market import history_frame, snapshot, seasonal_reference, valid_value

BLUE = "#2563EB"
AMBER = "#D97706"
TEAL = "#0F766E"
PURPLE = "#7C3AED"

STYLE = """
<style>
.morning-hero{background:linear-gradient(110deg,#102b49,#174e67);color:#fff;border-radius:18px;padding:22px 26px;margin:0 0 20px}
.morning-hero .eyebrow{font-size:11px;letter-spacing:2px;color:#a9d8e6;font-weight:700}
.morning-hero h2{font-size:29px;line-height:1.2;color:#fff;margin:8px 0}
.morning-hero p{color:#d4e6ef;margin:0;font-size:14px}
.morning-card{background:var(--secondary-background-color,#fff);border:1px solid #bfd0df;border-top:4px solid var(--accent);border-radius:13px;padding:15px 18px;min-height:178px}
.morning-card .label{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--text-color,#334155);font-weight:700}
.morning-card .value{font-size:31px;font-weight:750;line-height:1.2;margin:8px 0;color:var(--text-color,#14283f)}
.morning-card .unit{font-size:14px;font-weight:400}
.morning-card .move{font-size:13px;font-weight:700;color:var(--move)}
.morning-card .meta{font-size:11px;line-height:1.5;margin-top:7px;color:var(--text-color,#475569);opacity:.85}
.morning-note{padding:10px 14px;border-left:4px solid #94a3b8;background:var(--secondary-background-color,#edf2f7);border-radius:5px;font-size:13px;margin:5px 0 10px}
@media(max-width:700px){.morning-hero{padding:18px}.morning-hero h2{font-size:24px}.morning-card .value{font-size:27px}}
</style>
"""


def card_html(label, value, unit, delta, delta_unit, meta, accent=BLUE):
    shown = "—" if value is None else f"{value:,.2f}"
    direction = "↑" if delta is not None and delta > 0 else "↓" if delta is not None and delta < 0 else "→"
    change = "Comparaison J−1 indisponible" if delta is None else f"{direction} {delta:+,.2f} {delta_unit} vs J−1"
    color = BLUE if delta is not None and delta > 0 else AMBER if delta is not None and delta < 0 else "#64748B"
    return f'<div class="morning-card" style="--accent:{accent};--move:{color}"><div class="label">{escape(label)}</div><div class="value">{shown} <span class="unit">{escape(unit)}</span></div><div class="move">{escape(change)}</div><div class="meta">{escape(meta)}</div></div>'


def spark_figure(rows, metric, color=BLUE, bars=False, days=30):
    frame = history_frame(rows, metric).tail(days)
    fig = go.Figure()
    if not frame.empty:
        if bars:
            colors = [BLUE if v is not None and v >= 0 else AMBER for v in frame.value]
            fig.add_bar(x=frame.date, y=frame.value, marker_color=colors)
        else:
            fig.add_scatter(x=frame.date, y=frame.value, mode="lines", connectgaps=False,
                            line=dict(color=color, width=2.5))
        fig.update_traces(hovertemplate="%{x|%d/%m/%Y}<br>%{y:.2f}<extra></extra>")
    fig.update_layout(height=85, margin=dict(l=0, r=0, t=8, b=0), showlegend=False,
                      xaxis=dict(visible=False), yaxis=dict(visible=False),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def storage_figure(rows):
    latest = snapshot(rows, "storage_full")
    fig = go.Figure()
    if latest["date"]:
        day = date.fromisoformat(latest["date"])
        frame = history_frame(rows, "storage_full")
        frame = frame[frame.date.dt.year == day.year]
        refs = [seasonal_reference(rows, "storage_full", value.date()) for value in frame.date]
        last_year = [seasonal_reference(rows, "storage_full", value.date(), years=1)["mean"] for value in frame.date]
        fig.add_scatter(x=frame.date, y=[r["max"] for r in refs], line=dict(width=0), showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=frame.date, y=[r["min"] for r in refs], line=dict(width=0), fill="tonexty",
                        fillcolor="rgba(37,99,235,.10)", name="Fourchette 5 ans", hoverinfo="skip")
        fig.add_scatter(x=frame.date, y=[r["mean"] for r in refs], line=dict(color="#94A3B8", dash="dot"), name="Moyenne 5 ans")
        fig.add_scatter(x=frame.date, y=last_year, line=dict(color=AMBER, dash="dash"), name=str(day.year - 1))
        fig.add_scatter(x=frame.date, y=frame.value, line=dict(color=BLUE, width=3), name=str(day.year))
        fig.update_traces(connectgaps=False)
    fig.update_layout(height=320, margin=dict(l=0, r=5, t=12, b=5), yaxis=dict(title="Remplissage (%)", range=[0, 100]),
                      xaxis=dict(tickformat="%b"), legend=dict(orientation="h", y=1.12), hovermode="x unified")
    return fig


def flow_figure(rows, metric, label, color, days=45):
    frame = history_frame(rows, metric).tail(days)
    fig = go.Figure()
    if not frame.empty:
        fig.add_bar(x=frame.date, y=frame.value, marker_color=color, name=label,
                    hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.0f} GWh/j<extra></extra>")
    fig.update_layout(height=230, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="GWh/j", showlegend=False,
                      xaxis=dict(tickformat="%d %b"))
    return fig


def weather_figure(rows):
    fig = go.Figure()
    if rows:
        ordered = sorted(rows, key=lambda r: r["observation_date"])
        values = [valid_value(r) for r in ordered]
        fig.add_bar(x=[r["observation_date"] for r in ordered], y=values,
                    marker_color=[BLUE if v is not None and v < 18 else AMBER for v in values],
                    hovertemplate="%{x}<br>%{y:.1f} °C<extra></extra>")
        fig.add_hline(y=18, line_dash="dot", line_color="#64748B", annotation_text="Base HDD 18°C")
    fig.update_layout(height=230, margin=dict(l=0, r=0, t=20, b=0), yaxis_title="Température moyenne (°C)",
                      xaxis=dict(tickformat="%d %b"), showlegend=False)
    return fig
