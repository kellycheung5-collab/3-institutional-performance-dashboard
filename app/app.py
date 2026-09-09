import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from data_loader import load_enrollment_data, load_financial_fte_data

# Load Data
df_headcount = load_enrollment_data()
df_financials = load_financial_fte_data()

app = dash.Dash(__name__, title="BC Post-Secondary Performance Dashboard")

app.layout = html.Div([
    html.H1("BC Post-Secondary Institutional Performance Dashboard"),
    
    html.Div([
        html.Label("Select Institution:"),
        dcc.Dropdown(
            id="institution-dropdown",
            options=[{"label": inst, "value": inst} for inst in sorted(df_headcount["institution_name"].unique())],
            value=sorted(df_headcount["institution_name"].unique())[0],
            clearable=False
        )
    ], style={"width": "40%", "padding": "10px"}),

    dcc.Tabs(id="tabs-example", value='tab-1', children=[
        dcc.Tab(label='Enrollment Trends', value='tab-1'),
        dcc.Tab(label='Financials & FTE Performance', value='tab-2'),
    ]),
    
    html.Div(id='tabs-content')
])

@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs-example', 'value'),
     Input('institution-dropdown', 'value')]
)
def render_content(tab, selected_institution):
    if tab == 'tab-1':
        filtered_df = df_headcount[df_headcount["institution_name"] == selected_institution]
        
        fig = px.line(
            filtered_df, 
            x="fiscal_year", 
            y="headcount", 
            color="student_type",
            title=f"Headcount Trends: {selected_institution}",
            markers=True,  # Adds markers on data points
            text="headcount",  # Displays numbers directly on points
            labels={
                "fiscal_year": "Fiscal Year",
                "headcount": "Headcount",
                "student_type": "Student Classification"
            }
        )
        
        # Position numbers above line data points
        fig.update_traces(
            textposition="top center",
            hovertemplate="<b>Fiscal Year:</b> %{x}<br><b>Headcount:</b> %{y:,.0f}<extra></extra>"
        )
        
        return dcc.Graph(figure=fig)
        
    elif tab == 'tab-2':
        filtered_df = df_financials[df_financials["institution_name"] == selected_institution]
        
        fig = px.bar(
            filtered_df, 
            x="fiscal_year", 
            y=["fte_actual", "fte_target"],
            barmode="group",
            title=f"Actual vs. Target FTE: {selected_institution}",
            text_auto=',.0f',  # Automatically formats numbers on top of bars
            labels={
                "fiscal_year": "Fiscal Year",
                "value": "FTE Count",
                "variable": "FTE Type"
            }
        )
        
        name_map = {"fte_actual": "Actual FTE", "fte_target": "Target FTE"}
        for trace in fig.data:
            # Perform lookup once
            clean_name = name_map.get(trace.name, trace.name)
    
            trace.update(
                name=clean_name,
                hovertemplate=f"<b>FTE Type:</b> {clean_name}<br><b>Fiscal Year:</b> %{{x}}<br><b>Count:</b> %{{y:,.0f}}<extra></extra>"
            )

        # Place numbers directly above each bar
        fig.update_traces(textposition="outside")

        return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run(debug=False)