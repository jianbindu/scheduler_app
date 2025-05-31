import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from db_utils import get_all, execute_sql
import pandas as pd

dash.register_page(__name__, path="/classroom-admin", name="Configure Classroom")

def get_classrooms():
    return get_all("Classroom")

layout = dbc.Container([
    html.H2("Configure Classroom"),
    dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Label("Classroom NO."),
                dbc.Input(id="classroom-name", type="text"),
            ], width=6),
            dbc.Col([
                dbc.Label("Capacity"),
                dbc.Input(id="classroom-capacity", type="number", min=1),
            ], width=6),
        ]),
        dbc.Button("Add", id="add-classroom", color="primary", className="mt-3"),
        html.Div(id="add-classroom-msg")
    ], className="mb-4"),
    html.Hr(),
    html.H4("Classroom List"),
    html.Div(id="classroom-list")
])

@dash.callback(
    Output("add-classroom-msg", "children"),
    Output("classroom-list", "children"),
    Input("add-classroom", "n_clicks"),
    State("classroom-name", "value"),
    State("classroom-capacity", "value"),
)
def add_classroom(n, name, capacity):
    # 页面初次加载 or 按钮还没点
    if n is None:
        data = get_classrooms()
        table = dbc.Table.from_dataframe(pd.DataFrame(data), striped=True, bordered=True, hover=True) if data else html.Div("暂无教室")
        return "", table
    # 按钮点击
    if name and capacity:
        execute_sql("INSERT INTO Classroom (name, capacity) VALUES (?, ?)", (name, capacity))
        msg = dbc.Alert("添加成功", color="success")
    else:
        msg = dbc.Alert("请填写完整", color="danger")
    data = get_classrooms()
    table = dbc.Table.from_dataframe(pd.DataFrame(data), striped=True, bordered=True, hover=True) if data else html.Div("暂无教室")
    return msg, table