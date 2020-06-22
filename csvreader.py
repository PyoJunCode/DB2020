import csv
import pymysql

# 21800370 seo jun pyo DB team project

db = pymysql.connect(host='52.14.37.173', user='root', password='dba',

                       db='Project', charset='utf8mb4')

cursor = db.cursor()

db.commit()

if db is None:
    print("DB connect failed")
    exit()
    
print("SUCCESS!")


f = open('2018-1.csv','r',encoding = 'utf8')

csvReader = csv.reader(f)

open = 20181
checko = "select `open_id` from `open` where time =%s"
cursor.execute(checko,(open))
result = cursor.fetchone()
open_id = result[0]

for row in csvReader:

    lec_code = (row[0])

    check = "select `id` from `course` where course_code =%s"

    cursor.execute(check,(lec_code))

    result = cursor.fetchone()

    if result is None:
        continue

    course_id = result[0]

    sec_id = (row[1])

    first = (row[7])

    second = (row[8])

    third = (row[9])

    fourth = (row[10])

    all = (row[11])

    retake = (row[12])


    print (lec_code + ' ing...')


    sql = "insert into basket (`open_id`, `course_id`, `sec_id`, `1st`, `2nd`, `3rd`, `4th`,`all`,     `re_take`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    cursor.execute(sql, (open_id, course_id, sec_id, first, second, third, fourth, all, retake))
    
    db.commit()




    

f.close()

db.close()
