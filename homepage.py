#!/usr/bin/python3

import sys
import tkinter as tk
from datetime import date
from info_manager import Manager
from tkcalendar import DateEntry
from checker import InputCheck as ic
from background import BackgroundManager
from checker import StudentInfoException
from login_and_security import UserManager, UserManagementGUI
from tkinter import ttk, messagebox, scrolledtext
from format_io import StudentInfoFormat, StudentInfoExport


class BaseInterface:
    """共同操作界面类，之后Interface4Admin和Interface4User挂载在此之上"""

    def __init__(self, ver, username):
        self.ver = ver
        self.mgr = Manager()
        self.currentUsername = username
        self.mainWindow = None
        self.backgroundTheme = BackgroundManager('custom')

    def createMainWindow(self, title):
        # 主窗口
        self.mainWindow = tk.Tk()
        self.mainWindow.title(f'学生信息管理系统 {self.ver} - {title}')
        self.mainWindow.geometry('900x700')
        self.mainWindow.resizable(True, True)

        screenWidth = self.mainWindow.winfo_screenwidth()
        screenHeight = self.mainWindow.winfo_screenheight()
        x = (screenWidth - 900) // 2
        y = (screenHeight - 700) // 2
        self.mainWindow.geometry(f'900x700+{x}+{y}')

        self.backgroundTheme.applyBackground(self.mainWindow, 'main', 900, 700)

        self.mainWindow.protocol("WM_DELETE_WINDOW", self.exitSys)

        return self.mainWindow

    @staticmethod
    def showMessage(title, message, msgType='info'):
        # 警告窗口打包
        if msgType == 'info':
            messagebox.showinfo(title, message)
        elif msgType == 'warning':
            messagebox.showwarning(title, message)
        elif msgType == 'error':
            messagebox.showerror(title, message)

    @staticmethod
    def askYesOrNo(title, question):
        # 询问窗口打包
        return messagebox.askyesno(title, question)

    def formalExport(self):
        # 导出窗口界面
        students = self.mgr.exportStudentInfo()
        if not students:
            # 无学生信息警告
            self.showMessage('警告', '没有学生信息可导出！', 'warning')
            return

        exportWindow = tk.Toplevel(self.mainWindow)
        exportWindow.title('导出学生信息')
        exportWindow.geometry('600x600')
        exportWindow.transient(self.mainWindow)
        exportWindow.grab_set()

        exportWindow.update_idletasks()
        x = self.mainWindow.winfo_x() + (self.mainWindow.winfo_width() - 500) // 2
        y = self.mainWindow.winfo_y() + (self.mainWindow.winfo_height() - 450) // 2
        exportWindow.geometry(f'600x600+{x}+{y}')

        self.backgroundTheme.applyBackground(exportWindow, 'dialog', 500, 450)

        mainFrame = tk.Frame(exportWindow, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.85)

        titleLabel = tk.Label(mainFrame, text='选择导出格式',
                              font=('微软雅黑', 16, 'bold'),
                              bg='#F8F9FA')
        titleLabel.pack(pady=20)

        countLabel = tk.Label(mainFrame, text=f'共有 {len(students)} 条学生记录',
                              font=('微软雅黑', 12),
                              bg='#F8F9FA')
        countLabel.pack(pady=10)

        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.pack(pady=20, fill=tk.BOTH, expand=True)

        def export2excel():
            # 导出为.xlsx文件
            try:
                result = StudentInfoExport.export2xlsx(students)
                self.showMessage('成功', result)
                exportWindow.destroy()
            except Exception as e:
                self.showMessage('错误', f'导出失败：{str(e)}', 'error')

        def export2csv():
            # 导出为.csv文件
            try:
                result = StudentInfoExport.export2csv(students)
                self.showMessage('成功', result)
                exportWindow.destroy()
            except Exception as e:
                self.showMessage('错误', f'导出失败：{str(e)}', 'error')

        def export2txt():
            # 导出为.txt文件
            try:
                result = StudentInfoExport.export2txt(students)
                self.showMessage('成功', result)
                exportWindow.destroy()
            except Exception as e:
                self.showMessage('错误', f'导出失败：{str(e)}', 'error')

        def export2json():
            # 导出为.json文件
            try:
                result = StudentInfoExport.export2json(students)
                self.showMessage('成功', result)
                exportWindow.destroy()
            except Exception as e:
                self.showMessage('错误', f'导出失败：{str(e)}', 'error')

        buttonConfig = [
            ('导出为Excel', export2excel, '#28A745'),
            ('导出为CSV', export2csv, '#17A2B8'),
            ('导出为TXT', export2txt, '#6C757D'),
            ('导出为JSON', export2json, '#FFC107')
        ]

        for text, command, color in buttonConfig:
            button = tk.Button(buttonFrame, text=text, command=command,
                               font=('微软雅黑', 11),
                               bg=color, fg='white',
                               padx=20, pady=10,
                               relief='raised', borderwidth=1,
                               cursor='hand2')
            button.pack(pady=8, fill=tk.X)
            button.bind('<Enter>', lambda e, b=button: b.config(bg='#4A90E2'))
            button.bind('<Leave>', lambda e, b=button, c=color: b.config(bg=c))

        returnButton = tk.Button(mainFrame, text='返回',
                                 command=exportWindow.destroy,
                                 font=('微软雅黑', 10),
                                 bg='#DC3545', fg='white',
                                 padx=15, pady=8,
                                 relief='raised', borderwidth=1)
        returnButton.pack(pady=15)
        returnButton.bind('<Enter>', lambda e: returnButton.config(bg='#C82333'))
        returnButton.bind('<Leave>', lambda e: returnButton.config(bg='#DC3545'))

    def exitSys(self):
        # 退出系统
        if self.askYesOrNo('确认退出', '真的要退出学生信息管理系统吗？'):
            self.mainWindow.withdraw()
            self.showMessage('系统退出', '感谢使用学生信息管理系统！')
            sys.exit()

    def checkEmptyStudents(self):
        # 检查系统学生名单是否为空
        return not self.mgr.displayStudent(onlyNameSwitch='on')

    def showEmptyWarning(self):
        # 若checkEmptyStudents()函数返回True，则显示错误
        self.showMessage('警告', '系统内尚未录入学生！请添加后重试！', 'warning')


