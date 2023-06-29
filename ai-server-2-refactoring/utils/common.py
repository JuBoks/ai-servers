import glob
import os
import cv2
import shutil
import requests
import json
import asyncio

JSON_PATH = os.path.abspath("datasets/4_result")
BACK_URL = os.environ["BACK_URL"]
BACK_AI_URL = os.environ["BACK_AI_URL"]

# 이미지 전처리 함수
def resize_img(im, img_size):
    old_size = im.shape[:2]  # old_size is in (height, width) format
    ratio = float(img_size) / max(old_size)
    new_size = tuple([int(x * ratio) for x in old_size])
    # new_size should be in (width, height) format
    im = cv2.resize(im, (new_size[1], new_size[0]))
    delta_w = img_size - new_size[1]
    delta_h = img_size - new_size[0]
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)
    new_im = cv2.copyMakeBorder(
        im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0]
    )

    return new_im, ratio, top, left


# 산출물 일괄 삭제
def empty_directory(path):
    for file in glob.glob(path):
        try:
            os.remove(file)
        except:
            shutil.rmtree(file)


# 이미지 파일 저장
def save_image_from_url(url, file_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


# json파일 저장하기
async def save_json_file(data, file_name):
    try:
        with open(f"datasets/4_result/{file_name}.json", "w") as file:
            json.dump(data, file)
        await asyncio.sleep(0)  # 파일이 실제로 디스크에 저장되기까지 대기
        return True
    except Exception as e:
        return False


# json파일 읽기
def get_json_file(file_name):
    try:
        with open(f"{JSON_PATH}/{file_name}", "r") as file:
            data = json.load(file)
    except Exception as e:
        return
    return data

# tnr정보를 Back서버에 보냄
def send_cat_tnr_info(serial_number, date, catCount, tnrCount):
    data = {
        "catCount": catCount,
        "date": date,
        "dishSerialNum": serial_number,
        "tnrCount": tnrCount,
    }
    response = requests.put(BACK_AI_URL, json=data)

    # 응답 처리
    if response.status_code != 200:
        return False
    else:
        return True

# 사진 정보 가져오기
def get_files(serial_number, date, file_path):
    # 폴더 비우기
    empty_directory(f"{file_path}/*")

    # 사진 파일 가져오기
    url = "/ai/image"
    params = {"date": date, "dishSerialNum": serial_number}
    response = requests.get(BACK_URL + url, params=params)
    # 응답 처리
    if response.status_code != 200:
        return {"status": 500, "message": "get files failed."}

    result = response.json()  # JSON 응답 데이터 파싱

    os.makedirs(file_path, exist_ok=True)

    img_info = {}
    for el in result["data"]:
        path = el["imagePath"]
        id = el["dishImageId"]
        save_image_from_url(path, f"{file_path}/{id}.jpg")
        img_info[f"{id}.jpg"] = path

    return img_info