"""Dashboard sidebar: process button, stats, export."""

from dash import html, dcc


def sidebar_layout():
    return html.Div([
        html.H3("MyFinance", style={"margin": "0 0 4px 0"}),
        html.P("הכספים שלך, במחשב שלך", style={"color": "#888", "fontSize": "14px", "margin": "0 0 16px 0"}),

        html.Hr(),

        html.Button(
            "עבד קבצים חדשים",
            id="btn-process",
            style={
                "width": "100%", "padding": "10px", "backgroundColor": "#228be6",
                "color": "white", "border": "none", "borderRadius": "6px",
                "cursor": "pointer", "fontSize": "14px", "marginBottom": "8px",
            },
        ),
        html.Div(id="process-output"),

        html.Hr(),

        html.P("סטטיסטיקות", style={"fontWeight": "bold", "fontSize": "14px", "marginBottom": "8px"}),
        html.P("ריצה אחרונה: —", id="stat-last-run", style={"fontSize": "13px", "margin": "4px 0"}),
        html.P("סה״כ עסקאות: 0", id="stat-total", style={"fontSize": "13px", "margin": "4px 0"}),
        html.P("ממתינים לבדיקה: 0", id="stat-pending", style={"fontSize": "13px", "margin": "4px 0", "color": "red"}),

        html.Hr(),

        html.Button(
            "ייצוא Excel",
            id="btn-export",
            style={
                "width": "100%", "padding": "10px", "backgroundColor": "white",
                "color": "#40c057", "border": "2px solid #40c057", "borderRadius": "6px",
                "cursor": "pointer", "fontSize": "14px",
            },
        ),
        html.Div(id="export-output"),
    ])
