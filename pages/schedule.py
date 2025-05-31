import dash
from dash import html, dcc, Input, Output, State, ctx, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import auto_schedule

dash.register_page(__name__, path="/schedule", name="Scheduling")

def get_pending_applications():
    conn = sqlite3.connect('scheduler.db')
    sql = """
    SELECT 
        CA.id AS RequestID,
        C.name AS Course,
        CO.name AS Company,
        CA.num_trainees AS TraineesAmount,
        CA.group_info AS GroupInformation,
        CA.created_at AS SubmitionDate
    FROM CourseApplication CA
    LEFT JOIN Company CO ON CA.company_id = CO.id
    LEFT JOIN Course C ON CA.course_id = C.id
    WHERE CA.status = 'pending'
    ORDER BY CA.created_at DESC
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def delete_application(app_id):
    conn = sqlite3.connect('scheduler.db')
    conn.execute("DELETE FROM CourseApplication WHERE id = ?", (app_id,))
    conn.commit()
    conn.close()

def update_application(app_id, num_trainees, group_info):
    conn = sqlite3.connect('scheduler.db')
    conn.execute(
        "UPDATE CourseApplication SET num_trainees = ?, group_info = ? WHERE id = ?",
        (num_trainees, group_info, app_id)
    )
    conn.commit()
    conn.close()

layout = dbc.Container([
    html.H2("排课管理"),
    dbc.Button("Auto schedule", id="auto-schedule-btn", color="primary", className="mb-3"),
    html.Div(id="schedule-msg", className="mb-2"),
    html.Hr(),
    html.H4("未排课申请"),
    dash_table.DataTable(
        id='pending-table',
        columns=[
            {"name": "Request ID", "id": "Request ID"},
            {"name": "Course", "id": "Course"},
            {"name": "Company", "id": "Company"},
            {"name": "Trainees amount", "id": "Trainees amount"},
            {"name": "Group information", "id": "Group information"},
            {"name": "Submition date", "id": "Submition date"},
        ],
        data=get_pending_applications().to_dict("records"),
        row_selectable="single",
        selected_rows=[],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
    ),
    html.Div([
        dbc.Button("Edit", id="edit-row-btn", color="warning", className="me-2", n_clicks=0),
        dbc.Button("Delete", id="delete-row-btn", color="danger", n_clicks=0),
    ], className="mb-2"),
    dcc.Store(id="edit-app-id"),
    dcc.Store(id="delete-app-id"),
    dbc.Modal([
        dbc.ModalHeader("修改申请"),
        dbc.ModalBody([
            dbc.Row([
                dbc.Label("Trainees amount", width=3),
                dbc.Col(dbc.Input(id="edit-num-schedule", type="number"), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Label("Group information", width=3),
                dbc.Col(dbc.Input(id="edit-group", type="text"), width=9)
            ], className="mb-2"),
            html.Div(id="edit-msg"),
        ]),
        dbc.ModalFooter([
            dbc.Button("保存", id="save-edit", color="primary", className="me-2"),
            dbc.Button("取消", id="close-edit-modal", color="secondary")
        ])
    ], id="edit-modal", is_open=False),

    dbc.Modal([
        dbc.ModalHeader("确认删除"),
        dbc.ModalBody("你确定要删除这条排课申请吗？此操作不可恢复。"),
        dbc.ModalFooter([
            dbc.Button("确认", id="confirm-delete", color="danger", className="me-2"),
            dbc.Button("取消", id="cancel-delete", color="secondary")
        ])
    ], id="delete-confirm-modal", is_open=False),
])


# 刷新DataTable数据
@dash.callback(
    Output("pending-table", "data"),
    Input("auto-schedule-btn", "n_clicks"),
    Input("schedule-msg", "children"),
    Input("edit-msg", "children"),
    prevent_initial_call=False
)
def refresh_pending_applications(n1, _msg1, _msg2):
    df = get_pending_applications()
    return df.to_dict("records")

# 选中行+点击“修改申请”按钮，弹出编辑弹窗
@dash.callback(
    Output("edit-modal", "is_open"),
    Output("edit-num-schedule", "value"),
    Output("edit-group", "value"),
    Output("edit-app-id", "data"),
    Input("edit-row-btn", "n_clicks"),
    State("pending-table", "selected_rows"),
    State("pending-table", "data"),
    prevent_initial_call=True
)
def open_edit_modal(n, selected_rows, data):
    if n and selected_rows:
        idx = selected_rows[0]
        row = data[idx]
        return True, row["Trainees amount"], row["Group information"], row["Request ID"]
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# 关闭弹窗
@dash.callback(
    Output("edit-modal", "is_open", allow_duplicate=True),
    Input("close-edit-modal", "n_clicks"),
    prevent_initial_call=True
)
def close_edit_modal(n):
    return False

# 保存编辑
@dash.callback(
    Output("edit-msg", "children"),
    Output("edit-modal", "is_open", allow_duplicate=True),
    Input("save-edit", "n_clicks"),
    State("edit-app-id", "data"),
    State("edit-num-schedule", "value"),
    State("edit-group", "value"),
    prevent_initial_call=True
)
def save_edit_app(n, app_id, num, group):
    if not (app_id and num):
        return dbc.Alert("信息不完整", color="danger"), dash.no_update
    update_application(app_id, num, group)
    return dbc.Alert("保存成功", color="success"), False

# 选中行+点击“删除申请”按钮，弹出删除确认弹窗
@dash.callback(
    Output("delete-confirm-modal", "is_open"),
    Output("delete-app-id", "data"),
    Input("delete-row-btn", "n_clicks"),
    State("pending-table", "selected_rows"),
    State("pending-table", "data"),
    prevent_initial_call=True
)
def open_delete_modal(n, selected_rows, data):
    if n and selected_rows:
        idx = selected_rows[0]
        row = data[idx]
        return True, row["Request ID"]
    return dash.no_update, dash.no_update

# 取消删除弹窗
@dash.callback(
    Output("delete-confirm-modal", "is_open", allow_duplicate=True),
    Input("cancel-delete", "n_clicks"),
    prevent_initial_call=True
)
def close_delete_modal(n):
    return False

# 点确认才真正删除
@dash.callback(
    Output("schedule-msg", "children", allow_duplicate=True),   # 加 allow_duplicate
    Output("delete-confirm-modal", "is_open", allow_duplicate=True),
    Input("confirm-delete", "n_clicks"),
    State("delete-app-id", "data"),
    prevent_initial_call=True
)
def really_delete_app(n, app_id):
    if n and app_id:
        delete_application(app_id)
        return dbc.Alert("删除成功", color="success"), False
    return dash.no_update, dash.no_update

# 自动排课按钮
@dash.callback(
    Output("schedule-msg", "children", allow_duplicate=True),   # 加 allow_duplicate
    Input("auto-schedule-btn", "n_clicks"),
    prevent_initial_call=True
)
def run_auto_schedule(n_clicks):
    auto_schedule.main()
    return dbc.Alert("自动排课已完成！", color="success")
