#### :link: 프론트엔드 - [Tracycle_WebProject_Front](https://github.com/eoc940/Tracycle_WebProject_Front)
#### :link: 백엔드 - [Tracycle_WebProject_Back](https://github.com/eoc940/Tracycle_WebProject_Back)

<br>

### :computer: 개발환경
---
- 기본 환경 
  - IDE : VS Code
  - OS : Windows
  - Git
  - Jupyter Notebook
- 웹서비스 개발환경
  - Python
  - Flask
  - Pytorch

<br>

### :rocket: Flask API 
---
##### API : predict()
- 사용자로부터 입력값을 받고 yolo5로 이미지를 인식한 후 해당 지역구와 이미지 라벨에 해당하는 결과를 리턴
```
userId = request.form.get('userId')
if request.method == 'POST':
    areaId = int(request.form.get('areaId'))
    if "mainFile" not in request.files:
        return redirect(request.url)
    file = request.files["mainFile"]
```
- userId, areaId, mainFile을 입력받는다
```
    img_bytes = file.read()
    img = Image.open(io.BytesIO(img_bytes))
    results = model(img, size=640)
    
    results.render()  
    for img in results.imgs:
        img_base64 = Image.fromarray(img)
        img_base64.save("static/"+userId+".jpg", format="JPEG")

    data = results.pandas().xyxy[0].to_json(orient="records")
```
- image 받은 것을 model()에 넣어서 yolo로 분석
- base64로 렌더링해서 userId + jpg로 저장
- 분석에서 나온 label을 json으로 저장

```
    info_list = list()   
    list_data = json.loads(data)
    class_id=set()
    for x in list_data:
        class_id.add(x['class'])
    class_id = list(class_id)

    if not class_id:
        print("Can't find object")
        infos = "Can't find object"

    else:
        for c in class_id:
            categoryId = c
            infos = get_result('tracycle', areaId, categoryId)
            for info in infos:
                info_list.append(info)

return jsonify(info_list)
```
- 분석결과 라벨링된 카테고리가 여러개일 경우 해당 결과를 전부 받아 리스트에 저장후 json으로 리턴


##### Etc. :  if __name__ == "__main__":

- 시작 시 플라스크와 yolo 구동
- 플라스트 설정 (port, host 조건)
- yolo 설정 (torch를 통해 yolov5 전체 코드 받아서 입력, custom 파일로 설정 후 pt파일 위치 설정 )


```
    parser = argparse.ArgumentParser(
        description="Flask app exposing yolov5 models")
    parser.add_argument("--port", default=8085, type=int, help="port number")
    args = parser.parse_args()

    model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt').autoshape()  # force_reload = recache latest code
    model.eval()
    # debug=True causes Restarting with stat
    app.run(host="0.0.0.0", port=args.port)
```

<br>



### :rocket: YoloV5 
---
##### Tracycle(yolov5).ipynb
- Yolo v5 다운로드 및 설치. 
```
!git clone https://github.com/ultralytics/yolov5
!cd yolov5;pip install -qr requirements.txt
```
- 대용랑 이미지를 업로드한 Google Drive 접근을 위한 마운트
```
import os, sys 
from google.colab import drive 

drive.mount('/content/gdrive')
```
- 자료 정제하여 라벨링, 결로 설정 작업을 정의한 yaml 작성 파일 받아오기

```
!wget -O /content/gdrive/MyDrive/Project_Data/Tracycle_Train.yaml https://raw.github.com/Koartifact/Tracycle_Ai/master/data/util/Tracycle_Train.yaml

```
- Train 수행 부분
- img 600 : 이미지 사이즈 640에서 오류가 잦아서 600으로 다운하여 학습
- batch 8 : 16 설정시 보다 좋은 결과를 가져와 8로 설정 
- epochs : 130 
- weights : yolov5m. 처음에는 s모델로 시작하였으나 좀더 좋은 성능을 위해 m 모델로 변경학습
- data : yaml 파일위치 설정. (라벨링 정보와 파일 경로)

```
!cd /content/yolov5; python train.py --img 600 --batch 8 --epochs 130 --data /content/gdrive/MyDrive/Project_Data/Tracycle_Train.yaml --weights yolov5m.pt \
                                     --project=/mydrive/Project_Data --name summary --exist-ok 

```

##### Yolo v5 아키텍처
- 소스코드 : https://github.com/ultralytics/yolov5
- models/yolov5m.yaml
```
# YOLOv5 🚀 by Ultralytics, GPL-3.0 license

# Parameters
nc: 80  # number of classes
depth_multiple: 0.67  # model depth multiple
width_multiple: 0.75  # layer channel multiple
anchors:
  - [10,13, 16,30, 33,23]  # P3/8
  - [30,61, 62,45, 59,119]  # P4/16
  - [116,90, 156,198, 373,326]  # P5/32

# YOLOv5 backbone
backbone:
  # [from, number, module, args]
  [[-1, 1, Focus, [64, 3]],  # 0-P1/2
   [-1, 1, Conv, [128, 3, 2]],  # 1-P2/4
   [-1, 3, C3, [128]],
   [-1, 1, Conv, [256, 3, 2]],  # 3-P3/8
   [-1, 9, C3, [256]],
   [-1, 1, Conv, [512, 3, 2]],  # 5-P4/16
   [-1, 9, C3, [512]],
   [-1, 1, Conv, [1024, 3, 2]],  # 7-P5/32
   [-1, 1, SPP, [1024, [5, 9, 13]]],
   [-1, 3, C3, [1024, False]],  # 9
  ]

# YOLOv5 head
head:
  [[-1, 1, Conv, [512, 1, 1]],
   [-1, 1, nn.Upsample, [None, 2, 'nearest']],
   [[-1, 6], 1, Concat, [1]],  # cat backbone P4
   [-1, 3, C3, [512, False]],  # 13

   [-1, 1, Conv, [256, 1, 1]],
   [-1, 1, nn.Upsample, [None, 2, 'nearest']],
   [[-1, 4], 1, Concat, [1]],  # cat backbone P3
   [-1, 3, C3, [256, False]],  # 17 (P3/8-small)

   [-1, 1, Conv, [256, 3, 2]],
   [[-1, 14], 1, Concat, [1]],  # cat head P4
   [-1, 3, C3, [512, False]],  # 20 (P4/16-medium)

   [-1, 1, Conv, [512, 3, 2]],
   [[-1, 10], 1, Concat, [1]],  # cat head P5
   [-1, 3, C3, [1024, False]],  # 23 (P5/32-large)

   [[17, 20, 23], 1, Detect, [nc, anchors]],  # Detect(P3, P4, P5)
  ]

```
- Yolo v5도 일반적인 Object Detection 구성과 거의 같음
- 크게 Backbone 과 Head 부분으로 구성 
- 참고 : https://ropiens.tistory.com/44
- 참고 : https://blog.csdn.net/Q1u1NG/article/details/107511465

<br>
  
### :family: Contributors
--- 
- [Cloud0720](https://github.com/Cloud0720)
- [EunchongJeong](https://github.com/EunchongJeong)
- [root-devvoo](https://github.com/root-devvoo)
- [Koartifact](https://github.com/Koartifact)
- [SS0mmy](https://github.com/SS0mmy)
- [Suziny91](https://github.com/Suziny91)
- [sxxzin](https://github.com/sxxzin)
