from flask import Flask
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import jsonify, request
import pandas as encjson
import requests
import json

url ='mysql://root:dba@localhost:3306/Project?charset=utf8mb4'

app = Flask(__name__)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
    
app.config['SQLALCHEMY_DATABASE_URI'] = url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db = SQLAlchemy(app)

engine = create_engine(url, pool_size = 20, pool_recycle= 500)

def loadMajorList():
    
    query = "SELECT * from major"
    
    data = encjson.read_sql_query(query, engine)
    
    return json.loads(data.to_json(orient='records'))

def loadInjungList():

    query = "SELECT * from injung"

    data = encjson.read_sql_query(query, engine)

    return json.loads(data.to_json(orient='records'))
    
def wReview(course_id,open_id,prof_name,desc):

    #openId = "(SELECT open_id from open WHERE time = " + str(open_id) + ")"
    
    query = "INSERT INTO review VALUES( default," +str(course_id) +", "+ str(open_id) + ", '"+ prof_name +"', '"+ desc +"');"
    
    print(query)
    
    data = encjson.read_sql_query(query, engine)

    return ' '
    


def loadReview(course_id, prof_name):

    if course_id is not None :
        #condition_1 = " course.id = review.course_id and course.title = '" + course_id + "'"
        condition_1 = " course.id = " + course_id
    else:
        condition_1 = ' '
        
    if prof_name is not None : 
        condition_2 = " review.prof_name = '" + prof_name + "'"
    else:
        condition_2 = ' '

    test_list = [condition_1, condition_2] 
    condition = " course.id = review.course_id "

    for i in test_list:
        if(i != ' '):
            condition = condition + " and " +i

    section_query = "SELECT review.prof_name, review.description from review join course where " + condition +";"
    
    print(section_query)

    data = encjson.read_sql_query(section_query, engine)

    return json.loads(data.to_json(orient='records'))
    
def loadRecommend(major_code,semester):

     person_q = "SELECT id from user where major1 = " + major_code + ";"
     
     data = encjson.read_sql_query(person_q, engine)
     
     hak_list = data.values.tolist()
     
     concatJson = list()
     
     for stu in hak_list:
        print(stu)
        loadTaken = "SELECT DISTINCT (c.title),user_id,c.id from course as c JOIN (SELECT course_id, user_id from user_history where user_id = "+ str(stu[0]) +" AND semester = "+ str(semester) +") as s ON s.course_id = c.id;"
        result = encjson.read_sql_query(loadTaken, engine)

        concatJson.append(json.loads(result.to_json(orient='records')))
     
    
     return concatJson

def loadSearch (major_code, injung_code, prof_name, course_name, open_time) :

   
    if injung_code is not None:
        condition_1 = "inj_code = '" + injung_code + "'"
    else:
        condition_1 = ' '
        
    if open_time is not None:
        condition_2 = "open_id = (SELECT open_id from open WHERE time = " + str(open_time) + ")"
    else:
        condition_2 = ' '

    if course_name is not None:
        condition_3 = "title LIKE \"%%" + course_name + "%%\""
    else:
        condition_3 = ' '
        
    if major_code is not "0":
        condition_4 = "major_code = " + str(major_code) + ""
    else:
        condition_4 = ' '
        
    if prof_name is not None:
        condition_5 = "prof_name = '" + prof_name + "'"
    else:
        condition_5 = ' '
        
    list = []
    list.extend([condition_1,condition_2,condition_3,condition_4,condition_5])
    
    condition = ' '
    for i in list:
        if(i != ' '):
            if(condition == ' '):
                condition =  i
            else:
                condition = condition + " and " +i
        
    section_query = "SELECT c.id, c.title, sec_id as section, section.open_id, credits, prof_name ,time, building, inj_code, total_stu from section join course as c where (" + condition + " and c.id = course_id);"
    
    print(section_query)

    data = encjson.read_sql_query(section_query, engine)

    return json.loads(data.to_json(orient='records'))
    
def loadProgen():

    query = "SELECT course_id from condition1"
    
    data = encjson.read_sql_query(query, engine)
    
    return json.loads(data.to_json(orient='records'))

