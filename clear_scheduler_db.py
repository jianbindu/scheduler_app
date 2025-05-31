import sqlite3

DB_PATH = 'scheduler.db'

# 你可以根据实际情况增删要清空的表
TABLES = [
    'Schedule',
    'CourseApplication',
    'TrainerLeave',
    # 如有其他临时/辅助表也可加上
]

def clear_tables(db_path, tables):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for table in tables:
        print(f"正在清空 {table} ...")
        cursor.execute(f"DELETE FROM {table}")
        # 可选：重置自增id，如用AUTOINCREMENT，可以去掉注释
        # cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
    conn.commit()
    conn.close()
    print("所有指定表已清空！")

if __name__ == "__main__":
    clear_tables(DB_PATH, TABLES)
