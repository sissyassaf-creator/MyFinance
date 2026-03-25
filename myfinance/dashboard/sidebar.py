"""Dashboard sidebar: process button, stats, export."""

import dash_mantine_components as dmc
from dash import html


def sidebar_layout():
    return dmc.Stack(
        gap="md",
        p="md",
        children=[
            dmc.Title("MyFinance", order=3),
            dmc.Text("הכספים שלך, במחשב שלך", size="sm", c="dimmed"),

            dmc.Divider(),

            dmc.Button(
                "עבד קבצים חדשים",
                id="btn-process",
                fullWidth=True,
                variant="filled",
                color="blue",
            ),
            html.Div(id="process-output"),

            dmc.Divider(),

            dmc.Text("סטטיסטיקות", fw=700, size="sm"),
            html.Div(id="sidebar-stats", children=[
                dmc.Text("ריצה אחרונה: —", size="xs", id="stat-last-run"),
                dmc.Text("סה״כ עסקאות: 0", size="xs", id="stat-total"),
                dmc.Text("ממתינים לבדיקה: 0", size="xs", id="stat-pending", c="red"),
            ]),

            dmc.Divider(),

            dmc.Button(
                "ייצוא Excel",
                id="btn-export",
                fullWidth=True,
                variant="outline",
                color="green",
            ),
            html.Div(id="export-output"),
        ],
    )
