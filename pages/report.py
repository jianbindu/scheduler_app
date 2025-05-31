import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from db_utils import query_sql
import pandas as pd

dash.register_page(__name__, path="/report", name="Report")

# ====== 页面布局 ======
layout = dbc.Container([
    html.H2("Scheduling Report"),
    # Date选择+导出报告
    dbc.Row([
        dbc.Col([
            dcc.DatePickerSingle(
                id='report-date-picker',
                display_format='YYYY-MM-DD',
                placeholder='Please select date',
                style={'marginRight': '1rem'}
            ),
            dbc.Button("Export report", id="export-report-btn", color="success")
        ], width="auto"),
    ], justify='end', className="mb-3"),
    dcc.Download(id="download-report-xlsx"),
    html.Div(id="report-table")
])

# ====== 普通报表表格回调（原有） ======
@dash.callback(
    dash.Output("report-table", "children"),
    dash.Input("report-table", "id")
)
def show_report(_):
    rows = query_sql("""
        SELECT 
            S.id,
            S.application_id,
            S.date, S.period, CO.name AS company,
            C.name as course, T.name as trainer, CL.name as classroom, 
            S.num_assigned, S.status
        FROM Schedule S
        LEFT JOIN Course C ON S.course_id = C.id
        LEFT JOIN Trainer T ON S.trainer_id = T.id
        LEFT JOIN Classroom CL ON S.classroom_id = CL.id
        LEFT JOIN CourseApplication CA ON S.application_id = CA.id
        LEFT JOIN Company CO ON CA.company_id = CO.id
        ORDER BY S.date, S.period, S.id
    """)
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.rename(columns={
            'id': '排课ID',
            'application_id': 'Request ID',
            'date': 'Date',
            'period': 'Period',
            'company': 'Company',
            'course': 'Course',
            'trainer': 'Trainer',
            'classroom': 'Classroom',
            'num_assigned': 'assigned trainees',
            'status': 'Status'
        })
        columns = [
            '排课ID', 'Request ID', 'Date', 'Period', 'Company', 'Course',
            'Trainer', 'Classroom', 'assigned trainees', 'Status'
        ]
        df = df[columns]
        table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
    else:
        table = html.Div("暂无数据")
    return table

# ====== 导出矩阵风格日报表回调 ======
@dash.callback(
    dash.Output("download-report-xlsx", "data"),
    dash.Input("export-report-btn", "n_clicks"),
    dash.State("report-date-picker", "date"),
    prevent_initial_call=True
)
def export_day_report(n_clicks, date_value):
    if not date_value:
        return None
    rows = query_sql("""
        SELECT 
            S.date, S.period, C.name as course, CL.name as classroom, T.name as trainer,
            CO.name as company, S.num_assigned
        FROM Schedule S
        LEFT JOIN Course C ON S.course_id = C.id
        LEFT JOIN Trainer T ON S.trainer_id = T.id
        LEFT JOIN Classroom CL ON S.classroom_id = CL.id
        LEFT JOIN CourseApplication CA ON S.application_id = CA.id
        LEFT JOIN Company CO ON CA.company_id = CO.id
        WHERE S.date=?
        ORDER BY S.period, C.name, CL.name, T.name, CO.name
    """, [date_value])
    import pandas as pd
    if not rows:
        return None
    df = pd.DataFrame(rows)
    df['colkey'] = list(zip(df['course'], df['period'], df['classroom'], df['trainer']))
    pivot = df.pivot_table(
        index='company', columns='colkey', values='num_assigned', aggfunc='sum', fill_value=""
    )
    pivot = pivot.sort_index(axis=1, level=[0,1,2,3])
    idx_values = pivot.index.tolist()
    col_map = list(pivot.columns)
    nrow, ncol = pivot.shape

    from io import BytesIO
    output = BytesIO()
    sheet_name = '班级排班表'
    import xlsxwriter

    with xlsxwriter.Workbook(output) as wb:
        ws = wb.add_worksheet(sheet_name)
        # ------- 样式定义 -------
        fmt_title = wb.add_format({
            'align': 'left', 'valign': 'vcenter', 'bold': True,
            'font_size': 15, 'font_color': 'white', 'bg_color': '#636466', 'border': 0
        })
        fmt_date = wb.add_format({
            'align': 'right', 'valign': 'vcenter', 'bold': True,
            'font_size': 15, 'font_color': 'white', 'bg_color': '#636466', 'border': 0
        })
        fmt_head = wb.add_format({
            'align': 'center', 'valign': 'vcenter', 'bold': True,
            'font_size': 11, 'bg_color': '#E5E5E5', 'border': 1
        })
        fmt_head2 = wb.add_format({
            'align': 'center', 'valign': 'vcenter', 'bold': True,
            'font_size': 11, 'bg_color': '#F6F6F6', 'border': 1
        })
        fmt_head3 = wb.add_format({
            'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'bg_color': '#FAFAFA', 'border': 1
        })
        fmt_head4 = wb.add_format({
            'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'border': 1
        })
        fmt_company = wb.add_format({
            'align': 'left', 'valign': 'vcenter', 'bold': True, 'font_size': 11, 'border': 1
        })
        fmt_cell = wb.add_format({
            'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'border': 1
        })

        # ------- 标题 -------
        ws.merge_range(0, 0, 0, 0, "Date", fmt_title)
        ws.merge_range(0, 1, 0, ncol, date_value, fmt_date)

        # ------- Course合并表头 -------
        ws.write(1, 0, "Course", fmt_head)
        # Course分组
        col_spans = []
        curr_cname = None
        i1 = 0
        for i, col in enumerate(col_map):
            cname = col[0]
            if cname != curr_cname:
                if curr_cname is not None:
                    col_spans.append((curr_cname, i1, i-1))
                curr_cname = cname
                i1 = i
        col_spans.append((curr_cname, i1, len(col_map)-1))
        for cname, i1, i2 in col_spans:
            if i2 > i1:
                ws.merge_range(1, 1+i1, 1, 1+i2, cname, fmt_head)
            else:
                ws.write(1, 1+i1, cname, fmt_head)

        # ------- Period -------
        ws.write(2, 0, "Period", fmt_head)
        for i, col in enumerate(col_map):
            ws.write(2, 1+i, col[1], fmt_head2)
        # ------- Classroom -------
        ws.write(3, 0, "Classroom", fmt_head)
        for i, col in enumerate(col_map):
            ws.write(3, 1+i, col[2], fmt_head3)
        # ------- Trainer -------
        ws.write(4, 0, "Trainer", fmt_head)
        for i, col in enumerate(col_map):
            ws.write(4, 1+i, col[3], fmt_head4)

        # ------- 数据区 -------
        for r in range(nrow):
            ws.write(5+r, 0, idx_values[r], fmt_company)
            for c in range(ncol):
                val = pivot.iloc[r, c]
                ws.write(5+r, 1+c, "" if pd.isnull(val) else val, fmt_cell)

        # 列宽、行高、冻结
        ws.set_column(0, 0, 14)
        ws.set_column(1, ncol, 12)
        ws.set_row(0, 22)
        for i in range(1, 5):
            ws.set_row(i, 19)
        ws.freeze_panes(5, 1)

    output.seek(0)
    file_name = f"Course排班矩阵_{date_value}.xlsx"
    return dcc.send_bytes(output.getvalue(), file_name)
