import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from data_loader import load_enrollment_data, load_financial_fte_data

# Load Data from SQLite Database
df_headcount = load_enrollment_data()
df_financials = load_financial_fte_data()

# Initialize App with Bootstrap Theme
app = dash.Dash(
    __name__, 
    title="BC Post-Secondary Performance Dashboard",
    external_stylesheets=[dbc.themes.FLATLY]
)

app.layout = dbc.Container([
    # Header Title
    dbc.Row([
        dbc.Col(
            html.H2("BC Post-Secondary Institutional Performance Dashboard", className="my-3 text-primary"),
            width=12
        )
    ]),

    # Global Controls Row
    dbc.Row([
        dbc.Col([
            html.Label("Select Institution:", className="fw-bold me-2"),
            dcc.Dropdown(
                id="institution-dropdown",
                options=[{"label": inst, "value": inst} for inst in sorted(df_headcount["institution_name"].unique())],
                value=sorted(df_headcount["institution_name"].unique())[0],
                clearable=False
            )
        ], md=6, lg=4, className="mb-4")
    ]),

    # KPI Summary Cards Container
    dbc.Row(id="kpi-cards-container", className="mb-4"),

    # Navigation Tabs & Visualization Section
    dbc.Card([
        dbc.CardHeader(
            dcc.Tabs(id="tabs-example", value='tab-1', children=[
                dcc.Tab(label='Enrollment Trends', value='tab-1'),
                dcc.Tab(label='Financials & FTE Performance', value='tab-2'),
            ])
        ),
        dbc.CardBody([
            html.Div(id='tabs-content')
        ])
    ], className="shadow-sm mb-4"),

    # Data Table Section Header & Export Button
    dbc.Row([
        dbc.Col(html.H4("Institutional Summary Table", className="m-0"), width="auto"),
        dbc.Col(
            dbc.Button("📥 Export CSV", id="btn-csv-download", color="primary", size="sm"),
            width="auto"
        ),
        dcc.Download(id="download-dataframe-csv")
    ], className="align-items-center mb-3 mt-4"),

    # Dynamic Data Table Container
    dbc.Row([
        dbc.Col(html.Div(id='datatable-container'), width=12)
    ], className="mb-5")

], fluid=True, className="px-4 py-3")


# Callback 1: Render Dynamic KPI Summary Cards
@app.callback(
    Output("kpi-cards-container", "children"),
    Input("institution-dropdown", "value")
)
def update_kpi_cards(selected_institution):
    inst_headcount = df_headcount[df_headcount["institution_name"] == selected_institution]
    inst_financials = df_financials[df_financials["institution_name"] == selected_institution]

    # Calculate Headcount Metric
    latest_hc_row = inst_headcount.sort_values("fiscal_year").iloc[-1]
    latest_hc = latest_hc_row["headcount"]
    latest_hc_fy = latest_hc_row["fiscal_year"]

    # Calculate FTE Attainment Rate
    latest_fin_row = inst_financials.sort_values("fiscal_year").iloc[-1]
    actual_fte = latest_fin_row["fte_actual"]
    target_fte = latest_fin_row["fte_target"]
    attainment_rate = (actual_fte / target_fte * 100) if target_fte > 0 else 0
    latest_fin_fy = latest_fin_row["fiscal_year"]

    status_color = "success" if attainment_rate >= 100 else "danger"

    def make_kpi_card(title, value, subtitle, text_color="primary"):
        return dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H6(title, className="card-subtitle text-muted mb-2"),
                    html.H3(value, className=f"card-title text-{text_color} fw-bold mb-1"),
                    html.Small(subtitle, className="text-secondary")
                ])
            ], className="shadow-sm h-100 border-0 bg-light"),
            xs=12, md=4
        )

    return [
        make_kpi_card(
            f"Total Headcount ({latest_hc_fy})", 
            f"{latest_hc:,.0f}", 
            "Latest Fiscal Year Total",
            text_color="primary"
        ),
        make_kpi_card(
            f"FTE Target Attainment ({latest_fin_fy})", 
            f"{attainment_rate:.1f}%", 
            f"{actual_fte:,.0f} Actual / {target_fte:,.0f} Target",
            text_color=status_color
        ),
        make_kpi_card(
            f"Operating Grant ({latest_fin_fy})", 
            f"${latest_fin_row['operating_grant']:,.0f}", 
            "Provincial Funding Allocation",
            text_color="primary"
        )
    ]


