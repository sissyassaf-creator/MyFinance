"""Dash app factory with RTL Hebrew layout."""

import dash
from dash import dcc, html

from myfinance.dashboard.callbacks import register_callbacks
from myfinance.dashboard.sidebar import sidebar_layout
from myfinance.dashboard.tab_overview import overview_layout
from myfinance.dashboard.tab_transactions import transactions_layout


def create_app() -> dash.Dash:
    app = dash.Dash(
        __name__,
        title="MyFinance — הכספים שלך",
        suppress_callback_exceptions=True,
    )

    app.layout = html.Div(
        dir="rtl",
        style={
            "direction": "rtl",
            "textAlign": "right",
            "fontFamily": "Assistant, Arial, sans-serif",
            "display": "flex",
            "minHeight": "100vh",
            "backgroundColor": "#f8f9fa",
        },
        children=[
            # Sidebar
            html.Div(
                style={
                    "width": "280px",
                    "minWidth": "280px",
                    "backgroundColor": "white",
                    "borderLeft": "1px solid #dee2e6",
                    "padding": "20px",
                    "overflowY": "auto",
                },
                children=[sidebar_layout()],
            ),
            # Main content
            html.Div(
                style={
                    "flex": "1",
                    "padding": "24px",
                    "overflowY": "auto",
                },
                children=[
                    dcc.Tabs(
                        id="main-tabs",
                        value="overview",
                        style={"direction": "rtl"},
                        children=[
                            dcc.Tab(
                                label="סקירה כללית",
                                value="overview",
                                style={"fontFamily": "Assistant, Arial, sans-serif"},
                                selected_style={"fontFamily": "Assistant, Arial, sans-serif", "fontWeight": "bold"},
                            ),
                            dcc.Tab(
                                label="פירוט עסקאות",
                                value="transactions",
                                style={"fontFamily": "Assistant, Arial, sans-serif"},
                                selected_style={"fontFamily": "Assistant, Arial, sans-serif", "fontWeight": "bold"},
                            ),
                        ],
                    ),
                    html.Div(id="tab-content", style={"marginTop": "16px"}),
                ],
            ),
        ],
    )

    register_callbacks(app)
    return app
