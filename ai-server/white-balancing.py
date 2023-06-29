import cv2
import numpy as np

# 이미지 읽기
img = cv2.imread('static/img/image.png')

# white-balancing
img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
mean_y = cv2.mean(img_yuv[:,:,0])[0]
diff_y = 128 - mean_y
img_yuv[:,:,0] = cv2.add(img_yuv[:,:,0], diff_y)
result = cv2.cvtColor(img_yuv, cv2.COLOR_YCrCb2BGR)

# 결과 출력
cv2.imshow('image', img)
cv2.imshow('result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()