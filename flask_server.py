import gdown
from flask import Flask, render_template, request, redirect, jsonify
import torch
from PIL import Image
import io
import argparse
from flask_cors import CORS
import pymysql
import dbconfig
import json
############  파일 감시 추가
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



#### 구글 드라이브에서 가중치 파일 받는 것 추가 테스트 땐 한번 받고나면 주석처리
# google_path = 'https://drive.google.com/uc?id='
# file_id = '1-bEBxnujEU-R-p29-QM8eFFeRICwjYey'
# output_name = 'best.pt'
# gdown.download(google_path+file_id, output_name,quiet=False)
####


#### 파일 감시부분 ###########################################
class Target:
    watchDir = os.getcwd()
    #watchDir에 감시하려는 디렉토리를 명시한다.

    def __init__(self):
        self.observer = Observer()  # observer객체를 만듦

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDir,
                               recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print("Error")
            self.observer.join()

class Handler(FileSystemEventHandler):
    #FileSystemEventHandler 클래스를 상속받음.
    #아래 핸들러들을 오버라이드 함

    def on_created(self, event): #파일, 디렉터리가 생성되면 실행
        생성되면 result0 을 result1로 바꿈 바꿀때 덮어씌움 그럼 0은 다시 만들기 전까지 없어지는 것 만들기

# def on_modified(self, event): #파일, 디렉터리가 수정되면 실행

    
#############################################################



#### flask 서버 시작 #####################
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
CORS(app)


def get_result(dbname, areaId, categoryId):
    print(type(areaId))
    print(type(categoryId))
    if dbname != dbconfig.DATABASE_CONFIG['dbname']:
        raise ValueError("Could not find DB with given name")
    conn = pymysql.connect(host=dbconfig.DATABASE_CONFIG['host'],
                           user=dbconfig.DATABASE_CONFIG['user'],
                           password=dbconfig.DATABASE_CONFIG['password'],
                           db=dbconfig.DATABASE_CONFIG['dbname'])
    cursor = conn.cursor()
    sql = '''
    SELECT r.price, r.standard, r.description, c.category_name, a.area_name, a.url, a.telephone
    FROM result AS r
    JOIN category AS c ON c.category_id=r.category_id
    JOIN area AS a ON a.area_id=r.area_id
    WHERE a.area_id = %s and c.category_id = %s;
    '''
    cursor.execute(sql, (areaId, categoryId))
    result = cursor.fetchall()
    conn.close()
    return result


@app.route("/service", methods=["GET", "POST"])
def predict():
    print("지역구 :", request.form.get('areaId'))
    print("사용자 :", request.form.get('userId'))
    if request.method == 'POST':
        areaId = int(request.form.get('areaId'))
        if "mainFile" not in request.files:
            return redirect(request.url)
        file = request.files["mainFile"]
        print(file)

    ########################################################################
     # yolo에서 보내주는 값 json 으로 받음 기본설정이라 안건드림
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))
        results = model(img, size=640)

        results.render()  # updates results.imgs with boxes and labels
        for img in results.imgs:
            img_base64 = Image.fromarray(img)
            img_base64.save("static/result0.jpg", format="JPEG")

        data = results.pandas().xyxy[0].to_json(orient="records")
    ########################################################################

        # 파싱을 위해 리스트로 바꾸어서 파싱
        list_data = json.loads(data)
        # 클래스 명이 리스트로 저장 (detect 된 종류가 여려개면 여러개 순서로)
        class_name = []
        for x in list_data:
            class_name.append(x['class'])
        print(class_name)

        if not class_name:
            print("Can't find object")
            infos = "Can't find object"

        else:
         
            for c in class_name:
                categoryId = c
                print(categoryId)
                infos = get_result('tracycle', areaId, categoryId)
                print(infos)

    return jsonify(infos)

################################################
@app.route("/img", methods=["GET", "POST"])
def show():
    if request.method == 'GET':
        print('GET')
        link = "static/result1.jpg" # result0이 안만들어지거나 없으면 1이 안생김
    return jsonify(link)
################################################ 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Flask app exposing yolov5 models")
    parser.add_argument("--port", default=8085, type=int, help="port number")
    args = parser.parse_args()

    model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt').autoshape()  # force_reload = recache latest code
    model.eval()
    # debug=True causes Restarting with stat
    app.run(host="0.0.0.0", port=args.port)

    w = Target("static/")
    w.run()
