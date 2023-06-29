# -*- coding: utf-8 -*-
"""TNR_Filter_YOLO.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JISDszpvVPoxrx32oUmnzzcxg3NNrdmL
"""
import os
import ast
import subprocess
from utils.common import empty_directory

tnr_input_path = "datasets/3_tnr/input"
tnr_output_path = "datasets/3_tnr/output"
tnr_output_result_path = f"{tnr_output_path}/labels"


def is_tnr_by_yolo():
    try:
        cmd = f"python services/tnr_filtering/yolov5/detect.py --weights services/tnr_filtering/yolov5/weight/best.pt --img 416 --conf 0.7 --source {tnr_input_path} --project datasets/3_tnr/ --name output --save-txt --save-conf --exist-ok"
        output = subprocess.check_output(cmd, shell=True)
        output = output.decode("utf-8")
        result_arr = ast.literal_eval(output)

        if result_arr[0] and result_arr[1]:
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        print(f"오류: {e}\n종료 상태: {e.returncode}")
        return False


def detect_tnr():
    # 폴더 비우기
    empty_directory(f"{tnr_output_path}/*")

    # tnr detection
    is_tnr_by_yolo()

    # 결과 분석
    result, tnrCount = analyze_results()

    return result, tnrCount


def is_tnr(img_name):
    # 파일 읽기
    with open(f"{tnr_output_result_path}/{img_name}", "r") as file:
        contents = file.read()

    # 결과 분석
    cat = {"x": 0, "exist": False}
    tnr = {"x": 0, "exist": False}
    result = contents.split("\n")
    for line in result:
        txt = line.split(" ")
        # 정보 없는 부분 pass
        if len(txt) < 6:
            continue
        # class 판별
        cls = int(txt[0])
        if cls == 0:
            cat["exist"] = True
            cat["x"] = float(txt[1])
        elif cls == 1:
            if tnr["exist"] == False:
                tnr["exist"] = True
                tnr["x"] = float(txt[1])
            else:
                # 귀가 2개 잡힌경우
                x2 = float(txt[1])
                if x2 < tnr["x"]:
                    tnr["x"] = x2

    if (
        cat["exist"] and tnr["exist"] and cat["x"] > tnr["x"]
    ):  # 고양이 기준으로 오른쪽 귀가 잡혔으면 pass
        return True
    else:
        return False


def analyze_results():
    result = []
    tnrCount = 0
    for img_txt_name in os.listdir(tnr_output_result_path):
        img_name = f'{img_txt_name.split(".")[0]}.jpg'
        isTnr = is_tnr(img_txt_name)
        if isTnr:
            tnrCount += 1
        result.append([img_name, isTnr])

    return result, tnrCount
