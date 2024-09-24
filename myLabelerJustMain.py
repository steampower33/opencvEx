import cv2, sys, os
import numpy as np
from glob import glob

radius = 25

def getImageInfo():
    info = []
    
    # 현재 작업 디렉토리 확인
    basePath = os.getcwd()
    dataPath = os.path.join(basePath,'images')
    imgNames = glob(os.path.join(dataPath, '*.jpg'))
    
    for img in imgNames:
        label = img.replace('images', 'labels')
        label = label.replace('.jpg', '.txt')
        
        if not os.path.exists(label):
            with open(label, 'w') as f:
                pass
            print("New label created")
        info.append((img, label))
    
    return info

# corners : 좌표 (startPt, endPt)
# 2개 좌표를 이용해서 직사각형 그리기
def drawROI(img):
    global boxList
    # 박스를 그릴 레이어를생성 : cpy
    cpy = img.copy()
    line_c = (128, 128, 255)
    lineWidth = 2
    for coords in boxList:
        cv2.rectangle(cpy, (coords[0], coords[1]), (coords[2], coords[3]), line_c, thickness=lineWidth)
    return cpy

def onMouse(event, x, y, flags, param):
    global startPt, cpy
    if event == cv2.EVENT_LBUTTONDOWN:
        cpy = drawROI(param[0])
        startPt = (x, y)
        boxList.append([startPt[0], startPt[1], 0, 0])
    elif event == cv2.EVENT_LBUTTONUP:
        if boxList[-1][0] == x and boxList[-1][1] == y:
            boxList.pop()
            cpy = drawROI(param[0])
        startPt = None
    elif event == cv2.EVENT_MOUSEMOVE:
        if startPt:
            boxList[-1][2] = x
            boxList[-1][3] = y
            cpy = drawROI(param[0])
    cv2.imshow('label', cv2.addWeighted(param[0], 0.3, cpy, 0.7, 0))

if __name__ == '__main__':
    # images에 jpg 파일 확인
    # jpg 파일에 대응 되는 label txt 파일들 확인 -> 없으면 생성
    imageList = getImageInfo()
    
    # images와 label을 참고해서 화면에 이미지 출력
    # images에 label을 그리고, 수정
    # label 파일에 label 정보 덮어쓰기
    fileIdx = 0
    while True:
        # image 읽어오기 및 윈도우 생성, 마우스 콜백 설정
        img = cv2.imread(imageList[fileIdx][0])
        cv2.namedWindow('label')
        cv2.moveWindow('label', 0, 0)
        cv2.setMouseCallback('label', onMouse, [img])

        # 사각형 그릴 boxList 설정
        boxList = []
        with open(imageList[fileIdx][1], 'r') as f:
            for line in f:
                line = line.strip().replace('[', '').replace(']', '').replace(')', '').replace('(', '')  # 괄호 제거
                coords = line.split(',')
                boxList.append([int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])])
        
        # 시작위치 설정
        startPt = None

        # 프로그램이 시작될때 맨처음 이미지 출력
        cpy = drawROI(img)
        cv2.imshow('label', cpy)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 27: # 
                cv2.destroyAllWindows()
                break
            elif key == ord('q'): # 프로그램 종료
                cv2.destroyAllWindows()
                sys.exit()
            elif key == ord('d'): # 오른쪽 사진으로 이동
                if fileIdx == len(imageList) - 1:
                    fileIdx = 0
                else:
                    fileIdx += 1
                cv2.destroyAllWindows()
                break
            elif key == ord('a'): # 왼쪽 사진으로 이동
                if fileIdx == 0:
                    fileIdx = len(imageList) - 1
                else:
                    fileIdx -= 1
                cv2.destroyAllWindows()
                break
            elif key == ord('c'): # 모든 사각형 삭제
                boxList.clear()
                cpy = drawROI(img)
                cv2.imshow('label', cpy)
            elif key == ord('s'): # 저장
                with open(imageList[fileIdx][1], 'w') as f:
                    for coord in boxList:
                        f.write(f"[({coord[0]}, {coord[1]}), ({coord[2]}, {coord[3]})]\n")
            elif key == ord('z'): # 가장 최근 사각형 삭제
                boxList.pop()
                cpy = drawROI(img)
                cv2.imshow('label', cpy)
            