import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from db_utils import get_all, execute_sql, query_sql

dash.register_page(__name__, path="/trainer-admin", name="教师配置")

def get_trainers():
    return get_all("Trainer")

def get_courses():
    return get_all("Course")

layout = dbc.Container([
    html.H2("教师管理"),
    dbc.Row([
        dbc.Col([
            dbc.Form([
                dbc.Label("教师姓名"),
                dbc.Input(id="trainer-name", type="text"),
                dbc.Button("新增教师", id="add-trainer", color="primary", className="mt-2"),
                html.Div(id="add-trainer-msg")
            ]),
            html.Hr(),
            html.H4("教师列表"),
            html.Div(id="trainer-list")
        ], width=6),
        dbc.Col([
            html.H4("课程授权"),
            dcc.Dropdown(id="trainer-select", options=[], placeholder="选择教师"),
            dcc.Dropdown(id="course-select", options=[], multi=True, placeholder="授权课程"),
            dbc.Button("授权", id="auth-course", color="success", className="mt-2"),
            html.Div(id="auth-msg"),
            html.Hr(),
            html.H4("教师请假"),
            dcc.DatePickerRange(id="leave-dates"),
            dbc.Button("添加请假", id="add-leave", color="warning", className="mt-2"),
            html.Div(id="leave-msg"),
        ], width=6),
    ])
])

# 新增教师
@dash.callback(
    Output("add-trainer-msg", "children"),
    Output("trainer-list", "children"),
    Input("add-trainer", "n_clicks"),
    State("trainer-name", "value"),
    prevent_initial_call=True
)
def add_trainer(n_clicks, name):
    if name:
        execute_sql("INSERT INTO Trainer (name) VALUES (?)", (name,))
        msg = dbc.Alert("教师添加成功", color="success")
    else:
        msg = dbc.Alert("请输入姓名", color="danger")
    data = get_trainers()
    import pandas as pd
    table = dbc.Table.from_dataframe(pd.DataFrame(data), striped=True, bordered=True, hover=True) if data else html.Div("暂无教师")
    return msg, table

# 更新下拉框
@dash.callback(
    Output("trainer-select", "options"),
    Output("course-select", "options"),
    Input("trainer-list", "children")
)
def update_dropdowns(_):
    trainers = get_trainers()
    courses = get_courses()
    return (
        [{"label": t["name"], "value": t["id"]} for t in trainers],
        [{"label": c["name"], "value": c["id"]} for c in courses]
    )

# 授权课程
@dash.callback(
    Output("auth-msg", "children"),
    Input("auth-course", "n_clicks"),
    State("trainer-select", "value"),
    State("course-select", "value"),
    prevent_initial_call=True
)
def auth_course(n, trainer_id, course_ids):
    if not trainer_id or not course_ids:
        return dbc.Alert("请选择教师和课程", color="danger")
    for cid in course_ids:
        execute_sql("INSERT INTO TrainerCourse (trainer_id, course_id) VALUES (?, ?)", (trainer_id, cid))
    return dbc.Alert("授权成功", color="success")

# 教师请假
@dash.callback(
    Output("leave-msg", "children"),
    Input("add-leave", "n_clicks"),
    State("trainer-select", "value"),
    State("leave-dates", "start_date"),
    State("leave-dates", "end_date"),
    prevent_initial_call=True
)
def add_leave(n, trainer_id, start, end):
    if not trainer_id or not (start and end):
        return dbc.Alert("请选择教师和请假日期", color="danger")
    execute_sql("INSERT INTO TrainerLeave (trainer_id, start_date, end_date) VALUES (?, ?, ?)", (trainer_id, start, end))
    return dbc.Alert("请假添加成功", color="success")
