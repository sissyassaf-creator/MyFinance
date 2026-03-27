"""Tab 2: פירוט עסקאות — Transaction table with filters and inline editing."""

import dash_ag_grid as dag
from dash import html, dcc

from myfinance.config import CATEGORIES, SOURCES


def transactions_layout():
    return html.Div([
        # Filter bar
        html.Div(
            style={
                "backgroundColor": "white", "borderRadius": "8px", "padding": "16px",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "marginBottom": "16px",
            },
            children=[
                html.H4("מסננים", style={"margin": "0 0 12px 0"}),
                html.Div(
                    style={"display": "flex", "gap": "12px", "alignItems": "flex-end", "flexWrap": "wrap"},
                    children=[
                        html.Div([
                            html.Label("חודש", style={"fontSize": "13px", "display": "block", "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="filter-month",
                                placeholder="כל החודשים",
                                clearable=True,
                                style={"width": "150px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("קטגוריה", style={"fontSize": "13px", "display": "block", "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="filter-category",
                                options=[{"value": c, "label": c} for c in CATEGORIES],
                                placeholder="הכל",
                                multi=True,
                                style={"width": "250px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("מקור", style={"fontSize": "13px", "display": "block", "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="filter-source",
                                options=[{"value": k, "label": v} for k, v in SOURCES.items()],
                                placeholder="הכל",
                                multi=True,
                                style={"width": "200px"},
                            ),
                        ]),
                        html.Div([
                            dcc.Checklist(
                                id="filter-pending",
                                options=[{"value": "pending", "label": "ממתינים בלבד"}],
                                value=[],
                                style={"marginBottom": "6px"},
                            ),
                        ]),
                        html.Button(
                            "נקה מסננים",
                            id="btn-clear-filters",
                            style={
                                "padding": "8px 16px", "backgroundColor": "#f1f3f5",
                                "border": "1px solid #dee2e6", "borderRadius": "4px",
                                "cursor": "pointer", "fontSize": "13px",
                            },
                        ),
                    ],
                ),
            ],
        ),

        # Transactions table
        html.Div(
            style={
                "backgroundColor": "white", "borderRadius": "8px", "padding": "16px",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
            },
            children=[
                dag.AgGrid(
                    id="transactions-grid",
                    columnDefs=_column_defs(),
                    rowData=[],
                    defaultColDef={
                        "sortable": True,
                        "filter": True,
                        "resizable": True,
                    },
                    dashGridOptions={
                        "enableRtl": True,
                        "pagination": True,
                        "paginationPageSize": 50,
                        "animateRows": True,
                    },
                    style={"height": "600px"},
                    getRowStyle={
                        "styleConditions": [
                            {
                                "condition": "params.data.needs_review === 1",
                                "style": {"backgroundColor": "#FFF9C4"},
                            },
                        ],
                    },
                ),
            ],
        ),
    ])


def _column_defs():
    return [
        {
            "field": "date",
            "headerName": "תאריך",
            "width": 120,
        },
        {
            "field": "merchant",
            "headerName": "בית עסק",
            "width": 220,
            "filter": "agTextColumnFilter",
        },
        {
            "field": "amount_ils",
            "headerName": "סכום (₪)",
            "width": 120,
            "type": "numericColumn",
            "valueFormatter": {"function": "Number(params.value).toLocaleString('he-IL', {minimumFractionDigits: 2})"},
        },
        {
            "field": "category",
            "headerName": "קטגוריה",
            "width": 170,
            "editable": True,
            "cellEditor": "agSelectCellEditor",
            "cellEditorParams": {"values": CATEGORIES},
        },
        {
            "field": "source",
            "headerName": "מקור",
            "width": 130,
        },
        {
            "field": "payment_method",
            "headerName": "תשלום",
            "width": 100,
        },
        {
            "field": "needs_review",
            "headerName": "סטטוס",
            "width": 80,
            "valueFormatter": {"function": "params.value === 1 ? '⚠️' : '✓'"},
        },
        {
            "field": "transaction_id",
            "hide": True,
        },
    ]
