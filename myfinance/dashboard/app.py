"""Dash app factory with RTL Hebrew layout."""

import dash
import dash_mantine_components as dmc
from dash import html

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

    app.layout = dmc.MantineProvider(
        theme={"fontFamily": "Assistant, Arial, sans-serif"},
        children=[
            html.Div(
                dir="rtl",
                style={"direction": "rtl", "textAlign": "right"},
                children=[
                    dmc.AppShell(
                        children=[
                            dmc.AppShellNavbar(sidebar_layout()),
                            dmc.AppShellMain(
                                children=[
                                    dmc.Tabs(
                                        id="main-tabs",
                                        value="overview",
                                        children=[
                                            dmc.TabsList([
                                                dmc.TabsTab("סקירה כללית", value="overview"),
                                                dmc.TabsTab("פירוט עסקאות", value="transactions"),
                                            ]),
                                            dmc.TabsPanel(overview_layout(), value="overview"),
                                            dmc.TabsPanel(transactions_layout(), value="transactions"),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                        navbar={"width": 280, "breakpoint": "sm"},
                        padding="md",
                    ),
                ],
            ),
        ],
    )

    register_callbacks(app)
    return app
