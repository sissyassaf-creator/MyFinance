"""Tab 1: סקירה כללית — Monthly overview with charts and stats."""

from dash import dcc, html


def overview_layout():
    return html.Div([
        # Stats cards
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "24px"},
            children=[
                _stat_card("סה״כ הוצאות", "₪0", "stat-total-spend"),
                _stat_card("עסקאות", "0", "stat-txn-count"),
                _stat_card("ממתינים לבדיקה", "0", "stat-pending-count"),
            ],
        ),

        # Charts row
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "24px"},
            children=[
                html.Div(
                    style={"flex": "1", "backgroundColor": "white", "borderRadius": "8px",
                           "padding": "16px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"},
                    children=[
                        html.H4("התפלגות לפי קטגוריה", style={"margin": "0 0 8px 0"}),
                        dcc.Graph(id="pie-chart", config={"displayModeBar": False},
                                  style={"height": "350px"}),
                    ],
                ),
                html.Div(
                    style={"flex": "1", "backgroundColor": "white", "borderRadius": "8px",
                           "padding": "16px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"},
                    children=[
                        html.H4("הוצאות לפי קטגוריה", style={"margin": "0 0 8px 0"}),
                        dcc.Graph(id="bar-chart", config={"displayModeBar": False},
                                  style={"height": "350px"}),
                    ],
                ),
            ],
        ),

        # Top merchants
        html.Div(
            style={"backgroundColor": "white", "borderRadius": "8px", "padding": "16px",
                   "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "marginBottom": "24px"},
            children=[
                html.H4("5 בתי עסק מובילים", style={"margin": "0 0 12px 0"}),
                html.Div(id="top-merchants-table"),
            ],
        ),

        # Savings alerts
        html.Div(
            id="savings-alerts-container",
            style={"backgroundColor": "white", "borderRadius": "8px", "padding": "16px",
                   "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"},
            children=[
                html.H4("הצעות חיסכון", style={"margin": "0 0 12px 0"}),
                html.Div(id="savings-alerts"),
            ],
        ),
    ])


def _stat_card(label, value, card_id):
    return html.Div(
        style={
            "flex": "1", "backgroundColor": "white", "borderRadius": "8px",
            "padding": "16px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
        },
        children=[
            html.P(label, style={"color": "#888", "fontSize": "14px", "margin": "0 0 4px 0"}),
            html.P(value, id=card_id, style={"fontSize": "24px", "fontWeight": "bold", "margin": "0"}),
        ],
    )
