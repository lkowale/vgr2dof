import numpy as np
from subprocess import call
from robot.camera import Camera
from utils.utils import *


class ImageRoutines:

    red_BGR = (0, 0, 255)
    green_BGR = (50, 170, 50)
    blue_BGR = (255, 0, 0)

    @classmethod
    def gaus_blur_decor(cls, kernel):
        def gaus_blur(frame):
            return cv2.GaussianBlur(frame, kernel, 0)
        return gaus_blur

    @classmethod
    def color_convert_decor(cls, convert_type):
        def color_convert(frame):
            return cv2.cvtColor(frame, convert_type)
        return color_convert

    @classmethod
    def colour_mask_decor(cls, colour_lower, colour_upper):
        def colour_mask(frame):
            frame = cv2.inRange(frame, colour_lower, colour_upper)
            frame = cv2.erode(frame, None, iterations=4)
            frame = cv2.dilate(frame, None, iterations=4)
            return frame
        return colour_mask

    @classmethod
    def make_colour_treshold_pipeline(cls, colour_mask_lower, colour_mask_upper):
        return [ImageRoutines.gaus_blur_decor((5, 5)),
                ImageRoutines.color_convert_decor(cv2.COLOR_BGR2LAB),
                ImageRoutines.colour_mask_decor(colour_mask_lower, colour_mask_upper)
                ]


class Aspect:

    def __init__(self, name, plain_aspect=None):

        self.name = name
        self.eye = None
        self.frame_transform_pipeline = None
        self.frame = []
        self.BGR_treshold_colour = np.zeros((3,), dtype=int)
        self.LAB_treshold_colour = np.zeros((3,), dtype=int)
        self.LAB_treshold_lower = np.zeros((3,), dtype=int)
        self.LAB_treshold_upper = np.zeros((3,), dtype=int)
        self.colour_delta = 20
        # reference to generic aspect with plain frame inside
        self.plain_aspect = plain_aspect

    def frame_pipeline(self, frame):
        self.frame = np.copy(frame)
        # if pipeline exists
        if self.frame_transform_pipeline:
            for func in self.frame_transform_pipeline:
                self.frame = func(self.frame)

    def BGR_colour_acquired(self, BGR_colour):

        self.BGR_treshold_colour = BGR_colour
        self.LAB_treshold_colour = cv2.cvtColor(np.uint8([[BGR_colour]]), cv2.COLOR_BGR2LAB).ravel()
        self.update_treshold_boundries()
        self.make_pipeline()

    def make_pipeline(self):
        self.frame_transform_pipeline = \
            ImageRoutines.make_colour_treshold_pipeline(self.LAB_treshold_lower, self.LAB_treshold_upper)

    def update_treshold_boundries(self):
        # define colour boundaries LAB
        self.LAB_treshold_lower = self.LAB_treshold_colour - self.colour_delta
        self.LAB_treshold_lower[0] = 0
        self.LAB_treshold_upper = self.LAB_treshold_colour + self.colour_delta
        self.LAB_treshold_upper[0] = 255

    def colour_delta_changed(self, value):
        self.colour_delta = value
        self.update_treshold_boundries()
        self.make_pipeline()

    def as_csv_line(self):
        ret_line = self.name + ',' + str(self.BGR_treshold_colour) + ',' + str(self.LAB_treshold_colour) \
                   + ',' + str(self.colour_delta) + '\n'
        return ret_line

    def get_data(self):
        data = [self.name, self.eye.name, self.colour_delta]
        data += self.BGR_treshold_colour.tolist()
        data += self.LAB_treshold_colour.tolist()
        return [data]

    def set_data(self, dataframe):
        data = dataframe[(dataframe[0] == self.name) & (dataframe[1] == self.eye.name)]
        if data.size:
            # get last row
            data = data.values.tolist()[-1]
            # self.name, self.eye.name = data[0], data[1]
            self.colour_delta = data[2]
            self.BGR_treshold_colour = np.array([data[3], data[4], data[5]])
            self.LAB_treshold_colour = np.array([data[6], data[7], data[8]])
            self.update_treshold_boundries()
            self.make_pipeline()


class Eye:

    def __init__(self, name, source, aspects):

        self.name = name
        self.source = source
        call('./load_camera_ctrl.sh')
        self.camera = Camera(source)
        self.camera.start()
        self.aspects_list = aspects
        # give all aspects reference to eye
        for aspect in self.aspects_list:
            aspect.eye = self

    def glimpse(self):
        timer = cv2.getTickCount()
        plain_frame = self.camera.read()

        for aspect in self.aspects_list:
                aspect.frame_pipeline(plain_frame)

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        self.print_fps(fps)

    def print_fps(self, fps):

        frame = self.get_aspect('plain').frame
        cv2.putText(frame, "FPS : " + str(int(fps)), (400, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (50, 170, 50), 2)

    def get_aspect(self, aspect_name):
        return next(aspect for aspect in self.aspects_list if aspect.name is aspect_name)
