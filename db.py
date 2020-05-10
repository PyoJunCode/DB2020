# coding: utf-8
import requests
import re
import sys
from bs4 import BeautifulSoup
from os import system
from urllib.parse import urlencode, quote
from fake_useragent import UserAgent
import pymysql

# 21800370 seo jun pyo DB team project


getfake = lambda: getdateinfo().replace(' ', '%20')

urlencode_noquote = lambda query: urlencode(query, quote_via = lambda k,l,m,n: k)

class Lecture:


    _CAMOUFLAGE_CHROME = {'User-Agent' : UserAgent().chrome}

    HISNET_ROOT = 'http://hisnet.handong.edu'
    # http://hisnet.handong.edu/login/_login.php
    HISNET_LOGIN_PAGE = HISNET_ROOT + '/login/_login.php'
    # http://hisnet.handong.edu/for_student/course/PLES430M.php?
    HISNET_LECTURE_SEARCH_PAGE = HISNET_ROOT+'/for_student/course/PLES330M.php?'

    db = pymysql.connect(host='52.14.37.173', port=3306, user='root', passwd='dba', db='Project', charset='utf8mb4')
    
    cursor = db.cursor()


    def __init__(self, idpw, date):
        """ idpw : hisnet id/password
            term : semester info
            the_time : hot time
            targets : target lectures
            kakao_token : katalk info
        """
        self.s = requests.Session()
        self.idpw = {
            'id' :       idpw[0],
            'password' : idpw[1],
            'Language' : 'Korean'
        }
        self.date = date
        

        print('Sign in hisnet..')
        resp = self.disguised_post(self.HISNET_LOGIN_PAGE, data=self.idpw)
        soup = BeautifulSoup(resp.text, 'html.parser')
        script_txt = soup.select('script')[0].text.strip()
        if resp.status_code == 200:
            print('SUCCESS !')
        print('connect to DB server...')
        if self.db:
            print('SUCCESS !')
    




    def disguised_post(self, url, **kwargs):
        return self.s.post(url, headers = self._CAMOUFLAGE_CHROME, **kwargs)

    def disguised_get(self, url):
        return self.s.get(url, headers = self._CAMOUFLAGE_CHROME)
        

        

    def get_lecture_name(self,hakbu,date,open_id):
        
        hak_year = date[:-1]
        hak_term = date[-1:]
        
        query = {
            
            'hak_year' : hak_year,
            'hak_term' : hak_term,
            'hakbu': hakbu,
            'isugbn':'%C0%FC%C3%BC',
            'injung':'%C0%FC%C3%BC',
            'eng':'%C0%FC%C3%BC',
            'gwamok_code':'',
            'ksearch':'search'
        }
        #query['gwamok_code'] = lecture_code
        
        page = 1

        
        while page < 3 :
        
            lookup_lecture_url = self.HISNET_LECTURE_SEARCH_PAGE + 'Page='+ str(page)+ '&' +    urlencode_noquote(query)
            resp = self.disguised_get(lookup_lecture_url)
            soup = BeautifulSoup(resp.content, 'html.parser')
            tbody_items = soup.find_all('table', border='0', width='750', cellspacing='0',  cellpadding='0', id='att_list')
            
            if(len(tbody_items[0]) < 5):
                
                return

            for tr in tbody_items[0].select('tr')[1:]:

               lec_code = tr.text.split('\n')[2]
               sec_id = int(tr.text.split('\n')[3])
               lec_name = tr.text.split('\n')[4]
               credits = float(tr.text.split('\n')[5])
               prof = tr.text.split('\n')[6]
               time = tr.text.split('\n')[7]
               building = tr.text.split('\n')[9]
               total_stu = int(tr.text.split('\n')[10])
               curr_stu = int(tr.text.split('\n')[11])
               inj = tr.text.split('\n')[14]
               
               
               check = "select `id` from `course` where course_code =%s limit 1"
               self.cursor.execute(check,(lec_code))
               result = self.cursor.fetchone()
               

               
               
               if result is not None:
                  course_id = result[0]
               if result is None: # first appeared lecture
               
                  checkinj = "select `inj_code` from `injung` where `eng` LIKE %s"
                  self.cursor.execute(checkinj,("%"+inj+"%"))
                  injresult = self.cursor.fetchone()
                  inj_code = None
                  if injresult is not None:
                    inj_code = injresult[0]
                  
                  sql = "INSERT INTO `course` (`course_code`, `title` ,`credits`,`major_code`,`inj_code`) VALUES(%s, %s, %s, %s,%s)"
                  self.cursor.execute(sql,(lec_code,lec_name,credits, int(hakbu), inj_code ))
                  self.db.commit()
                  print('과목코드: ' + lec_code + ', lec_name: ' + lec_name + ', hakjum: ' + str(credits) )
                  course_id = self.cursor.lastrowid
               
             
               ssql = "INSERT INTO `section` (`open_id`, `course_id` ,`sec_id`,`building`, `time`,`prof_name`,`total_stu`,`curr_stu`) VALUES(%s,%s,%s,%s, %s, %s,%s,%s)"
               self.cursor.execute(ssql,(open_id,course_id,sec_id,building,time,prof,total_stu,curr_stu))
               print('분반: ' + str(sec_id) + ', time: ' + time )
               #print('prof: ' + prof  + ', building: ' + building)
               print()
               
            page=page + 1
       


                
    def get_lecture_list(self):
    
    
        lookup_lecture_url = self.HISNET_LECTURE_SEARCH_PAGE
        resp = self.disguised_get(lookup_lecture_url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        major_list = soup.find('select', attrs={'name':'hakbu'})
        gubun_list = soup.find('select', attrs={'name':''})
        #print(major_list.select('option'))
        
        
        for hak_term in self.date: # each date
            print(hak_term)
            
            check = "select `open_id` from `open` where time =%s limit 1"
            self.cursor.execute(check,(hak_term))
            result = self.cursor.fetchone()
            if result is not None:
                open_id = result[0]
            if result is None:
                sql = "INSERT INTO `open` (`time`) VALUES(%s) "
                self.cursor.execute(sql,(hak_term))
                self.db.commit()
                open_id = self.cursor.lastrowid
            
            for major in major_list.select('option')[1:]:
                sql = "INSERT INTO `major` (`major_code`, `major_name`) VALUES(%s, %s) ON DUPLICATE KEY UPDATE major_code=VALUES(major_code), major_name =VALUES(major_name)"
                self.cursor.execute(sql,(major.get('value'),major.text.strip()))
                self.db.commit()

                print(major.get('value'))
                print(major.text.strip())
                
                self.get_lecture_name(major.get('value'),hak_term,open_id)
    #
    #        db.commit()
    #        db.close()
    
    def get_kor_inj(self):
    
    
        lookup_lecture_url = self.HISNET_LECTURE_SEARCH_PAGE
        resp = self.disguised_get(lookup_lecture_url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        inj_list = soup.find('select', attrs={'name':'injung'})

        
        for injung in inj_list.select('option')[1:]:
            sql = "INSERT INTO `injung` (`inj_code`, `kor`) VALUES(%s, %s) ON DUPLICATE KEY UPDATE  kor=VALUES(kor)"
            self.cursor.execute(sql,(injung.get('value'),injung.text.strip()))
            self.db.commit()
    
            print(injung.text.strip())
                
                
    def get_eng_inj(self):
    
    
        lookup_lecture_url = self.HISNET_LECTURE_SEARCH_PAGE
        resp = self.disguised_get(lookup_lecture_url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        inj_list = soup.find('select', attrs={'name':'injung'})

        
        for injung in inj_list.select('option')[1:]:
            sql = "INSERT INTO `injung` (`inj_code`, `eng`) VALUES(%s, %s) ON DUPLICATE KEY UPDATE  eng=VALUES(eng)"
            self.cursor.execute(sql,(injung.get('value'),injung.text.strip()))
            self.db.commit()
       
            print(injung.text.strip())
                

s = Lecture(('id here','pw here'),('20191','20192','20201',))
#@todo delete id

s.get_lecture_list()