# Callback 2: Render Visualizations & Interactive Data Table
@app.callback(
    [Output('tabs-content', 'children'),
     Output('datatable-container', 'children')],
    [Input('tabs-example', 'value'),
     Input('institution-dropdown', 'value')]
)
def render_content_and_table(tab, selected_institution):
    if tab == 'tab-1':
        filtered_df = df_headcount[df_headcount["institution_name"] == selected_institution].copy()
        
        fig = px.line(
            filtered_df, 
            x="fiscal_year", 
            y="headcount", 
            color="student_type",
            title=f"Headcount Trends: {selected_institution}",
            markers=True,
            text="headcount",
            labels={
                "fiscal_year": "Fiscal Year",
                "headcount": "Headcount",
                "student_type": "Student Classification"
            }
        )
        fig.update_traces(
            textposition="top center",
            hovertemplate="<b>Fiscal Year:</b> %{x}<br><b>Headcount:</b> %{y:,.0f}<extra></extra>"
        )
        
        table_df = filtered_df[["fiscal_year", "institution_name", "region_name", "student_type", "headcount"]]
        table_df = table_df.rename(columns={
            "fiscal_year": "Fiscal Year",
            "institution_name": "Institution",
            "region_name": "Region",
            "student_type": "Student Classification",
            "headcount": "Headcount"
        })

    elif tab == 'tab-2':
        filtered_df = df_financials[df_financials["institution_name"] == selected_institution].copy()
        
        fig = px.bar(
            filtered_df, 
            x="fiscal_year", 
            y=["fte_actual", "fte_target"],
            barmode="group",
            title=f"Actual vs. Target FTE: {selected_institution}",
            text_auto=',.0f',
            labels={
                "fiscal_year": "Fiscal Year",
                "value": "FTE Count",
                "variable": "FTE Type"
            }
        )
        name_map = {"fte_actual": "Actual FTE", "fte_target": "Target FTE"}
        fig.for_each_trace(lambda t: t.update(
            name=name_map.get(t.name, t.name),
            hovertemplate=f"<b>FTE Type:</b> {name_map.get(t.name, t.name)}<br><b>Fiscal Year:</b> %{{x}}<br><b>Count:</b> %{{y:,.0f}}<extra></extra>"
        ))
        fig.update_traces(textposition="outside")

        table_df = filtered_df[["fiscal_year", "institution_name", "fte_actual", "fte_target", "operating_grant"]]
        table_df = table_df.rename(columns={
            "fiscal_year": "Fiscal Year",
            "institution_name": "Institution",
            "fte_actual": "Actual FTE",
            "fte_target": "Target FTE",
            "operating_grant": "Operating Grant ($)"
        })

    # Modebar Configuration (Camera Icon Only)
    graph_component = dcc.Graph(
        figure=fig,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': [
                'zoom2d', 'pan2d', 'select2d', 'lasso2d', 
                'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
                'sendDataToCloud', 'editInChartStudio'
            ],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'bc_post_secondary_chart',
                'height': 500,
                'width': 700,
                'scale': 2
            }
        }
    )

    data_table = dash_table.DataTable(
        data=table_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in table_df.columns],
        page_size=10,
        sort_action="native",
        filter_action="native",
        style_header={
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold',
            'border': '1px solid #dee2e6'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontFamily': 'inherit',
            'fontSize': '14px',
            'border': '1px solid #dee2e6'
        },
        style_data_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': '#f8f9fa'
        }]
    )

    return [graph_component, data_table]


# Callback 3: Handle CSV Download Trigger
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-csv-download", "n_clicks"),
    State("tabs-example", "value"),
    State("institution-dropdown", "value"),
    prevent_initial_call=True
)
def export_csv(n_clicks, tab, selected_institution):
    if tab == 'tab-1':
        df = df_headcount[df_headcount["institution_name"] == selected_institution]
        filename = f"{selected_institution.lower().replace(' ', '_')}_enrollment_data.csv"
    else:
        df = df_financials[df_financials["institution_name"] == selected_institution]
        filename = f"{selected_institution.lower().replace(' ', '_')}_financials_fte_data.csv"

    return dcc.send_data_frame(df.to_csv, filename, index=False)


if __name__ == '__main__':
    app.run(debug=True, port=8050)