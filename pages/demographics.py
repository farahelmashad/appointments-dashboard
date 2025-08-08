from dash import html, register_page
import dash
from dash import callback, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from utils import df

register_page(__name__, path='/demographics', name='Demographics')

#df=pd.read_csv("Data\preprocessed-app-data.csv")
counts = df['No-show'].value_counts()
fig = px.pie(
    names=counts.index,
    values=counts.values,
    title='Show vs No-show'
)
# filters:
gender_filter=dcc.Dropdown(id='gender_dropdown', options=[{'label':'All', 'value':'All'}]+[{'label':x, 'value':x} for x in df['Gender'].unique()])

layout = html.Div([
    html.H2('Demographics', style={'textAlign': 'left', 'marginBottom': '40px','marginLeft':'15px','color':'white'}),

    dbc.Row([
        html.H4('Filters', style={'marginLeft': '15px','color':'white'}, )
    ]),
    dbc.Row([
       dbc.Col(gender_filter, width=4)
        
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='g1', figure={})
        ], md=6), 
        dbc.Col([
            dcc.Graph(id='g2',figure=fig)
        ], md=5)  
    ], className='mb-4'), 

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='g3', figure={})
        ], md=6),

        dbc.Col([
            dcc.Graph(id='g4', figure={})
        ], md=6)
    ])
], style={'backgroundColor':"#eee9e9"})
