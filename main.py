import copy
import json
import threading
from typing import List

import requests
import time
import bs4
import re
from PIL import Image
from io import BytesIO
import ddddocr


class Spider:
    class Lesson:
        def __init__(self, name, code, teacher_name, Time, number):
            self.name = name
            self.code = code
            self.teacher_name = teacher_name
            self.Time = Time
            self.number = number
        
        def show(self):
            print(
                f'name:{self.name} code:{self.code} teacher name:{self.teacher_name} Time:{self.Time} number:{self.number}')
    
    def __init__(self):
        self.__base_data = {
            '__EVENTTARGET'           : '',
            '__EVENTARGUMENT'         : '',
            '__VIEWSTATE'             : '',
            'ddl_kcxz'                : '',
            'ddl_ywyl'                : '',
            'ddl_kcgs'                : '',
            'ddl_xqbs'                : '1',
            'ddl_sksj'                : '',
            'TextBox1'                : '',
            'dpkcmcGrid:txtChoosePage': '1',
            'dpkcmcGrid:txtPageSize'  : '200',
        }
        
        self.__name = None
        self.__uid = None
        self.__password = None
        self.__real_base_url: str = ''
        self.__base_url: str = 'https://jws.syuct.edu.cn/'
        self.__headers: dict[str, str] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
        }
        
        self.session = requests.Session()
    
    def __set_real_url(self) -> requests.Response:
        request: requests.Response = self.session.get(self.__base_url, headers=self.__headers)
        real_url: str = request.url
        self.__real_base_url: str = real_url[:len(real_url) - len("default2.aspx")]
        return request
    
    def __get_code(self):
        request: requests.Response = self.session.get(self.__real_base_url + 'CheckCode.aspx', headers=self.__headers)
        img_data = BytesIO(request.content)
        img = Image.open(img_data)
        ocr = ddddocr.DdddOcr()
        code = ocr.classification(img)
        print(f"the code is {code}")
        return code
    
    def __get_login_data(self,uid,password):
        request = self.__set_real_url()
        soup = bs4.BeautifulSoup(request.text, 'lxml')
        form_tag = soup.find("input")
        __VIEWSTATE = form_tag['value']
        code = self.__get_code()
        data: dict[str, str] = {
            '__VIEWSTATE'     : __VIEWSTATE,
            'txtUserName'     : uid,
            'TextBox2'        : password,
            'txtSecretCode'   : code,
            'RadioButtonList1': '学生'.encode('gb2312'),
            'Button1'         : "",
            'lbLanguage'      : "",
            'hidPdrs'         : "",
            'hidsc'           : "",
        }
        return data
    
    def login(self,uid,password):
        while True:
            data: dict = self.__get_login_data(uid,password)
            request: requests.Response = self.session.post(self.__real_base_url + 'default2.aspx',
                                                           headers=self.__headers,
                                                           data=data)
            soup = bs4.BeautifulSoup(request.text, 'lxml')
            try:
                name_tag = soup.find(id='xhxm')
                self.__name = name_tag.string[:len(name_tag.string) - 2]
                print(f'login success! {self.__name}')
            except:
                print('Unknown Error, try login again.')
                time.sleep(1)
                continue
            finally:
                return True
    
    def __enter_lessons_first(self):
        data: dict = {
            'xh'    : self.__uid,
            'xm'    : self.__name.encode('gb2312'),
            'gnmkdm': 'N121111',
        }
        self.__headers['Referer'] = self.__real_base_url + 'xs_main.aspx?xh=' + self.__uid
        request = self.session.get(self.__real_base_url + 'xf_xsqxxxk.aspx', params=data, headers=self.__headers)
        self.__headers["Referer"] = request.url
        soup = bs4.BeautifulSoup(request.text, 'lxml')
        self.__set_VIEWSTATE(soup)
    
    def __set_VIEWSTATE(self, soup):
        __VIEWSTATE_taf = soup.find("input", attrs={"name": "__VIEWSTATE"})
        self.__base_data['__VIEWSTATE'] = __VIEWSTATE_taf['value']
    
    def __search_lessons(self, lesson_name=''):
        self.__base_data['TextBox1'] = lesson_name.encode('gb2312')
        data = self.__base_data.copy()
        data['Button2'] = '确定'.encode('gb2312')
        request = self.session.post(self.__headers['Referer'], data=data, headers=self.__headers)
        soup = bs4.BeautifulSoup(request.text, 'lxml')
        self.__set_VIEWSTATE(soup)
        return self.__get_lessons(soup)
    
    def __get_lessons(self, soup):
        lessons_list = []
        lessons_tag = soup.find('table', id='kcmcGrid')
        lessons_tag_list = lessons_tag.find_all('tr')[1:]
        for lesson_tag in lessons_tag_list:
            td_list = lesson_tag.find_all('td')
            code = td_list[0].input['name']
            name = td_list[1].string
            teacher_name = td_list[3].string
            Time = td_list[4]['title']
            number = td_list[10].string
            lesson = self.Lesson(name, code, teacher_name, Time, number)
            lessons_list.append(lesson)
        return lessons_list
    
    def __select_lesson(self, lesson)->bool:
        data = copy.deepcopy(self.__base_data)
        data['Button1'] = '  提交  '.encode('gb2312')
        code = lesson.code
        data[code] = 'on'
        while True:
            request = self.session.post(self.__headers['Referer'], data=data, headers=self.__headers)
            soup = bs4.BeautifulSoup(request.text, 'lxml')
            self.__set_VIEWSTATE(soup)
            error_tag = soup.html.head.script
            
            selected_lessons_tag = soup.find('table', id='DataGrid2')
            tr_list = selected_lessons_tag.find_all('tr')[1:]
            selected_lessons:List[str] = []
            print("以选课程：")
            for tr in tr_list:
                td = tr.find('td')
                selected_lessons.append(td.string)
                print(td.string)
            if lesson.name in selected_lessons:
                print(f"选课成功：{lesson.name}")
                return True
            
            if not error_tag is None:
                error_tag_text = error_tag.string
                r = "alert\('(.+?)'\);"
                for s in re.findall(r, error_tag_text):
                    print(f"error on {lesson.name}:{s}")
                return False
    
    def run(self):
        config = json.load(open('config.json'))
        self.__name = config['name']
        self.__uid = config['uid']
        self.__password = config['password']
        if self.login(config["uid"],config["password"]):
            lessons = config['lessons']
            self.__enter_lessons_first()
            selected_lessons = list()
            for lesson in lessons:
                lesson_list = self.__search_lessons(lesson['name'])
                for i in range(len(lesson_list)):
                    if lesson_list[i].teacher_name == lesson['teacher_name'] and lesson_list[i].Time == lesson['Time']:
                        selected_lessons.append(lesson_list[i])
            for item in selected_lessons:
                item.show()
            
            thread_liet = list()
            for i in selected_lessons:
                thread_liet.append(threading.Thread(target=self.__select_lesson, args=(i,),daemon=True))
                
            for i in thread_liet:
                i.start()
            
            for i in thread_liet:
                i.join()

            input("press enter to quit")
            
def main():
    spider = Spider()
    spider.run()


if __name__ == '__main__':
    main()
