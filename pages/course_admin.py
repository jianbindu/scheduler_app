import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from db_utils import get_all, execute_sql
import pandas as pd

dash.register_page(__name__, path="/course-admin", name="Configure Course")

def get_courses():
    data = get_all("Course")
    return data

layout = dbc.Container([
    html.H2("Configure Course"),
    dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Label("Course Name"),
                dbc.Input(id="course-name", type="text"),
            ], width=3),
            dbc.Col([
                dbc.Label("Course Code"),
                dbc.Input(id="course-code", type="text"),
            ], width=3),
            dbc.Col([
                dbc.Label("maximum capacity(Option)"),
                dbc.Input(id="course-max", type="number", min=1),
            ], width=3),
            dbc.Col([
                dbc.Label("Duration(Day，0.5=half day，1=Full day)"),
                dbc.Input(id="course-duration", type="number", min=0.5, step=0.5, value=0.5),
            ], width=3),
        ], className="mb-3"),
        dbc.Button("Add", id="add-course", color="primary", className="mt-3"),
        html.Div(id="add-course-msg")
    ], className="mb-4"),
    html.Hr(),
    html.H4("Course List"),
    html.Div(id="course-list")
])


@dash.callback(
    Output("add-course-msg", "children"),
    Output("course-list", "children"),
    Input("add-course", "n_clicks"),
    State("course-name", "value"),
    State("course-code", "value"),
    State("course-max", "value"),
    State("course-duration", "value"),
)
def add_course(n_clicks, name, code, max_capacity, duration):
    import pandas as pd
    if n_clicks is None:
        data = get_courses()
        table = dbc.Table.from_dataframe(pd.DataFrame(data), striped=True, bordered=True, hover=True) if data else html.Div("暂无课程")
        return "", table
    msg = ""
    if name and code:
        if not duration:
            duration = 0.5  # 默认半天
        sql = "INSERT INTO Course (name, code, max_capacity, duration) VALUES (?, ?, ?, ?)"
        execute_sql(sql, (name, code, max_capacity, duration))
        msg = dbc.Alert("添加成功", color="success")
    else:
        msg = dbc.Alert("课程名和编号必填", color="danger")
    data = get_courses()
    table = dbc.Table.from_dataframe(pd.DataFrame(data), striped=True, bordered=True, hover=True) if data else html.Div("暂无课程")
    return msg, table
