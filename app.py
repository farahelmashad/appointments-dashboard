import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from utils import create_data_card  

df = pd.read_csv('Data/preprocessed-app-data.csv')
df_coords = pd.read_csv('Data/neighborhoods_coords.csv')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Appointments Dashboard"

gender_options = ['All'] + df['Gender'].unique().tolist()
age_group_options = ['All'] + sorted(df['AgeGroup'].dropna().unique())

COLOR_MAP = {
    'Attended': "#286BB3",
    'Missed Appointment': '#E15759',
}

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H5("Filters", className="text-white mt-3 mb-4"),
            html.Hr(style={"borderColor": "#777"}),

            html.Label("Gender", className="text-light"),
            dcc.Dropdown(
                id='gender-filter',
                options=[{'label': i, 'value': i} for i in gender_options],
                value='All',
                clearable=False,
                className="mb-4"
            ),

            html.Label("Age Group", className="text-light"),
            dcc.Dropdown(
                id='age-group-filter',
                options=[{'label': i, 'value': i} for i in age_group_options],
                value='All',
                clearable=False,
                className="mb-4"
            ),

            html.Label("Recurring Patient", className="text-light"),
            dbc.RadioItems(
                id='recurring-filter',
                options=[
                    {'label': 'All', 'value': 'All'},
                    {'label': 'Yes', 'value': True},
                    {'label': 'No', 'value': False},
                ],
                value='All',
                inline=True,
                className="text-light mb-4"
            ),

            html.Label("Same Day Appointment", className="text-light"),
            dbc.RadioItems(
                id='sameday-filter',
                options=[
                    {'label': 'All', 'value': 'All'},
                    {'label': 'Yes', 'value': True},
                    {'label': 'No', 'value': False},
                ],
                value='All',
                inline=True,
                className="text-light mb-4"
            ),

            html.Label("Number of Conditions", className="text-light"),
            dcc.RangeSlider(
                id='condition-slider',
                min=df['NumberOfConditions'].min(),
                max=df['NumberOfConditions'].max(),
                step=1,
                value=[df['NumberOfConditions'].min(), df['NumberOfConditions'].max()],
                marks={i: str(i) for i in range(df['NumberOfConditions'].min(), df['NumberOfConditions'].max() + 1)},
                tooltip={"placement": "bottom", "always_visible": False},
                className="mb-4"
            ),
        ],
            width=2,
            style={'backgroundColor': '#212529', 'height': '100vh', 'position': 'sticky', 'top': 0, 'padding': '20px'}
        ),
        dbc.Col([
        html.H3(
            "📊 Appointments Dashboard",
            className="text-center mt-3 mb-3",
            style={
                "fontFamily": "Segoe UI, Roboto, Helvetica, sans-serif",
                "fontWeight": "bold",
                "fontSize": "28px"
            }
        ),

            dbc.Row([
                dbc.Col(create_data_card("No-Show Rate", "card-no-show-rate", icon="📉"), md=4),
                dbc.Col(create_data_card("Total Appointments", "card-total-appointments", icon="📅"), md=4),
                dbc.Col(create_data_card("Recurring Patients %", "card-recurring-pct", icon="🔄"), md=4),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(dcc.Graph(id='graph-1', config={'displayModeBar': False}, style={"height": "300px"}), md=4),
                dbc.Col(dcc.Graph(id='graph-2', config={'displayModeBar': False}, style={"height": "300px"}), md=4),
                dbc.Col(dcc.Graph(id='graph-3', config={'displayModeBar': False}, style={"height": "300px"}), md=4),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(dcc.Graph(id='graph-4', config={'displayModeBar': False}, style={"height": "300px"}), md=7),
                dbc.Col(dcc.Graph(id='graph-5', config={'displayModeBar': False}, style={"height": "300px"}), md=5),
            ]),
        ], width=10, className="p-2")
    ])
], fluid=True)


