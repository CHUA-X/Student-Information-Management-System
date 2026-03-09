#!/usr/bin/python3

# 导入相关模块
import re
from datetime import datetime

# 姓名验证规则
namePattern = re.compile(r'^[\u4e00-\u9fa5]{2,4}$')  # Unicode编码区中常见汉字编码范围

# 性别验证规则
sexPattern = re.compile(r'^([男女])$')

# 出生日期验证规则 - 只接受 YYYY年M月D日 格式
birthPattern = re.compile(r'''^
                              (19|20)\d{2}                  # 年份：1900-2099
                              年                      
                              ([1-9]|1[0-2])                # 月份：1-12
                              月                     
                              ([1-9]|[12]\d|3[01])          # 日期：1-31
                              日                         
                              $''', re.X | re.S)

# 身份证号验证规则
IDPattern = re.compile(r'''^
                            [1-9]\d{5}                                           # 地址码
                            (18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])  # 出生日期码
                            \d{3}                                                # 顺序码
                            [\dX]                                                # 校验码
                            $''', re.X | re.S)

# 学籍号验证规则
schoolRollPattern = re.compile(r'''^
                                    ([GLJ])  # 学生学籍号分类————G字头为正式学籍号，L字头为临时学籍号，J字头学籍号为暂无公民身份证号或原公民身份证号不可用
                                    [1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]  # 学生身份证号，编码规则参见IDPattern变量注释
                                    $''', re.X | re.S)

# 政治面貌验证规则
politicalAffiliationPattern = re.compile(r'^(群众|共青团员|中共党员)$')


class StudentInfoException(Exception):
    """创建StudentInfoException异常基类，之后子异常挂载在此之上"""
    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def __str__(self):
        return self.msg


class StudentNameError(StudentInfoException):
    """当学生姓名错误时抛出此异常"""
    pass


class StudentSexError(StudentInfoException):
    """当学生性别错误时抛出此异常"""
    pass


class StudentBirthError(StudentInfoException):
    """当学生出生日期错误时抛出此异常"""
    pass


class StudentIDError(StudentInfoException):
    """当学生身份证号错误时抛出此异常"""
    pass


class StudentSchoolRollError(StudentInfoException):
    """当学生学籍号错误时抛出此异常"""
    pass


class StudentPoliticalAffiliationError(StudentInfoException):
    """当学生政治面貌异常时抛出此异常"""
    pass


class InputCheck:
    """对输入数据的检验，防止无效数据"""

    @staticmethod
    def validateChecksum(ID):
        """身份证号码校验"""
        factors = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
        checksumChars = "10X98765432"
        total = sum(int(ID[i]) * factors[i] for i in range(17))
        return ID[17].upper() == checksumChars[total % 11]

    @staticmethod
    def validateBirth(birth):
        """提取年月日进行实际日期验证"""
        try:
            # 将YYYY年MM月DD日格式转换为YYYY/MM/DD
            birth = birth.replace('年', '/').replace('月', '/').replace('日', '')
            dateSplitList = birth.split('/')

            # 确保有年月日三部分
            if len(dateSplitList) != 3:
                return False

            # 转换为整数
            year = int(dateSplitList[0])
            month = int(dateSplitList[1])
            day = int(dateSplitList[2])

            # 验证日期有效性
            datetime(year=year, month=month, day=day)
            return True
        except (ValueError, IndexError):
            return False

    @staticmethod
    def checkName(name):
        """验证学生姓名"""
        if bool(re.match(namePattern, name)):
            return True
        else:
            raise StudentNameError('无效姓名，姓名应为2-4个中文字符')

    @staticmethod
    def checkSex(sex):
        """验证学生性别"""
        if bool(re.match(sexPattern, sex)):
            return True
        else:
            raise StudentSexError('无效性别，性别只能输入"男"或"女"')

    @staticmethod
    def checkBirth(birth):
        """验证学生出生年月"""
        # 只接受YYYY年MM月DD日格式
        if bool(re.match(birthPattern, birth)):
            if bool(InputCheck.validateBirth(birth)):
                return True
            else:
                raise StudentBirthError('出生日期非法，请重新检查')
        else:
            raise StudentBirthError('出生年月格式非法，请使用格式：YYYY年MM月DD日')

    @staticmethod
    def checkID(ID):
        """验证学生身份证号"""
        if bool(re.match(IDPattern, ID)) and bool(InputCheck.validateChecksum(ID)):
            return True
        else:
            raise StudentIDError('身份证号非法，第二代身份证号应为18位数字（最后一位校验码可为X）')

    @staticmethod
    def checkSchoolRoll(schoolRoll):
        """验证学生学籍号"""
        if bool(re.match(schoolRollPattern, schoolRoll)) and bool(InputCheck.checkID(schoolRoll[1:])):
            return True
        else:
            raise StudentSchoolRollError('学籍号非法，学籍号应为"G/L/J+第二代身份证号"')

    @staticmethod
    def checkPoliticalAffiliation(politicalAffiliation):
        """验证学生政治面貌"""
        if bool(re.match(politicalAffiliationPattern, politicalAffiliation)):
            return True
        else:
            raise StudentPoliticalAffiliationError('无效政治面貌，对普通学生，政治面貌为中共党员、共青团员或群众')
