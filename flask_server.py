import gdown
from flask import Flask, render_template, request, redirect
import torch
from PIL import Image
import os
import io
import argparse
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
CORS(app)

#구글 드라이브에서 가중치 파일 받는 것 추가 
google_path = 'https://drive.google.com/uc?id='
file_id = '1SpZl2eB4zELOFmNBkObP1DAmTdmOWPZP'
output_name = 'best.pt'
gdown.download(google_path+file_id, output_name,quiet=False)

@app.route("/", methods=["GET", "POST"])
def predict():
    print("되나?")
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if not file:
            return

        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))
        results = model(img, size=640)

        # for debugging
        # data = results.pandas().xyxy[0].to_json(orient="records")
        # return data

        results.render()  # updates results.imgs with boxes and labels
        for img in results.imgs:
            img_base64 = Image.fromarray(img)
            img_base64.save("static/result0.jpg", format="JPEG")
        return redirect("static/result0.jpg")

    return render_template("index.html")


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