def loadDetail(course_id, open_time) :
    condition = " basket.course_id = section.course_id and basket.sec_id = section.sec_id and section.open_id = basket.open_id"
    
    condition_1 = " and section.open_id = " + str(open_time)
    
    condition_2 = " and section.course_id = " + str(course_id) + ";"
    
    condition = condition + condition_1 + condition_2
    
    section_query = "SELECT prof_name, section.sec_id, time, total_stu, `1st`,`2nd`,`3rd`,`4th`, `all`, re_take from section join basket where " + condition
    
    print(section_query)
    
    data = encjson.read_sql_query(section_query, engine)
    return json.loads(data.to_json(orient='records'))

def loadBasket (major_code, injung_code, prof_name, course_name, open_time) :

   
    if injung_code is not None:
        condition_1 = "inj_code = (SELECT inj_code from injung WHERE kor = '" + injung_code + "')"
    else:
        condition_1 = ' '
        
    if open_time is not None:
        condition_2 = "section.open_id = (SELECT open_id from open WHERE time = " + str(open_time) + ")"
    else:
        condition_2 = ' '

    if course_name is not None:
        condition_3 = "c.title LIKE '%%" + course_name + "%%'"
    else:
        condition_3 = ' '
        
    if major_code is not "0":
        condition_4 = "major_code = " + str(major_code) + ""
    else:
        condition_4 = ' '
        
    if prof_name is not None:
        condition_5 = "prof_name = '" + prof_name + "'"
    else:
        condition_5 = ' '
        
    list = []
    list.extend([condition_1,condition_2,condition_3,condition_4,condition_5])
    
    condition = ' '
    for i in list:
        if(i != ' '):
            if(condition == ' '):
                condition =  i
            else:
                condition = condition + " and " +i
        
    section_query = "SELECT c.id, c.title, section.sec_id as section, o.time as open, credits, prof_name ,section.time, building, inj_code, total_stu, `1st`, `2nd`,`3rd`,`4th`, `all`, re_take from section join course as c on c.id = course_id join basket as b on c.id = b.course_id join open as o on b.open_id = o.open_id and section.open_id = b.open_id and section.sec_id = b.sec_id where (" + condition + " );"
    
    print(section_query)

    data = encjson.read_sql_query(section_query, engine)

    return json.loads(data.to_json(orient='records'))
    
def loadBasketC (major_code, injung_code, prof_name, course_name, open_time, order) :

    if order is None:
        order = 'DESC'


    if injung_code is not None:
        condition_1 = "i.inj_code = (SELECT inj_code from injung WHERE kor = '" + injung_code + "')"
    else:
        condition_1 = ' '
    
    if open_time is not None:
        condition_2 = " AND s.open_id = (SELECT open_id from open WHERE time = " + str(open_time) +    ")"
    else:
        condition_2 = ' '
    
    if course_name is not None:
        condition_3 = " AND c.title LIKE '%%" + course_name + "%%'"
    else:
        condition_3 = ' '
    
    if major_code is not "0":
        condition_4 = "i.major_code = " + str(major_code) + ""
    else:
        condition_4 = ' '
    
    if prof_name is not None:
        condition_5 = "i.prof_name = '" + prof_name + "'"
    else:
        condition_5 = ' '
    
    list = []
    list.extend([condition_1,condition_4,condition_5])
    
    condition = ' '
    for i in list:
        if(i != ' '):
            if(condition == ' '):
                condition =  i
            else:
                condition = condition + " AND " +i
    
    section_query = "select i.title, i.sec_id, i.prof_name, o.time as open, i.total_stu,  b.all as apply, (b.all / i.total_stu) as competition, i.time, i.building from basket as b JOIN (select c.id, c.title, s.sec_id, s.building, s.time, s.open_id, s.total_stu, s.prof_name, c.major_code, c.inj_code from course as c JOIN section as s ON c.id= s.course_id WHERE s.total_stu <> 1 "+ condition_2 +condition_3+") as i ON i.id = b.course_id AND "+ condition +" AND i.sec_id = b.sec_id AND i.open_id = b.open_id JOIN open as o on i.open_id = o.open_id ORDER BY competition "+ order +";"
    
    print(section_query)
    
    data = encjson.read_sql_query(section_query, engine)
    
    return json.loads(data.to_json(orient='records'))

