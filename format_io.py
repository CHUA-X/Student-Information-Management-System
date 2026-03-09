#!/usr/bin/python3

# 导入相关模块
import csv
import json
from pathlib import Path
from datetime import datetime
from openpyxl import Workbook


class StudentInfoFormat:
    def __init__(self, name, sex, birth, ID, schoolRoll, politicalAffiliation):
        """对应学生的姓名、性别、出生日期、身份证号、学籍号、政治面貌"""
        self.name = name
        self.sex = sex
        self.birth = birth
        self.ID = ID
        self.schoolRoll = schoolRoll
        self.politicalAffiliation = politicalAffiliation

    def output(self):
        """格式化学生信息并输出"""
        return [f'姓名:{self.name}', f'性别:{self.sex}', f'出生年月:{self.birth}', f'身份证号：{self.ID}',
                f'学籍号:{self.schoolRoll}', f'政治面貌:{self.politicalAffiliation}']


class StudentInfoExport:
    """导出学生数据"""
    @staticmethod
    def export2xlsx(students):
        """导出到Excel文件"""
        nowTime = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = Path(f'学生信息_{nowTime}.xlsx')

        # 建立工作簿
        wb = Workbook()
        sheet = wb.active
        sheet.title = '学生信息'

        # 建立表头
        headers = ['姓名', '性别', '出生年月', '身份证号', '学籍号', '政治面貌']
        sheet.append(headers)

        # 输出数据
        for student in students:
            sheet.append([
                student.name,
                student.sex,
                student.birth,
                student.ID,
                student.schoolRoll,
                student.politicalAffiliation
            ])
        wb.save(filename)
        return f'Excel文件{filename}导出成功！'

    @staticmethod
    def export2csv(students):
        """导出到csv文件"""
        nowTime = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = Path(f'学生信息_{nowTime}.csv')

        # 创建csv文件
        with open(filename, 'a', newline='', encoding='utf-8') as csvObj:
            writtenObj = csv.DictWriter(csvObj, ['姓名', '性别', '出生年月', '身份证号', '学籍号', '政治面貌'])
            writtenObj.writeheader()
            for student in students:
                writtenObj.writerow({
                    '姓名': student.name,
                    '性别': student.sex,
                    '出生年月': student.birth,
                    '身份证号': student.ID,
                    '学籍号': student.schoolRoll,
                    '政治面貌': student.politicalAffiliation
                })
        return f'CSV文件{filename}导出成功！'

    @staticmethod
    def export2txt(students):
        """导出到TXT文件"""
        nowTime = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = Path(f'学生信息_{nowTime}.txt')

        # 写入TXT文件
        with open(filename, 'a', encoding='utf-8') as f:
            for student in students:
                f.write(f'姓名: {student.name}\n')
                f.write(f'性别: {student.sex}\n')
                f.write(f'出生年月: {student.birth}\n')
                f.write(f'身份证号: {student.ID}\n')
                f.write(f'学籍号: {student.schoolRoll}\n')
                f.write(f'政治面貌: {student.politicalAffiliation}\n\n')
        return f'TXT文件{filename}导出成功！'

    @staticmethod
    def export2json(students):
        """导出到JSON文件"""
        nowTime = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = Path(f'学生信息_{nowTime}.json')

        # 写入JSON文件
        with open(filename, 'a', encoding='utf-8') as jsonObj:
            writing2json = []
            for student in students:
                studentDict = {
                    '姓名': student.name,
                    '性别': student.sex,
                    '出生年月': student.birth,
                    '身份证号': student.ID,
                    '学籍号': student.schoolRoll,
                    '政治面貌': student.politicalAffiliation
                }
                writing2json.append(studentDict)
            json.dump(writing2json, jsonObj, ensure_ascii=False, indent=2)
        return f'JSON文件{filename}导出成功！'
