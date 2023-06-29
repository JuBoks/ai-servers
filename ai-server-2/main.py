from fastapi import FastAPI, Request
from pydantic import BaseModel
# FastAPI에서 CORSMiddleware라는 모듈로 CORS를 제어한다.
from fastapi.middleware.cors import CORSMiddleware
# from face_detection import detection
from face_detection import detection
from image_clustering import cluster_images
from tnr_filtering import detect_tnr
from common.util import save_image_from_url, empty_directory, save_json_file, get_json_file, send_cat_tnr_info
import requests
import os
from dotenv import load_dotenv

class Cluster(BaseModel):
  status: int
  num_clusters: int
  representative_images: list
  width: float
  height: float
  file_feature_info: list
  closest_images: list
  tnr_info: list
  tnr_count: int

class ClusterRequest(BaseModel):
  serial_number: object
  date: object
  result: Cluster


app = FastAPI()

app.mount("/aiapi", app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

FILE_SAVE_PATH = os.path.abspath('datasets/0_files')
JSON_PATH = os.path.abspath('datasets/4_result')
BACK_URL = os.environ['BACK_URL']
BACK_AI_URL = BACK_URL + "/ai/count"

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # cookie 포함 여부를 설정한다. 기본은 False
    allow_methods=["*"],    # 허용할 method를 설정할 수 있으며, 기본값은 'GET'이다.
    allow_headers=["*"],	# 허용할 http header 목록을 설정할 수 있으며 Content-Type, Accept, Accept-Language, Content-Language은 항상 허용된다.
)

@app.get("/")
def index():
  return "Hello World!"

# @app.get("/file")
def get_files(serial_number, date, file_path):
  # 폴더 비우기
  empty_directory(f'{file_path}/*')

  url = "/ai/image"
  params = {
    'date': date,
    'dishSerialNum': serial_number
  }
  response = requests.get(BACK_URL + url, params=params)
  # 응답 처리
  if response.status_code != 200:
     return {'status': 500, 'message': "get files failed." }
  
  result = response.json()  # JSON 응답 데이터 파싱

  os.makedirs(file_path, exist_ok=True)
  
  img_info = {}
  for el in result['data']:
    path = el['imagePath']
    id = el['dishImageId']
    save_image_from_url(path, f'{file_path}/{id}.jpg')
    img_info[f'{id}.jpg'] = path

  return img_info

# cluster 관련 정보 조회
@app.get("/info")
async def get_info(serial_number, date):
  file_name = f'{date}_{serial_number}.json'
  result = get_json_file(file_name)
  return result

# cluster 관련 정보 수정
@app.put("/info")
async def modify_cluster_info(cluster: ClusterRequest):
  file_name = f'{cluster.date}_{cluster.serial_number}'
  result_json = cluster.result.dict()
  isSuccess = await save_json_file(result_json, file_name)
  if isSuccess:
    isUpdateSuccess = send_cat_tnr_info(BACK_AI_URL, cluster.serial_number, cluster.date, result_json['num_clusters'], result_json['tnr_count'])
    if isUpdateSuccess == False:
      return {'status': 500, 'message': "send cluster information is failed." }
    return {'status': 200, 'message': "cluster information is modified." }
  else:
    return {'status': 500, 'message': "Internal Server Error."}

# [batch] 이미지 전처리, Clustering, TNR, Back으로 전송
@app.get("/detection")
async def face_detection(serial_number, date):
  try:
    folder_name = os.environ[f'{serial_number}']
    file_path = os.path.abspath(f'{FILE_SAVE_PATH}/{folder_name}')

    # 1. back으로부터 사진 파일 다운로드 하기
    img_info = get_files(serial_number, date, file_path)

    # 2. 다운로드 받은 사진들에 대해서 detection 진행하기
    detection(file_path)

    # 3. cluster 진행
    result = cluster_images()

    # 4. tnr판별
    result_tnr, tnrCount = detect_tnr()

    # 5. 데이터 정제
    for el in result['representative_images']:
      el[1] = img_info[el[1]]
    for el in result['file_feature_info']:
      el[0] = img_info[el[0]]
    for images in result['closest_images']:
      for i in range(len(images)):
        images[i] = img_info[images[i]]
    result['tnr_info'] = []
    for el in result_tnr:
      result['tnr_info'].append([img_info[el[0]], el[1]])
    result['tnr_count'] = tnrCount

    # 6. 데이터(result) 저장
    file_name = f'{date}_{serial_number}'
    await save_json_file(result, file_name)

    # 7. Back서버에 개체 수와 tnr 수 update하기
    isSuccess = send_cat_tnr_info(BACK_AI_URL, serial_number, date, result['num_clusters'], tnrCount)

    # 응답 처리
    if isSuccess == False:
      return {'status': 500, 'message': "send cluster information is failed." }
  except:
    file_name = f'{date}_{serial_number}'
    result = {
      'status': -1,
      # 'num_clusters': 0,
      # 'representative_images': [],
      # 'width': 0,
      # 'height': 0,
      # 'file_feature_info': [],
      # 'closest_images': [],
      # 'tnr_info': [],
      # 'tnr_count': 0
    }
    await save_json_file(result, file_name)

    # 7. Back서버에 개체 수와 tnr 수 update하기
    isSuccess = send_cat_tnr_info(BACK_AI_URL, serial_number, date, 0, 0)

    # 응답 처리
    if isSuccess == False:
      return {'status': 500, 'message': "send cluster information is failed." }
    
    return {'status': 500, 'message': "Internal Server Error, status: -1" }

  return result

@app.get("/representatives")
async def get_representatives(serial_number):
  result = {}
  for json_name in os.listdir(JSON_PATH):
    json_split = json_name.split('.')
    json_file_name = json_split[0]
    # Check if the file is a valid json file
    if json_split[-1].lower() not in ('.json'):
        continue
    
    json_split = json_file_name.split('_')
    json_file_date = json_split[0]
    json_file_serialNumber = json_split[1]

    # Serial Number가 다르면 Pass
    if json_file_serialNumber != serial_number: continue

    # 파일 읽어오기
    json_file = get_json_file(json_name)

    # '날짜': [] 형태로 result 만들기
    image_arr = []
    if 'representative_images' in json_file:
      for el in json_file['representative_images']:
        image_arr.append(el[1])
      result[f'{json_file_date}'] = image_arr
  
  return result

@app.get("/info/status")
def get_info_status(serial_number):
  result = {}
  for json_name in os.listdir(JSON_PATH):
    json_split = json_name.split('.')
    json_file_name = json_split[0]
    # Check if the file is a valid json file
    if json_split[-1].lower() not in ('.json'):
        continue
    
    json_split = json_file_name.split('_')
    json_file_date = json_split[0]
    json_file_serialNumber = json_split[1]

    # Serial Number가 다르면 Pass
    if json_file_serialNumber != serial_number: continue

    # 파일 읽어오기
    json_file = get_json_file(json_name)

    # '날짜': [] 형태로 result 만들기
    try:
      status = json_file['status']
    except:
      status = -1

    result[f'{json_file_date}'] = status
  
  return result