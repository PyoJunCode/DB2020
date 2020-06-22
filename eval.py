
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import re
import pymysql

#21800370 seojunpyo DB team project

db = pymysql.connect(host='52.14.37.173', port=3306, user='root', passwd='dba', db='Project', charset='utf8mb4')

cursor = db.cursor()

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(executable_path=r'./chromedriver', chrome_options=options)


driver.get('https://everytime.kr/login')

driver.implicitly_wait(2)


driver.find_element_by_name('userid').send_keys('everytimeID')
driver.find_element_by_name('password').send_keys('pswd')


driver.find_element_by_xpath('//*[@id="container"]/form/p[3]/input').click()

driver.get('https://everytime.kr/lecture')

sleep(5)
driver.find_element_by_xpath('//*[@id="sheet"]/ul/li[3]/a').click()


pre_count = 0

last_height = driver.execute_script("return document.body.scrollHeight")
while True:
   
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
  
    sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight-50);")
    sleep(1)
   
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

articles = soup.select('.article')

for article in articles:
    
    open = re.findall(r'\d+', article.select('.semester')[0].text)
    opencat = '20'+open[0]+open[1]
    lec_name = article.select('h3')[0].text.split(':')[0].strip()
    prof_name = article.select('h3')[0].text.split(':')[1].strip()
    desc = article.select('.text')[0].text
    rate = article.select('.on')
    rating = int(re.findall(r'\d+', rate[0]['style'])[0]) / 20
    

    checkc = "select `id` from `course` where title LIKE %s"
    cursor.execute(checkc,("%"+lec_name+"%"))
    result = cursor.fetchone()
    if result is None:
        print(lec_name +' not founded')
        continue
    print(lec_name +' founded')
    course_id = result[0]

        
    checko = "select `open_id` from `open` where time =%s"
    cursor.execute(checko,(opencat))
    result = cursor.fetchone()
    if result is None:
        continue
    open_id = result[0]

    sql = "INSERT INTO review (`course_id`,`open_id`,`prof_name`,`description`) VALUES(%s,%s,%s,%s)"
    cursor.execute(sql,(course_id,open_id,prof_name,desc))
    db.commit()
    
driver.quit()
