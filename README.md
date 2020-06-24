# DB TEAM PROJECT

DB수업 데이터베이스 구축을 위한 python 코드들.

## Env.
 OS : ubuntu18.04.4LTS<br>
 mySQL : 5.7.30<br>
 python3
 gunicorn3
 supervisord

## Files

  app.py (REST API Server)<br>
  API서버 구축으로 인해 어플리케이션 뿐 만 아니라, 웹이나 다른 서비스로도 쉽게 DB를 이식/사용할 수 있다.
  
  ```python
  #home/ubuntu/app.py
  
  #mobile application으로 부터 요청된 request를 가공하여 mySQL로 쿼리문을 날리고 그 결과를 json으로 반환해주는 WSGI REST API 서버.
  #해당하는 라우팅주소 + parameter를 만들어 인터넷 창에 쳐서 가시적으로 확인 
  #예시 : http://52.14.37.173:5000/basket_byC?major_code=1&open_time=20201&order=DESC 인터넷  주소창에 쳐보면 확인 가능. 
  #이렇게 얻은 json 데이터를 flutter App에서 받아서 가공 후 표시하는것이 목적
  #AWS서버 안에 gunicorn3와 supervisord를 이용해서 항상 켜져있다.
  
  
  #추가하는 법.
  #=> 기본적으로 라우팅함수와 그에 대한 쿼리함수를 작성해서 사용.
  
  #쿼리함수예:
  def getGLS():
    query = "SELECT * from course where inj_code = 'W57'" #실질적인 쿼리 부분 유동적인 부분은에 대한 작성은 뒤에 기술
    
    data = encjson.read_sql_query(query, engine) #앞에 입력한 쿼리를 넣어줌
    
    return json.loads(data.to_json(orient='records')) #이부분은 거의 고정
  
  #라우팅함수 형식
  @app.route('/<사용할경로>', methods=['GET', 'POST']) //요청할 경로와 method를 설정해준다
  def 함수이름():
   ... //쿼리함수로 넘겨줄 변수를 선언하는 등 작업
   return jsonify(쿼리함수())//쿼리함수의 데이터 결과를 json화 하여 반환
   
  #라우팅함수 예: 
  @app.route('/gls', methods=['GET', 'POST'])
  def test():
   return jsonify(getGLS())
   
  #변수에 따른 쿼리문 예 (전달받은 전공코드에 해당하는 수업 가져오기):
  
  def getMajor(major_code):
    
    query = "SELECT * from course where major_code = " + str(major_code) # +를 통해 쿼리문에 변수 합치기
    
    data = encjson.read_sql_query(query, engine) #동일
    
    return json.loads(data.to_json(orient='records')) #동일
    
  @app.route('/major', methods=['GET', 'POST'])
  def test():
  #요청을 통해 전달받은 값을 변수로 저장 예: http://52.14.37.173:5000/major?major_code=1로 요청을 보냈을때 request.args.get으로가져옴
    major_code = request.args.get('major_code') 
    
    return jsonify(getMajor(major_code)) #위에서 저장한거 함수로넘겨주기
  
   
 
  ```

  db.py
  ```
  Dependencies: requests, bs4, pymysql
  
  한동대학교의 수업 정보를 추출해 mySQL에 추가한다.
  추출경로는 Hisnet - 개설강의정보 페이지에 적절한 파라미터를 post하여 결과를 crawling한다.
  우선 전공을 탐색 -> 각 전공 별 과목검색. 이때 보존하고있던 전공 코드를 과목의 fk로 사용한다.
  각 과목은 한 번만 저장하고, 과목별 분반을 저장할 때는 해당 과목의 course_id를 fk로 사용한다.
  위의 작업을 유저가 제공한 연도-학기 에 대해 반복한다.
  
  Functions
  
  get_lecture_list() -> 존재하는 전공과 그에 대한 수업들을 추출하고 저장
  get_kor_inj() -> 인정구분 목록 추출하여 저장
  
  init params : (('id','pw'),year)     #year format : 20201  == 2020년 1학기
  
  ```
  ![스크린샷 2020-05-10 오후 11 42 31](https://user-images.githubusercontent.com/47979730/81502274-fa3c2d00-9317-11ea-84b4-68168d3eaa51.png)
  
  
  eval.py
  ```
  Dependencies:  bs4, pymysql, selenium
  
  한동대학교 에브리타임의 강의평가를 추출해 mySQL에 추가한다.
  requests 대신에 selenium을 사용했으므로 사용 시 chrome_driver가 필요하다.
  모든 강의평가를 추출해 해당 과목명, 개설시기를 DB상에 있는 정보에 참조하여 FK로 사용한다.
  
  id,pw를 설정한뒤 실행
  ```
  
  ![image](https://user-images.githubusercontent.com/47979730/85479538-52459f00-b5f9-11ea-9f31-a1caa7b17bba.png){: width="50%" height="50%"}
  
  csvreader.py
  ```
  Dependencies: csv, pymysql
  
  2020-1 이전에 제공된 예비수강 엑셀파일을 DB에 추가한다.
  과목코드를 DB의 course 테이블과 대조해 FK키로 쓸 course_id값을 추출해주는 역할을 한다.
  
  파일 이름을 설정하고 실행
  
  ```
  
  ![image](https://user-images.githubusercontent.com/47979730/85479506-435eec80-b5f9-11ea-9009-5d955d91139f.png){: width="50%" height="50%"}
## Todo
- csvreader.py 파일이름, 연도-학기 외부 파라미터로 받게 설정
- DB.py get_kor_inj, get_eng_inj 통일화


