import cv2, sys
import numpy as np

# 직선과 원을 그리는 함수
def drawROI(img, srcQuad):
    cpy = img.copy()
    
    # 컬러 지정
    c1 = (192, 192, 255) # 원
    c2 = (128, 128, 255) # 직선
    radius = 25
    lineWidth = 2
    
    # 4개의 좌표에 원을 그리기
    for pt in srcQuad:
        cv2.circle(cpy, tuple(pt.astype(int)), radius, c1, -1, cv2.LINE_AA)
        
    # 4개 모서리 라인 그리기
    cv2.line(cpy, tuple(srcQuad[0].astype(int)), tuple(srcQuad[1].astype(int)), c2, lineWidth, cv2.LINE_AA)
    cv2.line(cpy, tuple(srcQuad[1].astype(int)), tuple(srcQuad[2].astype(int)), c2, lineWidth, cv2.LINE_AA)
    cv2.line(cpy, tuple(srcQuad[2].astype(int)), tuple(srcQuad[3].astype(int)), c2, lineWidth, cv2.LINE_AA)
    cv2.line(cpy, tuple(srcQuad[3].astype(int)), tuple(srcQuad[0].astype(int)), c2, lineWidth, cv2.LINE_AA)
    
    distp = cv2.addWeighted(img, 0.3, cpy, 0.7, 0)
    return distp
    
# 마우스 좌표를 얻기 위해 콜백함수 이용
def mouse_callback(event, x, y, flags, param):
    global srcQuad, img, dragSrc, ptOld
    
    # 이미지 복사해서 레이어를 하나 추가 (가이드 라인과 모서리 포인트를 추가로 그려주는)
    if event == cv2.EVENT_LBUTTONDOWN:
        for i in range(4):
            if cv2.norm(srcQuad[i] - (x, y)) < 25:
                dragSrc[i] = True
                ptOld = (x, y)
                break
            
    elif event == cv2.EVENT_LBUTTONUP:
        for i in range(4):
            dragSrc[i] = False
            
    if event == cv2.EVENT_MOUSEMOVE:
        for i in range(4):
            if dragSrc[i]:
                dx = x - ptOld[0]
                dy = y - ptOld[1]
                
                srcQuad[i] += (dx, dy)
                cpy = drawROI(img, srcQuad)
                cv2.imshow('img', cpy)
                ptOld = (x, y)

if __name__ == '__main__':
    img = cv2.imread('data/book.jpg')
    
    img = cv2.resize(img, (0,0), None, fx=0.5, fy=0.5)
    w, h = img.shape[1], img.shape[0]
    print(w,h)
    
    # 다각형의 좌표를 그릴때는 시계방향으로()
    spare = 30
    srcQuad = np.array([[spare,spare],[w-spare,spare],[w-spare,h-spare],[spare,h-spare]], np.float32)
    
    # 변환될 좌표
    dstQuad = np.array([[0,0],[w-1,0],[w-1,h-1],[0,h-1]],np.float32)
    
    # 마우스 포인터로 4개 좌표를 이동했는지 체크하는 플래그
    dragSrc = [False, False, False, False]
    
    # 마우스 이벤트
    cv2.namedWindow('img')
    cv2.setMouseCallback('img', mouse_callback, [img])
    while True:
        # 처음 한번은 직접 화면에 drawROI함수를 호출해서 그려준다.
        distp = drawROI(img, srcQuad)
        
        cv2.imshow('img', distp)
        key = cv2.waitKey(1) & 0xFF
        # ESC
        if key == 27:
            cv2.destroyAllWindows()
            sys.exit()
        if key == 13:
            pers = cv2.getPerspectiveTransform(srcQuad, dstQuad)
            dst = cv2.warpPerspective(img, pers, (w,h))
            cv2.imshow('dst', dst)

    cv2.destroyAllWindows()
        