import cv2, sys, os
import numpy as np
from glob import glob

class Labler:
    def __init__(self, imagePath, labelPath):
        self.imagePath = imagePath
        self.labelPath = labelPath
        self.imageList = self.getImageList()
        self.fileIdx = 0
        self.boxList = []
        self.startPt = None
        self.cpy = None
    
    # images에 jpg 파일 확인
    # jpg 파일에 대응 되는 label txt 파일들 확인 -> 없으면 생성
    def getImageList(self):
        info = []
        
        # 현재 작업 디렉토리 확인
        basePath = os.getcwd()
        dataPath = os.path.join(basePath, self.imagePath)
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
    def drawROI(self, img):
        # 박스를 그릴 레이어를생성 : cpy
        self.cpy = img.copy()
        line_c = (128, 128, 255)
        lineWidth = 2
        for coords in self.boxList:
            cv2.rectangle(self.cpy, (coords[0], coords[1]), (coords[2], coords[3]), line_c, thickness=lineWidth)
        # return self.cpy

    def onMouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawROI(param[0])
            self.startPt = (x, y)
            self.boxList.append([self.startPt[0], self.startPt[1], 0, 0])
        elif event == cv2.EVENT_LBUTTONUP:
            if self.boxList[-1][0] == x and self.boxList[-1][1] == y:
                self.boxList.pop()
                self.drawROI(param[0])
            self.startPt = None
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.startPt:
                self.boxList[-1][2] = x
                self.boxList[-1][3] = y
                self.drawROI(param[0])
        cv2.imshow('label', cv2.addWeighted(param[0], 0.3, self.cpy, 0.7, 0))
    
    # 윈도우 생성, 마우스 콜백 설정
    def setWindowAndCallback(self, img):
        cv2.namedWindow('label')
        cv2.moveWindow('label', 0, 0)
        cv2.setMouseCallback('label', self.onMouse, [img])
    
    # 해당 이미지에 매칭되는 labels 확인
    # [(x1, y1), (x2, y2)] -> [x1, y1, x2, y2]
    def setLabelInfo(self):
        self.boxList.clear()
        with open(self.imageList[self.fileIdx][1], 'r') as f:
            for line in f:
                line = line.strip().replace('[', '').replace(']', '').replace(')', '').replace('(', '')  # 괄호 제거
                coords = line.split(',')
                self.boxList.append([int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])])
    
    def run(self):
        
        # images와 label을 참고해서 화면에 이미지 출력
        # images에 label을 그리고, 수정
        # label 파일에 label 정보 덮어쓰기
        while True:
            # image 읽어오기
            img = cv2.imread(self.imageList[self.fileIdx][0])
            
            # 윈도우 생성, 마우스 콜백 설정
            self.setWindowAndCallback(img)
            
            # 해당 이미지에 매칭되는 labels 확인
            # [(x1, y1), (x2, y2)] -> [x1, y1, x2, y2]
            self.setLabelInfo()
            
            # 시작위치 설정
            self.startPt = None

            # 프로그램이 시작될때 맨처음 이미지 출력
            self.drawROI(img)
            cv2.imshow('label', cv2.addWeighted(img, 0.3, self.cpy, 0.7, 0))
            
            while True:
                key = cv2.waitKey(1) & 0xFF
                if key == 27: # 
                    cv2.destroyAllWindows()
                    break
                elif key == ord('q'): # 프로그램 종료
                    cv2.destroyAllWindows()
                    sys.exit()
                elif key == ord('d'): # 오른쪽 사진으로 이동
                    if self.fileIdx == len(self.imageList) - 1:
                        self.fileIdx = 0
                    else:
                        self.fileIdx += 1
                    cv2.destroyAllWindows()
                    break
                elif key == ord('a'): # 왼쪽 사진으로 이동
                    if self.fileIdx == 0:
                        self.fileIdx = len(self.imageList) - 1
                    else:
                        self.fileIdx -= 1
                    cv2.destroyAllWindows()
                    break
                elif key == ord('c'): # 모든 사각형 삭제
                    self.boxList.clear()
                    self.drawROI(img)
                    cv2.imshow('label', self.cpy)
                elif key == ord('s'): # 저장
                    with open(self.imageList[self.fileIdx][1], 'w') as f:
                        for coord in self.boxList:
                            f.write(f"[({coord[0]}, {coord[1]}), ({coord[2]}, {coord[3]})]\n")
                elif key == ord('z'): # 가장 최근 사각형 삭제
                    self.boxList.pop()
                    self.drawROI(img)
                    cv2.imshow('label', self.cpy)

if __name__ == '__main__':
    l = Labler('images', 'labels')
    
    l.run()