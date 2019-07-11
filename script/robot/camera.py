import threading
import cv2
import time


class Camera(threading.Thread):

    def __init__(self, source):
        threading.Thread.__init__(self)
        self.source = source
        self.width = 600
        self.height = 450
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(self.source)
        (self.grabbed, self.frame) = self.stream.read()
        # wait fo camera to start
        time.sleep(1.0)
        self.stop_flag = False

    def run(self):
        while not self.stop_flag:
            (self.grabbed, self.frame) = self.stream.read()
        return

    def read(self):
        return self.resize(self.frame, self.width, self.height)

    def resize(self, image, width=None, height=None):

        dim = None
        (h, w) = image.shape[:2]

        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        return resized

    def stop(self):
        self.stop_flag = True
