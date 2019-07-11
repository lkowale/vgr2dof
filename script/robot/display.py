import cv2


class Display:

    def __init__(self, windows):
        # display windows positions
        str_pnt = [
            (10, 10),
            (460, 10),
            (30, 30),
            (490, 30)
        ]
        self.windows = []
        self.lclick = False

        self.events = []

        # for i, window in enumerate(windows):
        #     self.windows.append(DisplayWindow(window, str_pnt[i], self.click_callback))

    def show(self, displ_frames):
        # annotate all windows for garbage, the ones called to show will be unannotated
        for window in self.windows:
            window.garbage = True
        # for each frame find corresponding window
        for layer_frame in displ_frames:
            layer_name = layer_frame.get('source_name') + '_' + layer_frame.get('layer')
            if layer_name in DisplayWindow.windows_list:
                # window for this frame already exists
                display_window = next(displ_window for displ_window in self.windows
                            if displ_window.name == layer_name)
                display_window.show(layer_frame.get('frame'))
            else:
                # if windows does'n exist create it
                new_window = DisplayWindow(layer_name, (20, 20), self.click_callback)
                self.windows.append(new_window)
                new_window.show(layer_frame.get('frame'))
        # filtered_values = [value for value in sequence if value != x]
        # garbage_windows = [window for window in self.windows if window.garbage ]
        # self.garbage(garbage_windows)

    def click_callback(self, name, event, x, y):
        self.lclick = True
        self.events.append({'name': name, 'x': x, 'y': y})

    def dispatch_lclick(self):
        self.lclick = False

    def garbage(self, garbage_windows):
        self.windows = [window for window in self.windows if not window.garbage]
        # remove from DisplayWindow.windows_list
        DisplayWindow.windows_list = [window_name for window_name in DisplayWindow.windows_list if window_name in
                                      [window.name for window in garbage_windows]
                                      ]


class DisplayWindow:

    windows_list = []

    def __init__(self, name, start_point, callback_func):

        self.name = name
        self.open_cv_window = cv2.namedWindow(self.name)
        self.callback_func = callback_func
        cv2.setMouseCallback(self.name, self.window_callback)
        # cv2.createButton('save_contour', self.save_contour)
        x, y = start_point
        cv2.moveWindow(self.name, x, y)
        # add self to windows_list
        self.windows_list.append(self.name)
        self.garbage = False

    def show(self, frame):
        cv2.imshow(self.name, frame)
        self.garbage = False

    def window_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.callback_func(self.name, event, x, y)


    # def save_contour(self):
    #     pass