class Interface4Admin(BaseInterface):
    """管理员界面"""

    def __init__(self, ver, username):
        super().__init__(ver, username)
        self.current_username = username

    @staticmethod
    def formatDate4Display(dateObj):
        # 日期格式化
        return f"{dateObj.year}年{dateObj.month}月{dateObj.day}日"

    @staticmethod
    def parseDateFromString(dateStr):
        # 日期第一验证
        try:
            if dateStr and '年' in dateStr and '月' in dateStr and '日' in dateStr:
                year = int(dateStr.split('年')[0])
                month = int(dateStr.split('年')[1].split('月')[0])
                day = int(dateStr.split('月')[1].split('日')[0])
                return date(year, month, day)
        except (ValueError, IndexError):
            return None

    def createStudentInputDialog(self, title, fields, default=None):
        # 添加学生信息窗口
        dialog = tk.Toplevel(self.mainWindow)
        dialog.title(title)
        dialog.geometry('600x750')
        dialog.transient(self.mainWindow)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.mainWindow.winfo_x() + (self.mainWindow.winfo_width() - 600) // 2
        y = self.mainWindow.winfo_y() + (self.mainWindow.winfo_height() - 750) // 2
        dialog.geometry(f'600x750+{x}+{y}')

        self.backgroundTheme.applyBackground(dialog, 'dialog', 600, 750)

        mainFrame = tk.Frame(dialog, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.95, relheight=0.95)

        entries = {}
        errorLabels = {}

        titleLabel = tk.Label(mainFrame, text=title,
                              font=('微软雅黑', 16, 'bold'),
                              bg='#F8F9FA')
        titleLabel.grid(row=0, column=0, columnspan=2, pady=(20, 30), sticky=tk.W)

        row = 1
        for field, label in fields.items():
            fieldLabel = tk.Label(mainFrame, text=label,
                                  font=('微软雅黑', 11),
                                  bg='#F8F9FA')
            fieldLabel.grid(row=row, column=0, sticky=tk.W, pady=12, padx=(20, 10))

            if field == 'sex':
                combo = ttk.Combobox(mainFrame, font=('微软雅黑', 11), width=35)
                combo['values'] = ('男', '女')
                combo.grid(row=row, column=1, pady=12, padx=(0, 20), sticky=tk.W)
                entries[field] = combo

            elif field == 'birth':
                dateValue = DateEntry(mainFrame,
                                      font=('微软雅黑', 11),
                                      width=33,
                                      date_pattern='yyyy-MM-dd',
                                      locale='zh_CN',
                                      background='white',
                                      foreground='black',
                                      borderwidth=1)
                dateValue.grid(row=row, column=1, pady=12, padx=(0, 20), sticky=tk.W)
                entries[field] = dateValue

            elif field == 'schoolRoll':
                schoolRollFrame = tk.Frame(mainFrame, bg='#F8F9FA')
                schoolRollFrame.grid(row=row, column=1, sticky=tk.W, padx=(0, 20), pady=12)

                prefixCombo = ttk.Combobox(schoolRollFrame, font=('微软雅黑', 11), width=5)
                prefixCombo['values'] = ('G', 'L', 'J')
                prefixCombo.pack(side=tk.LEFT, padx=(0, 5))

                IDEntry = tk.Entry(schoolRollFrame, font=('微软雅黑', 11), width=28)
                IDEntry.pack(side=tk.LEFT)

                entries[field] = {
                    '_prefix': prefixCombo,
                    'IDPart': IDEntry
                }

            elif field == 'politicalAffiliation':
                combo = ttk.Combobox(mainFrame, font=('微软雅黑', 11), width=35)
                combo['values'] = ('群众', '共青团员', '中共党员')
                combo.grid(row=row, column=1, pady=12, padx=(0, 20), sticky=tk.W)
                entries[field] = combo

            else:
                entry = tk.Entry(mainFrame, font=('微软雅黑', 11), width=37)
                entry.grid(row=row, column=1, pady=12, padx=(0, 20), sticky=tk.W)
                entries[field] = entry

            errorLabel = tk.Label(mainFrame, text="", font=('微软雅黑', 9),
                                  foreground='red', wraplength=400,
                                  bg='#F8F9FA')
            errorLabel.grid(row=row + 1, column=1, sticky=tk.W, padx=(0, 20), pady=(0, 5))
            errorLabels[field] = errorLabel
            errorLabel.grid_remove()

            if default and field in default:
                defaultValue = default[field]
                if field == 'sex' or field == 'politicalAffiliation':
                    entries[field].set(defaultValue)
                elif field == 'birth':
                    date_obj = self.parseDateFromString(defaultValue)
                    if date_obj:
                        entries[field].set_date(date_obj)
                elif field == 'schoolRoll':
                    try:
                        if defaultValue and len(defaultValue) > 1:
                            prefix = defaultValue[0]
                            IDPart = defaultValue[1:]
                            entries[field]['_prefix'].set(prefix)
                            entries[field]['IDPart'].insert(0, IDPart)
                    except (IndexError, KeyError):
                        pass
                else:
                    entries[field].insert(0, defaultValue)

            row += 2

        result = {'confirmed': False, 'values': {}}

        def validateField(_field, value):
            # 输入验证
            try:
                if _field == 'name':
                    ic.checkName(value)
                elif _field == 'sex':
                    ic.checkSex(value)
                elif _field == 'birth':
                    ic.checkBirth(value)
                elif _field == 'ID':
                    ic.checkID(value)
                elif _field == 'schoolRoll':
                    ic.checkSchoolRoll(value)
                elif _field == 'politicalAffiliation':
                    ic.checkPoliticalAffiliation(value)
                return True, ""
            except StudentInfoException as err:
                return False, str(err)

        def validateAllFields(values):
            # 空值检测
            errors = []
            for _field, value in values.items():
                if not value:
                    errors.append((_field, f"{fields[_field]}不能为空"))
                else:
                    isValid, errorMsg = validateField(_field, value)
                    if not isValid:
                        errors.append((_field, errorMsg))
            return errors

        def clearErrorLabels():
            for _label in errorLabels.values():
                _label.grid_remove()

        def showFieldError(_field, errorMsg):
            clearErrorLabels()
            if _field in errorLabels:
                errorLabels[_field].config(text=errorMsg)
                errorLabels[_field].grid()

        def onConfirm():
            # 按下“确认”键时执行
            collectedValues = {}

            for _field, widget in entries.items():
                if _field == 'birth':
                    try:
                        dateClass = widget.get_date()
                        if dateClass:
                            collectedValues[_field] = Interface4Admin.formatDate4Display(dateClass)
                        else:
                            collectedValues[_field] = ''
                    except Exception as e:
                        print(f"获取出生日期时出错: {e}")
                        collectedValues[_field] = ''
                elif _field == 'schoolRoll':
                    _prefix = widget['_prefix'].get().strip()
                    _identifyPart = widget['IDPart'].get().strip()
                    if _prefix and _identifyPart:
                        collectedValues[_field] = f"{_prefix}{_identifyPart}"
                    else:
                        collectedValues[_field] = ''
                elif isinstance(widget, ttk.Combobox):
                    collectedValues[_field] = widget.get().strip()
                else:
                    collectedValues[_field] = widget.get().strip()

            errors = validateAllFields(collectedValues)

            if errors:
                errorField1st, errorMsg1st = errors[0]
                showFieldError(errorField1st, errorMsg1st)

                if len(errors) > 1:
                    print(f"发现多个错误: {errors}")
                return
            else:
                clearErrorLabels()
                result['values'] = collectedValues
                result['confirmed'] = True
                dialog.destroy()

        def onCancel():
            # 按下“取消”键时执行
            dialog.destroy()

        # 绘制确认键和取消键
        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.grid(row=row, column=0, columnspan=2, pady=(30, 20))

        confirmButton = tk.Button(buttonFrame, text='确 认', command=onConfirm,
                                  font=('微软雅黑', 11, 'bold'),
                                  bg='#28A745', fg='white',
                                  padx=25, pady=10,
                                  relief='raised', borderwidth=1,
                                  cursor='hand2')
        confirmButton.pack(side=tk.LEFT, padx=10)
        confirmButton.bind('<Enter>', lambda e: confirmButton.config(bg='#218838'))
        confirmButton.bind('<Leave>', lambda e: confirmButton.config(bg='#28A745'))

        cancelButton = tk.Button(buttonFrame, text='取 消', command=onCancel,
                                 font=('微软雅黑', 11),
                                 bg='#DC3545', fg='white',
                                 padx=25, pady=10,
                                 relief='raised', borderwidth=1,
                                 cursor='hand2')
        cancelButton.pack(side=tk.LEFT, padx=10)
        cancelButton.bind('<Enter>', lambda e: cancelButton.config(bg='#C82333'))
        cancelButton.bind('<Leave>', lambda e: cancelButton.config(bg='#DC3545'))

        dialog.bind('<Return>', lambda event: onConfirm())

        dialog.wait_window(dialog)
        return result

    def addStudentInfo(self):
        # 添加学生信息
        fields = {
            'name': '姓名：',
            'sex': '性别：',
            'birth': '出生日期：',
            'ID': '身份证号：',
            'schoolRoll': '学籍号：',
            'politicalAffiliation': '政治面貌：'
        }

        result = self.createStudentInputDialog('添加学生信息', fields)

        # 保存学生信息
        if result['confirmed']:
            values = result['values']
            try:
                student = StudentInfoFormat(
                    values['name'], values['sex'], values['birth'],
                    values['ID'], values['schoolRoll'], values['politicalAffiliation']
                )
                success, message = self.mgr.add(student)
                if success:
                    self.showMessage('成功', message)
                else:
                    self.showMessage('错误', message, 'error')

            except Exception as err:
                self.showMessage('系统错误', f'添加失败：{str(err)}', 'error')

    def deleteStudentInfo(self):
        # 删除学生信息
        studentList = self.mgr.displayStudent(onlyNameSwitch='on')
        if not studentList:
            self.showEmptyWarning()
            return

        # 删除学生信息窗口
        deleteWindow = tk.Toplevel(self.mainWindow)
        deleteWindow.title('删除学生信息')
        deleteWindow.geometry('600x600')
        deleteWindow.transient(self.mainWindow)
        deleteWindow.grab_set()

        deleteWindow.update_idletasks()
        x = self.mainWindow.winfo_x() + (self.mainWindow.winfo_width() - 400) // 2
        y = self.mainWindow.winfo_y() + (self.mainWindow.winfo_height() - 300) // 2
        deleteWindow.geometry(f'600x600+{x}+{y}')

        self.backgroundTheme.applyBackground(deleteWindow, 'dialog', 400, 300)

        mainFrame = tk.Frame(deleteWindow, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.9)

        titleLabel = tk.Label(mainFrame, text='选择要删除的学生',
                              font=('微软雅黑', 14, 'bold'),
                              bg='#F8F9FA')
        titleLabel.pack(pady=10)

        listboxFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        listboxFrame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listboxFrame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(listboxFrame, font=('微软雅黑', 11),
                             yscrollcommand=scrollbar.set,
                             bg='white', relief='sunken', borderwidth=1)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        for student in studentList:
            listbox.insert(tk.END, student)

        def onDelete():
            # 按下“删除”键时执行
            selection = listbox.curselection()
            if not selection:
                self.showMessage('警告', '请选择要删除的学生！', 'warning')
                return

            studentName = listbox.get(selection[0])
            if self.askYesOrNo('确认删除', f'确定要删除学生 "{studentName}" 吗？'):
                success, message = self.mgr.delete(studentName)
                if success:
                    self.showMessage('成功', message)
                    deleteWindow.destroy()
                else:
                    self.showMessage('错误', message, 'error')

        def onCancel():
            # 按下“删除”键时执行
            deleteWindow.destroy()

        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.pack(pady=10)

        deleteButton = tk.Button(buttonFrame, text='删除', command=onDelete,
                                 font=('微软雅黑', 11),
                                 bg='#DC3545', fg='white',
                                 padx=20, pady=8,
                                 relief='raised', borderwidth=1)
        deleteButton.grid(row=0, column=0, padx=5)
        deleteButton.bind('<Enter>', lambda e: deleteButton.config(bg='#C82333'))
        deleteButton.bind('<Leave>', lambda e: deleteButton.config(bg='#DC3545'))

        cancelButton = tk.Button(buttonFrame, text='取消', command=onCancel,
                                 font=('微软雅黑', 11),
                                 bg='#6C757D', fg='white',
                                 padx=20, pady=8,
                                 relief='raised', borderwidth=1)
        cancelButton.grid(row=0, column=1, padx=5)
        cancelButton.bind('<Enter>', lambda e: cancelButton.config(bg='#545B62'))
        cancelButton.bind('<Leave>', lambda e: cancelButton.config(bg='#6C757D'))

    def modifyStudentInfo(self):
        # 修改学生信息
        studentList = self.mgr.displayStudent(onlyNameSwitch='on')
        if not studentList:
            self.showEmptyWarning()
            return

        # 修改学生信息窗口
        selectWindow = tk.Toplevel(self.mainWindow)
        selectWindow.title('选择要修改的学生')
        selectWindow.geometry('600x600')
        selectWindow.transient(self.mainWindow)
        selectWindow.grab_set()

        selectWindow.update_idletasks()
        x = self.mainWindow.winfo_x() + (self.mainWindow.winfo_width() - 400) // 2
        y = self.mainWindow.winfo_y() + (self.mainWindow.winfo_height() - 300) // 2
        selectWindow.geometry(f'600x600+{x}+{y}')

        self.backgroundTheme.applyBackground(selectWindow, 'dialog', 400, 300)

        mainFrame = tk.Frame(selectWindow, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.9)

        titleLabel = tk.Label(mainFrame, text='选择要修改的学生',
                              font=('微软雅黑', 14, 'bold'),
                              bg='#F8F9FA')
        titleLabel.pack(pady=10)

        listboxFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        listboxFrame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listboxFrame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(listboxFrame, font=('微软雅黑', 11),
                             yscrollcommand=scrollbar.set,
                             bg='white', relief='sunken', borderwidth=1)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        for student in studentList:
            listbox.insert(tk.END, student)

        def onSelect():
            # 按下“确认”键后执行
            selection = listbox.curselection()
            if not selection:
                self.showMessage('警告', '请选择要修改的学生！', 'warning')
                return

            student_name = listbox.get(selection[0])
            selectWindow.destroy()

            # 修改学生信息代码
            student_info = self.mgr.getStudentByName(student_name)
            if student_info:
                fields = {
                    'name': '姓名：',
                    'sex': '性别：',
                    'birth': '出生日期：',
                    'ID': '身份证号：',
                    'schoolRoll': '学籍号：',
                    'politicalAffiliation': '政治面貌：'
                }

                default_values = {
                    'name': student_name,
                    'sex': student_info['sex'],
                    'birth': student_info['birth'],
                    'ID': student_info['id_card'],
                    'schoolRoll': student_info['school_roll'],
                    'politicalAffiliation': student_info['political_affiliation']
                }

                result = self.createStudentInputDialog('修改学生信息', fields, default_values)

                if result['confirmed']:
                    values = result['values']
                    try:
                        _student = StudentInfoFormat(
                            values['name'], values['sex'], values['birth'],
                            values['ID'], values['schoolRoll'], values['politicalAffiliation']
                        )
                        success, message = self.mgr.change(_student)
                        if success:
                            self.showMessage('成功', message)
                        else:
                            self.showMessage('错误', message, 'error')

                    except Exception as err:
                        self.showMessage('系统错误', f'修改失败：{str(err)}', 'error')

        def onCancel():
            selectWindow.destroy()

        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.pack(pady=10)

        select_btn = tk.Button(buttonFrame, text='选择', command=onSelect,
                               font=('微软雅黑', 11),
                               bg='#007BFF', fg='white',
                               padx=20, pady=8,
                               relief='raised', borderwidth=1)
        select_btn.grid(row=0, column=0, padx=5)
        select_btn.bind('<Enter>', lambda e: select_btn.config(bg='#0056B3'))
        select_btn.bind('<Leave>', lambda e: select_btn.config(bg='#007BFF'))

        cancelButton = tk.Button(buttonFrame, text='取消', command=onCancel,
                                 font=('微软雅黑', 11),
                                 bg='#6C757D', fg='white',
                                 padx=20, pady=8,
                                 relief='raised', borderwidth=1)
        cancelButton.grid(row=0, column=1, padx=5)
        cancelButton.bind('<Enter>', lambda e: cancelButton.config(bg='#545B62'))
        cancelButton.bind('<Leave>', lambda e: cancelButton.config(bg='#6C757D'))

    def displayStudentInfo(self):
        # 显示学生信息
        if self.checkEmptyStudents():  # 确认数据库中学生信息是否为空
            self.showEmptyWarning()
        else:
            # 显示学生信息窗口
            displayWindow = tk.Toplevel(self.mainWindow)
            displayWindow.title('学生信息列表')
            displayWindow.geometry('1000x700')
            displayWindow.transient(self.mainWindow)

            displayWindow.update_idletasks()
            x = self.mainWindow.winfo_x() + (self.mainWindow.winfo_width() - 1000) // 2
            y = self.mainWindow.winfo_y() + (self.mainWindow.winfo_height() - 700) // 2
            displayWindow.geometry(f'1000x700+{x}+{y}')

            self.backgroundTheme.applyBackground(displayWindow, 'dialog', 1000, 700)

            mainFrame = tk.Frame(displayWindow, bg='#F8F9FA', relief='raised', borderwidth=1)
            mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.95, relheight=0.9)

            titleLabel = tk.Label(mainFrame, text='学生信息列表',
                                  font=('微软雅黑', 16, 'bold'),
                                  bg='#F8F9FA')
            titleLabel.pack(pady=15)

            textFrame = tk.Frame(mainFrame, bg='#F8F9FA')
            textFrame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

            textWidget = scrolledtext.ScrolledText(textFrame, wrap=tk.WORD,
                                                   font=('微软雅黑', 11),
                                                   bg='white',
                                                   relief='sunken',
                                                   borderwidth=2)
            textWidget.pack(fill=tk.BOTH, expand=True)

            studentText = self.mgr.displayStudent()
            textWidget.insert(tk.END, studentText)

            textWidget.config(state=tk.DISABLED)

            closeButton = tk.Button(mainFrame, text='关闭',
                                    command=displayWindow.destroy,
                                    font=('微软雅黑', 11),
                                    bg='#6C757D', fg='white',
                                    padx=25, pady=10,
                                    relief='raised', borderwidth=1)
            closeButton.pack(pady=10)
            closeButton.bind('<Enter>', lambda e: closeButton.config(bg='#5A6268'))
            closeButton.bind('<Leave>', lambda e: closeButton.config(bg='#6C757D'))

    def exportStudentInfo(self):
        # 导出学生信息
        if self.checkEmptyStudents():  # 检测数据库中学生信息是否为空
            self.showEmptyWarning()
        else:
            # 调用formalExport()函数导出
            self.formalExport()

    def functionView(self):
        # 管理员界面
        self.createMainWindow('管理员')

        # 绘制管理员界面
        mainFrame = tk.Frame(self.mainWindow, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.85)

        titleLabel = tk.Label(mainFrame, text='学生信息管理系统 - 管理员',
                              font=('微软雅黑', 18, 'bold'),
                              bg='#F8F9FA')
        titleLabel.pack(pady=(20, 10))

        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.pack(expand=True)

        functions = [
            ('添加学生信息', self.addStudentInfo, '#28A745'),
            ('删除学生信息', self.deleteStudentInfo, '#DC3545'),
            ('修改学生信息', self.modifyStudentInfo, '#FFC107'),
            ('查询所有学生信息', self.displayStudentInfo, '#17A2B8'),
            ('导出学生信息', self.exportStudentInfo, '#6C757D'),
            ('统计信息', self.showStatistics, '#6610F2'),
            ('用户管理', self.showUserManagement, '#20C997'),
            ('退出系统', self.exitSys, '#343A40')
        ]

        for i, (text, command, color) in enumerate(functions):
            button = tk.Button(buttonFrame, text=text, command=command,
                               font=('微软雅黑', 11),
                               bg=color, fg='white',
                               padx=30, pady=15,
                               relief='raised', borderwidth=2,
                               cursor='hand2')
            button.grid(row=i // 2, column=i % 2, padx=15, pady=10, sticky='nsew')

            button.bind('<Enter>', lambda e, b=button: b.config(bg='#4A90E2'))
            button.bind('<Leave>', lambda e, b=button, c=color: b.config(bg=c))

            buttonFrame.columnconfigure(i % 2, weight=1)

        buttonFrame.rowconfigure(len(functions) // 2, weight=1)

        self.mainWindow.mainloop()

    def showStatistics(self):
        # 统计学生信息
        statistics = self.mgr.getStatistics()

        # 统计学生信息界面
        statisticsWindow = tk.Toplevel(self.mainWindow)
        statisticsWindow.title('统计信息')
        statisticsWindow.geometry('600x500')
        statisticsWindow.transient(self.mainWindow)

        statisticsWindow.update_idletasks()
        x = self.mainWindow.winfo_x() + (self.mainWindow.winfo_width() - 600) // 2
        y = self.mainWindow.winfo_y() + (self.mainWindow.winfo_height() - 500) // 2
        statisticsWindow.geometry(f'600x500+{x}+{y}')

        self.backgroundTheme.applyBackground(statisticsWindow, 'dialog', 600, 500)

        mainFrame = tk.Frame(statisticsWindow, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.9)

        titleLabel = tk.Label(mainFrame, text='学生信息统计',
                              font=('微软雅黑', 16, 'bold'),
                              bg='#F8F9FA')
        titleLabel.pack(pady=20)

        statistics_frame = tk.Frame(mainFrame, bg='#F8F9FA')
        statistics_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        totalFrame = tk.Frame(statistics_frame, bg='#F8F9FA')
        totalFrame.pack(fill=tk.X, pady=10)

        totalIco = tk.Label(totalFrame, text='', font=('Arial', 24),
                            bg='#F8F9FA')
        totalIco.pack(side=tk.LEFT, padx=(0, 15))

        # 统计学生总数
        totalText = tk.Label(totalFrame,
                             text=f'学生总数：{statistics["total"]}',
                             font=('微软雅黑', 16),
                             bg='#F8F9FA',
                             fg='#343A40')
        totalText.pack(side=tk.LEFT)

        # 统计性别分布
        sexFrame = tk.Frame(statistics_frame, bg='#F8F9FA')
        sexFrame.pack(fill=tk.X, pady=15)

        sexTitle = tk.Label(sexFrame, text='性别分布：',
                            font=('微软雅黑', 14, 'bold'),
                            bg='#F8F9FA')
        sexTitle.pack(anchor=tk.W, pady=(0, 10))

        if statistics['sexStatistics']:
            for sex, count in statistics['sexStatistics'].items():
                sexItemFrame = tk.Frame(sexFrame, bg='#F8F9FA')
                sexItemFrame.pack(fill=tk.X, pady=5)

                sexIco = ''
                sexLabel = tk.Label(sexItemFrame, text=sexIco,
                                    font=('Arial', 18),
                                    bg='#F8F9FA')
                sexLabel.pack(side=tk.LEFT, padx=(20, 15))

                sexText = tk.Label(sexItemFrame,
                                   text=f'{sex}：{count}人 ({count / statistics["total"] * 100:.1f}%)',
                                   font=('微软雅黑', 12),
                                   bg='#F8F9FA')
                sexText.pack(side=tk.LEFT)

        # 统计政治面貌分布
        politicalAffiliationFrame = tk.Frame(statistics_frame, bg='#F8F9FA')
        politicalAffiliationFrame.pack(fill=tk.X, pady=15)

        politicalAffiliationTitle = tk.Label(politicalAffiliationFrame, text='政治面貌分布：',
                                             font=('微软雅黑', 14, 'bold'),
                                             bg='#F8F9FA')
        politicalAffiliationTitle.pack(anchor=tk.W, pady=(0, 10))

        politicalAffiliationIcos = {
            '群众': '',
            '共青团员': '',
            '中共党员': ''
        }

        if statistics['politicalAffiliationStatistics']:
            for politicalAffiliation, count in statistics['politicalAffiliationStatistics'].items():
                politicalAffiliationItemFrame = tk.Frame(politicalAffiliationFrame, bg='#F8F9FA')
                politicalAffiliationItemFrame.pack(fill=tk.X, pady=5)

                icon = politicalAffiliationIcos.get(politicalAffiliation, '')
                politicalAffiliationLabel = tk.Label(politicalAffiliationItemFrame, text=icon,
                                                     font=('Arial', 18),
                                                     bg='#F8F9FA')
                politicalAffiliationLabel.pack(side=tk.LEFT, padx=(20, 15))

                politicalAffiliationText = tk.Label(politicalAffiliationItemFrame,
                                                    text=f'{politicalAffiliation}：{count}人 ({count / statistics["total"] * 100:.1f}%)',
                                                    font=('微软雅黑', 12),
                                                    bg='#F8F9FA')
                politicalAffiliationText.pack(side=tk.LEFT)

        # 关闭按键
        closeButton = tk.Button(mainFrame, text='关闭',
                                command=statisticsWindow.destroy,
                                font=('微软雅黑', 11),
                                bg='#6C757D', fg='white',
                                padx=25, pady=10,
                                relief='raised', borderwidth=1)
        closeButton.pack(pady=20)
        closeButton.bind('<Enter>', lambda e: closeButton.config(bg='#5A6268'))
        closeButton.bind('<Leave>', lambda e: closeButton.config(bg='#6C757D'))

    def showUserManagement(self):
        # 显示用户管理界面
        user_mgr_gui = UserManagementGUI(self.mainWindow, "admin")
        user_mgr_gui.showUserManagement()


class Interface4User(BaseInterface):
    """普通用户界面"""

    def __init__(self, ver, username):
        super().__init__(ver, username)
        self.currentUsername = username

    def displayStudentInfo(self):
        # 显示学生信息
        if self.checkEmptyStudents():  # 检查数据库学生信息是否为空
            self.showEmptyWarning()
        else:
            # 绘制显示学生信息窗口
            displayWindow = tk.Toplevel(self.mainWindow)
            displayWindow.title('学生信息列表')
            displayWindow.geometry('1000x700')
            displayWindow.transient(self.mainWindow)

            displayWindow.update_idletasks()
            x = self.mainWindow.winfo_x() + (self.mainWindow.winfo_width() - 1000) // 2
            y = self.mainWindow.winfo_y() + (self.mainWindow.winfo_height() - 700) // 2
            displayWindow.geometry(f'1000x700+{x}+{y}')

            self.backgroundTheme.applyBackground(displayWindow, 'dialog', 1000, 700)

            mainFrame = tk.Frame(displayWindow, bg='#F8F9FA', relief='raised', borderwidth=1)
            mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.95, relheight=0.9)

            titleLabel = tk.Label(mainFrame, text='学生信息列表',
                                  font=('微软雅黑', 16, 'bold'),
                                  bg='#F8F9FA')
            titleLabel.pack(pady=15)

            textFrame = tk.Frame(mainFrame, bg='#F8F9FA')
            textFrame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

            textWidget = scrolledtext.ScrolledText(textFrame, wrap=tk.WORD,
                                                   font=('微软雅黑', 11),
                                                   bg='white',
                                                   relief='sunken',
                                                   borderwidth=2)
            textWidget.pack(fill=tk.BOTH, expand=True)

            studentText = self.mgr.displayStudent()
            textWidget.insert(tk.END, studentText)

            textWidget.config(state=tk.DISABLED)

            closeButton = tk.Button(mainFrame, text='关闭',
                                    command=displayWindow.destroy,
                                    font=('微软雅黑', 11),
                                    bg='#6C757D', fg='white',
                                    padx=25, pady=10,
                                    relief='raised', borderwidth=1)
            closeButton.pack(pady=10)
            closeButton.bind('<Enter>', lambda e: closeButton.config(bg='#5A6268'))
            closeButton.bind('<Leave>', lambda e: closeButton.config(bg='#6C757D'))

    def changePassword(self):
        """普通用户修改自己的密码"""
        dialog = tk.Toplevel(self.mainWindow)
        dialog.title("修改密码")
        dialog.geometry("400x300")
        dialog.transient(self.mainWindow)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.mainWindow.winfo_x() + (self.mainWindow.winfo_width() - 400) // 2
        y = self.mainWindow.winfo_y() + (self.mainWindow.winfo_height() - 300) // 2
        dialog.geometry(f'400x300+{x}+{y}')

        self.backgroundTheme.applyBackground(dialog, 'dialog', 400, 300)

        mainFrame = tk.Frame(dialog, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.85)

        # 标题
        titleLabel = tk.Label(mainFrame, text="修改密码",
                              font=('微软雅黑', 14, 'bold'),
                              bg='#F8F9FA')
        titleLabel.pack(pady=10)

        # 当前用户信息
        userLabel = tk.Label(mainFrame, text=f"用户: {self.currentUsername}",
                             font=('微软雅黑', 11),
                             bg='#F8F9FA', fg='#6C757D')
        userLabel.pack(pady=5)

        # 输入框框架
        inputFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        inputFrame.pack(pady=15)

        # 旧密码
        tk.Label(inputFrame, text="旧密码:", bg='#F8F9FA',
                 font=('微软雅黑', 11)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        oldPwdEntry = tk.Entry(inputFrame, font=('微软雅黑', 11), width=20, show='•')
        oldPwdEntry.grid(row=0, column=1, padx=5, pady=5)

        # 新密码
        tk.Label(inputFrame, text="新密码:", bg='#F8F9FA',
                 font=('微软雅黑', 11)).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        newPwdEntry = tk.Entry(inputFrame, font=('微软雅黑', 11), width=20, show='•')
        newPwdEntry.grid(row=1, column=1, padx=5, pady=5)

        # 确认新密码
        tk.Label(inputFrame, text="确认新密码:", bg='#F8F9FA',
                 font=('微软雅黑', 11)).grid(row=2, column=0, padx=5, pady=5, sticky='e')
        confirmEntry = tk.Entry(inputFrame, font=('微软雅黑', 11), width=20, show='•')
        confirmEntry.grid(row=2, column=1, padx=5, pady=5)

        # 消息标签
        msgLable = tk.Label(mainFrame, text="", font=('微软雅黑', 10),
                            bg='#F8F9FA', fg='red')
        msgLable.pack(pady=5)

        def executeChange():
            """执行密码修改"""
            oldPwd = oldPwdEntry.get()
            newPwd = newPwdEntry.get()
            confirmPwd = confirmEntry.get()

            # 验证输入
            if not oldPwd or not newPwd or not confirmPwd:
                msgLable.config(text="所有字段都必须填写！")
                return

            if newPwd != confirmPwd:
                msgLable.config(text="新密码和确认密码不一致！")
                return

            # 调用UserManager修改密码
            try:
                usrMgr = UserManager()
                success, msg = usrMgr.changePassword(
                    self.currentUsername, oldPwd, newPwd
                )

                if success:
                    msgLable.config(text=msg, fg='green')
                    # 延迟关闭对话框
                    dialog.after(1500, dialog.destroy)
                else:
                    msgLable.config(text=msg)
            except Exception as e:
                msgLable.config(text=f"修改失败: {str(e)}")

        # 按钮框架
        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.pack(pady=10)

        changeButton = tk.Button(buttonFrame, text="修改", command=executeChange,
                                 font=('微软雅黑', 11), bg='#28A745', fg='white',
                                 padx=20, pady=8, relief='raised', borderwidth=1,
                                 cursor='hand2')
        changeButton.pack(side=tk.LEFT, padx=5)
        changeButton.bind('<Enter>', lambda e: changeButton.config(bg='#218838'))
        changeButton.bind('<Leave>', lambda e: changeButton.config(bg='#28A745'))

        cancelButton = tk.Button(buttonFrame, text="取消", command=dialog.destroy,
                                 font=('微软雅黑', 11), bg='#6C757D', fg='white',
                                 padx=20, pady=8, relief='raised', borderwidth=1,
                                 cursor='hand2')
        cancelButton.pack(side=tk.LEFT, padx=5)
        cancelButton.bind('<Enter>', lambda e: cancelButton.config(bg='#5A6268'))
        cancelButton.bind('<Leave>', lambda e: cancelButton.config(bg='#6C757D'))

        # 绑定回车键
        dialog.bind('<Return>', lambda event: executeChange())

    def exportStudentInfo(self):
        # 导出学生信息
        if self.checkEmptyStudents():  # 检查数据库学生信息是否为空
            self.showEmptyWarning()
        else:
            # 调用formalExport()函数导出
            self.formalExport()

    def functionView(self):
        # 普通用户操作界面
        self.createMainWindow('普通用户')

        # 绘制普通用户操作界面窗口
        mainFrame = tk.Frame(self.mainWindow, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.85)

        titleLabel = tk.Label(mainFrame, text='学生信息管理系统 - 普通用户',
                              font=('微软雅黑', 18, 'bold'),
                              bg='#F8F9FA')
        titleLabel.pack(pady=(20, 10))

        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.pack(expand=True)

        # 普通用户界面选项
        functions = [
            ('查询所有学生信息', self.displayStudentInfo, '#17A2B8'),
            ('修改密码', self.changePassword, '#20C997'),
            ('退出系统', self.exitSys, '#343A40')
        ]

        for i, (text, command, color) in enumerate(functions):
            button = tk.Button(buttonFrame, text=text, command=command,
                               font=('微软雅黑', 12),
                               bg=color, fg='white',
                               padx=40, pady=20,
                               relief='raised', borderwidth=2,
                               cursor='hand2')
            button.grid(row=i, column=0, padx=10, pady=15, sticky='nsew')

            button.bind('<Enter>', lambda e, b=button: b.config(bg='#4A90E2'))
            button.bind('<Leave>', lambda e, b=button, c=color: b.config(bg=c))

            buttonFrame.rowconfigure(i, weight=1)

        buttonFrame.columnconfigure(0, weight=1)

        self.mainWindow.mainloop()


# 测试区域，可忽略
if __name__ == '__main__':
    Interface4Admin('1', 'admin').functionView()
