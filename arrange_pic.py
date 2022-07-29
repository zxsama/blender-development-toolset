from math import ceil, floor
import cv2
import os
import numpy as np
import time

def getboundingrect(gary_img):
    contours, _ = cv2.findContours(gary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x, y, w, h = 0,0,0,0
    for cnt in contours:
        tmp_x, tmp_y, tmp_w, tmp_h = cv2.boundingRect(cnt)
        if tmp_w>w and tmp_h>h:
            x, y, w, h = tmp_x, tmp_y, tmp_w, tmp_h
    return x, y, w, h

if __name__ == '__main__':
    
    sour_redr = r"E:\MH\RenderOut"
    pics = os.listdir(sour_redr)
    single_size = 130
    result_pic = np.zeros((single_size, 0, 4), np.uint8)
    
    for pic in pics:
        pic_path = os.path.join(sour_redr, pic)
        print(pic_path)
        img = cv2.imread(pic_path, cv2.IMREAD_UNCHANGED)
        if len(cv2.split(img)) > 3:
            b, g, r, a = cv2.split(img)
            img_gray = a.astype(np.uint8)
        else:
            print("no alpha")
            # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # TODO:
            
        x, y, w, h = getboundingrect(img_gray)
        img = img[y:y+h, x:x+w]
        border_y = (single_size - h)/2
        border_x = (single_size - w)/2
        if single_size<h or single_size<w:
            print("too small in size.")
            break
        img = cv2.copyMakeBorder(img,
                                 int(ceil(border_y)),
                                 int(floor(border_y)),
                                 int(ceil(border_x)),
                                 int(floor(border_x)),
                                 cv2.BORDER_CONSTANT,
                                 value=[0,0,0,0]
                                 )
        result_pic = cv2.hconcat([result_pic,img])
        
    ftime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    tar_redr = os.path.dirname(sour_redr)
    tar_redr = os.path.join(tar_redr, "comp_"+ftime+".png")
    cv2.imwrite(tar_redr,result_pic)