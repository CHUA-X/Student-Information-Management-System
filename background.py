#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw


# noinspection PyBroadException
class BackgroundManager:
    """背景管理器"""
    # 背景图文件，存放在images目录下，可自定义
    THEMES = {
        'default': {
            'login': 'images/默认/默认登录框.jpg',
            'main': 'images/默认/默认主界面.jpg',
            'dialog': 'images/默认/默认对话框.jpg'
        },
        'blue': {
            'login': 'images/蓝色/蓝色登录框.jpg',
            'main': 'images/蓝色/蓝色主界面.jpg',
            'dialog': 'images/蓝色/蓝色对话框.jpg'
        },
        'green': {
            'login': 'images/绿色/默认登录框.jpg',
            'main': 'images/绿色/绿色主界面.jpg',
            'dialog': 'images/绿色/绿色对话框.jpg'
        },
        'light': {
            'login': 'images/浅色/浅色登录框.jpg',
            'main': 'images/浅色/浅色主界面.jpg',
            'dialog': 'images/浅色/浅色对话框.jpg'
        },
        'custom': {
            'login': 'images/自定义/登录框.jpg',
            'main': 'images/自定义/主界面.jpg',
            'dialog': 'images/自定义/对话框.jpg'
        }
    }

    def __init__(self, theme='default'):
        # 定义变量
        self.theme = theme
        self.backgrounds = {}
        self.backgroundImgs = {}
        self.photoImgs = {}
        self.styleCache = {}
        self.imageFolder = Path('images')
        self.imageFolder.mkdir(exist_ok=True)

    def setTheme(self, theme):
        # 设置初始背景
        self.theme = theme
        self.backgrounds = {}

    def getBackgroundPath(self, window_type):
        # 获取背景路径
        if self.theme in self.THEMES and window_type in self.THEMES[self.theme]:
            return self.THEMES[self.theme][window_type]
        return None

    @staticmethod
    def createGradientBackground(width, height, color1, color2,
                                 direction='vertical'):
        # 当images文件夹不存在时创建应急梯度背景
        image = Image.new('RGB', (width, height), color1)
        draw = ImageDraw.Draw(image)

        if direction == 'vertical':
            for y in range(height):
                ratio = y / height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)

                draw.line([(0, y), (width, y)], fill=(r, g, b))
        else:
            for x in range(width):
                ratio = x / width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)

                draw.line([(x, 0), (x, height)], fill=(r, g, b))

        return image

    def loadOrCreateBackground(self, windowType, width, height):
        # 加载或创建应急背景
        cacheKey = f'{self.theme}_{windowType}_{width}_{height}'

        if cacheKey in self.photoImgs:
            return self.photoImgs[cacheKey]

        backgroundPath = self.getBackgroundPath(windowType)
        backgroundImg = None

        if backgroundPath and Path(backgroundPath).exists():  # 判断是否存在images文件夹
            try:
                backgroundImg = Image.open(backgroundPath)
                backgroundImg = backgroundImg.resize((width, height),
                                                     Image.Resampling.LANCZOS)
            except Exception as e:
                print(f'加载背景图片失败: {e}')
                backgroundImg = None

        # 不存在images文件夹时调用createGradientBackground()函数创建应急梯度图片
        if backgroundImg is None:
            if windowType == 'login':
                backgroundImg = self.createGradientBackground(
                    width, height,
                    color1=(30, 60, 114),
                    color2=(70, 130, 180),
                    direction='vertical'
                )
            elif windowType == 'main':
                backgroundImg = self.createGradientBackground(
                    width, height,
                    color1=(240, 248, 255),
                    color2=(173, 216, 230),
                    direction='horizontal'
                )
            else:
                backgroundImg = self.createGradientBackground(
                    width, height,
                    color1=(255, 250, 240),
                    color2=(245, 245, 220),
                    direction='vertical'
                )

        photoImg = ImageTk.PhotoImage(backgroundImg)

        self.backgroundImgs[cacheKey] = backgroundImg
        self.photoImgs[cacheKey] = photoImg

        return photoImg

    def applyBackground(self, window, windowType, width=None, height=None):
        # 应用背景
        if width is None:
            width = window.winfo_width()
        if height is None:
            height = window.winfo_height()

        if width <= 0 or height <= 0:
            width = window.winfo_reqwidth()
            height = window.winfo_reqheight()

        backgroundImg = self.loadOrCreateBackground(windowType, width, height)

        backgroundLabel = tk.Label(window, image=backgroundImg)
        backgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)
        backgroundLabel.image = backgroundImg

        return backgroundLabel

    def applyTranslucentBackground(self, frame, alpha=0.9):
        # alpha值处理
        try:
            # 使用半透明化
            alphaStr = str(alpha).replace('.', '_')
            styleName = f'Translucent.TFrame.{alphaStr}'

            if styleName not in self.styleCache:
                try:
                    rootWindow = frame.winfo_toplevel()
                    style = ttk.Style(rootWindow)
                except Exception:
                    style = ttk.Style()

                if alpha >= 0.9:
                    backgroundColor = '#F8F9FA'
                elif alpha >= 0.7:
                    backgroundColor = '#E9ECEF'
                else:
                    backgroundColor = '#FFFFFF'

                style.configure(styleName, background=backgroundColor)
                self.styleCache[styleName] = True

            try:
                frame.configure(style=styleName)
            except Exception as e:
                print(f'应用样式失败: {e}')
                frame.configure(style='TFrame')

            frame.configure(relief='raised', borderwidth=1)

            return styleName

        except Exception as e:
            # 应用半透明背景失败时使用普通模式
            print(f'应用半透明背景失败: {e}')
            if alpha >= 0.9:
                backgroundColor = '#F8F9FA'
            elif alpha >= 0.7:
                backgroundColor = '#E9ECEF'
            else:
                backgroundColor = '#FFFFFF'

            frame.configure(bg=backgroundColor, relief='raised', borderwidth=1)
            return 'default'
