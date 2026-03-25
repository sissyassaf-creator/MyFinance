"""Tab 1: סקירה כללית — Monthly overview with charts and stats."""

import dash_mantine_components as dmc
from dash import dcc, html


def overview_layout():
    return dmc.Stack(
        gap="lg",
        p="md",
        children=[
            # Stats cards row
            dmc.Group(
                gap="md",
                id="overview-stats-group",
                children=[
                    _stat_card("סה״כ הוצאות", "₪0", "stat-total-spend", "blue"),
                    _stat_card("עסקאות", "0", "stat-txn-count", "teal"),
                    _stat_card("ממתינים לבדיקה", "0", "stat-pending-count", "red"),
                ],
            ),

            # Charts row
            dmc.Grid(
                children=[
                    dmc.GridCol(
                        span=6,
                        children=[
                            dmc.Paper(
                                p="md",
                                shadow="sm",
                                children=[
                                    dmc.Text("התפלגות לפי קטגוריה", fw=700, mb="sm"),
                                    dcc.Graph(id="pie-chart", config={"displayModeBar": False}),
                                ],
                            ),
                        ],
                    ),
                    dmc.GridCol(
                        span=6,
                        children=[
                            dmc.Paper(
                                p="md",
                                shadow="sm",
                                children=[
                                    dmc.Text("הוצאות לפי קטגוריה", fw=700, mb="sm"),
                                    dcc.Graph(id="bar-chart", config={"displayModeBar": False}),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # Top merchants
            dmc.Paper(
                p="md",
                shadow="sm",
                children=[
                    dmc.Text("5 בתי עסק מובילים", fw=700, mb="sm"),
                    html.Div(id="top-merchants-table"),
                ],
            ),

            # Savings alerts
            dmc.Paper(
                p="md",
                shadow="sm",
                id="savings-alerts-container",
                children=[
                    dmc.Text("הצעות חיסכון", fw=700, mb="sm"),
                    html.Div(id="savings-alerts"),
                ],
            ),
        ],
    )


def _stat_card(label: str, value: str, card_id: str, color: str):
    return dmc.Paper(
        p="md",
        shadow="sm",
        style={"flex": 1, "minWidth": 150},
        children=[
            dmc.Text(label, size="sm", c="dimmed"),
            dmc.Text(value, size="xl", fw=700, id=card_id),
        ],
    )
