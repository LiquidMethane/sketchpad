class Controller:
    def __init__(self, gui):
        # gui object
        self.gui = gui

        # gui canvas object
        self.canvas = gui.get_canvas()

        # gui button list
        self.btn_list = gui.get_btn_list()

        # state for mode
        self.mode = None

        # used to draw square or circle
        self.regular = False

        # original positions
        self.x0 = self.y0 = 0

        # to store temporary canvas item
        self.temp_shape = None

        # to store a list of temporary canvas items
        self.temp_list = []

        # used for drawing polygon
        self.first_poly_click = True

        # stores all drawn shapes on screen
        self.__drawables = []

        self.__initialize()

    def __initialize(self):
        # shift key detection for drawing regular shapes (square and circle)
        self.gui.get_root().bind('<KeyPress-Shift_L>', self.set_regular_mode)
        self.gui.get_root().bind('<KeyRelease-Shift_L>', self.reset_regular_mode)

        # set up behaviours for function buttons
        self.btn_list[0].bind('<Button-1>', self.set_freehand_mode)
        self.btn_list[1].bind('<Button-1>', self.set_line_mode)
        self.btn_list[2].bind('<Button-1>', self.set_rect_mode)
        self.btn_list[3].bind('<Button-1>', self.set_oval_mode)
        self.btn_list[4].bind('<Button-1>', self.set_poly_mode)

    def set_regular_mode(self, _):
        self.regular = True
        self.gui.get_root().unbind('<KeyPress-Shift_L>')

    def reset_regular_mode(self, _):
        self.regular = False
        self.gui.get_root().bind('<KeyPress-Shift_L>', self.set_regular_mode)

    # canvas behaviour for drawing straight lines
    def set_line_mode(self, _):
        self.reset()
        self.mode = 'line'
        print('line mode')
        self.canvas.bind('<Button-1>', self.line_down)
        self.canvas.bind('<B1-Motion>', self.line_drag)
        self.canvas.bind('<ButtonRelease-1>', self.line_up)

    def line_down(self, event):
        self.x0, self.y0 = event.x, event.y
        self.temp_shape = self.canvas.create_line(self.x0, self.y0, self.x0, self.y0, width=3, fill=self.gui.get_color())

    def line_drag(self, event):
        self.canvas.delete(self.temp_shape)
        self.temp_shape = self.canvas.create_line(self.x0, self.y0, event.x, event.y, width=3, fill=self.gui.get_color())

    def line_up(self, _):
        self.__drawables.append(self.temp_shape)
        self.temp_shape = None
        self.debug()

    # canvas behaviour for freehand drawing
    def set_freehand_mode(self, _):
        self.reset()
        self.mode = 'freehand'
        print('freehand mode')
        self.canvas.bind('<Button-1>', self.fh_down)
        self.canvas.bind('<B1-Motion>', self.fh_drag)
        self.canvas.bind('<ButtonRelease-1>', self.fh_up)

    def fh_down(self, event):
        self.x0, self.y0 = event.x, event.y

    def fh_drag(self, event):
        self.temp_list.append(self.canvas.create_line(self.x0, self.y0, event.x, event.y, width=3, fill=self.gui.get_color()))
        self.x0, self.y0 = event.x, event.y

    def fh_up(self, _):
        self.__drawables.append(self.temp_list)
        self.temp_list = []
        self.debug()

    # canvas behaviour for drawing rectangles (and squares)
    def set_rect_mode(self, _):
        self.reset()
        self.mode = 'rectangle'
        print('rectangle mode')
        self.canvas.bind('<Button-1>', self.rect_down)
        self.canvas.bind('<B1-Motion>', self.rect_drag)
        self.canvas.bind('<ButtonRelease-1>', self.rect_up)

    def rect_down(self, event):
        self.x0, self.y0 = event.x, event.y
        self.temp_shape = self.canvas.create_rectangle(self.x0, self.y0, self.x0, self.y0, width=3, outline=self.gui.get_color())

    def rect_drag(self, event):
        self.canvas.delete(self.temp_shape)
        if self.regular:
            width = event.x - self.x0
            height = event.y - self.y0
            if width >= 0 and height >= 0:
                side = min(width, height)
                self.temp_shape = self.canvas.create_rectangle(self.x0, self.y0, self.x0 + side, self.y0 + side, width=3, outline=self.gui.get_color())
            elif width >= 0 and height < 0:
                side = min(width, -height)
                self.temp_shape = self.canvas.create_rectangle(self.x0, self.y0, self.x0 + side, self.y0 - side, width=3, outline=self.gui.get_color())
            elif width < 0 and height >= 0:
                side = min(-width, height)
                self.temp_shape = self.canvas.create_rectangle(self.x0, self.y0, self.x0 - side, self.y0 + side, width=3, outline=self.gui.get_color())
            else:
                side = min(-width, -height)
                self.temp_shape = self.canvas.create_rectangle(self.x0, self.y0, self.x0 - side, self.y0 - side, width=3, outline=self.gui.get_color())
        else:
            self.temp_shape = self.canvas.create_rectangle(self.x0, self.y0, event.x, event.y, width=3, outline=self.gui.get_color())

    def rect_up(self, _):
        self.__drawables.append(self.temp_shape)
        self.temp_shape = None
        self.debug()

    # canvas behaviour for drawing ovals (and circles)
    def set_oval_mode(self, _):
        self.reset()
        self.mode = 'oval'
        print('oval mode')
        self.canvas.bind('<Button-1>', self.oval_down)
        self.canvas.bind('<B1-Motion>', self.oval_drag)
        self.canvas.bind('<ButtonRelease-1>', self.oval_up)

    def oval_down(self, event):
        self.x0, self.y0 = event.x, event.y
        self.temp_shape = self.canvas.create_oval(self.x0, self.y0, self.x0, self.y0, width=3, outline=self.gui.get_color())

    def oval_drag(self, event):
        self.canvas.delete(self.temp_shape)
        if self.regular:
            width = event.x - self.x0
            height = event.y - self.y0
            if width >= 0 and height >= 0:
                side = min(width, height)
                self.temp_shape = self.canvas.create_oval(self.x0, self.y0, self.x0 + side, self.y0 + side, width=3, outline=self.gui.get_color())
            elif width >= 0 and height < 0:
                side = min(width, -height)
                self.temp_shape = self.canvas.create_oval(self.x0, self.y0, self.x0 + side, self.y0 - side, width=3, outline=self.gui.get_color())
            elif width < 0 and height >= 0:
                side = min(-width, height)
                self.temp_shape = self.canvas.create_oval(self.x0, self.y0, self.x0 - side, self.y0 + side, width=3, outline=self.gui.get_color())
            else:
                side = min(-width, -height)
                self.temp_shape = self.canvas.create_oval(self.x0, self.y0, self.x0 - side, self.y0 - side, width=3, outline=self.gui.get_color())
        else:
            self.temp_shape = self.canvas.create_oval(self.x0, self.y0, event.x, event.y, width=3, outline=self.gui.get_color())

    def oval_up(self, _):
        self.__drawables.append(self.temp_shape)
        self.temp_shape = None
        self.debug()

    # canvas behaviour for drawing polygons
    def set_poly_mode(self, _):
        self.reset()
        self.mode = 'poly'
        print('polygon mode')
        self.canvas.bind('<Button-1>', self.poly_single)
        self.canvas.bind('<Motion>', self.poly_move)
        self.canvas.bind('<Double-Button-1>', self.poly_double)
        self.first_poly_click = True

    def poly_single(self, event):
        if self.first_poly_click:
            self.x0, self.y0 = event.x, event.y
            self.temp_shape = self.canvas.create_line(self.x0, self.y0, self.x0, self.y0, width=3, fill=self.gui.get_color())
            self.first_poly_click = False
        else:
            self.temp_list.append(self.canvas.create_line(self.x0, self.y0, event.x, event.y, width=3, fill=self.gui.get_color()))
            self.x0, self.y0 = event.x, event.y

    def poly_move(self, event):
        if not self.first_poly_click:
            self.canvas.delete(self.temp_shape)
            self.temp_shape = self.canvas.create_line(self.x0, self.y0, event.x, event.y, width=3, fill=self.gui.get_color())

    def poly_double(self, event):
        print('got double click')
        self.temp_list.append(self.canvas.create_line(self.x0, self.y0, event.x, event.y, width=3, fill=self.gui.get_color()))
        self.__drawables.append(self.temp_list)
        self.temp_list = []
        self.first_poly_click = True
        self.debug()

    # reset canvas behaviour
    def reset(self):
        self.x0 = self.y0 = 0
        if self.mode == 'line' or 'freehand' or 'rect' or 'oval':
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<B1-Motion>')
            self.canvas.unbind('<ButtonRelease-1>')

        elif self.mode == 'poly':
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<Motion>')
            self.canvas.unbind('<Double-Button-1>')

    # for debug purpose
    def debug(self):
        print(self.__drawables)
