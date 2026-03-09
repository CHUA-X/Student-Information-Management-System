#!/usr/bin/python3

import sys
import shelve
import secrets
import tkinter as tk
from pathlib import Path
from pysmx.SM3 import hash_msg
from tkinter import messagebox, ttk
from background import BackgroundManager


class SignIn:
    """登录学生信息管理系统"""

    def __init__(self, ver):
        self.ver = ver
        self.userDbPath = Path('data/users')
        self.backgroundTheme = BackgroundManager('custom')
        self.initUserDatabase()

    def initUserDatabase(self):
        """设置默认账号密码"""
        self.userDbPath.parent.mkdir(parents=True, exist_ok=True)  # 确保data目录存在

        defaultUsers = {
            'admin': {
                '用户名': 'admin',
                '密码': 'admin',
                '身份': 'administrator',
                '描述': '系统管理员'
            },
            'user': {
                '用户名': 'user',
                '密码': '12345678',
                '身份': 'user',
                '描述': '普通用户'
            }
        }

        try:
            # 建立含加盐SM3后的账号密码的Shelve数据库
            with shelve.open(str(self.userDbPath)) as db:
                if 'initialized' not in db:
                    print("初始化用户数据库...")
                    for usernameKey, userInfo in defaultUsers.items():
                        salt = self.generateSalt(32)

                        encryptedUsername = self.SM3WithSalt(userInfo['用户名'], salt)
                        encryptedPassword = self.SM3WithSalt(userInfo['密码'], salt)

                        db[usernameKey] = {
                            'salt': salt.hex(),
                            'usernameHash': encryptedUsername[64:],
                            'passwordHash': encryptedPassword[64:],
                            'role': userInfo['身份'],
                            'description': userInfo['描述']
                        }
                        print(f"创建用户: {usernameKey} ({userInfo['描述']})")

                    db['initialized'] = True
                    print("用户数据库初始化完成。")
        except Exception as e:
            print(f"初始化用户数据库失败: {e}")

    @staticmethod
    def generateSalt(length=32):
        """盐值生成"""
        return secrets.token_bytes(length)

    @staticmethod
    def SM3WithSalt(data, salt):
        """加盐SM3生成"""
        integratedStr = data.encode('utf-8') + salt
        SM3Hash = hash_msg(integratedStr)
        return salt.hex() + SM3Hash

    def verifyUser(self, inputUsername, inputPassword):
        """账号密码登录验证"""
        try:
            with shelve.open(str(self.userDbPath)) as db:
                if inputUsername not in db:
                    return False, None

                usrInfo = db[inputUsername]

                saltHex = usrInfo['salt']
                salt = bytes.fromhex(saltHex)

                integratedUsername = inputUsername.encode('utf-8') + salt
                computedUsernameHash = hash_msg(integratedUsername)

                integratedPassword = inputPassword.encode('utf-8') + salt
                computedPasswordHash = hash_msg(integratedPassword)

                if (computedUsernameHash == usrInfo['usernameHash'] and
                        computedPasswordHash == usrInfo['passwordHash']):
                    return True, usrInfo['role']
                else:
                    return False, None
        except Exception as e:
            print(f"验证用户失败: {e}")
            return False, None

    def createLoginWindow(self):
        """登录界面窗口"""
        loginWindow = tk.Tk()
        loginWindow.title(f'学生信息管理系统 {self.ver}')
        loginWindow.geometry('500x400')
        loginWindow.resizable(False, False)

        screenWidth = loginWindow.winfo_screenwidth()
        screenHeight = loginWindow.winfo_screenheight()
        x = (screenWidth - 500) // 2
        y = (screenHeight - 400) // 2
        loginWindow.geometry(f'500x400+{x}+{y}')

        self.backgroundTheme.applyBackground(loginWindow, 'login', 500, 400)

        # 组件设置
        mainFrame = tk.Frame(loginWindow, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.8, relheight=0.75)

        titleLabel = tk.Label(mainFrame, text='学生信息管理系统',
                              font=('微软雅黑', 18, 'bold'),
                              bg='#F8F9FA')
        titleLabel.pack(pady=(20, 10))

        verLabel = tk.Label(mainFrame, text=f'版本 {self.ver}',
                            font=('微软雅黑', 9),
                            bg='#F8F9FA',
                            fg='#6C757D')
        verLabel.pack(pady=(0, 20))

        # 标签左对齐、输入框右对齐
        inputFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        inputFrame.pack(pady=10)

        # 用户名标签和输入框
        usernameLabel = tk.Label(inputFrame, text='用户名:',
                                 font=('微软雅黑', 11),
                                 bg='#F8F9FA',
                                 anchor='w')  # 左对齐
        usernameLabel.grid(row=0, column=0, padx=(10, 5), pady=5, sticky='w')

        usernameVar = tk.StringVar()
        usernameEntry = tk.Entry(inputFrame, textvariable=usernameVar,
                                 font=('微软雅黑', 11), width=22)
        usernameEntry.grid(row=0, column=1, padx=(5, 10), pady=5, sticky='e')
        usernameEntry.focus_set()

        # 密码标签和输入框
        passwordLabel = tk.Label(inputFrame, text='密码:',
                                 font=('微软雅黑', 11),
                                 bg='#F8F9FA',
                                 anchor='w')  # 左对齐
        passwordLabel.grid(row=1, column=0, padx=(10, 5), pady=5, sticky='w')

        passwordVar = tk.StringVar()
        passwordEntry = tk.Entry(inputFrame, textvariable=passwordVar,
                                 font=('微软雅黑', 11), width=22, show='•')
        passwordEntry.grid(row=1, column=1, padx=(5, 10), pady=5, sticky='e')

        # 配置grid列
        inputFrame.columnconfigure(0, weight=1)  # 标签列左对齐
        inputFrame.columnconfigure(1, weight=1)  # 输入框列右对齐

        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.pack(pady=20)

        def onLogin():
            # 按下"登录"键时执行行为
            username = usernameVar.get().strip()
            password = passwordVar.get().strip()

            if not username or not password:
                messagebox.showerror('错误', '用户名和密码不能为空！')
                return

            isValid, role = self.verifyUser(username, password)

            if isValid:
                loginWindow.destroy()
                if role == 'administrator':
                    from homepage import Interface4Admin
                    ctrl = Interface4Admin(self.ver, username)
                    ctrl.functionView()
                else:
                    from homepage import Interface4User
                    ctrl = Interface4User(self.ver, username)
                    ctrl.functionView()
            else:
                messagebox.showerror('错误', '用户名或密码错误！')
                passwordVar.set('')
                passwordEntry.focus_set()

        def onExit():
            # 按下"退出"键时执行行为
            if messagebox.askyesno('确认退出', '确定要退出学生信息管理系统吗？'):
                loginWindow.withdraw()
                loginWindow.destroy()
                messagebox.showinfo('系统退出', '感谢使用学生信息管理系统！')
                sys.exit()

        # 登录按键
        loginButton = tk.Button(buttonFrame, text='登 录', command=onLogin,
                                font=('微软雅黑', 11, 'bold'),
                                bg='#007BFF', fg='white',
                                padx=20, pady=6,
                                relief='raised', borderwidth=1,
                                cursor='hand2')
        loginButton.grid(row=0, column=0, padx=10)
        loginButton.bind('<Enter>', lambda e: loginButton.config(bg='#0056B3'))
        loginButton.bind('<Leave>', lambda e: loginButton.config(bg='#007BFF'))

        # 退出按键
        exitButton = tk.Button(buttonFrame, text='退 出', command=onExit,
                               font=('微软雅黑', 11),
                               bg='#6C757D', fg='white',
                               padx=20, pady=6,
                               relief='raised', borderwidth=1,
                               cursor='hand2')
        exitButton.grid(row=0, column=1, padx=10)
        exitButton.bind('<Enter>', lambda e: exitButton.config(bg='#545B62'))
        exitButton.bind('<Leave>', lambda e: exitButton.config(bg='#6C757D'))

        loginWindow.bind('<Return>', lambda event: onLogin())

        loginWindow.protocol("WM_DELETE_WINDOW", onExit)

        return loginWindow

    # 执行显示登录界面
    def verify(self):
        signInWindow = self.createLoginWindow()
        signInWindow.mainloop()


