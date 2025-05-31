import sqlite3

DB_PATH = 'scheduler.db'   # 修改为你的实际数据库文件名

def print_db_structure(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f"数据库文件: {db_path}\n")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    if not tables:
        print("没有找到任何表！")
        return
    for table in tables:
        print(f"\n表：{table}")
        cursor.execute(f"PRAGMA table_info('{table}');")
        columns = cursor.fetchall()
        if not columns:
            print("  无字段信息")
            continue
        for col in columns:
            # col: (cid, name, type, notnull, dflt_value, pk)
            print(f"  字段: {col[1]}  类型: {col[2]}  主键: {col[5]}  允许为空: {'否' if col[3] else '是'}  默认值: {col[4]}")
    conn.close()

if __name__ == "__main__":
    print_db_structure(DB_PATH)
