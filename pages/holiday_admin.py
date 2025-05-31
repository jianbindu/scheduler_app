@dash.callback(
    Output("add-holiday-msg", "children"),
    Output("holiday-list", "children"),
    Input("add-holiday", "n_clicks"),
    State("holiday-date", "date"),
    prevent_initial_call=True
)
def add_holiday(n, date):
    if date:
        execute_sql("INSERT INTO Holiday (date) VALUES (?)", (date,))
        msg = dbc.Alert("添加成功", color="success")
    else:
        msg = dbc.Alert("请选择日期", color="danger")
    data = get_holidays()
    table = dbc.Table.from_dataframe(
        pd.DataFrame(data), striped=True, bordered=True, hover=True
    ) if data else html.Div("暂无节假日")
    return msg, table

@dash.callback(
    Output("holiday-list", "children"),
    Input("holiday-list", "id")
)
def initial_holiday_list(_):
    data = get_holidays()
    table = dbc.Table.from_dataframe(
        pd.DataFrame(data), striped=True, bordered=True, hover=True
    ) if data else html.Div("暂无节假日")
    return table
