#!/usr/bin/python3

import sqlite3
from pathlib import Path
from format_io import StudentInfoFormat


class Manager:
    """学生信息管理"""
    def __init__(self):
        # 初始化SQLite3数据库
        self.dbPath = Path('./data/student.db')
        self.initDb()

    def initDb(self):
        # 初始化数据库表结构
        conn = self.getConn()
        cursor = conn.cursor()

        # 创建学生信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sex TEXT NOT NULL,
                birth TEXT NOT NULL,
                id_card TEXT NOT NULL UNIQUE,
                school_roll TEXT NOT NULL UNIQUE,
                political_affiliation TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建索引以提高查询性能
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON students(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_school_roll ON students(school_roll)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_id_card ON students(id_card)')

        conn.commit()
        conn.close()

    def getConn(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.dbPath)
        # 启用外键约束
        conn.execute('PRAGMA foreign_keys = ON')
        # 使用字典游标
        conn.row_factory = sqlite3.Row
        return conn

    def add(self, student):
        """添加学生"""
        try:
            conn = self.getConn()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO students (name, sex, birth, id_card, school_roll, political_affiliation)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                student.name, student.sex, student.birth,
                student.ID, student.schoolRoll, student.politicalAffiliation
            ))

            conn.commit()
            conn.close()

            return True, f'添加学生 {student.name} 成功!'
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed: students.id_card' in str(e):
                return False, '身份证号已存在，不能重复添加！'
            elif 'UNIQUE constraint failed: students.school_roll' in str(e):
                return False, '学籍号已存在，不能重复添加！'
            else:
                return False, f'添加失败！错误信息：{str(e)}'
        except Exception as err:
            return False, f'添加失败！错误信息：{str(err)}'

    def delete(self, studentName):
        """删除学生"""
        try:
            conn = self.getConn()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM students WHERE name = ?', (studentName,))

            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, f'删除学生 {studentName} 成功!'
            else:
                conn.close()
                return False, f'学生 {studentName} 不存在！'
        except Exception as err:
            return False, f'删除失败！错误信息：{str(err)}'

    def change(self, student):
        """修改学生信息"""
        try:
            conn = self.getConn()
            cursor = conn.cursor()

            # 首先检查学生是否存在
            cursor.execute('SELECT id FROM students WHERE name = ?', (student.name,))
            existingStudent = cursor.fetchone()

            if existingStudent:
                # 检查除了当前学生外，身份证号或学籍号是否已被其他学生使用
                cursor.execute('''
                    SELECT name FROM students 
                    WHERE (id_card = ? OR school_roll = ?) AND name != ?
                ''', (student.ID, student.schoolRoll, student.name))

                conflictingStudent = cursor.fetchone()

                if conflictingStudent:
                    conn.close()
                    return False, f'身份证号或学籍号已被学生 {conflictingStudent["name"]} 使用！'

                # 更新学生信息
                cursor.execute('''
                    UPDATE students 
                    SET sex = ?, birth = ?, id_card = ?, school_roll = ?, political_affiliation = ?, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                ''', (
                    student.sex, student.birth, student.ID,
                    student.schoolRoll, student.politicalAffiliation, student.name
                ))

                conn.commit()
                conn.close()
                return True, f'修改学生 {student.name} 信息成功!'
            else:
                conn.close()
                return False, f'学生 {student.name} 不存在！'
        except Exception as err:
            return False, f'修改失败！错误信息：{str(err)}'

    def getStudentByName(self, name):
        """根据姓名获取学生信息"""
        try:
            conn = self.getConn()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM students WHERE name = ?', (name,))
            student = cursor.fetchone()

            conn.close()
            return dict(student) if student else None
        except Exception as err:
            print(f'查询失败：{err}')
            return None

    def getAllStudents(self):
        """获取所有学生信息"""
        try:
            conn = self.getConn()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM students ORDER BY name')
            students = cursor.fetchall()

            conn.close()
            return [dict(student) for student in students]
        except Exception as err:
            print(f'查询失败：{err}')
            return []

    def getStudentNames(self):
        """获取所有学生姓名"""
        try:
            conn = self.getConn()
            cursor = conn.cursor()

            cursor.execute('SELECT name FROM students ORDER BY name')
            names = [row['name'] for row in cursor.fetchall()]

            conn.close()
            return names
        except Exception as err:
            print(f'查询失败：{err}')
            return []

    def displayStudent(self, onlyNameSwitch='off'):
        """显示学生信息"""
        try:
            if onlyNameSwitch == 'on':
                return self.getStudentNames()
            else:
                students = self.getAllStudents()
                if not students:
                    return '系统中暂无学生信息。\n'

                text = '相关学生信息：\n\n'
                for student in students:
                    text += f"姓名: {student['name']}\n"
                    text += f"性别: {student['sex']}\n"
                    text += f"出生日期: {student['birth']}\n"
                    text += f"身份证号: {student['id_card']}\n"
                    text += f"学籍号: {student['school_roll']}\n"
                    text += f"政治面貌: {student['political_affiliation']}\n"
                    text += "-" * 50 + "\n\n"

                text += f"总计: {len(students)} 名学生\n"
                return text
        except Exception as err:
            return f'查看学生失败！错误信息：{str(err)}'

    def exportStudentInfo(self):
        """导出学生信息"""
        try:
            students = self.getAllStudents()
            studentObjs = []

            for student in students:
                studentObj = StudentInfoFormat(
                    student['name'], student['sex'], student['birth'],
                    student['id_card'], student['school_roll'], student['political_affiliation']
                )
                studentObjs.append(studentObj)

            return studentObjs
        except Exception as err:
            print(f'导出失败：{err}')
            return []

    def getStatistics(self):
        """获取学生信息统计"""
        try:
            conn = self.getConn()
            cursor = conn.cursor()

            # 统计总数
            cursor.execute('SELECT COUNT(*) as total FROM students')
            total = cursor.fetchone()['total']

            # 按性别统计
            cursor.execute('SELECT sex, COUNT(*) as count FROM students GROUP BY sex')
            sexStatistics = cursor.fetchall()

            # 按政治面貌统计
            cursor.execute(
                'SELECT political_affiliation, COUNT(*) as count FROM students GROUP BY political_affiliation')
            politicalAffiliationStatistics = cursor.fetchall()

            conn.close()

            return {
                'total': total,
                'sexStatistics': dict(sexStatistics),
                'politicalAffiliationStatistics': dict(politicalAffiliationStatistics)
            }
        except Exception as err:
            print(f'统计失败：{err}')
            return {'total': 0, 'sexStatistics': {}, 'politicalAffiliationStatistics': {}}
