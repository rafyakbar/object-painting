from paint import Paint
import cv2
import numpy as np
import ctypes

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
[monitor_width, monitor_height] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

# capture = cv2.VideoCapture('http://192.168.43.245:8080/video')
capture = cv2.VideoCapture(0)

ret, frame = capture.read()

paint = Paint(frame)
paint.color_changer_colors.extend([
    (255, 0, 0),
    (255,255,0),
    (0,255,255),
    (128,128,128),
    (150,75,0),
    (255,127,0),
    (191,0,255),
    (0,0,0),
    (255,0,255),
    (0,255,255),
    (143,0,255)
])
paint.pause = True


exit = False
while not exit:
    ret, frame = capture.read()

    # flip kamera supaya mirror
    img = cv2.flip(frame, 1)

    # painting
    img, board = paint.draw(img)
    img = np.hstack((img, board))

    # face detection dari opencv
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            center_eye_x = (((ex + ew) - ex) / 2) + ex
            center_eye_y = (((ey + eh) - ey) / 2) + ey
            radius_eye = (((ex + ew) - ex) / 2)
            cv2.circle(roi_color, (int(center_eye_x), int(center_eye_y)), int(radius_eye), (255, 255, 255), 2)

    # resize gambar sesuai dengan width monitor
    tinggi = int(((monitor_width - img.shape[1]) / img.shape[1] + 1) * img.shape[0])
    img = cv2.resize(img, (monitor_width, tinggi))

    cv2.imshow('Frame', img)

    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q') or key == ord('Q'):
        exit = True
    elif key == ord('w') or key == ord('W'):
        paint.color_changer_placement = paint.PLACEMENT_TOP
    elif key == ord('a') or key == ord('A'):
        paint.color_changer_placement = paint.PLACEMENT_LEFT
    elif key == ord('s') or key == ord('S'):
        paint.color_changer_placement = paint.PLACEMENT_BOTTOM
    elif key == ord('d') or key == ord('D'):
        paint.color_changer_placement = paint.PLACEMENT_RIGHT
    elif key == ord(',') or key == ord('<'):
        paint.color_changer_thickness -= 1
    elif key == ord('.') or key == ord('>'):
        paint.color_changer_thickness += 1
    elif key == ord('p') or key == ord('P'):
        while True:
            key = cv2.waitKey(1) & 0xff
            cv2.imshow('Frame', img)
            if key == ord('p') or key == ord('P'):
                break
            elif key == 27 or key == ord('q') or key == ord('Q'):
                exit = True
                break
    elif key == ord(' '):
        paint.pause = not paint.pause