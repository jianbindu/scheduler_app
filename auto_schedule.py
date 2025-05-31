import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict

def get_workdays(start_date, max_days, conn):
    holidays = set(r[0] for r in conn.execute("SELECT date FROM Holiday"))
    days = []
    d = start_date
    while len(days) < max_days:
        if d.weekday() < 5 and d.strftime('%Y-%m-%d') not in holidays:
            days.append(d.strftime('%Y-%m-%d'))
        d += timedelta(days=1)
    return days

def get_teachers_for_course(conn, course_id):
    return [row[0] for row in conn.execute(
        "SELECT trainer_id FROM TrainerCourse WHERE course_id=?", (course_id,)
    )]

def is_teacher_available(conn, trainer_id, date, period):
    sql = "SELECT 1 FROM Schedule WHERE trainer_id=? AND date=? AND period=?"
    busy = conn.execute(sql, (trainer_id, date, period)).fetchone()
    return not busy

def is_room_available(conn, room_id, date, period):
    sql = "SELECT 1 FROM Schedule WHERE classroom_id=? AND date=? AND period=?"
    busy = conn.execute(sql, (room_id, date, period)).fetchone()
    return not busy

def get_classroom_capacities(conn):
    return {row[0]: row[1] for row in conn.execute("SELECT id, capacity FROM Classroom")}

def get_course_info(conn, course_id):
    row = conn.execute("SELECT name, max_capacity, duration FROM Course WHERE id=?", (course_id,)).fetchone()
    return {'name': row[0], 'max_capacity': row[1], 'duration': float(row[2])}

def main():
    db_path = 'scheduler.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    today = datetime.now().date()
    max_days = 14
    days = get_workdays(today + timedelta(days=1), max_days, conn)
    classroom_caps = get_classroom_capacities(conn)
    classrooms = sorted(classroom_caps.items(), key=lambda x: -x[1])  # 优先大教室

    cursor.execute("""
        SELECT id, company_id, course_id, num_trainees, group_info, created_at
        FROM CourseApplication
        WHERE status='pending'
        ORDER BY created_at
    """)
    applications = cursor.fetchall()

    for app in applications:
        app_id, company_id, course_id, num_trainees, group_info, created_at = app
        course_info = get_course_info(conn, course_id)
        duration = course_info['duration']  # 0.5=半天, 1=一天
        course_max = course_info['max_capacity']
        num_remaining = num_trainees
        trainers = get_teachers_for_course(conn, course_id)
        trainer_objs = [(tid, conn.execute("SELECT name FROM Trainer WHERE id=?", (tid,)).fetchone()[0]) for tid in trainers]

        scheduled_any = False
        for d in days:
            if num_remaining <= 0:
                break

            if duration == 1:
                # 全天课只用AM period（自动同时锁定AM/PM）
                for room_id, cap in classrooms:
                    # 查AM/PM是否有已排班，是否有空位
                    cur = conn.execute("""
                        SELECT id, trainer_id, num_assigned
                        FROM Schedule
                        WHERE date=? AND (period='am' OR period='pm') AND course_id=? AND classroom_id=?
                        GROUP BY trainer_id
                    """, (d, course_id, room_id))
                    rows = cur.fetchall()
                    assigned = sum([row[2] for row in rows])
                    left = min(cap, course_max) - assigned
                    # 优先补进已排班
                    if rows and left > 0:
                        n_add = min(left, num_remaining)
                        trainer_id = rows[0][1]
                        for p in ['am', 'pm']:
                            cursor.execute("""
                                INSERT INTO Schedule
                                (application_id, course_id, trainer_id, classroom_id, date, period, num_assigned, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (app_id, course_id, trainer_id, room_id, d, p, n_add, 'scheduled'))
                        num_remaining -= n_add
                        scheduled_any = True
                        if num_remaining <= 0:
                            break
                        continue
                    # 否则新开班
                    for trainer_id, trainer_name in trainer_objs:
                        if (is_teacher_available(conn, trainer_id, d, 'am') and
                            is_teacher_available(conn, trainer_id, d, 'pm') and
                            is_room_available(conn, room_id, d, 'am') and
                            is_room_available(conn, room_id, d, 'pm')):
                            n_assign = min(num_remaining, cap, course_max)
                            for p in ['am', 'pm']:
                                cursor.execute("""
                                    INSERT INTO Schedule
                                    (application_id, course_id, trainer_id, classroom_id, date, period, num_assigned, status)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (app_id, course_id, trainer_id, room_id, d, p, n_assign, 'scheduled'))
                            num_remaining -= n_assign
                            scheduled_any = True
                            if num_remaining <= 0:
                                break
                    if num_remaining <= 0:
                        break
                if num_remaining <= 0:
                    break

            else:
                # 半天课（优先AM, 再PM）
                for p in ['am', 'pm']:
                    if num_remaining <= 0:
                        break
                    for room_id, cap in classrooms:
                        # 查同period是否有已排班，有空位则补进
                        cur = conn.execute("""
                            SELECT id, trainer_id, num_assigned
                            FROM Schedule
                            WHERE date=? AND period=? AND course_id=? AND classroom_id=?
                        """, (d, p, course_id, room_id))
                        rows = cur.fetchall()
                        assigned = sum([row[2] for row in rows])
                        left = min(cap, course_max) - assigned
                        if rows and left > 0:
                            n_add = min(left, num_remaining)
                            trainer_id = rows[0][1]
                            cursor.execute("""
                                INSERT INTO Schedule
                                (application_id, course_id, trainer_id, classroom_id, date, period, num_assigned, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (app_id, course_id, trainer_id, room_id, d, p, n_add, 'scheduled'))
                            num_remaining -= n_add
                            scheduled_any = True
                            if num_remaining <= 0:
                                break
                            continue
                        # 否则新开班
                        for trainer_id, trainer_name in trainer_objs:
                            if is_teacher_available(conn, trainer_id, d, p) and is_room_available(conn, room_id, d, p):
                                n_assign = min(num_remaining, cap, course_max)
                                cursor.execute("""
                                    INSERT INTO Schedule
                                    (application_id, course_id, trainer_id, classroom_id, date, period, num_assigned, status)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (app_id, course_id, trainer_id, room_id, d, p, n_assign, 'scheduled'))
                                num_remaining -= n_assign
                                scheduled_any = True
                                if num_remaining <= 0:
                                    break
                        if num_remaining <= 0:
                            break
                    if num_remaining <= 0:
                        break
            if num_remaining <= 0:
                break

        # 新版处理：有未排满就新建pending记录
        if num_remaining == 0:
            cursor.execute("UPDATE CourseApplication SET status='scheduled' WHERE id=?", (app_id,))
        elif num_remaining < num_trainees:
            cursor.execute("UPDATE CourseApplication SET status='partial' WHERE id=?", (app_id,))
            cursor.execute("""
                INSERT INTO CourseApplication 
                (company_id, course_id, num_trainees, group_info, status, created_at) 
                VALUES (?, ?, ?, NULL, 'pending', ?)
            """, (company_id, course_id, num_remaining, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        # 否则维持pending

    conn.commit()
    conn.close()
    print("自动排课完成！")

if __name__ == '__main__':
    main()
