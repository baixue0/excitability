import numpy as np

def findcontour(binarymask):
    import cv2
    contours, hierarchy = cv2.findContours(binarymask.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    i = np.argmax([cv2.contourArea(cnt) for cnt in contours])
    return contours[i]

class Rotate_Crop(object):
    def __init__(self,outline):
        import cv2
        self.outline = outline
        self.contour = findcontour(self.outline)
        (x,y),(w,h),angle = cv2.minAreaRect(self.contour)#( top-left corner(x,y), (width, height), angle of rotation )
        if w<h:
            self.angle = -90-angle
        else:
            self.angle = -angle
        
        M = cv2.moments(self.contour)
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        self.centroid = (cx,cy)

    def rotate(self,image2d,borderValue,cropW=180,cropH=120):
        import cv2
        # grab the dimensions of the image and then determine the center
        (h, w) = image2d.shape[:2]
        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        # Rotation angle in degrees. Positive values mean counter-clockwise rotation (the coordinate origin is assumed to be the top-left corner)
        M = cv2.getRotationMatrix2D(self.centroid, -self.angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
        # adjust the rotation matrix to take into account translation
        cX,cY = self.centroid
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY
        # perform the actual rotation and return the image
        image_rotated = cv2.warpAffine(image2d, M, (nW, nH), borderValue=borderValue)
        cx_rotated,cy_rotated = (np.array(image_rotated.shape)/2).astype(int)
        return image_rotated[cx_rotated-cropH:cx_rotated+cropH,cy_rotated-cropW:cy_rotated+cropW]

    def rotate_stk(self,stk,borderValue,channel=3):
        iterdim0 = lambda imstk: np.stack([self.rotate(im,borderValue) for im in imstk],0)
        if channel==1:
            return iterdim0(stk).astype(stk.dtype)
        elif channel==3:
            return np.stack([iterdim0(stk[...,c]) for c in range(3)],-1)