@app.callback(
    [
        Output('card-no-show-rate', 'children'),
        Output('card-total-appointments', 'children'),
        Output('card-recurring-pct', 'children'),
        Output('graph-1', 'figure'),
        Output('graph-2', 'figure'),
        Output('graph-3', 'figure'),
        Output('graph-4', 'figure'),
        Output('graph-5', 'figure'),
    ],
    [
        Input('gender-filter', 'value'),
        Input('age-group-filter', 'value'),
        Input('recurring-filter', 'value'),
        Input('sameday-filter', 'value'),
        Input('condition-slider', 'value'),
    ]
)
def update_data_cards(gender, age_group, recurring, same_day, slider_range_value):
    filtered_df = df.copy()

    if gender != 'All':
        filtered_df = filtered_df[filtered_df['Gender'] == gender]
    if age_group != 'All':
        filtered_df = filtered_df[filtered_df['AgeGroup'] == age_group]
    if recurring != 'All':
        filtered_df = filtered_df[filtered_df['IsRecurring'] == recurring]
    if same_day != 'All':
        filtered_df = filtered_df[filtered_df['SameDayAppt'] == same_day]
    if slider_range_value is not None:
        filtered_df = filtered_df[
            (filtered_df['NumberOfConditions'] >= slider_range_value[0]) &
            (filtered_df['NumberOfConditions'] <= slider_range_value[1])
        ]

    no_show_rate = filtered_df['MissedAppointment'].mean() * 100
    recurring_pct = filtered_df['IsRecurring'].mean() * 100
    total = len(filtered_df)

    same_day_df = filtered_df.groupby('SameDayAppt')['Status'].value_counts(normalize=True).mul(100).reset_index()
    same_day_df.columns = ['SameDayAppt', 'Status', 'Percentage']
    fig1 = px.bar(same_day_df, x='SameDayAppt', y='Percentage', color='Status',
                  barmode='group', title='Same Day Appointment vs Attendance',
                  color_discrete_map=COLOR_MAP)
    fig1.update_layout(
        margin=dict(t=30, b=20, l=10, r=10),
        legend=dict(orientation='h', yanchor="bottom", y=-0.4, xanchor="center", x=0.5, font=dict(size=10))
    )

    age_group_df = filtered_df.groupby('AgeGroup')['MissedAppointment'].mean().reset_index()
    fig2 = px.bar(age_group_df, x='AgeGroup', y='MissedAppointment',
                  title='Missed Rate by Age Group', labels={'MissedAppointment': 'Missed Rate'})
    fig2.update_layout(
        margin=dict(t=30, b=20, l=10, r=10),
        legend=dict(orientation='h', y=1.02, x=0.5, xanchor='center', font=dict(size=10))
    )

    days_waited = filtered_df.groupby('Days_Waited_Range')['Status'].value_counts(normalize=True).mul(100).reset_index()
    days_waited.columns = ['Days_Waited_Range', 'Status', 'Percentage']
    fig3 = px.bar(days_waited, x='Days_Waited_Range', y='Percentage', color='Status',
                  barmode='group', title='Days Waited vs Attendance',
                  color_discrete_map=COLOR_MAP)
    fig3.update_layout(
        margin=dict(t=60, b=40, l=10, r=10),  
        legend=dict(
            orientation='h',
            y=1.1,  
            x=0.5,
            xanchor='center',
            font=dict(size=10)
        )
    )

    time_series = filtered_df.groupby('Scheduled_Date')['Status'].apply(lambda x: (x == 'Missed Appointment').sum()).reset_index()
    time_series.columns = ['Scheduled_Date', 'Number of Missed Appointments']
    fig4 = px.line(time_series, x='Scheduled_Date', y='Number of Missed Appointments',
                   title='Missed Appointments Over Time')
    fig4.update_layout(
            margin=dict(t=60, b=20, l=30, r=10),
    legend=dict(orientation='h', y=1.1, x=0.5, xanchor='center', font=dict(size=10)),
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        ),
    )

    )

    hood_df = filtered_df.groupby('Neighbourhood')['MissedAppointment'].mean().reset_index()
    top_hoods = hood_df.sort_values('MissedAppointment', ascending=False).head(5)
    top_hoods['Neighbourhood'] = top_hoods['Neighbourhood'].str.capitalize()
    fig5 = px.pie(top_hoods, names='Neighbourhood', values='MissedAppointment',
                  title='Top 5 Neighbourhoods by Missed Appointments', hole=0.4)
    fig5.update_layout(
        title=dict(x=0.5),
        margin=dict(t=40, b=20, l=20, r=20), 
        legend=dict(
            orientation="h",        
            yanchor="bottom",      
            y=-0.4,                
            xanchor="center",
            x=0.5,
            font=dict(size=9),
            bgcolor='rgba(0,0,0,0)' 
        ),
        showlegend=True
    )
    if total == 0:
        return "0.00%", "0", "0.00%", fig1, fig2, fig3, fig4, fig5

    return (
        f"{no_show_rate:.2f}%",
        f"{total}",
        f"{recurring_pct:.2f}%",
        fig1, fig2, fig3, fig4, fig5
    )

if __name__ == '__main__':
    app.run(debug=True)
