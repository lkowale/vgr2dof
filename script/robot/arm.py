import threading
import serial


class Arm:

    shoulder_min = 0
    shoulder_max = 80
    elbow_min = 0
    elbow_max = 80

    ser = serial.Serial('/dev/ttyACM0', 9600)
    # time added to total wait for end_of_move time
    move_time_offset = 100
    # tpmg996r Speed: 4.8V: 0.19 sec/60° =~3,3ms/1°
    move_speed_pdgree = 8

    def __init__(self):

        self.states = ['ready', 'busy']

        self.state = 'ready'

        self.prev_elbow_pos = 0
        self.prev_shoulder_pos = 0

        self.set_elbow_pos = 0
        self.set_shoulder_pos = 0

    def move(self, a, elbow, shoulder, b):
        if self.elbow_min < elbow < self.elbow_max and self.shoulder_min < shoulder < self.shoulder_max:
            self.prev_elbow_pos = self.set_elbow_pos
            self.prev_shoulder_pos = self.set_shoulder_pos
            # print("move")
            self.set_elbow_pos = elbow
            self.set_shoulder_pos = shoulder
            # set Timer to calculated wait time
            threading.Timer(self.calculate_wait_time(), self.stopped).start()
            self.moving()
            # send command
            # command = str(j1)+","+str(j2)+","+str(tower_direction)+","+str(tower_amount)
            command = "{},{},{},{}".format(0, elbow, shoulder, 0)
            # self.logger.info("      Send move command: %s", command)
            self.ser.write(command.encode('ASCII'))
            command = 'Moving to: ' + command
            print(command)

    def calculate_wait_time(self):

        shoulder_time = abs(self.prev_shoulder_pos-self.set_shoulder_pos) * self.move_speed_pdgree
        elbow_time = abs(self.prev_elbow_pos-self.set_elbow_pos)*self.move_speed_pdgree
        wait_time_s = (max(shoulder_time, elbow_time) + self.move_time_offset)/1000.0
        # self.logger.info("    Calculate out of: %i,%i,%i wait time %.3f s", tower_time, j1_time, j2_time,wait_time_s)
        # wait_time_s = 2
        print("calculate_wait_time :{}".format(wait_time_s))
        return wait_time_s

    def reset_position(self):
        self.move(0, 0, 0, 0)

    def reference_position(self):
        self.move(0, 30, 30, 0)

    def stopped(self):
        self.state = 'ready'

    def moving(self):
        self.state = 'busy'

    def delta_move(self, elbow_delta, shoulder_delta):
        elbow_left = elbow_delta + self.set_elbow_pos
        shoulder_left = shoulder_delta + self.set_shoulder_pos
        self.move(0, elbow_left, shoulder_left, 0)
