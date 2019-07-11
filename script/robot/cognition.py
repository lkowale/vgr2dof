from robot.eye import Eye
from robot.eye import Aspect
from utils.utils import *
import pandas as pd
from robot.world import World
from robot.world import WorldObject
from robot.world import RotatedRectangle


class Cognition:

    def __init__(self):
        self.eyes = []

        eyes_inits = [
            {'name': 'upper', 'source_number': 0},
            {'name': 'side', 'source_number': 1},

        ]

        for eye_params in eyes_inits:
            # def __init__(self, name, pipeline):
            plain_aspect = Aspect('plain')
            aspects = [
                        plain_aspect,
                        Aspect('blue_treshold', plain_aspect),
                        Aspect('red_treshold', plain_aspect),
                        Aspect('green_treshold', plain_aspect),
                        Aspect('orange_treshold', plain_aspect)
                        ]
            self.eyes.append(Eye(eye_params.get('name'), eye_params.get('source_number'), aspects))

        humerus_aspects = self.get_aspect_all_eyes('blue_treshold')
        ulna_aspects = self.get_aspect_all_eyes('green_treshold')
        blob_aspects = self.get_aspect_all_eyes('red_treshold')
        ball_aspects = self.get_aspect_all_eyes('orange_treshold')

        self.world = World()
        self.world.objects = [
            RotatedRectangle('ulna', 1, ulna_aspects),
            RotatedRectangle('humerus', 0, humerus_aspects),
            WorldObject('blob', 2, blob_aspects),
            WorldObject('ball', 3, ball_aspects)
        ]

    def observe(self):
        for eye in self.eyes:
            eye.glimpse()
        # self.world.describe()
        # self.world.draw_objectst_contours()

    def get_displayable(self):
        cognition_frames = []
        for eye in self.eyes:
            for aspect in eye.aspects_list:
                cognition_frames.append({'source_name': eye.name, 'layer': aspect.name, 'frame': aspect.frame})

        return cognition_frames

    def save_all_aspects(self):
        AspectDataManager("adm_data.csv").save_all_aspects(self.eyes)

    def load_all_aspects(self):
        AspectDataManager("adm_data.csv").load_all_aspects(self.eyes)

    def take_readings(self):
        return self.world.describe()
        # return {'eye': 'upper', 'ulna_x': 10, 'ulna_y': 20, 'ulna_a': 30,
        #         'humers_x': 11, 'humers_y': 21, 'humers_a': 31}

    def get_aspect_all_eyes(self, name):
        aspects = []
        for eye in self.eyes:
            aspect = eye.get_aspect(name)
            if aspect:
                aspects.append(aspect)
        return aspects

    def take_readings(self):
        return self.world.describe()


class AspectDataManager:
    def __init__(self, file_name):
        self.file_name = file_name
        self.loaded_df = None

    def save_all_aspects(self, eyes_list):
        for eye in eyes_list:
            for aspect in eye.aspects_list:
                if aspect.name is not 'plain':
                    self.save_aspect(aspect)

    def save_aspect(self, aspect):
        aspect_data = aspect.get_data()
        self.append_csv(aspect_data)

    def append_csv(self, aspect_data):
        # existing_df = pd.read_csv(file_name)     # "./data.csv"
        df = pd.DataFrame(aspect_data)
        with open(self.file_name, 'a') as fd:
            # df.to_csv(fd, index=False, header=fd.tell() == 0, mode='a')
            df.to_csv(fd, index=False, header=False, mode='a')

    def load_all_aspects(self, eyes_list):
        self.loaded_df = pd.read_csv(self.file_name, header=None)
        for eye in eyes_list:
            for aspect in eye.aspects_list:
                self.load_aspect(self.loaded_df, aspect)

    def load_aspect(self, dataframe, aspect):
        aspect.set_data(dataframe)
