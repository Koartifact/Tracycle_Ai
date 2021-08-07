import gdown
from flask import Flask, render_template, request, redirect, jsonify
import torch
from PIL import Image
import io
import argparse
from flask_cors import CORS
import pymysql
import dbconfig

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
CORS(app)

#구글 드라이브에서 가중치 파일 받는 것 추가 
google_path = 'https://drive.google.com/uc?id='
file_id = '1-bEBxnujEU-R-p29-QM8eFFeRICwjYey'

output_name = 'best.pt'
gdown.download(google_path+file_id, output_name,quiet=False)

#
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
        
        # 진철님 카테고리 받아오는 코드 들어갈 곳
        categoryId = 3 # 테스트용으로 3이라고 함

        result = get_result('tracycle', areaId, categoryId)
        print(result, "???")
        return jsonify(result)
        
        # if not file:
        #     return

        # img_bytes = file.read()
        # img = Image.open(io.BytesIO(img_bytes))
        # results = model(img, size=640)

        # # for debugging
        # data = results.pandas().xyxy[0].to_json(orient="records")
        # print(data)

        # results.render()  # updates results.imgs with boxes and labels
        # for img in results.imgs: 
        #     img_base64 = Image.fromarray(img)
        #     img_base64.save("static/result0.jpg", format="JPEG")
        #     img_url="static/result0.jpg"
        # return str(img_url)+str(data)
    return "no"
    #return render_template("index.html")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Flask app exposing yolov5 models")
    parser.add_argument("--port", default=8085, type=int, help="port number")
    args = parser.parse_args()

    model = torch.hub.load(
        'ultralytics/yolov5', 'custom', path='best.pt'
    ).autoshape()  # force_reload = recache latest code
    model.eval()
    app.run(host="0.0.0.0", port=args.port)  # debug=True causes Restarting with stat
