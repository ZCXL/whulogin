#coding=utf-8
import requests, re, os, tempfile, sys
import base64, hashlib, rsa, binascii
import ImageProcess

class WHUEdu:
    urlIndex = 'http://210.42.121.241'
    urlLogin = 'http://210.42.121.241/servlet/Login'
    urlImg = 'http://210.42.121.241/servlet/GenImg'
    urlPage = 'http://210.42.121.241/stu/stu_index.jsp'
    urlGrade = 'http://210.42.121.241/servlet/Svlt_QueryStuScore'
    imgPath = os.environ['HOME'] + '/code.jpeg'
    count = 20
    isLogin = False
    jsessionid = ""
    sto_id_20480 = 'IGHJCKNCFAAA'

    def __init__(self, uid, pwd):
        self.uid = uid
        self.pwd = pwd
        self.requests = requests.Session()

        self.login()
        
    def login(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
        }
        while self.count > 0:
            #访问登陆主界面，获取cookie
            r = self.requests.get(self.urlIndex, headers = headers)

            #获取验证码图片
            r = self.requests.get(self.urlImg, headers = headers)
            fileName = self.imgPath
            with open(fileName, 'wb') as imgFile:
                imgFile.write(r.content)
            jsessionid = r.cookies['JSESSIONID']


            #调用ImageProcess获取图片验证码
            code = ImageProcess.getCode(fileName)
            #当验证码数据结果长度不为4时，重新获取
            if len(code) != 4:
                self.count -= 1
                continue
            
            #构造登陆请求页面数据
            headers.update({
                'Host': '210.42.121.241',
                'Origin': 'http://210.42.121.241',
                'Referer': 'http://210.42.121.241/servlet/Login'
            })
            data = {
                'id':       self.uid,
                'pwd':      hashlib.md5(self.pwd.encode()).hexdigest(),
                'xdvfb':    code
            }
            cookies = {
                'sto-id-20480': self.sto_id_20480,
                'JSESSIONID': jsessionid
            }
            #关闭重定向，获取页面jsessionid
            r = self.requests.post(self.urlLogin, data = data, headers = headers, cookies = cookies, allow_redirects=False)
            if str(r.status_code) == '302':
                self.isLogin = True
                self.jsessionid = jsessionid
                break
            self.count -= 1

        #打印登陆结果信息
        if self.isLogin:
            print "Login Successfully"
            print "JSESSIONID:", self.jsessionid
        else:
            print "Login Failed,Please try again"
        #删除最后的临时文件
        os.remove(self.imgPath)

    def __getToke(self):
        #通过访问主页获取csfrtoken
        cookies = {
            'sto-id-20480': self.sto_id_20480,
            'JSESSIONID': self.jsessionid
        }
        r = self.requests.get(self.urlPage, cookies = cookies)
        reg = r'csrftoken=(.*?)\''
        pattern = re.compile(reg, re.S)
        items = re.findall(pattern, r.text)
        csrftoken = items[0]
        return csrftoken

    def getGPA(self):
        #构造cookie
        cookies = {
            'sto-id-20480': self.sto_id_20480,
            'JSESSIONID': self.jsessionid
        }

        #获取token
        csrftoken = self.__getToke()
        
        #依次访问成绩页面统计成绩
        learnTypes = [
            '\271\253\271\262\261\330\320\336', #公共必修
            '\271\253\271\262\321\241\320\336', #公共选修
            '\327\250\322\265\261\330\320\336', #专业必修
            '\327\250\322\265\321\241\320\336'] #专业选修
        submit = '\262\351\321\257'
        score = 0
        grade = 0
        reg = r'<td>(\d{1,3}\.\d{1})</td>'
        pattern = re.compile(reg, re.S)
        for learnType in learnTypes:
            data = {
                'year': 0,
                'term': "",
                'learnType': learnType,
                'scoreFlag': 1,
                'submit': submit,
                'csrftoken': csrftoken
            }
            r = self.requests.post(self.urlGrade, data= data, cookies = cookies, allow_redirects =False)
            text = r.text.encode('utf8')
            items = re.findall(pattern, text)
            for i in range(len(items)):
                if i % 2 == 0:
                    score += float(items[i])
                else:
                    grade += float(items[i]) * float(items[i - 1])
        print 'GPA', grade / score

    def getGrade(self):
        #构造cookie
        cookies = {
            'sto-id-20480': self.sto_id_20480,
            'JSESSIONID': self.jsessionid
        }

        #获取token
        csrftoken = self.__getToke()

        #依次访问成绩页面统计成绩
        learnTypes = [
            '\271\253\271\262\261\330\320\336', #公共必修
            '\271\253\271\262\321\241\320\336', #公共选修
            '\327\250\322\265\261\330\320\336', #专业必修
            '\327\250\322\265\321\241\320\336'] #专业选修
        submit = '\262\351\321\257'
        scores = []
        reg = r'<td>(\d{1}\.\d{1})</td>'
        pattern = re.compile(reg, re.S)
        for learnType in learnTypes:
            data = {
                'year': 0,
                'term': "",
                'learnType': learnType,
                'scoreFlag': 1,
                'submit': submit,
                'csrftoken': csrftoken
            }
            r = self.requests.post(self.urlGrade, data= data, cookies = cookies, allow_redirects =False)
            text = r.text.encode('utf8')
            items = re.findall(pattern, text)
            score = 0
            for item in items:
                score += float(item)
            scores.append(score)
            print learnType.decode('gbk').encode('utf8'), score
        
        print u'合计', sum(scores)

if __name__ == '__main__':
    edu = WHUEdu('2013302580121', '*')
    edu.getGrade()
    edu.getGPA()