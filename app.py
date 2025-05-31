import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# 页面注册方式，建议后续模块化
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)

app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="Scheduling System",
        color="primary",
        dark=True,
        children=[
            dbc.NavItem(dbc.NavLink("Submit Request", href="/application")),
            dbc.NavItem(dbc.NavLink("Scheduling", href="/schedule")),
            dbc.NavItem(dbc.NavLink("Scheduling Report", href="/report")),
            dbc.NavItem(dbc.NavLink("Configure Course", href="/course-admin")),
            dbc.NavItem(dbc.NavLink("Configure Trainer", href="/trainer-admin")),
            dbc.NavItem(dbc.NavLink("Configure Classroom", href="/classroom-admin")),
            dbc.NavItem(dbc.NavLink("Configure Holiday", href="/holiday-admin")),
        ]
    ),
    dash.page_container
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True)
