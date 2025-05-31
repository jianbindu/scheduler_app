import dash
from dash import html, dcc, Input, Output, State, ctx
import sqlite3
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/application", name="Submit request")

def get_companies():
    conn = sqlite3.connect('scheduler.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM Company")
    result = c.fetchall()
    conn.close()
    return [{"label": n, "value": i} for i, n in result]

def get_courses():
    conn = sqlite3.connect('scheduler.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM Course")
    result = c.fetchall()
    conn.close()
    return [{"label": n, "value": i} for i, n in result]

layout = dbc.Container([
    html.H2("Request"),
    dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Label("公司"),
                dbc.InputGroup([
                    dcc.Dropdown(id="company-input", options=get_companies(), placeholder="Please select company", style={"minWidth": "200px", "width": "300px"}),
                    dbc.Button("Add company", id="open-company-modal", color="secondary", outline=True, n_clicks=0)
                ], style={"width": "350px"})
            ], width=4),
            dbc.Col([
                dbc.Label("Course"),
                dcc.Dropdown(id="course-input", options=get_courses(), placeholder="Please select course"),
            ], width=4),
            dbc.Col([
                dbc.Label("trainees amount"),
                dbc.Input(id="num-input", type="number", min=1, step=1, placeholder="trainees amount"),
            ], width=4),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Label("Group information"),
                dbc.Input(id="group-input", type="text", placeholder="please identify the group if allpied"),
            ], width=12)
        ]),
        dbc.Button("Submit request", id="submit-application", color="primary", className="mt-3"),
    ]),
    html.Div(id="submit-msg", className="mt-2"),
    # 新增公司弹窗
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Add Company")),
        dbc.ModalBody([
            dbc.Row([
                dbc.Label("Company Name", width=3),
                dbc.Col(dbc.Input(id="new-company-name", type="text"), width=9)
            ], className="mb-3"),
            dbc.Row([
                dbc.Label("E-mail", width=3),
                dbc.Col(dbc.Input(id="new-company-email", type="email"), width=9)
            ], className="mb-3"),
            html.Div(id="add-company-msg")
        ]),
        dbc.ModalFooter([
            dbc.Button("Save", id="save-company", color="primary", className="me-2"),
            dbc.Button("Cancel", id="close-company-modal", color="secondary")
        ])
    ], id="company-modal", is_open=False)
])

# 打开/关闭公司弹窗
@dash.callback(
    Output("company-modal", "is_open"),
    [Input("open-company-modal", "n_clicks"),
     Input("close-company-modal", "n_clicks"),
     Input("save-company", "n_clicks")],
    [State("company-modal", "is_open")],
)
def toggle_modal(open_clicks, close_clicks, save_clicks, is_open):
    triggered_id = ctx.triggered_id
    if triggered_id in ["open-company-modal", "close-company-modal", "save-company"]:
        return not is_open
    return is_open

# 新增公司，返回提示，刷新下拉
@dash.callback(
    Output("add-company-msg", "children"),
    Output("company-input", "options"),
    Input("save-company", "n_clicks"),
    State("new-company-name", "value"),
    State("new-company-email", "value"),
    prevent_initial_call=True
)
def add_company(n, name, email):
    if not name:
        return dbc.Alert("公司名称不能为空", color="danger"), get_companies()
    conn = sqlite3.connect('scheduler.db')
    conn.execute("INSERT INTO Company (name, contact_email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()
    return dbc.Alert("添加成功", color="success"), get_companies()

# 课程申请提交
@dash.callback(
    Output("submit-msg", "children"),
    Input("submit-application", "n_clicks"),
    State("company-input", "value"),
    State("course-input", "value"),
    State("num-input", "value"),
    State("group-input", "value"),
    prevent_initial_call=True
)
def submit_application(n_clicks, company, course, num, group):
    if not (company and course and num):
        return dbc.Alert("请完整填写表单。", color="danger")
    conn = sqlite3.connect('scheduler.db')
    conn.execute(
        "INSERT INTO CourseApplication (company_id, course_id, num_trainees, group_info, status, created_at) VALUES (?, ?, ?, ?, 'pending', datetime('now'))",
        (company, course, num, group)
    )
    conn.commit()
    conn.close()
    return dbc.Alert("succeed！", color="success")
