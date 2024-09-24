import cv2, sys, os
import numpy as np
from glob import glob

class Labeler:
    def __init__(self, imagePath, labelPath):
        self.imagePath = imagePath
        self.labelPath = labelPath
        self.imageList = self.getImageList()
        self.fileIdx = 0
        self.labelList = []
        self.startPt = None
        self.cpy = None
        self.colors = [(0, 0, 255),  # 빨강
                       (0, 165, 255),  # 주황
                       (0, 255, 255),  # 노랑
                       (0, 255, 0),  # 초록
                       (255, 0, 0),  # 파랑
                       (255, 0, 255),  # 남색 
                       (128, 0, 128)  # 보라
                       ]
    
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

        lineWidth = 2
        for label in self.labelList:
            class_id, x1, y1, x2, y2 = label
            line_color = self.colors[class_id]

            # 경계 상자 그리기 (색상, 두께 등은 원하는대로 설정 가능)
            cv2.rectangle(self.cpy, (x1, y1), (x2, y2), line_color, thickness=lineWidth)

    def onMouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawROI(param[0])
            self.startPt = (x, y)
            self.labelList.append([0, self.startPt[0], self.startPt[1], 0, 0])
        elif event == cv2.EVENT_LBUTTONUP:
            if self.labelList[-1][0] == x and self.labelList[-1][1] == y:
                self.labelList.pop()
                self.drawROI(param[0])
            self.startPt = None
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.startPt:
                self.labelList[-1][3] = x
                self.labelList[-1][4] = y
                self.drawROI(param[0])
        cv2.imshow('label', cv2.addWeighted(param[0], 0.3, self.cpy, 0.7, 0))
    
    def convert_to_yolo_format(self, img, label):
        """두 점 좌표를 YOLO 형식으로 변환합니다.

        Args:
            image_width: 이미지 너비
            image_height: 이미지 높이
            point1: 좌상단 좌표 (x1, y1)
            point2: 우하단 좌표 (x2, y2)

        Returns:
            YOLO 형식 라벨 [x_center, y_center, width, height] (모두 0.0 ~ 1.0 사이의 값)
        """
        
        image_height, image_width = img.shape[:2]  # 이미지 높이, 너비 추출
        x1, y1 = label[1], label[2]
        x2, y2 = label[3], label[4]

        # 경계 상자의 너비와 높이 계산
        bbox_width = x2 - x1
        bbox_height = y2 - y1

        # 경계 상자 중심 좌표 계산
        x_center = (x1 + bbox_width / 2) / image_width
        y_center = (y1 + bbox_height / 2) / image_height

        # 경계 상자 너비와 높이를 이미지 크기에 대한 비율로 계산
        width = bbox_width / image_width
        height = bbox_height / image_height

        return [label[0], x_center, y_center, width, height]

    # 윈도우 생성, 마우스 콜백 설정
    def setWindowAndCallback(self, img):
        cv2.namedWindow('label')
        cv2.moveWindow('label', 0, 0)
        cv2.setMouseCallback('label', self.onMouse, [img])  
    
    # 해당 이미지에 매칭되는 labels 확인
    # [(x1, y1), (x2, y2)] -> [x1, y1, x2, y2]
    def setLabelInfo(self, img):
        self.labelList.clear()
        
        img_height, img_width = img.shape[:2]  # 이미지 높이, 너비 추출
        with open(self.imageList[self.fileIdx][1], 'r') as f:
            for line in f:
                class_id, x_center, y_center, w, h = list(map(float, line.split()))

                class_id = int(class_id)
                # 상대 좌표를 픽셀 좌표로 변환
                x1 = int((x_center - w / 2) * img_width)
                y1 = int((y_center - h / 2) * img_height)
                x2 = int((x_center + w / 2) * img_width)
                y2 = int((y_center + h / 2) * img_height)

                self.labelList.append([class_id, x1, y1, x2, y2])
    
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
            self.setLabelInfo(img)
            
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
                    self.labelList.clear()
                    self.drawROI(img)
                    cv2.imshow('label', self.cpy)
                elif key == ord('s'): # 저장
                    with open(self.imageList[self.fileIdx][1], 'w') as f:
                        for label in self.labelList:
                            line = self.convert_to_yolo_format(img, label)
                            f.write(f"{line[0]} {' '.join(f'{float(x):.6f}' for x in line[1:6])}\n")
                elif key == ord('z'): # 가장 최근 사각형 삭제
                    self.labelList.pop()
                    self.drawROI(img)
                    cv2.imshow('label', self.cpy)

if __name__ == '__main__':
    l = Labeler('images', 'labels')
    
    l.run()