class UserManager:
    def __init__(self):
        self.userDbPath = Path('data/users')

    def addUser(self, username, password, role='user', description='普通用户'):
        """添加用户"""
        try:
            with shelve.open(str(self.userDbPath)) as db:
                if username in db:
                    return False, f"用户 '{username}' 已存在！"

                salt = secrets.token_bytes(32)

                # 使用SignIn类的静态方法进行加密
                encryptedUsername = SignIn.SM3WithSalt(username, salt)
                encryptedPassword = SignIn.SM3WithSalt(password, salt)

                db[username] = {
                    'salt': salt.hex(),
                    'usernameHash': encryptedUsername[64:],
                    'passwordHash': encryptedPassword[64:],
                    'role': role,
                    'description': description
                }

                return True, f"用户 '{username}' 创建成功！"
        except Exception as e:
            return False, f"添加用户失败: {str(e)}"

    def deleteUser(self, username):
        """删除用户"""
        try:
            with shelve.open(str(self.userDbPath)) as db:
                if username not in db:
                    return False, f"用户 '{username}' 不存在！"

                # 防止删除最后一个管理员
                if db[username].get('role') == 'administrator':
                    adminNum = 0
                    for key in db:
                        if key != 'initialized' and db[key].get('role') == 'administrator':
                            adminNum += 1

                    if adminNum <= 1:
                        return False, "不能删除最后一个管理员账户！"

                del db[username]
                return True, f"用户 '{username}' 删除成功！"
        except Exception as e:
            return False, f"删除用户失败: {str(e)}"

    def changePassword(self, username, oldPwd, newPwd):
        """修改密码（需要验证旧密码）"""
        try:
            with shelve.open(str(self.userDbPath)) as db:
                if username not in db:
                    return False, f"用户 '{username}' 不存在！"

                userInfo = db[username]

                # 验证旧密码
                salt = bytes.fromhex(userInfo['salt'])
                integratedOldPwd = oldPwd.encode('utf-8') + salt
                computedOldHash = hash_msg(integratedOldPwd)

                if computedOldHash != userInfo['passwordHash']:
                    return False, "旧密码不正确！"

                # 生成新密码哈希
                integratedNewPwd = newPwd.encode('utf-8') + salt
                newPwdHash = hash_msg(integratedNewPwd)

                # 更新密码哈希
                userInfo['passwordHash'] = newPwdHash
                db[username] = userInfo

                return True, "密码修改成功！"
        except Exception as e:
            return False, f"修改密码失败: {str(e)}"

    def resetPassword(self, username, newPwd):
        """重置密码"""
        try:
            with shelve.open(str(self.userDbPath)) as db:
                if username not in db:
                    return False, f"用户 '{username}' 不存在！"

                userInfo = db[username]

                # 检查是否为管理员账户
                if userInfo.get('role') == 'administrator':
                    return False, "不能重置管理员账户的密码！管理员必须使用修改密码功能。"

                # 使用现有盐值生成新密码哈希
                salt = bytes.fromhex(userInfo['salt'])
                integratedNewPwd = newPwd.encode('utf-8') + salt
                newPwdHash = hash_msg(integratedNewPwd)

                # 更新密码哈希
                userInfo['passwordHash'] = newPwdHash
                db[username] = userInfo

                return True, f"用户 '{username}' 密码重置成功！"
        except Exception as e:
            return False, f"重置密码失败: {str(e)}"

    # noinspection PyBroadException
    def isAdmin(self, username):
        """检查用户是否为管理员"""
        try:
            with shelve.open(str(self.userDbPath)) as db:
                if username not in db:
                    return False
                userInfo = db[username]
                return userInfo.get('role') == 'administrator'
        except Exception:
            return False

    def listUsers(self):
        """获取用户列表"""
        try:
            with shelve.open(str(self.userDbPath)) as db:
                users = []
                for key in db:
                    if key != 'initialized':
                        userInfo = db[key]
                        users.append({
                            'username': key,
                            'role': userInfo.get('role', 'unknown'),
                            'description': userInfo.get('description', '无描述')
                        })
                return True, users
        except Exception as e:
            return False, f"获取用户列表失败: {str(e)}"

    def getUserInfo(self, username):
        """获取用户信息"""
        try:
            with shelve.open(str(self.userDbPath)) as db:
                if username not in db:
                    return False, f"用户 '{username}' 不存在！", None

                userInfo = db[username]
                info = {
                    'username': username,
                    'role': userInfo.get('role', 'unknown'),
                    'description': userInfo.get('description', '无描述'),
                    'created': userInfo.get('created', '未知')
                }
                return True, "获取用户信息成功", info
        except Exception as e:
            return False, f"获取用户信息失败: {str(e)}", None

    def updateUserRole(self, username, newRole, newDescription=None):
        """更新用户角色和描述"""
        try:
            with shelve.open(str(self.userDbPath)) as db:
                if username not in db:
                    return False, f"用户 '{username}' 不存在！"

                userInfo = db[username]

                # 防止修改最后一个管理员角色
                if userInfo.get('role') == 'administrator' and newRole != 'administrator':
                    adminCount = 0
                    for key in db:
                        if key != 'initialized' and db[key].get('role') == 'administrator':
                            adminCount += 1

                    if adminCount <= 1:
                        return False, "不能修改最后一个管理员账户的角色！"

                userInfo['role'] = newRole
                if newDescription:
                    userInfo['description'] = newDescription

                db[username] = userInfo
                return True, f"用户 '{username}' 角色更新成功！"
        except Exception as e:
            return False, f"更新用户角色失败: {str(e)}"


