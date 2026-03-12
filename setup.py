import os
from setuptools import setup

# 获取所有 .py 模块
py_modules = [
    'background', 'checker', 'format_io', 'homepage',
    'info_manager', 'login_and_security', 'main'
]

# 收集 images 下所有文件
def collect_image_files():
    data_files = []
    for root, dirs, files in os.walk('images'):
        target = os.path.join('images', os.path.relpath(root, 'images'))
        data_files.append((target, [os.path.join(root, f) for f in files]))
    return data_files

# 收集 docs 下所有文件（说明书）
def collect_doc_files():
    data_files = []
    for root, dirs, files in os.walk('docs'):
        target = os.path.join('docs', os.path.relpath(root, 'docs'))
        data_files.append((target, [os.path.join(root, f) for f in files]))
    return data_files

# 合并数据文件
extraDatas = collect_image_files() + collect_doc_files()

setup(
    name='Student-Information-Management-System',
    version='5.0.0',
    description='学生信息管理系统 ——针对学生信息特点及实际需要，高效率地、规范地管理大量学生信息，减轻学校管理人员的工作负担',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='CHUA某人',
    author_email='chua-x@outlook.com',
    license='Apache 2.0',
    py_modules=py_modules,
    data_files=extraDatas,
    install_requires=[
        'pillow>=9.5.0',
        'tkcalendar',
        'openpyxl>=3.1.5',
        'snowland-smx>=0.3.1',
    ],
    entry_points={
        'console_scripts': [
            'student-info = main:main',
        ],
    },
    classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3 :: Only",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Natural Language :: Chinese (Simplified)",
    "Intended Audience :: End Users/Desktop"
    ],
    python_requires='>=3.6',
)
