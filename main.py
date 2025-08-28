from base64 import encode
import copy
import json
import threading
import time
import re
from typing import List, Dict, Optional
from io import BytesIO

from numpy import e
import requests
import bs4
from PIL import Image
import ddddocr

class Spider:
    class Lesson:
        def __init__(self, name, code, teacher_name, Time, number):
            self.name:str = name
            self.code:str = code
            self.teacher_name:str = teacher_name
            self.Time:str = Time
            self.number = number

        def show(self):
            print(f'课程名称: {self.name}')
            print(f'课程代码: {self.code}')
            print(f'教师姓名: {self.teacher_name}')
            print(f'上课时间: {self.Time}')
            print(f'课程容量: {self.number}')
            print('-' * 50)

    def __init__(self):
        self.__base_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': '',
            'ddl_kcxz': '',
            'ddl_ywyl': '',
            'ddl_kcgs': '',
            'ddl_xqbs': '1',
            'ddl_sksj': '',
            'TextBox1': '',
            'dpkcmcGrid:txtChoosePage': '1',
            'dpkcmcGrid:txtPageSize': '200',
        }

        self.__name = None
        self.__uid = None
        self.__password = None
        self.__real_base_url: str = ''
        self.__base_url: str = 'http://jws.syuct.edu.cn/'
        self.__headers: Dict[str, str] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
        }

        self.session = requests.Session()
        # 禁用SSL警告
        requests.packages.urllib3.disable_warnings()

    def __set_real_url(self) -> requests.Response:
        """获取真实的URL地址"""
        try:
            request: requests.Response = self.session.get(
                self.__base_url,
                headers=self.__headers,
                verify=False,
                timeout=10,
            )
            request.encoding = 'gbk'
            real_url: str = request.url
            self.__real_base_url: str = real_url[:len(real_url) - len("default2.aspx")]
            return request
        except requests.exceptions.RequestException as e:
            print(f"获取真实URL失败: {e}")
            raise

    def __get_code(self) -> str:
        """获取并识别验证码"""
        try:
            request: requests.Response = self.session.get(
                self.__real_base_url + 'CheckCode.aspx',
                headers=self.__headers,
                verify=False,
                timeout=10
            )
            request.encoding = 'gbk'
            img_data = BytesIO(request.content)
            img = Image.open(img_data)
            ocr = ddddocr.DdddOcr()
            code = ocr.classification(img)
            print(f"验证码识别结果: {code}")
            return code
        except Exception as e:
            print(f"验证码识别失败: {e}")
            raise

    def __get_login_data(self, uid: str, password: str) -> Dict[str, str]:
        """获取登录所需数据"""
        request = self.__set_real_url()
        soup = bs4.BeautifulSoup(request.text, 'lxml')
        form_tag = soup.find("input", {"name": "__VIEWSTATE"})

        if not form_tag:
            raise ValueError("无法找到__VIEWSTATE字段")

        __VIEWSTATE = form_tag['value']
        code = self.__get_code()

        data: Dict[str, str] = {
            '__VIEWSTATE': __VIEWSTATE,
            'txtUserName': uid,
            'TextBox2': password,
            'txtSecretCode': code,
            'RadioButtonList1': '学生'.encode('gb2312'),
            'Button1': "",
            'lbLanguage': "",
            'hidPdrs': "",
            'hidsc': "",
        }
        return data

    def login(self, uid: str, password: str) -> bool:
        """登录系统"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                data: Dict = self.__get_login_data(uid, password)
                request: requests.Response = self.session.post(
                    self.__real_base_url + 'default2.aspx',
                    headers=self.__headers,
                    data=data,
                    verify=False,
                    timeout=10
                )

                request.encoding = 'gbk'
                # 检查登录是否成功
                if '用户名不存在或未按照要求参加教学活动' in request.text:
                    print("登录失败: 用户名或密码错误")
                    return False

                soup = bs4.BeautifulSoup(request.text, 'lxml')
                name_tag = soup.find(id='xhxm')

                if name_tag:
                    self.__name = name_tag.string[:len(name_tag.string) - 2]
                    self.__uid = uid
                    self.__password = password
                    print(f'登录成功! 欢迎 {self.__name}')
                    return True
                else:
                    print(f'登录失败，第{attempt+1}次尝试')
                    time.sleep(1)

            except Exception as e:
                print(f'登录过程中发生错误: {e}')
                time.sleep(1)

        print("登录失败，已达到最大重试次数")
        return False

    def __enter_lessons_first(self) -> bool:
        """进入选课页面"""
        try:
            data: Dict = {
                'xh': self.__uid,
                'xm': self.__name.encode('gb2312'),
                'gnmkdm': 'N121111',
            }
            self.__headers['Referer'] = self.__real_base_url + 'xs_main.aspx?xh=' + self.__uid

            request = self.session.get(
                self.__real_base_url + 'xf_xsqxxxk.aspx',
                params=data,
                headers=self.__headers,
                verify=False,
                timeout=10
            )

            request.encoding = 'gbk'
            if request.status_code != 200:
                print("进入选课页面失败")
                return False

            self.__headers["Referer"] = request.url
            soup = bs4.BeautifulSoup(request.text, 'lxml')
            self.__set_VIEWSTATE(soup)
            return True

        except Exception as e:
            print(f"进入选课页面时发生错误: {e}")
            return False

    def __set_VIEWSTATE(self, soup: bs4.BeautifulSoup):
        """设置VIEWSTATE值"""
        __VIEWSTATE_tag = soup.find("input", attrs={"name": "__VIEWSTATE"})
        if __VIEWSTATE_tag:
            self.__base_data['__VIEWSTATE'] = __VIEWSTATE_tag['value']
        else:
            print("警告: 未找到__VIEWSTATE字段")

    def __search_lessons(self, lesson_name: str = '') -> List[Lesson]:
        """搜索课程"""
        try:
            self.__base_data['TextBox1'] = lesson_name.encode('gb2312')
            data = self.__base_data.copy()
            data['Button2'] = '确定'.encode('gb2312')

            request = self.session.post(
                self.__headers['Referer'],
                data=data,
                headers=self.__headers,
                verify=False,
                timeout=10
            )

            request.encoding = 'gbk'

            soup = bs4.BeautifulSoup(request.text, 'lxml')
            self.__set_VIEWSTATE(soup)
            return self.__get_lessons(soup)

        except Exception as e:
            print(f"搜索课程时发生错误: {e}")
            return []

    def __get_lessons(self, soup: bs4.BeautifulSoup) -> List[Lesson]:
        """从页面中提取课程信息"""
        lessons_list = []
        lessons_tag = soup.find('table', id='kcmcGrid')

        if not lessons_tag:
            print("未找到课程表格")
            return lessons_list

        lessons_tag_list = lessons_tag.find_all('tr')[1:]

        for lesson_tag in lessons_tag_list:
            try:
                td_list = lesson_tag.find_all('td')
                if len(td_list) < 11:
                    continue

                code = td_list[0].input['name'] if td_list[0].input else ''
                name = td_list[1].string if td_list[1].string else ''
                teacher_name = td_list[3].string if td_list[3].string else ''
                Time = td_list[4].get('title', '') if td_list[4] else ''
                number = td_list[10].string if td_list[10].string else ''

                lesson = self.Lesson(name, code, teacher_name, Time, number)
                lessons_list.append(lesson)
            except Exception as e:
                print(f"解析课程信息时发生错误: {e}")
                continue

        return lessons_list

    def __select_lesson(self, lesson: Lesson) -> bool:
        """选择课程"""
        try:
            data = copy.deepcopy(self.__base_data)
            data['Button1'] = '  提交  '.encode('gb2312')
            code = lesson.code
            data[code] = 'on'

            request = self.session.post(
                self.__headers['Referer'],
                data=data,
                headers=self.__headers,
                verify=False,
                timeout=10,
            )
            request.encoding = 'gbk'

            soup = bs4.BeautifulSoup(request.text, 'lxml')
            self.__set_VIEWSTATE(soup)

            # 检查是否选课成功
            selected_lessons_tag = soup.find('table', id='DataGrid2')
            if selected_lessons_tag:
                tr_list = selected_lessons_tag.find_all('tr')[1:]
                selected_lessons: List[str] = []

                print("已选课程:")
                for tr in tr_list:
                    td = tr.find('td')
                    if td and td.string:
                        selected_lessons.append(td.string)
                        print(td.string)

                if lesson.name in selected_lessons:
                    print(f"选课成功: {lesson.name}")
                    return True

            # 检查错误信息
            error_tag = soup.html.head.script
            if error_tag and error_tag.string:
                error_tag_text = error_tag.string
                r = "alert\('(.+?)'\);"
                for s in re.findall(r, error_tag_text):
                    print(f"选课错误: {s}")

            return False

        except Exception as e:
            print(f"选课过程中发生错误: {e}")
            return False

    def run(self):
        """运行选课程序"""
        try:
            # 读取配置文件
            with open('config.json', 'r') as f:
                config = json.load(f)

            # self.__name = config.get('name', '')
            self.__uid = config.get('uid', '')
            self.__password = config.get('password', '')

            if not self.__uid or not self.__password:
                print("配置文件中缺少学号或密码")
                return

            # 登录系统
            if not self.login(self.__uid, self.__password):
                print("登录失败，程序退出")
                return

            # 进入选课页面
            if not self.__enter_lessons_first():
                print("进入选课页面失败，程序退出")
                return

            # 搜索课程
            lessons_config = config.get('lessons', [])
            selected_lessons = []

            for lesson in lessons_config:
                lesson_name = lesson.get('name', '')
                teacher_name:str = lesson['teacher_name']
                time_slot = lesson.get('Time', '')

                if not lesson_name:
                    continue

                print(f"正在搜索课程: {lesson_name}")
                lesson_list = self.__search_lessons(lesson_name)

                if not lesson_list:
                    print(f"未找到课程: {lesson_name}")
                    continue

                # 筛选符合条件的课程
                for found_lesson in lesson_list:
                    print(f"{found_lesson.teacher_name}   {teacher_name}")
                    if (found_lesson.teacher_name== teacher_name and
                        found_lesson.Time == time_slot):
                        selected_lessons.append(found_lesson)
                        print(f"找到匹配课程: {found_lesson.name}")

            if not selected_lessons:
                print("未找到任何匹配的课程")
                return

            # 显示找到的课程
            print("\n找到以下匹配课程:")
            for item in selected_lessons:
                item.show()

            # 开始选课
            print("开始选课...")
            thread_list = []
            results = []

            # 使用线程安全的方式存储结果
            lock = threading.Lock()

            def select_lesson_with_result(lesson, result_list):
                success = self.__select_lesson(lesson)
                with lock:
                    result_list.append((lesson.name, success))

            for lesson in selected_lessons:
                thread = threading.Thread(
                    target=select_lesson_with_result,
                    args=(lesson, results),
                    daemon=True
                )
                thread_list.append(thread)
                thread.start()

            # 等待所有线程完成
            for thread in thread_list:
                thread.join()

            # 显示选课结果
            print("\n选课结果:")
            for lesson_name, success in results:
                status = "成功" if success else "失败"
                print(f"{lesson_name}: {status}")

        except FileNotFoundError:
            print("未找到配置文件 config.json")
        except json.JSONDecodeError:
            print("配置文件格式错误")
        except Exception as e:
            print(f"程序运行过程中发生错误: {e}")
        finally:
            input("按回车键退出程序")

def main():
    """主函数"""
    print("=" * 50)
    print("选课系统自动化工具")
    print("=" * 50)

    spider = Spider()
    spider.run()

if __name__ == '__main__':
    main()
