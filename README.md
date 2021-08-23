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
- image 받은 것을 yolo로 분석
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

<br>

  
### :family: Contributors
--- 
- [Cloud0720](https://github.com/Cloud0720)
- [EunchongJeong](https://github.com/EunchongJeong)
- [iceman-brandon](https://github.com/iceman-brandon)
- [Koartifact](https://github.com/Koartifact)
- [SS0mmy](https://github.com/SS0mmy)
- [Suziny91](https://github.com/Suziny91)
- [sxxzin](https://github.com/sxxzin)
