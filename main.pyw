#!/usr/bin/python3
# 学生信息管理系统（4.0）——针对学生信息特点及实际需要，高效率地、规范地管理大量学生信息，减轻学校管理人员的工作负担

# 本系统主要由以下文件组成：
# main.pyw ————系统主程序
# login_and_security.py ————登录及账号管理
# format_io.py ————格式化学生相关信息,输出或导出信息
# info_manager.py ————对学生信息的相关操作
# checker.py ————对输入数据进行输入验证
# background.py ————程序背景管理
# homepage.py ————整个系统API相关操作

# 需要的原生第一方库：
# os、re、csv、sys、json、shelve、tkinter、pathlib、sqlite3、platform、datetime、tempfile、traceback、subprocess

# 需要额外安装的第三方库：
# pillow（使用pip install pillow==9.5.0安装）
# tkcalendar（使用 pip install tkcalendar安装）
# openpyxl（使用 pip install openpyxl==3.1.5安装）
# snowland-smx（使用 pip install snowland-smx==0.3.1安装）

# 导入相关模块
import os
import sys
import platform
import tempfile
import traceback
import subprocess
import tkinter as tk
from pathlib import Path
from datetime import datetime
from tkinter import messagebox
from login_and_security import SignIn

# 版本号
VER = '5.0'


def fixBug():
    """修复pyinstaller打包后工作目录指向’%windir%\\system32‘的问题"""
    if getattr(sys, 'frozen', False):  # 确定程序实际位置
        # 打包后的exe路径
        appPath = Path(sys.executable).parent
    else:
        # 开发环境
        appPath = Path(__file__).parent

    # 设置正确的工作目录
    os.chdir(str(appPath))

    # 添加到sys.path
    if str(appPath) not in sys.path:
        sys.path.insert(0, str(appPath))

    # 创建必要的目录
    requiredDirs = ['images', 'data']
    for dirName in requiredDirs:
        dirPath = appPath / dirName
        try:
            dirPath.mkdir(exist_ok=True)
        except PermissionError:
            # 如果当前目录不可写，使用用户目录
            userDir = Path(tempfile.gettempdir()) / f'StudentInfoSystem_{dirName}'
            userDir.mkdir(exist_ok=True)
            print(f"无法在程序目录创建 {dirName}，已使用目录: {str(userDir)}")

    return appPath


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        os.environ['STUDENT_INFO_APP_DIR'] = str(fixBug())  # 设置环境变量
        loader = SignIn(VER)
        loader.verify()

    except Exception:
        # 更改运行路径
        if getattr(sys, 'frozen', False):
            logDir = Path(sys.executable).parent
        else:
            logDir = Path(__file__).parent
        logPath = logDir / '错误日志.log'

        # 确保日志文件有足够权限
        try:
            logPath.touch(exist_ok=True)
        except PermissionError:
            logPath = Path(tempfile.gettempdir()) / '学生信息管理系统_错误日志.log'

        with open(logPath, 'a', encoding='utf-8') as log:
            log.write(f"{datetime.now().strftime('%Y年%m月%d日%H时%M分%S秒')}的错误：\n{traceback.format_exc()}\n\n")

        # 使用tkinter显示错误信息
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口

        response = messagebox.askyesno('警告',
                                       f'异常操作，程序保护性退出，错误日志已写入"{logPath}"中\n是否打开此文件？')

        if response:
            try:
                if platform.system() == 'Windows':  # Windows系统下打开文件
                    subprocess.run(['start', logPath], shell=True)
            except NameError:
                messagebox.showinfo('提示', f'无法自动打开文件，请手动访问：\n{logPath}')
