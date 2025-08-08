import dash_bootstrap_components as dbc
from dash import html

def create_data_card(title, id_value, icon=None, color="primary"):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                # Icon (optional)
                html.Div(icon, style={'fontSize': '30px', 'marginRight': '10px'}) if icon else None,
                html.H6(title, className="card-title mb-1", style={'fontWeight': '600', 'color': '#555'})
            ], style={'display': 'flex', 'alignItems': 'center'}),

            html.H2(id=id_value, className="card-text", style={
                'fontWeight': '700',
                'fontSize': '2.5rem',
                'marginTop': '5px',
                'color': '#222',
                'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            })

        ]),
        className="shadow-sm rounded-3",
        style={'height': '140px'}
    )
