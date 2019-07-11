import cv2
from utils.utils import describe_contour
import numpy as np
from robot.eye import ImageRoutines


class World:

    def __init__(self):

        self.objects = []

    def describe(self):
        world_description = {}
        for world_object in self.objects:
            world_description.update(world_object.describe())
        return world_description

    def draw_objects_contours(self):
        for world_object in self.objects:
            world_object.show_on_plain()

    def get_object_by_name(self, name):
        return next(world_object for world_object in self.objects if world_object.name is name)


class WorldObjectType:

    def __init__(self, name, aspects):
        self.name = name
        self.aspects = aspects
        self.objects = []


class WorldObject:

    def __init__(self, name, _id, aspects):

        self.name = name
        self._id = _id
        self.aspects = aspects
        self.cx = 0
        self.cy = 0
        self.radius = 0
        self.contour = None

    def describe(self):
        row = {}
        for aspect in self.aspects:
            frame = np.copy(aspect.frame)
            cnts = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # take actual contour points list
            # there is at least one contour
            # mec - Minimum Enclosing Circle
            for i, contour in enumerate(cnts[1]):
                self.contour = contour
                # name_core = self.name + '_' + aspect.eye.name + '_' + aspect.name + '_cnt_' + str(i) + '_'
                name_core = self.name
                (x, y), radius = describe_contour(contour)
                self.cx = int(x)
                self.cy = int(y)
                self.radius = int(radius)
                row.update({name_core + 'mec_cx': x, name_core + 'mec_cy': y, name_core + 'mec_radius': radius})
        return row

    def show_on_plain(self):
        aspect = self.aspects[0]
        x = self.cx
        y = self.cy
        frame = aspect.plain_aspect.frame
        cv2.circle(frame, (x, y), 5, ImageRoutines.red_BGR, -1)
        cv2.putText(frame, self.name, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, ImageRoutines.red_BGR, 2)
        cv2.drawContours(frame, [self.contour], -1, ImageRoutines.red_BGR, 2)
        self.show_on_plain_addon(x, y, frame)

    def show_on_plain_addon(self, x, y, frame):
        # cv2.putText(frame, "Radius: " + str(self.radius), (x - 10, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.50, ImageRoutines.red_BGR, 2)
        pass


class RotatedRectangle(WorldObject):

    def __init__(self, name, _id, aspects):
        WorldObject.__init__(self, name, _id, aspects)
        self.angle = 0
        self.height = 0
        self.width = 0

    def describe(self):
        rows = {}
        for aspect in self.aspects:
            frame = np.copy(aspect.frame)
            cnts = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # take actual contour points list
            # there is at least one contour
            # rbr - Rotated Bounding Rectangle
            for i, contour in enumerate(cnts[1]):
                contour = cv2.approxPolyDP(contour, 0.03, True)
                self.contour = contour
                rect = cv2.minAreaRect(contour)
                (x, y), (width, height), angle = rect
                self.cx = int(x)
                self.cy = int(y)
                self.width = width
                self.height = height
                self.angle = int(angle)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                # name_core = self.name + '_' + aspect.eye.name + '_' + aspect.name + '_cnt_' + str(i) + '_'
                name_core = self.name + '_'
                row = {name_core + 'rbr_cx': x, name_core + 'rbr_cy': y, name_core + 'rbr_angle': angle}
                rows.update(row)
        return rows

    def show_on_plain_addon(self, x, y, frame):
        # cv2.drawContours(aspect.frame, [box], 0, (0, 0, 255), 2)
        rect = ((self.cx, self.cy), (self.width, self.height), self.angle)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame, [box], 0, (55, 0, 55), 2)


