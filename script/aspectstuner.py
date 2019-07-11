import tkinter
from tkinter import ttk
from robot.robot import Robot
import cv2
import PIL.Image
import PIL.ImageTk
import time
import cProfile
from keras.models import Sequential
from keras.layers import Dense

def baseline_model():
    # create model
    model = Sequential()
    model.add(Dense(64, input_dim=8, kernel_initializer='normal', activation='relu'))
    model.add(Dense(64, kernel_initializer='normal', activation='relu'))
    # model.add(Dense(32, kernel_initializer='normal', activation='relu'))
    model.add(Dense(2, kernel_initializer='normal', activation='linear'))
    # Compile model
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


class EyeFrame(tkinter.Frame):
    def __init__(self, parent, eye, click_callback):
        tkinter.Frame.__init__(self, parent)

        self.eye = eye
        width = eye.camera.width
        height = eye.camera.height
        self.canvas = tkinter.Canvas(self, width=width, height=height)
        self.canvas.bind("<Button-1>", click_callback)
        self.canvas.grid()
        self.photo = []


class AspectFrame(tkinter.Frame):
    def __init__(self, parent, eye, aspect):
        tkinter.Frame.__init__(self, parent)

        self.aspect = aspect
        width = eye.camera.width
        height = eye.camera.height
        self.canvas = tkinter.Canvas(self, width=width, height=height)
        self.canvas.bind("<Button-1>", self.canvasLclick)

        self.canvas.grid()
        self.photo = []

    def canvasLclick(self, event):
        x = event.x
        y = event.y
        event.widget.create_oval(x-5, y-5, x+5, y+5, fill="red")


class AspectDetails(ttk.Labelframe):

    def __init__(self, parent, label, aspect):
        ttk.Labelframe.__init__(self, parent, text=label)

        self.aspect = None

        self.bgr_label = tkinter.Label(self, text='BGR colour:')
        self.lab_label = tkinter.Label(self, text='LAB colour:')
        self.bgr_value = tkinter.Label(self, text=' ')
        self.lab_value = tkinter.Label(self, text=' ')
        self.colour_delta_label = tkinter.Label(self, text='Colour delta')
        # self.colour_delta_value = tkinter.Label(self, text=' ')
        self.colour_delta_scale = tkinter.Scale(self, orient='horizontal', length=200, from_=0, to=100.0,
                                            command=self.scale_moved, tickinterval=25, resolution=1, )

        self.bgr_label.grid(column=0, row=0)
        self.lab_label.grid(column=0, row=1)
        self.bgr_value.grid(column=2, row=0)
        self.lab_value.grid(column=2, row=1)
        self.colour_delta_label.grid(column=0, row=3)
        # self.colour_delta_value.grid(column=2, row=2)
        self.colour_delta_scale.grid(column=1, row=3, columnspan=2)

        self.haul_aspect_details(aspect)

    def scale_moved(self, value):
        self.aspect.colour_delta_changed(int(value))

    def haul_aspect_details(self, aspect):

        self.aspect = aspect
        self.colour_delta_scale.set(self.aspect.colour_delta)
        self.bgr_value['text'] = self.aspect.BGR_treshold_colour
        self.lab_value['text'] = self.aspect.LAB_treshold_colour


