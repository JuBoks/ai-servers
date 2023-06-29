import subprocess
import ast


async def detectCatByYolo(input_path):
    cmd = f"python yolov5/detect.py --weights yolov5/weight/best.pt --img 480 --conf 0.1 --source {input_path} --project static/yolov5 --name output --save-txt --save-conf --exist-ok"
    output = subprocess.check_output(cmd, shell=True)
    output = output.decode("utf-8")
    result_arr = ast.literal_eval(output)

    print("result_arr", result_arr)
    if result_arr[0]:
        return True
    else:
        return False
