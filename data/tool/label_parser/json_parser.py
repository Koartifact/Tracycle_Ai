import json
import glob


def convert(size, box):
        dw = 1./size[0]
        dh = 1./size[1]
        x = (box[0] + box[1])/2.0
        y = (box[2] + box[3])/2.0
        w = box[1] - box[0]
        h = box[3] - box[2]
        x = round(x*dw, 6)
        w = round(w*dw, 6)
        y = round(y*dh, 6)
        h = round(h*dh, 6)
        return (x,y,w,h)

def categorize(category):
    if '액자' in category:
        return '0'
    elif '자전거' in category:
        return '1'
    elif '화분' in category:
        return '2'
    elif '항아리' in category:
        return '3'
    elif '냉장고' in category:
        return '4'
    elif '세탁기' in category:
        return '5'
    elif 'TV' in category:
        return '6'
    elif '에어컨' in category:
        return '7'
    elif '전기정수기' in category:
        return '8'
    elif '컴퓨터' in category:
        return '9'
    elif '전기밥솥' in category:
        return '10'
    elif '이동전화단말기' in category:
        return '11'
    elif '선풍기' in category:
        return '12'
    elif '믹서' in category:
        return '13'
    elif '가습기' in category:
        return '14'
    elif '프린터' in category:
        return '15'
    elif '전기다리미' in category:
        return '16'
    elif '청소기' in category:
        return '17'
    elif '공기청정기' in category:
        return '18'
    elif '장롱' in category:
        return '19'
    elif '의자' in category:
        return '20'
    elif '소파' in category:
        return '21'
    elif '화장대' in category:
        return '22'
    elif '책상' in category:
        return '23'
    elif '수납장' in category:
        return '24'
    elif '밥상' in category:
        return '25'
    elif '골프채' in category:
        return '26'
    elif '서랍장' in category:
        return '27'
    elif '전자레인지' in category:
        return '28'
    elif '프라이팬' in category:
        return '29'
    else: 
        return 'False'


file_lists = glob.glob(r'C:/encore_kdh/Yolo_Data/Training/형광등/**/**/*.Json', recursive=True)

for path in file_lists:
    json_name = path.split('.Json')[0]

    with open(f'{path}', encoding='utf-8') as f:
        data = json.load(f)
        f.close()

    bound = data['Bounding']
    size = data['RESOLUTION'].split('*')
    size=list(map(float,size))


    i=0
    while i < len(bound):
        type = categorize(bound[i]['DETAILS'])

        if type !='False' and bound[i]['Drawing'] == 'BOX':
                box =[bound[i]['x1'], bound[i]['x2'], bound[i]['y1'], bound[i]['y2']]
                box=list(map(float, box))

                yolo_bound = list(map(str,convert(size,box)))
                result = type+' '+yolo_bound[0]+' '+yolo_bound[1]+' '+yolo_bound[2]+' '+yolo_bound[3]+'\n'

                if i==0:
                    with open(f'{json_name}.txt', 'w') as f:
                        f.write(result)
                else:
                    with open(f'{json_name}.txt', 'a') as f:
                        f.write(result)        

        i+=1

    f.close()