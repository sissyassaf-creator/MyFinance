"""All Dash callbacks — processing, filtering, chart updates, category editing."""

from datetime import datetime

import dash
import plotly.express as px
from dash import Input, Output, State, callback_context, html, no_update
import dash_mantine_components as dmc

from myfinance.config import CATEGORIES, SOURCES, UNRECOGNIZED_CATEGORY
from myfinance.db import (
    get_connection,
    get_stats,
    get_transactions,
    update_transaction_category,
    upsert_merchant_map,
)
from myfinance.processing.categorizer import normalize_merchant


def register_callbacks(app: dash.Dash):
    """Register all callbacks on the app."""

    # ── Sidebar stats (on load + after processing) ─────
    @app.callback(
        [
            Output("stat-last-run", "children"),
            Output("stat-total", "children"),
            Output("stat-pending", "children"),
        ],
        Input("main-tabs", "value"),
        Input("process-output", "children"),
    )
    def update_sidebar_stats(_tab, _process_result):
        conn = get_connection()
        stats = get_stats(conn)
        conn.close()
        last_run = stats['last_run'] or '—'
        return (
            f"ריצה אחרונה: {last_run}",
            f"סה״כ עסקאות: {stats['total_transactions']}",
            f"ממתינים לבדיקה: {stats['pending_review']}",
        )

    # ── Process files button ───────────────────────────
    @app.callback(
        Output("process-output", "children"),
        Input("btn-process", "n_clicks"),
        prevent_initial_call=True,
    )
    def process_files(n_clicks):
        if not n_clicks:
            return no_update

        from myfinance.db import backup_db, init_db
        from myfinance.processing.pipeline import run_pipeline

        init_db()
        backup_db()
        result = run_pipeline()

        alerts_text = ""
        if result.get('savings_alerts'):
            alerts_text = " | ".join(
                a['description'] for a in result['savings_alerts'][:3]
            )

        return dmc.Notification(
            title="עיבוד הושלם",
            message=f"{result['new_transactions']} עסקאות חדשות, {result['duplicates_skipped']} כפילויות. {alerts_text}",
            color="green",
        )

    # ── Overview tab data ──────────────────────────────
    @app.callback(
        [
            Output("stat-total-spend", "children"),
            Output("stat-txn-count", "children"),
            Output("stat-pending-count", "children"),
            Output("pie-chart", "figure"),
            Output("bar-chart", "figure"),
            Output("top-merchants-table", "children"),
            Output("savings-alerts", "children"),
        ],
        Input("main-tabs", "value"),
        Input("process-output", "children"),
    )
    def update_overview(tab, _process):
        conn = get_connection()
        transactions = get_transactions(conn)
        conn.close()

        if not transactions:
            empty_fig = px.pie(title="אין נתונים")
            return "₪0", "0", "0", empty_fig, empty_fig, "אין נתונים", "אין הצעות"

        import pandas as pd
        df = pd.DataFrame(transactions)

        total_spend = df['amount_ils'].sum()
        txn_count = len(df)
        pending = df[df['needs_review'] == 1].shape[0]

        # Pie chart by category
        cat_totals = df.groupby('category')['amount_ils'].sum().reset_index()
        cat_totals = cat_totals[cat_totals['category'] != UNRECOGNIZED_CATEGORY]
        pie_fig = px.pie(
            cat_totals, values='amount_ils', names='category',
            hole=0.4,
        )
        pie_fig.update_layout(
            font=dict(family="Assistant, Arial"),
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=True,
            legend=dict(font=dict(size=11)),
        )

        # Bar chart by category
        cat_sorted = cat_totals.sort_values('amount_ils', ascending=True)
        bar_fig = px.bar(
            cat_sorted, x='amount_ils', y='category', orientation='h',
        )
        bar_fig.update_layout(
            font=dict(family="Assistant, Arial"),
            margin=dict(t=20, b=20, l=20, r=80),
            xaxis_title="סכום (₪)",
            yaxis_title="",
            showlegend=False,
        )

        # Top 5 merchants
        top5 = (
            df.groupby('merchant')['amount_ils']
            .agg(['sum', 'count'])
            .sort_values('sum', ascending=False)
            .head(5)
            .reset_index()
        )
        top5_rows = [
            dmc.Group(
                justify="space-between",
                children=[
                    dmc.Text(row['merchant'], size="sm"),
                    dmc.Text(f"₪{row['sum']:,.0f} ({row['count']} עסקאות)", size="sm", c="dimmed"),
                ],
            )
            for _, row in top5.iterrows()
        ]

        # Savings alerts
        from myfinance.processing.savings import detect_savings
        alerts = detect_savings(transactions)
        if alerts:
            alert_cards = [
                dmc.Alert(
                    title=a['title'],
                    children=a['description'],
                    color="yellow",
                    mb="xs",
                )
                for a in alerts[:5]
            ]
        else:
            alert_cards = [dmc.Text("אין הצעות חיסכון כרגע", c="dimmed")]

        return (
            f"₪{total_spend:,.0f}",
            str(txn_count),
            str(pending),
            pie_fig,
            bar_fig,
            html.Div(top5_rows) if top5_rows else "אין נתונים",
            html.Div(alert_cards),
        )

    # ── Month filter options ───────────────────────────
    @app.callback(
        Output("filter-month", "data"),
        Input("main-tabs", "value"),
        Input("process-output", "children"),
    )
    def update_month_options(_tab, _process):
        conn = get_connection()
        rows = conn.execute(
            "SELECT DISTINCT strftime('%Y-%m', date) as m FROM transactions ORDER BY m DESC"
        ).fetchall()
        conn.close()
        return [{"value": r['m'], "label": r['m']} for r in rows]

    # ── Transactions table data ────────────────────────
    @app.callback(
        Output("transactions-grid", "rowData"),
        [
            Input("filter-month", "value"),
            Input("filter-category", "value"),
            Input("filter-source", "value"),
            Input("filter-pending", "checked"),
            Input("process-output", "children"),
            Input("main-tabs", "value"),
        ],
    )
    def update_transactions_table(month, categories, sources, pending_only, _process, _tab):
        conn = get_connection()

        # Build query with filters
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if month:
            query += " AND strftime('%Y-%m', date) = ?"
            params.append(month)
        if categories:
            placeholders = ','.join(['?'] * len(categories))
            query += f" AND category IN ({placeholders})"
            params.extend(categories)
        if sources:
            placeholders = ','.join(['?'] * len(sources))
            query += f" AND source IN ({placeholders})"
            params.extend(sources)
        if pending_only:
            query += " AND needs_review = 1"

        query += " ORDER BY date DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()

        return [dict(r) for r in rows]

    # ── Clear filters ──────────────────────────────────
    @app.callback(
        [
            Output("filter-month", "value"),
            Output("filter-category", "value"),
            Output("filter-source", "value"),
            Output("filter-pending", "checked"),
        ],
        Input("btn-clear-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_filters(n_clicks):
        return None, [], [], False

    # ── Inline category edit ───────────────────────────
    @app.callback(
        Output("transactions-grid", "rowData", allow_duplicate=True),
        Input("transactions-grid", "cellValueChanged"),
        prevent_initial_call=True,
    )
    def on_category_edit(cell_changed):
        if not cell_changed:
            return no_update

        data = cell_changed[0] if isinstance(cell_changed, list) else cell_changed
        txn_id = data['data']['transaction_id']
        new_category = data['value']

        if new_category not in CATEGORIES:
            return no_update

        conn = get_connection()
        # Update the transaction
        update_transaction_category(conn, txn_id, new_category)

        # Update merchant map with user confirmation
        merchant = data['data'].get('merchant', '')
        if merchant:
            normalized = normalize_merchant(merchant)
            upsert_merchant_map(conn, normalized, new_category, confirmed_by='user')

        conn.close()
        return no_update

    # ── Export button ──────────────────────────────────
    @app.callback(
        Output("export-output", "children"),
        Input("btn-export", "n_clicks"),
        prevent_initial_call=True,
    )
    def export_excel(n_clicks):
        if not n_clicks:
            return no_update

        from myfinance.export import export_month
        month = datetime.now().strftime('%Y-%m')
        path = export_month(month)
        if path:
            return dmc.Notification(
                title="ייצוא הושלם",
                message=f"נשמר ב: {path}",
                color="green",
            )
        return dmc.Notification(
            title="אין נתונים",
            message=f"אין עסקאות לחודש {month}",
            color="yellow",
        )