def loadPick(user_id, course_code, section_code, semester, open_id) :
   
    condition_2 = str(user_id) + ", "
    
    condition_3 = str(course_code) + ", "
        
    condition_4 = str(section_code) + ","
  
    condition_5 = str(semester) + "," + str(open_id)

    condition = "VALUES ( " + condition_2 + condition_3 + condition_4 + condition_5 + ");"
  
    section_query = "INSERT INTO user_history(user_id, course_id, section_code, semester, open_id) " + condition

    print(section_query)

    data = encjson.read_sql_query(section_query, engine)

    return "<html><body><h1>working!</h1></body></html>"


def loadDelete(user_id, course_name, semester) :

    condition = "where user_id = " + str(user_id) + " and course_id = (SELECT id FROM course WHERE title = '" + course_name + "') and semester = " + semester  
    section_query = "DELETE FROM user_history " + condition +";"

    print(section_query)

    data = encjson.read_sql_query(section_query, engine)

    return "<html><body><h1>working!</h1></body></html>"


def loadAccount (user_id, user_name, semester, major1, major2) :

    condition_1 = str(user_id) + ", "
   
    condition_2 = "'" +user_name + "', "

    condition_3 = str(semester) + ", "
        
    condition_4 = str(major1)
    
    if major2 is None:
        condition = "VALUES (" + condition_1 + condition_2 + condition_3 + condition_4 + ", 0);"
    else:
        condition = "VALUES (" + condition_1 + condition_2 + condition_3 + condition_4 + ", " + str(major2) + ");"

    section_query = "INSERT INTO user " + condition

    print(section_query)

    data = encjson.read_sql_query(section_query, engine)

    return ' '

def loadLogin (user_id):
    
    section_query = "SELECT * from user where id = " + str(user_id) + ";"
    print(section_query)
    data = encjson.read_sql_query(section_query, engine)
    
    return json.loads(data.to_json(orient='records'))

def loadCourses(key_word, major) :

    section_query = "SELECT course.id, title, credits from course "

    if(key_word >= '0' and key_word < '1'):
        section_query = section_query + "WHERE major_code =" + str(major) + ";"
    elif (key_word >= '1' and key_word < '2'):
        section_query = section_query + "WHERE inj_code = 'W04' OR inj_code = 'W07' OR inj_code = 'W08' OR inj_code = 'W09';"
    elif (key_word >= '2' and key_word < '3'):
        section_query = section_query + "WHERE inj_code = 'W05' OR inj_code = 'W06' OR inj_code = 'W30';"
    elif (key_word >= '3' and key_word < '4'):
        section_query = section_query + "WHERE inj_code = 'W19' OR inj_code = 'W32';"
    elif (key_word >= '4' and key_word < '5'):
        section_query = section_query + "WHERE inj_code = 'W29';"
    elif (key_word >= '5' and key_word < '6'):
        section_query = section_query + "join condition1 c on course.id = c.course_id;"
    elif (key_word >= '6' and key_word < '7'):
        section_query = section_query + "WHERE inj_code = 'W57';"


    print(section_query)

    data = encjson.read_sql_query(section_query, engine)

    return json.loads(data.to_json(orient='records'))
    
def loadMyCourses(hakbun,semester):

    if semester is None: #모든수업 불러오기. 학점계산용

        query = "SELECT c.id, c.title, c.credits, c.major_code, c.inj_code from course as c JOIN(SELECT course_id from user_history WHERE user_id = "+ str(hakbun) + ") as h ON c.id= h.course_id;"
        
    else: #현재학기의 시간표 불러오기.
        
        query = "SELECT c.id, c.title, h.time, c.credits, c.major_code, c.inj_code, h.open_id from course as c JOIN(SELECT s.course_id, s.time, s.open_id from section as s JOIN(SELECT course_id,section_code, open_id from user_history WHERE user_id = " + str(hakbun) +" AND semester = " + str(semester) + ") as h ON h.course_id = s.course_id AND s.open_id = h.open_id AND h.section_code = s.sec_id) as h ON c.id= h.course_id;"

    data =encjson.read_sql_query(query, engine)
    
    
    return json.loads(data.to_json(orient='records'))
    
def loadGraduate():

    query = "SELECT * from graduate"
    
    data =encjson.read_sql_query(query, engine)
    
    return json.loads(data.to_json(orient='records'))
    
    
