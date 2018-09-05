import cv2
import imutils
import numpy as np

class Paint:
    PLACEMENT_TOP = 'up'

    PLACEMENT_BOTTOM = 'bottom'

    PLACEMENT_LEFT = 'left'

    PLACEMENT_RIGHT = 'right'

    """
    construct
    """
    def __init__(self, image, lower_color_object=(29, 100, 6), upper_color_object=(50, 255, 200), board_color=[255, 255, 255]):
        # inisialisasi warna objek
        self.__lowerColorObject = lower_color_object
        self.__upperColorObject = upper_color_object

        # inisialisasi board
        self.__board = np.zeros_like(image)
        self.__board[:,:] = np.array(board_color)
        self.board_color = board_color

        # inisialisasi warna paint
        self.__paint_color = (255, 0, 0)

        # flag hapus
        self.eraser = False

        # temporary old point
        self.__old_point = None

        # inisialisasi color changer
        self.color_changer_placement = self.PLACEMENT_TOP
        self.color_changer_colors = []
        self.color_changer_thickness = 75

        # inisialisasi pause
        self.pause = False

    """
    method untuk menggambar color changer
    """
    def __drawColorChanger(self, image):
        counter = 0
        if self.color_changer_placement == self.PLACEMENT_TOP or self.color_changer_placement == self.PLACEMENT_BOTTOM:
            len_area = int(image.shape[1] / (len(self.color_changer_colors) + 1)) - 3
            y_point = 0 if self.color_changer_placement == self.PLACEMENT_TOP else (image.shape[0] - self.color_changer_thickness)
            for color in self.color_changer_colors:
                cv2.rectangle(
                    image,
                    (counter, y_point),
                    (counter + len_area, self.color_changer_thickness + y_point),
                    color,
                    3
                )
                counter += len_area + 3
            cv2.rectangle(
                image,
                (counter, y_point),
                (counter + len_area, self.color_changer_thickness + y_point),
                self.board_color,
                3
            )
        elif self.color_changer_placement == self.PLACEMENT_RIGHT or self.color_changer_placement == self.PLACEMENT_LEFT:
            len_area = int(image.shape[0] / (len(self.color_changer_colors) + 1)) - 3
            x_point = (image.shape[1] - self.color_changer_thickness) if self.color_changer_placement == self.PLACEMENT_RIGHT else 0
            for color in self.color_changer_colors:
                cv2.rectangle(
                    image,
                    (x_point, counter),
                    (x_point + self.color_changer_thickness, counter + len_area),
                    color,
                    3
                )
                counter += len_area + 3
            cv2.rectangle(
                image,
                (x_point, counter),
                (x_point + self.color_changer_thickness, counter + len_area),
                self.board_color,
                3
            )

    """
    method untuk mengubah warna paint
    """
    def __checkColorChangerArea(self,image, center):
        counter = 0
        if self.color_changer_placement == self.PLACEMENT_TOP or self.color_changer_placement == self.PLACEMENT_BOTTOM:
            len_area = int(image.shape[1] / (len(self.color_changer_colors) + 1)) - 3
            y_point = 0 if self.color_changer_placement == self.PLACEMENT_TOP else (
                        image.shape[0] - self.color_changer_thickness)
            for color in self.color_changer_colors:
                if self.__isInColorChangerArea(
                        y_point,
                        self.color_changer_thickness + y_point,
                        counter,
                        counter + len_area,
                        center[0],
                        center[1]
                ):
                    self.eraser = False
                    self.__paint_color = color
                counter += len_area + 3
            if self.__isInColorChangerArea(
                    y_point,
                    self.color_changer_thickness + y_point,
                    counter,
                    counter + len_area,
                    center[0],
                    center[1]
            ):
                self.eraser = True
                self.__paint_color = self.board_color
        elif self.color_changer_placement == self.PLACEMENT_RIGHT or self.color_changer_placement == self.PLACEMENT_LEFT:
            len_area = int(image.shape[0] / (len(self.color_changer_colors) + 1)) - 3
            x_point = (image.shape[1] - self.color_changer_thickness) if self.color_changer_placement == self.PLACEMENT_RIGHT else 0
            for color in self.color_changer_colors:
                if self.__isInColorChangerArea(
                        counter,
                        counter + len_area,
                        x_point,
                        x_point + self.color_changer_thickness,
                        center[0],
                        center[1]
                ):
                    self.eraser = False
                    self.__paint_color = color
                counter += len_area + 3
            if self.__isInColorChangerArea(
                    counter, counter + len_area,
                    x_point,
                    x_point + self.color_changer_thickness,
                    center[0],
                    center[1]
            ):
                self.eraser = True
                self.__paint_color = self.board_color

    """
    method untuk mengecek apakah point berada pada area rectangle tertentu
    """
    def __isInColorChangerArea(self, top, bottom, left, right, x, y):
        return top <= y and bottom >= y and left <= x and right >= x

    """
    method untuk menggambar
    """
    def draw(self, image):
        # deteksi range warna dengan hsv
        converted = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(converted, self.__lowerColorObject, self.__upperColorObject)

        # erosi dan dilasi
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # mencari contour pada frame
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]

        # inislialisasi center objek
        center = None

        # jika menemukan minimal 1 contour
        if len(cnts) > 0:
            # mencari area terbesar
            max_area = max(cnts, key=cv2.contourArea)

            # mengambil jari-jari
            ((x, y), radius) = cv2.minEnclosingCircle(max_area)

            # moment dan center pada contour
            moment = cv2.moments(max_area)
            center = int(moment["m10"] / moment["m00"]), int(moment["m01"] / moment["m00"])

            # menggambar color changer
            self.__drawColorChanger(image)

            if radius > 10:
                self.__checkColorChangerArea(image, center)

                cv2.circle(
                    image,
                    (int(x), int(y)),
                    int(radius),
                    self.__paint_color if not self.eraser else self.board_color,
                    2
                )
                cv2.circle(
                    image,
                    center,
                    5,
                    self.board_color if self.eraser else self.__paint_color,
                    -1 if not self.eraser else int(radius)
                )

                if not self.__old_point is None and not self.pause:
                    if self.eraser:
                        cv2.line(self.__board, self.__old_point, center, self.board_color, int(radius))
                    else:
                        cv2.line(self.__board, self.__old_point, center, self.__paint_color, 5)

                # memasukkan center ke dalam old_point untuk proses selanjutnya
                self.__old_point = center

        return image, self.__board