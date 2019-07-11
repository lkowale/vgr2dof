from robot.cognition import Cognition
from robot.display import Display
from robot.arm import Arm
from sklearn.externals import joblib
from keras.models import load_model
import cv2
import pandas as pd
from robot.eye import ImageRoutines

# Set up logging; The basic log level will be DEBUG
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s%(msecs)03d %(message)s', datefmt='%H:%M:%S.%p')


class Robot:
    def __init__(self, display_handler=None, task=None):
        self.states = ['initialize', 'doing_task', 'waiting_for_task']
        # define cogntion layer
        self.cognition = Cognition()
        # define mechanical arm
        self.arm = Arm()
        self.display_handler = display_handler
        if self.display_handler is 'opencv':
            self.display = Display([])

        self.current_task = task

    def update(self):
        timer = cv2.getTickCount()
        self.cognition.observe()

        if self.current_task:
            state = self.current_task.update()
            if state is 'done':
                self.current_task = None

        if self.display_handler is 'opencv':
            # pass images from cognition layer to display layer
            displayable = self.cognition.get_displayable()
            self.display.show(displayable)

        # count overall fps
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        # print overall fps on first plane
        fps_frame = self.cognition.eyes[0].get_aspect('plain').frame
        cv2.putText(fps_frame, "Ov FPS : " + str(int(fps)), (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

    def shut_down(self):
        # release cameras
        for eye in self.cognition.eyes:
            eye.camera.stop()

    def start_recorder(self):
        self.current_task = Recorder('Recorder', self.cognition, self.arm)

    def start_chaser(self):
        self.current_task = Chaser('Chaser', self.cognition, self.arm)


class Task:
    def __init__(self, name, cognition, arm):
        self.name = name
        self.cognition = cognition
        self.arm = arm


class Chaser(Task):

    def __init__(self, name, cognition, arm):
        Task.__init__(self, name, cognition, arm)
        self.states = ['ready', 'wait_for_arm', 'done']
        self.state = 'ready'
        self.world = self.cognition.world
        self.pipeline = joblib.load('sklearn_pipeline.pkl')
        self.pipeline.named_steps['regresor'].model = load_model('model_pipeline.h5')
        self.chased = self.world.get_object_by_name('ball')

    def update(self):
        self.world.describe()

        if self.state is 'ready':
            # get world objects parameters
            # X = df[['blobmec_cx', 'blobmec_cy', 'ulnarbr_angle', 'ulnarbr_cx', 'ulnarbr_cy', 'humerusrbr_angle', 'humerusrbr_cx', 'humerusrbr_cy']]
            chased = self.chased
            ulna = self.world.get_object_by_name('ulna')
            humerus = self.world.get_object_by_name('humerus')
            X = [chased.cx, chased.cy, ulna.angle, ulna.cx, ulna.cy, humerus.angle, humerus.cx, humerus.cy]
            # make inference of theme
            # Y = Y[['elbow_delta', 'shoulder_delta']]
            elbow, shoulder = self.pipeline.predict([X])
            elbow = int(elbow)
            shoulder = int(shoulder)
            self.arm.delta_move(elbow, shoulder)
            # get plain aspect
            frame = ulna.aspects[0].plain_aspect.frame
            # cv2.putText(frame, 'delta ' + str(elbow), (ulna.cx-10, ulna.cy+20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, ImageRoutines.red_BGR, 2)
            # cv2.putText(frame, 'delta ' + str(shoulder), (humerus.cx-10, humerus.cy+20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, ImageRoutines.red_BGR, 2)
            self.state = 'wait_for_arm'

        if self.state is 'wait_for_arm':
            if self.arm.state is 'ready':
                self.state = 'ready'
        # move arm to grab object
        self.world.draw_objects_contours()