#========================= Router functions ============================

@app.route('/', methods=['GET',])
def index():
    return "<html><body><h1>working!</h1></body></html>"


@app.route('/majorList', methods=['GET'])
def getMajorList():
    return jsonify(loadMajorList())
    
@app.route('/injungList', methods=['GET'])
def getInjungList():
    return jsonify(loadInjungList())

@app.route('/review', methods=['GET', 'POST'])
def getReview():

    course_id = request.args.get('course_id')
    prof_name = request.args.get('prof_name')
    return jsonify(loadReview(course_id,prof_name))
    
@app.route('/writeReview', methods=['GET','POST'])
def writeReview():

    course_id = request.args.get('course_id')
    open_id = request.args.get('open_id')
    prof_name = request.args.get('prof_name')
    desc = request.args.get('desc')
    
    return jsonify(wReview(course_id,open_id,prof_name,desc))
    

@app.route('/search', methods=['GET', 'POST'])
def getSearch():

    major_code = request.args.get('major_code')
    injung_code = request.args.get('injung_code')
    prof_name = request.args.get('prof_name')
    course_name = request.args.get('course_name')
    open_time = request.args.get('open_time')

    return jsonify(loadSearch(major_code,injung_code,prof_name,course_name,open_time))

@app.route('/basket', methods=['GET', 'POST'])
def getBasket():

    major_code = request.args.get('major_code')
    injung_code = request.args.get('injung_code')
    prof_name = request.args.get('prof_name')
    course_name = request.args.get('course_name')
    open_time = request.args.get('open_time')

    return jsonify(loadBasket(major_code,injung_code,prof_name,course_name,open_time))

@app.route('/basket_byC', methods=['GET', 'POST'])
def getBasketC():

    major_code = request.args.get('major_code')
    injung_code = request.args.get('injung_code')
    prof_name = request.args.get('prof_name')
    course_name = request.args.get('course_name')
    open_time = request.args.get('open_time')
    order = request.args.get('order')
    
    return jsonify(loadBasketC(major_code,injung_code,prof_name,course_name,open_time,order))

@app.route('/pick', methods=['GET', 'POST'])
def getPick():

    user_id = request.args.get('user_id')
    course_code = request.args.get('course_code')
    section_code = request.args.get('section_code')
    semester = request.args.get('semester')
    open_id = request.args.get('open_id')

    return loadPick(user_id ,course_code, section_code, semester, open_id)

@app.route('/delete', methods=['GET', 'POST'])
def getDelete():

    user_id = request.args.get('user_id')
    course_name = request.args.get('course_name')
    semester = request.args.get('semester')

    return loadDelete(user_id ,course_name,semester)


@app.route('/account', methods=['GET', 'POST'])
def getAccont():

    user_id = request.args.get('user_id')
    user_name = request.args.get('user_name')
    semester = request.args.get('semester')
    major1 = request.args.get('major1')
    major2 = request.args.get('major2')

    return loadAccount (user_id, user_name, semester, major1, major2)

@app.route('/login', methods=['GET', 'POST'])
def getLogin():
    
    user_id = request.args.get('user_id')
    
    return jsonify(loadLogin(user_id))


@app.route('/detail', methods=['GET', 'POST'])
def getDetail():

    course_id = request.args.get('course_id')
    open_time = request.args.get('open_time')

    return jsonify(loadDetail(course_id,open_time))
    
    
@app.route('/recommend', methods=['GET', 'POST'])
def getRecommand():

    major_code = request.args.get('major_code')
    semester = request.args.get('semester')

    return jsonify(loadRecommend(major_code,semester))

@app.route('/courses', methods=['GET', 'POST'])
def getCourses():

    key_word = request.args.get('key_word')
    major = request.args.get('major')

    return jsonify(loadCourses(key_word, major))

@app.route('/progen', methods=['GET', 'POST'])
def getProgen():


    return jsonify(loadProgen())
    
@app.route('/my_courses', methods=['GET'])
def getMyCourses():
    
    hakbun = request.args.get('hakbun')
    semester = request.args.get('semester')

    return jsonify(loadMyCourses(hakbun,semester))

@app.route('/check', methods=['GET'])
def getGraduate():

    return jsonify(loadGraduate())

