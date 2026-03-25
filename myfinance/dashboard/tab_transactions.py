"""Tab 2: פירוט עסקאות — Transaction table with filters and inline editing."""

import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import html

from myfinance.config import CATEGORIES, SOURCES


def transactions_layout():
    return dmc.Stack(
        gap="md",
        p="md",
        children=[
            # Filter bar
            dmc.Paper(
                p="md",
                shadow="sm",
                children=[
                    dmc.Text("מסננים", fw=700, mb="sm"),
                    dmc.Group(
                        gap="md",
                        children=[
                            dmc.Select(
                                id="filter-month",
                                label="חודש",
                                placeholder="כל החודשים",
                                clearable=True,
                                data=[],  # Populated by callback
                                style={"width": 150},
                            ),
                            dmc.MultiSelect(
                                id="filter-category",
                                label="קטגוריה",
                                placeholder="הכל",
                                data=[{"value": c, "label": c} for c in CATEGORIES],
                                style={"width": 250},
                            ),
                            dmc.MultiSelect(
                                id="filter-source",
                                label="מקור",
                                placeholder="הכל",
                                data=[
                                    {"value": k, "label": v}
                                    for k, v in SOURCES.items()
                                ],
                                style={"width": 200},
                            ),
                            dmc.Checkbox(
                                id="filter-pending",
                                label="ממתינים בלבד",
                            ),
                            dmc.Button(
                                "נקה מסננים",
                                id="btn-clear-filters",
                                variant="subtle",
                                size="sm",
                            ),
                        ],
                    ),
                ],
            ),

            # Transactions table
            dmc.Paper(
                p="md",
                shadow="sm",
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
                            "rowSelection": "single",
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
        ],
    )


def _column_defs():
    return [
        {
            "field": "date",
            "headerName": "תאריך",
            "width": 120,
            "valueFormatter": {"function": "d3.timeFormat('%d/%m/%Y')(new Date(params.value))"},
        },
        {
            "field": "merchant",
            "headerName": "בית עסק",
            "width": 200,
            "filter": "agTextColumnFilter",
        },
        {
            "field": "amount_ils",
            "headerName": "סכום (₪)",
            "width": 120,
            "type": "numericColumn",
            "valueFormatter": {"function": "Number(params.value).toLocaleString('he-IL', {style: 'currency', currency: 'ILS'})"},
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
            "valueFormatter": {"function": _source_formatter()},
        },
        {
            "field": "payment_method",
            "headerName": "תשלום",
            "width": 110,
            "valueFormatter": {"function": _payment_formatter()},
        },
        {
            "field": "installment_info",
            "headerName": "תשלומים",
            "width": 100,
            "valueGetter": {"function": _installment_getter()},
        },
        {
            "field": "needs_review",
            "headerName": "לבדיקה",
            "width": 80,
            "valueFormatter": {"function": "params.value === 1 ? '⚠️' : '✓'"},
        },
        {
            "field": "transaction_id",
            "hide": True,
        },
    ]


def _source_formatter():
    return """
    function(params) {
        const map = {'visa-mizrahi': 'ויזה מזרחי', 'diners-el-al': 'דיינרס', 'max': 'מקס'};
        return map[params.value] || params.value;
    }
    """


def _payment_formatter():
    return """
    function(params) {
        const map = {'regular': 'רגיל', 'installments': 'תשלומים', 'immediate_debit': 'מיידי'};
        return map[params.value] || params.value;
    }
    """


def _installment_getter():
    return """
    function(params) {
        if (params.data.installment_number && params.data.installments_total) {
            return params.data.installment_number + '/' + params.data.installments_total;
        }
        return '';
    }
    """