class UserManagementGUI:
    """用户管理图形界面"""

    def __init__(self, parentWindow, currentUser):
        self.parent = parentWindow
        self.currentUser = currentUser
        self.userMgr = UserManager()
        self.background = BackgroundManager('custom')

    def showUserManagement(self):
        """显示用户管理界面"""
        self.managementWindow = tk.Toplevel(self.parent)
        self.managementWindow.title("用户管理")
        self.managementWindow.geometry("800x600")
        self.managementWindow.resizable(True, True)

        # 居中窗口
        self.managementWindow.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 800) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 600) // 2
        self.managementWindow.geometry(f'800x600+{x}+{y}')

        self.background.applyBackground(self.managementWindow, 'dialog', 800, 600)

        # 主框架
        mainFrame = tk.Frame(self.managementWindow, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.95, relheight=0.9)

        # 标题
        titleLabel = tk.Label(mainFrame, text="用户管理",
                              font=('微软雅黑', 16, 'bold'),
                              bg='#F8F9FA')
        titleLabel.pack(pady=15)

        # 当前用户信息
        currentUserFrame = tk.Frame(mainFrame, bg='#E9ECEF', relief='sunken', borderwidth=1)
        currentUserFrame.pack(fill=tk.X, padx=20, pady=10)

        currentUserLabel = tk.Label(currentUserFrame,
                                    text=f"当前用户: {self.currentUser}",
                                    font=('微软雅黑', 10),
                                    bg='#E9ECEF')
        currentUserLabel.pack(pady=5)

        # 按钮框架
        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.pack(fill=tk.X, padx=20, pady=10)

        # 功能按钮
        functions = [
            ("添加用户", self.showAddUserDialog, '#28A745'),
            ("修改密码", self.showChangePasswordDialog, '#007BFF'),
            ("重置密码", self.showResetPasswordDialog, '#FFC107'),
            ("删除用户", self.showDeleteUserDialog, '#DC3545'),
            ("查看用户列表", self.showUserList, '#17A2B8'),
            ("返回", self.managementWindow.destroy, '#6C757D')
        ]

        for i, (text, command, color) in enumerate(functions):
            button = tk.Button(buttonFrame, text=text, command=command,
                               font=('微软雅黑', 10),
                               bg=color, fg='white',
                               padx=15, pady=8,
                               relief='raised', borderwidth=1,
                               cursor='hand2')
            button.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky='ew')
            button.bind('<Enter>', lambda e, b=button: b.config(bg='#4A90E2'))
            button.bind('<Leave>', lambda e, b=button, c=color: b.config(bg=c))

            buttonFrame.columnconfigure(i % 3, weight=1)

        # 用户列表显示区域
        self.listFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        self.listFrame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 初始显示用户列表
        self.showUserList()

    def showAddUserDialog(self):
        """显示添加用户对话框"""
        dialog = tk.Toplevel(self.managementWindow)
        dialog.title("添加用户")
        dialog.geometry("400x300")
        dialog.transient(self.managementWindow)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.managementWindow.winfo_x() + (self.managementWindow.winfo_width() - 400) // 2
        y = self.managementWindow.winfo_y() + (self.managementWindow.winfo_height() - 300) // 2
        dialog.geometry(f'400x300+{x}+{y}')

        self.background.applyBackground(dialog, 'dialog', 400, 300)

        mainFrame = tk.Frame(dialog, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.85)

        # 表单
        tk.Label(mainFrame, text="用户名:", bg='#F8F9FA', font=('微软雅黑', 11)).grid(row=0, column=0, padx=10, pady=10,
                                                                               sticky='e')
        usernameEntry = tk.Entry(mainFrame, font=('微软雅黑', 11), width=25)
        usernameEntry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(mainFrame, text="密码:", bg='#F8F9FA', font=('微软雅黑', 11)).grid(row=1, column=0, padx=10, pady=10,
                                                                              sticky='e')
        pwdEntry = tk.Entry(mainFrame, font=('微软雅黑', 11), width=25, show='•')
        pwdEntry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(mainFrame, text="确认密码:", bg='#F8F9FA', font=('微软雅黑', 11)).grid(row=2, column=0, padx=10, pady=10,
                                                                                sticky='e')
        confirmEntry = tk.Entry(mainFrame, font=('微软雅黑', 11), width=25, show='•')
        confirmEntry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(mainFrame, text="角色:", bg='#F8F9FA', font=('微软雅黑', 11)).grid(row=3, column=0, padx=10, pady=10,
                                                                              sticky='e')
        roleCombo = ttk.Combobox(mainFrame, font=('微软雅黑', 11), width=23, state='readonly')
        roleCombo['values'] = ('user', 'administrator')
        roleCombo.set('user')
        roleCombo.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(mainFrame, text="描述:", bg='#F8F9FA', font=('微软雅黑', 11)).grid(row=4, column=0, padx=10, pady=10,
                                                                              sticky='e')
        aboutEntry = tk.Entry(mainFrame, font=('微软雅黑', 11), width=25)
        aboutEntry.grid(row=4, column=1, padx=10, pady=10)

        def addUser():
            username = usernameEntry.get().strip()
            password = pwdEntry.get().strip()
            confirm = confirmEntry.get().strip()
            role = roleCombo.get()
            description = aboutEntry.get().strip() or f"{role}用户"

            if not username or not password:
                messagebox.showerror("错误", "用户名和密码不能为空！")
                return

            if password != confirm:
                messagebox.showerror("错误", "两次输入的密码不一致！")
                return

            success, msg = self.userMgr.addUser(username, password, role, description)
            if success:
                messagebox.showinfo("成功", msg)
                dialog.destroy()
                self.showUserList()
            else:
                messagebox.showerror("错误", msg)

        # 按钮
        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.grid(row=5, column=0, columnspan=2, pady=20)

        tk.Button(buttonFrame, text="添加", command=addUser,
                  font=('微软雅黑', 10), bg='#28A745', fg='white',
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(buttonFrame, text="取消", command=dialog.destroy,
                  font=('微软雅黑', 10), bg='#6C757D', fg='white',
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)

    def showChangePasswordDialog(self):
        """显示修改密码对话框"""
        dialog = tk.Toplevel(self.managementWindow)
        dialog.title("修改密码")
        dialog.geometry("400x250")
        dialog.transient(self.managementWindow)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.managementWindow.winfo_x() + (self.managementWindow.winfo_width() - 400) // 2
        y = self.managementWindow.winfo_y() + (self.managementWindow.winfo_height() - 250) // 2
        dialog.geometry(f'400x250+{x}+{y}')

        self.background.applyBackground(dialog, 'dialog', 400, 250)

        mainFrame = tk.Frame(dialog, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.85)

        # 表单
        tk.Label(mainFrame, text="用户名:", bg='#F8F9FA', font=('微软雅黑', 11)).grid(row=0, column=0, padx=10, pady=10,
                                                                               sticky='e')
        usernameEntry = tk.Entry(mainFrame, font=('微软雅黑', 11), width=25)
        usernameEntry.insert(0, self.currentUser)
        if self.currentUser:
            usernameEntry.config(state='readonly')
        usernameEntry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(mainFrame, text="旧密码:", bg='#F8F9FA', font=('微软雅黑', 11)).grid(row=1, column=0, padx=10, pady=10,
                                                                               sticky='e')
        oldEntry = tk.Entry(mainFrame, font=('微软雅黑', 11), width=25, show='•')
        oldEntry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(mainFrame, text="新密码:", bg='#F8F9FA', font=('微软雅黑', 11)).grid(row=2, column=0, padx=10, pady=10,
                                                                               sticky='e')
        newEntry = tk.Entry(mainFrame, font=('微软雅黑', 11), width=25, show='•')
        newEntry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(mainFrame, text="确认新密码:", bg='#F8F9FA', font=('微软雅黑', 11)).grid(row=3, column=0, padx=10, pady=10,
                                                                                 sticky='e')
        confirmEntry = tk.Entry(mainFrame, font=('微软雅黑', 11), width=25, show='•')
        confirmEntry.grid(row=3, column=1, padx=10, pady=10)

        def changePassword():
            username = usernameEntry.get().strip()
            oldPwd = oldEntry.get().strip()
            newPwd = newEntry.get().strip()
            confirm = confirmEntry.get().strip()

            if not oldPwd or not newPwd:
                messagebox.showerror("错误", "密码不能为空！")
                return

            if newPwd != confirm:
                messagebox.showerror("错误", "两次输入的新密码不一致！")
                return

            success, msg = self.userMgr.changePassword(username, oldPwd, newPwd)
            if success:
                messagebox.showinfo("成功", msg)
                dialog.destroy()
            else:
                messagebox.showerror("错误", msg)

        # 按钮
        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.grid(row=4, column=0, columnspan=2, pady=15)

        tk.Button(buttonFrame, text="修改", command=changePassword,
                  font=('微软雅黑', 10), bg='#007BFF', fg='white',
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(buttonFrame, text="取消", command=dialog.destroy,
                  font=('微软雅黑', 10), bg='#6C757D', fg='white',
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)

    def showResetPasswordDialog(self):
        """显示重置密码对话框"""
        dialog = tk.Toplevel(self.managementWindow)
        dialog.title("重置密码")
        dialog.geometry("400x200")
        dialog.transient(self.managementWindow)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.managementWindow.winfo_x() + (self.managementWindow.winfo_width() - 400) // 2
        y = self.managementWindow.winfo_y() + (self.managementWindow.winfo_height() - 200) // 2
        dialog.geometry(f'400x200+{x}+{y}')

        self.background.applyBackground(dialog, 'dialog', 400, 200)

        mainFrame = tk.Frame(dialog, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.85)

        # 表单
        tk.Label(mainFrame, text="用户名:", bg='#F8F9FA', font=('微软雅黑', 11)).grid(row=0, column=0, padx=10, pady=10,
                                                                               sticky='e')
        usernameEntry = tk.Entry(mainFrame, font=('微软雅黑', 11), width=25)
        usernameEntry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(mainFrame, text="新密码:", bg='#F8F9FA', font=('微软雅黑', 11)).grid(row=1, column=0, padx=10, pady=10,
                                                                               sticky='e')
        newEntry = tk.Entry(mainFrame, font=('微软雅黑', 11), width=25, show='•')
        newEntry.grid(row=1, column=1, padx=10, pady=10)

        def resetPassword():
            username = usernameEntry.get().strip()
            newPwd = newEntry.get().strip()

            if not username or not newPwd:
                messagebox.showerror("错误", "用户名和新密码不能为空！")
                return

            # 检查是否为管理员账户
            if self.userMgr.isAdmin(username):
                messagebox.showerror("错误", "不能重置管理员账户的密码！管理员必须使用修改密码功能。")
                return

            # 确认操作
            if not messagebox.askyesno("确认", f"确定要重置用户 '{username}' 的密码吗？"):
                return

            success, msg = self.userMgr.resetPassword(username, newPwd)
            if success:
                messagebox.showinfo("成功", msg)
                dialog.destroy()
            else:
                messagebox.showerror("错误", msg)

        # 按钮
        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.grid(row=2, column=0, columnspan=2, pady=15)

        tk.Button(buttonFrame, text="重置", command=resetPassword,
                  font=('微软雅黑', 10), bg='#FFC107', fg='white',
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(buttonFrame, text="取消", command=dialog.destroy,
                  font=('微软雅黑', 10), bg='#6C757D', fg='white',
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)

    def showDeleteUserDialog(self):
        """显示删除用户对话框"""
        # 获取用户列表
        success, users = self.userMgr.listUsers()
        if not success:
            messagebox.showerror("错误", users)
            return

        if not users:
            messagebox.showinfo("提示", "没有可删除的用户")
            return

        dialog = tk.Toplevel(self.managementWindow)
        dialog.title("删除用户")
        dialog.geometry("500x400")
        dialog.transient(self.managementWindow)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.managementWindow.winfo_x() + (self.managementWindow.winfo_width() - 500) // 2
        y = self.managementWindow.winfo_y() + (self.managementWindow.winfo_height() - 400) // 2
        dialog.geometry(f'500x400+{x}+{y}')

        self.background.applyBackground(dialog, 'dialog', 500, 400)

        mainFrame = tk.Frame(dialog, bg='#F8F9FA', relief='raised', borderwidth=1)
        mainFrame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.9)

        tk.Label(mainFrame, text="选择要删除的用户:",
                 font=('微软雅黑', 12, 'bold'),
                 bg='#F8F9FA').pack(pady=10)

        # 用户列表
        listFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        listFrame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(listFrame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        userListbox = tk.Listbox(listFrame, font=('微软雅黑', 11),
                                 yscrollcommand=scrollbar.set,
                                 bg='white', relief='sunken', borderwidth=1,
                                 selectmode=tk.SINGLE)
        userListbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=userListbox.yview)

        for user in users:
            display_text = f"{user['username']} - {user['role']} ({user['description']})"
            userListbox.insert(tk.END, display_text)
            userListbox.user_data = users  # 保存用户数据

        def deleteUser():
            selection = userListbox.curselection()
            if not selection:
                messagebox.showerror("错误", "请选择一个用户！")
                return

            index = selection[0]
            username = users[index]['username']

            # 防止删除当前用户
            if username == self.currentUser:
                messagebox.showerror("错误", "不能删除当前登录的用户！")
                return

            # 确认删除
            if not messagebox.askyesno("确认", f"确定要删除用户 '{username}' 吗？"):
                return

            victory, msg = self.userMgr.deleteUser(username)
            if victory:
                messagebox.showinfo("成功", msg)
                dialog.destroy()
                self.showUserList()
            else:
                messagebox.showerror("错误", msg)

        # 按钮
        buttonFrame = tk.Frame(mainFrame, bg='#F8F9FA')
        buttonFrame.pack(pady=10)

        tk.Button(buttonFrame, text="删除", command=deleteUser,
                  font=('微软雅黑', 10), bg='#DC3545', fg='white',
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(buttonFrame, text="取消", command=dialog.destroy,
                  font=('微软雅黑', 10), bg='#6C757D', fg='white',
                  padx=15, pady=5).pack(side=tk.LEFT, padx=5)

    def showUserList(self):
        """显示用户列表"""
        # 清除现有内容
        for widget in self.listFrame.winfo_children():
            widget.destroy()

        success, users = self.userMgr.listUsers()

        if not success:
            tk.Label(self.listFrame, text=f"错误: {users}",
                     font=('微软雅黑', 11), bg='#F8F9FA', fg='red').pack(pady=20)
            return

        if not users:
            tk.Label(self.listFrame, text="没有用户数据",
                     font=('微软雅黑', 11), bg='#F8F9FA').pack(pady=20)
            return

        # 创建表格标题
        headerFrame = tk.Frame(self.listFrame, bg='#343A40')
        headerFrame.pack(fill=tk.X, pady=(0, 5))

        headers = ['用户名', '角色', '描述']
        for i, header in enumerate(headers):
            tk.Label(headerFrame, text=header, font=('微软雅黑', 11, 'bold'),
                     bg='#343A40', fg='white', padx=10, pady=5).grid(row=0, column=i, sticky='w')
            headerFrame.columnconfigure(i, weight=1)

        # 创建滚动区域
        canvas = tk.Canvas(self.listFrame, bg='#F8F9FA', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.listFrame, orient=tk.VERTICAL, command=canvas.yview)
        scrollableFrame = tk.Frame(canvas, bg='#F8F9FA')

        scrollableFrame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollableFrame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 显示用户数据
        for i, user in enumerate(users):
            rowColor = '#FFFFFF' if i % 2 == 0 else '#F2F2F2'
            rowFrame = tk.Frame(scrollableFrame, bg=rowColor)
            rowFrame.pack(fill=tk.X, pady=1)

            # 高亮显示当前用户
            if user['username'] == self.currentUser:
                rowFrame.config(bg='#E3F2FD')

            # 用户名
            usernameLabel = tk.Label(rowFrame, text=user['username'],
                                     font=('微软雅黑', 10),
                                     bg=rowFrame['bg'], padx=10, pady=5)
            usernameLabel.grid(row=0, column=0, sticky='w')

            # 角色
            roleLabel = tk.Label(rowFrame, text=user['role'],
                                 font=('微软雅黑', 10),
                                 bg=rowFrame['bg'], padx=10, pady=5)
            roleLabel.grid(row=0, column=1, sticky='w')

            # 描述
            aboutLabel = tk.Label(rowFrame, text=user['description'],
                                  font=('微软雅黑', 10),
                                  bg=rowFrame['bg'], padx=10, pady=5)
            aboutLabel.grid(row=0, column=2, sticky='w')

            rowFrame.columnconfigure(0, weight=1)
            rowFrame.columnconfigure(1, weight=1)
            rowFrame.columnconfigure(2, weight=2)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定鼠标滚轮滚动
        def lock2mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", lock2mousewheel)

        # 显示用户统计
        allUsers = len(users)
        adminCount = sum(1 for u in users if u['role'] == 'administrator')
        userCount = allUsers - adminCount

        statisticsFrame = tk.Frame(self.listFrame, bg='#F8F9FA')
        statisticsFrame.pack(fill=tk.X, pady=(10, 0))

        stats_text = f"总计: {allUsers} 用户 (管理员: {adminCount}, 普通用户: {userCount})"
        tk.Label(statisticsFrame, text=stats_text, font=('微软雅黑', 10),
                 bg='#F8F9FA', fg='#6C757D').pack()
