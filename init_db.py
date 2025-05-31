import sqlite3

def insert_demo_data():
    conn = sqlite3.connect('scheduler.db')
    c = conn.cursor()
    # 公司
    c.execute("INSERT OR IGNORE INTO Company (id, name, contact_email) VALUES (1, '演示公司', 'demo@company.com')")
    # 课程
    c.execute("INSERT OR IGNORE INTO Course (id, name, code, max_capacity) VALUES (1, '入职安全', 'SEC101', 30)")
    # 教师
    c.execute("INSERT OR IGNORE INTO Trainer (id, name) VALUES (1, '王老师')")
    # 教室
    c.execute("INSERT OR IGNORE INTO Classroom (id, name, capacity) VALUES (1, '一号教室', 25)")
    conn.commit()
    conn.close()
    print("插入了演示数据。")

def init_db():
    conn = sqlite3.connect('scheduler.db')
    c = conn.cursor()

    # 公司表
    c.execute('''
    CREATE TABLE IF NOT EXISTS Company (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact_email TEXT
    )
    ''')

    # 课程表
    c.execute('''
    CREATE TABLE IF NOT EXISTS Course (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL,
        max_capacity INTEGER
    )
    ''')

    # 培训师表
    c.execute('''
    CREATE TABLE IF NOT EXISTS Trainer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')

    # 培训师-课程授权
    c.execute('''
    CREATE TABLE IF NOT EXISTS TrainerCourse (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trainer_id INTEGER,
        course_id INTEGER,
        FOREIGN KEY(trainer_id) REFERENCES Trainer(id),
        FOREIGN KEY(course_id) REFERENCES Course(id)
    )
    ''')

    # 培训师请假
    c.execute('''
    CREATE TABLE IF NOT EXISTS TrainerLeave (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trainer_id INTEGER,
        start_date DATE,
        end_date DATE,
        FOREIGN KEY(trainer_id) REFERENCES Trainer(id)
    )
    ''')

    # 教室
    c.execute('''
    CREATE TABLE IF NOT EXISTS Classroom (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        capacity INTEGER NOT NULL
    )
    ''')

    # 节假日
    c.execute('''
    CREATE TABLE IF NOT EXISTS Holiday (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL
    )
    ''')

    # 课程申请
    c.execute('''
    CREATE TABLE IF NOT EXISTS CourseApplication (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        course_id INTEGER,
        num_trainees INTEGER,
        group_info TEXT,
        status TEXT,
        created_at DATETIME,
        FOREIGN KEY(company_id) REFERENCES Company(id),
        FOREIGN KEY(course_id) REFERENCES Course(id)
    )
    ''')

    # 课程排课安排
    c.execute('''
    CREATE TABLE IF NOT EXISTS Schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER,
        course_id INTEGER,
        trainer_id INTEGER,
        classroom_id INTEGER,
        date DATE,
        period TEXT,
        num_assigned INTEGER,
        status TEXT,
        FOREIGN KEY(application_id) REFERENCES CourseApplication(id),
        FOREIGN KEY(course_id) REFERENCES Course(id),
        FOREIGN KEY(trainer_id) REFERENCES Trainer(id),
        FOREIGN KEY(classroom_id) REFERENCES Classroom(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("数据库初始化完成。")

if __name__ == '__main__':
    init_db()
    insert_demo_data()