class AspectsTuner:
    def __init__(self, window, window_title):
        self.window = window
        self.robot = Robot('tkinter')
        self.window.title(window_title)
        # register behaviour on clicking red cross 'close' button
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        # create two notebooks side by side , one for plain eye images, second for aspects
        self.eye_notebook = ttk.Notebook(window)
        self.aspect_notebook = ttk.Notebook(window)

        # create notebook frame for each eye and add it to notebook
        for eye in self.robot.cognition.eyes:
            frame = EyeFrame(self.eye_notebook, eye, self.eyeframe_click_callback)
            self.eye_notebook.add(frame, text=eye.name)
            # bind eye frame notebook tab change routine
            frame.bind("<Visibility>", self.on_eye_tab_changed)

        current_eye = self.get_current_eye_frame().eye
        # make tabs for first eye aspects
        self.populate_aspect_notebook(current_eye)
        current_aspect = self.get_current_aspect_frame().aspect
        # create aspect details frame
        self.aspect_details = AspectDetails(window, 'Details', current_aspect)

        self.btn_save_all_aspects = tkinter.Button(window, text="Save all aspects", width=20,
                                                   command=self.save_all_aspects)
        self.btn_load_all_aspects = tkinter.Button(window, text="Load all aspects", width=20,
                                                   command=self.load_all_aspects)
        self.btn_start_record = tkinter.Button(window, text="Start Recorder", width=20,
                                                   command=self.start_recorder)
        self.btn_start_chaser = tkinter.Button(window, text="Start Chaser", width=20,
                                                   command=self.start_chaser)

        # grid manager
        self.eye_notebook.grid(column=0, row=0, columnspan=3)
        self.aspect_notebook.grid(column=4, row=0, columnspan=3)
        self.btn_save_all_aspects.grid(column=0, row=1)
        self.btn_load_all_aspects.grid(column=1, row=1)
        self.btn_start_record.grid(column=2, row=1)
        self.btn_start_chaser.grid(column=3, row=1)
        self.aspect_details.grid(column=4, row=1, columnspan=3)

        # # Define the codec and create VideoWriter object
        # self.fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        # self.out = cv2.VideoWriter('output.avi', self.fourcc, 15.0, (600, 450))

        # After it is called once, the update method will be automatically called every delay milliseconds
        # should be about 30FPS
        self.delay = 30
        self.update()

        self.window.mainloop()

    def eyeframe_click_callback(self, event):
        current_aspect = self.get_current_aspect_frame().aspect
        x = event.x
        y = event.y
        # get bgr colour from plain aspect of current eye
        notebook_frame = self.get_current_eye_frame()
        image_frame = notebook_frame.eye.get_aspect('plain').frame
        # define colour boundaries based on BGR colour LAB
        current_aspect.BGR_colour_acquired(image_frame[y, x])
        self.aspect_details.haul_aspect_details(current_aspect)

    def on_eye_tab_changed(self, event):
        # which eye become visible
        self.populate_aspect_notebook(event.widget.eye)

    def populate_aspect_notebook(self, eye):
        # clear aspect frames notebook
        for i, item in enumerate(self.aspect_notebook.tabs()):
            self.aspect_notebook.forget(item)
        # create notebook frame for each aspect and add it to notebook
        for aspect in eye.aspects_list:
            # add every aspect excluding 'plain'
            if aspect.name is not 'plain':
                frame = AspectFrame(self.aspect_notebook, eye, aspect)
                self.aspect_notebook.add(frame, text=aspect.name)
                frame.bind("<Visibility>", self.on_aspect_tab_changed)

    def on_aspect_tab_changed(self, event):
        # get current aspect
        self.aspect_details.haul_aspect_details(event.widget.aspect)

    def update(self):

        # update robot state including taking images from cameras
        self.robot.update()

        # show active eye image on tab
        notebook_frame = self.get_current_eye_frame()
        image_frame = notebook_frame.eye.get_aspect('plain').frame
        image_canvas = notebook_frame.canvas
        notebook_frame.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(image_frame))
        image_canvas.tag_lower(image_canvas.create_image(0, 0, image=notebook_frame.photo, anchor=tkinter.NW))
        # # save to file
        # self.out.write(image_frame)

        # show active eye aspect image on tab
        notebook_frame = self.get_current_aspect_frame()
        image_frame = notebook_frame.aspect.frame
        image_canvas = notebook_frame.canvas
        notebook_frame.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(image_frame))
        image_canvas.tag_lower(image_canvas.create_image(0, 0, image=notebook_frame.photo, anchor=tkinter.NW))

        self.window.after(self.delay, self.update)

    def get_current_eye_frame(self):
        index = self.eye_notebook.index("current")
        tab_id = self.eye_notebook.tabs()[index]
        tab_id = tab_id[tab_id.rindex('.')+1:]
        return self.eye_notebook.children[tab_id]

    def get_current_aspect_frame(self):
        index = self.aspect_notebook.index("current")
        tab_id = self.aspect_notebook.tabs()[index]
        tab_id = tab_id[tab_id.rindex('.')+1:]
        return self.aspect_notebook.children[tab_id]

    def close_window(self):
        self.robot.shut_down()
        self.out.release()
        self.window.destroy()

    def save_all_aspects(self):
        self.robot.cognition.save_all_aspects()

    def load_all_aspects(self):
        self.robot.cognition.load_all_aspects()
        # refresh aspect details
        self.aspect_details

    def start_recorder(self):
        self.robot.start_recorder()

    def start_chaser(self):
        self.robot.start_chaser()


AspectsTuner(tkinter.Tk(), "VGR")

# Create a window and pass it to the Application object
# cProfile.run('App(tkinter.Tk(), "VGR")', 'stats')

# source activate profiler
# pyprof2calltree -k -i /home/aa/PycharmProjects/profiler/stats
# pyprof2calltree -k -i "/home/aa/PycharmProjects/VGR 2d/impro/stats_1_min"