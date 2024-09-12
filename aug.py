# 1. 배경 : 흰색 책상, 우드 테이블
# 2. 데이터 증식 조건 
#    2.0 스마트폰으로 사진 촬영후 이미지 크기를 줄여주자. (이미지 크기 224x224)
#        대상물 촬영을 어떻게 해야할지 확인
#    2.1 rotate : 회전(10~30도)범위 안에서 어느 정도 각도를 넣어야 인식이 잘되는가?
#    2.2 hflip, vflip : 도움이 되는가? 넣을 것인가?
#    2.3 resize, crop : 가능하면 적용해 보자.
#    2.4 파일명을 다르게 저장 cf) jelly_wood.jpg, jelly_white.jpg
#        jelly_wood_rot_15.jpg, jelly_wood_hflip.jpg,jelly_wood_resize.jpg 
#    2.5 클래스 별로 폴더를 생성
#    2.6 데이터를 어떻게 넣느냐에 따라 어떻게 동작되는지 1~2줄로 요약

# 구성 순서 
# 1. 촬영한다.
# 2. 이미지를 컴퓨터로 복사, resize한다.
# 3. 육안으로 확인, 이렇게 사용해도 되는가?
# 4. 함수들을 만든다. resize, rotate, hflip, vflip, crop, 
#    원본파일명을 읽어서 파일명을 생성하는 기능은 모든 함수에 있어야 한다.(함수)
# 5. 단일 함수들 검증
# 6. 함수를 활용해서 기능 구현
# 7. 테스트(경우의수)
# 8. 데이터셋을 teachable machine사이트에 올려서 테스트
# 9. 인식이 잘 안되는 케이스를 분석하고 케이스 추가 1~8에서 구현된 기능을 이용

import cv2, sys, os
import numpy as np
from glob import glob

class DataAugmenter():
    
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.base_path = os.getcwd()
        self.data_path = os.path.join(self.base_path, self.data_folder)
        self.org_path = os.path.join(self.data_path, 'org')
        self.aug_path = os.path.join(self.data_path, 'aug')
        self.org_folders = os.listdir(self.org_path)
        self.aug_folders = os.listdir(self.aug_path)
    
    def make_aug_folder(self):
        for folder in self.org_folders:
            if folder not in self.aug_folders:
                os.mkdir(os.path.join(self.aug_path, folder))
    
    def resize_image(self):
        for c in self.org_folders:
            data_path = os.path.join(self.org_path, c)
            print(data_path)
            
            # aug 폴더에 resize 폴더 있는지 확인하고 없으면 생성 있으면, 파일 모두 삭제
            if 'resize' not in os.listdir(os.path.join(self.aug_path, c)):
                os.mkdir(os.path.join(self.aug_path, c, 'resize'))
            else:
                for r in os.listdir(os.path.join(self.aug_path, c, 'resize')):
                    os.remove(os.path.join(self.aug_path, c, 'resize', r))
                    
            for f in os.listdir(data_path):
                split_name = os.path.splitext(f)
                
                img = cv2.imread(os.path.join(data_path, f), cv2.IMREAD_COLOR)
                dst = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
                name = os.path.join(self.aug_path, c, 'resize', split_name[0] + '_resize' + split_name[1])
                print(name)
                cv2.imwrite(name, dst)
    
    def flip_image(self):
        for c in self.aug_folders:
            data_path = os.path.join(self.aug_path, c, 'resize')
            print(data_path)
            
            # aug 폴더에 flip 폴더 있는지 확인하고 없으면 생성 있으면, 파일 모두 삭제
            if 'flip' not in os.listdir(os.path.join(self.aug_path, c)):
                os.mkdir(os.path.join(self.aug_path, c, 'flip'))
            else:
                for r in os.listdir(os.path.join(self.aug_path, c, 'flip')):
                    os.remove(os.path.join(self.aug_path, c, 'flip', r))
                    
            for f in os.listdir(data_path):
                split_name = os.path.splitext(f)
                
                img = cv2.imread(os.path.join(data_path, f), cv2.IMREAD_COLOR) # 원본
                name = os.path.join(self.aug_path, c, 'flip', f)
                cv2.imwrite(name, img)
                
                dst = cv2.flip(img, 1) # 좌우 반전
                name = os.path.join(self.aug_path, c, 'flip', split_name[0] + '_flip' + split_name[1])
                print(name)
                cv2.imwrite(name, dst)
    
    def rotate_image(self):
        for c in self.org_folders:
            data_path = os.path.join(self.aug_path, c, 'flip')
            print(data_path)
            
            # aug 폴더에 rotate 폴더 있는지 확인하고 없으면 생성 있으면, 파일 모두 삭제
            if 'rotate' not in os.listdir(os.path.join(self.aug_path, c)):
                os.mkdir(os.path.join(self.aug_path, c, 'rotate'))
            else:
                for r in os.listdir(os.path.join(self.aug_path, c, 'rotate')):
                    os.remove(os.path.join(self.aug_path, c, 'rotate', r))
                    
            for f in os.listdir(data_path):
                img = cv2.imread(os.path.join(data_path, f), cv2.IMREAD_COLOR)
                
                (h, w) = img.shape[:2]
                (cX, cY) = (w // 2, h // 2)
                theta = 20
                split_name = os.path.splitext(f)
                for r_cnt in range(int(360 / theta)):
                    M = cv2.getRotationMatrix2D((cX, cY), theta * r_cnt, 1.0)
                    dst = cv2.warpAffine(img, M, (w, h))
                    name = os.path.join(self.aug_path, c, 'rotate', split_name[0] + '_' + str(theta * r_cnt) + split_name[1])
                    print(name)
                    cv2.imwrite(name, dst)
    

if __name__ == '__main__':
    aug = DataAugmenter('floor5')
    
    aug.make_aug_folder()
    aug.resize_image()
    aug.flip_image()
    aug.rotate_image()