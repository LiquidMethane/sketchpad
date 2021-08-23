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

        # width of drawable items
        self.width = 3

        # used to draw square or circle
        self.regular = False

        # original positions
        self.x0 = self.y0 = 0

        # to store temporary canvas item
        self.temp_shape = None

        # to store a list of temporary canvas items
        self.temp_list = []

        # to store the index for selected item(s)
        self.selected_idx = None

        # to store copied or cut item(s)
        self.clipboard = None

        self.is_cut = False

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
        self.btn_list[5].bind('<Button-1>', self.set_cursor_mode)

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
        self.gui.set_label_text('Line Mode')

    def line_down(self, event):
        self.x0, self.y0 = event.x, event.y
        self.temp_shape = self.canvas.create_line(self.x0,
                                                  self.y0,
                                                  self.x0,
                                                  self.y0,
                                                  width=self.width,
                                                  fill=self.gui.get_color(),
                                                  tags='line'
                                                  )

    def line_drag(self, event):
        self.canvas.delete(self.temp_shape)
        self.temp_shape = self.canvas.create_line(self.x0,
                                                  self.y0,
                                                  event.x,
                                                  event.y,
                                                  width=self.width,
                                                  fill=self.gui.get_color(),
                                                  tags='line'
                                                  )

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
        self.gui.set_label_text('Scribble Mode')

    def fh_down(self, event):
        self.x0, self.y0 = event.x, event.y

    def fh_drag(self, event):
        self.temp_list.append(self.canvas.create_line(self.x0,
                                                      self.y0,
                                                      event.x,
                                                      event.y,
                                                      width=self.width,
                                                      fill=self.gui.get_color(),
                                                      tags='freehand'
                                                      )
                              )

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
        self.gui.set_label_text('Rectangle Mode')

    def rect_down(self, event):
        self.x0, self.y0 = event.x, event.y
        self.temp_shape = self.canvas.create_rectangle(self.x0,
                                                       self.y0,
                                                       self.x0,
                                                       self.y0,
                                                       width=self.width,
                                                       outline=self.gui.get_color(),
                                                       tags='rectangle'
                                                       )

    def rect_drag(self, event):
        self.canvas.delete(self.temp_shape)
        if self.regular:
            width = event.x - self.x0
            height = event.y - self.y0
            if width >= 0 and height >= 0:
                side = min(width, height)
                self.temp_shape = self.canvas.create_rectangle(self.x0,
                                                               self.y0,
                                                               self.x0 + side,
                                                               self.y0 + side,
                                                               width=self.width,
                                                               outline=self.gui.get_color(),
                                                               tags='rectangle'
                                                               )

            elif width >= 0 and height < 0:
                side = min(width, -height)
                self.temp_shape = self.canvas.create_rectangle(self.x0,
                                                               self.y0,
                                                               self.x0 + side,
                                                               self.y0 - side,
                                                               width=self.width,
                                                               outline=self.gui.get_color(),
                                                               tags='rectangle'
                                                               )

            elif width < 0 and height >= 0:
                side = min(-width, height)
                self.temp_shape = self.canvas.create_rectangle(self.x0,
                                                               self.y0,
                                                               self.x0 - side,
                                                               self.y0 + side,
                                                               width=self.width,
                                                               outline=self.gui.get_color(),
                                                               tags='rectangle'
                                                               )

            else:
                side = min(-width, -height)
                self.temp_shape = self.canvas.create_rectangle(self.x0,
                                                               self.y0,
                                                               self.x0 - side,
                                                               self.y0 - side,
                                                               width=self.width,
                                                               outline=self.gui.get_color(),
                                                               tags='rectangle'
                                                               )

        else:
            self.temp_shape = self.canvas.create_rectangle(self.x0,
                                                           self.y0,
                                                           event.x,
                                                           event.y,
                                                           width=self.width,
                                                           outline=self.gui.get_color(),
                                                           tags='rectangle'
                                                           )

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
        self.gui.set_label_text('Oval Mode')

    def oval_down(self, event):
        self.x0, self.y0 = event.x, event.y
        self.temp_shape = self.canvas.create_oval(self.x0,
                                                  self.y0,
                                                  self.x0,
                                                  self.y0,
                                                  width=self.width,
                                                  outline=self.gui.get_color(),
                                                  tag='oval'
                                                  )

    def oval_drag(self, event):
        self.canvas.delete(self.temp_shape)
        if self.regular:
            width = event.x - self.x0
            height = event.y - self.y0
            if width >= 0 and height >= 0:
                side = min(width, height)
                self.temp_shape = self.canvas.create_oval(self.x0,
                                                          self.y0,
                                                          self.x0 + side,
                                                          self.y0 + side,
                                                          width=self.width,
                                                          outline=self.gui.get_color(),
                                                          tag='oval'
                                                          )

            elif width >= 0 and height < 0:
                side = min(width, -height)
                self.temp_shape = self.canvas.create_oval(self.x0,
                                                          self.y0,
                                                          self.x0 + side,
                                                          self.y0 - side,
                                                          width=self.width,
                                                          outline=self.gui.get_color(),
                                                          tag='oval'
                                                          )

            elif width < 0 and height >= 0:
                side = min(-width, height)
                self.temp_shape = self.canvas.create_oval(self.x0,
                                                          self.y0,
                                                          self.x0 - side,
                                                          self.y0 + side,
                                                          width=self.width,
                                                          outline=self.gui.get_color(),
                                                          tag='oval'
                                                          )

            else:
                side = min(-width, -height)
                self.temp_shape = self.canvas.create_oval(self.x0,
                                                          self.y0,
                                                          self.x0 - side,
                                                          self.y0 - side,
                                                          width=self.width,
                                                          outline=self.gui.get_color(),
                                                          tag='oval'
                                                          )

        else:
            self.temp_shape = self.canvas.create_oval(self.x0,
                                                      self.y0,
                                                      event.x,
                                                      event.y,
                                                      width=self.width,
                                                      outline=self.gui.get_color(),
                                                      tag='oval'
                                                      )

    def oval_up(self, _):
        self.__drawables.append(self.temp_shape)
        self.temp_shape = None
        self.debug()

    # canvas behaviour for drawing polygons
    def set_poly_mode(self, _):
        self.reset()
        self.mode = 'poly'
        print('polygon mode')
        self.canvas.bind('<Button-1>', self.poly_left)
        self.canvas.bind('<Motion>', self.poly_move)
        self.canvas.bind('<Button-3>', self.poly_right)
        self.first_poly_click = True
        self.gui.set_label_text('Polygon Mode')

    def poly_left(self, event):
        print('left click')
        if self.first_poly_click:
            self.x0, self.y0 = event.x, event.y
            self.temp_shape = self.canvas.create_line(self.x0,
                                                      self.y0,
                                                      self.x0,
                                                      self.y0,
                                                      width=self.width,
                                                      fill=self.gui.get_color(),
                                                      tag='poly'
                                                      )

            self.first_poly_click = False
        else:
            self.temp_list.append(self.canvas.create_line(self.x0,
                                                          self.y0,
                                                          event.x,
                                                          event.y,
                                                          width=self.width,
                                                          fill=self.gui.get_color(),
                                                          tag='poly')
                                  )

            self.x0, self.y0 = event.x, event.y

    def poly_move(self, event):
        if not self.first_poly_click:
            self.canvas.delete(self.temp_shape)
            self.temp_shape = self.canvas.create_line(self.x0,
                                                      self.y0,
                                                      event.x,
                                                      event.y,
                                                      width=self.width,
                                                      fill=self.gui.get_color(),
                                                      tag='poly'
                                                      )

    def poly_right(self, _):
        if self.temp_shape:
            self.temp_list.append(self.temp_shape)
        if self.temp_list:
            self.__drawables.append(self.temp_list)
        self.temp_list = []
        self.first_poly_click = True
        self.debug()

    # canvas behaviour for selecting items
    def set_cursor_mode(self, _):
        self.reset()
        self.mode = 'cursor'
        print('cursor mode')
        self.canvas.bind('<Button-1>', self.cursor_single)
        self.canvas.bind('<B1-Motion>', self.cursor_drag)
        self.gui.get_root().bind('<Control-x>', self.cut)
        self.gui.get_root().bind('<Control-c>', self.copy)
        self.gui.get_root().bind('<Control-v>', self.paste)
        self.gui.set_label_text('Cursor Mode')

    def cursor_single(self, event):
        clicked = list(self.canvas.find_withtag('current'))

        if not clicked:
            return

        self.x0, self.y0 = event.x, event.y
        self.selected_idx = self.search(self.__drawables, clicked[0])

    def search(self, container, item):
        for idx, i in enumerate(container):
            if type(i) is not list:
                if i == item:
                    return idx

            elif type(i) is list:
                if self.does_contain(i, item):
                    return idx
        return -1

    def does_contain(self, container, item):
        for i in container:
            if type(i) is not list:
                if i == item:
                    return True
            elif type(i) is list:
                return self.does_contain(i, item)

    def cursor_drag(self, event):
        clicked = list(self.canvas.find_withtag('current'))
        if not clicked:
            return
        self.selected_idx = self.search(self.__drawables, clicked[0])

        if self.selected_idx is not None:
            to_be_moved = self.__drawables[self.selected_idx]
            offset = [event.x - self.x0, event.y - self.y0]

            if type(to_be_moved) is list:
                self.move(to_be_moved, offset)
            else:
                self.canvas.move(to_be_moved, offset[0], offset[1])

            self.x0, self.y0 = event.x, event.y
            self.selected_idx = None

    def move(self, items, offset):
        for i in items:
            if type(i) is list:
                self.move(i, offset)
            else:
                self.canvas.move(i, offset[0], offset[1])

    def cut(self, _):

        if self.selected_idx is None:
            return

        self.delete_items_recur(self.__drawables[self.selected_idx])
        del self.__drawables[self.selected_idx]
        self.is_cut = True

    def delete_items_recur(self, item):
        if type(item) is list:
            for i in item:
                if type(i) is list:
                    self.delete_items_recur(i)
                else:
                    self.canvas.delete(i)
        else:
            self.canvas.delete(item)

    def copy(self, _):

        if self.selected_idx is None:
            return

        self.clipboard = self.__drawables[self.selected_idx]
        self.is_cut = False

    def paste(self, _):

        if self.selected_idx is None or self.is_cut:
            return

        self.paste_items(self.clipboard, self.__drawables)
        self.debug()

    def paste_items(self, item, container):
        if type(item) is list:
            inner_container = []
            for i in item:
                self.paste_items(i, inner_container)
            container.append(inner_container)
        else:
            container.append(self.paste_item(item))

    def paste_item(self, item):
        shape = list(self.canvas.gettags(item))
        coords = [coord + 10 for coord in list(self.canvas.coords(item))]

        if 'rectangle' in shape:
            color = self.canvas.itemcget(item, 'outline')
            return self.canvas.create_rectangle(coords[0],
                                                coords[1],
                                                coords[2],
                                                coords[3],
                                                width=self.width,
                                                outline=color,
                                                tags='rectangle'
                                                )

        elif 'oval' in shape:
            color = self.canvas.itemcget(item, 'outline')
            return self.canvas.create_oval(coords[0],
                                           coords[1],
                                           coords[2],
                                           coords[3],
                                           width=self.width,
                                           outline=color,
                                           tags='oval'
                                           )

        else:
            color = self.canvas.itemcget(item, 'fill')
            return self.canvas.create_line(coords[0],
                                           coords[1],
                                           coords[2],
                                           coords[3],
                                           width=self.width,
                                           fill=color,
                                           tags='line'
                                           )

    # reset canvas behaviour
    def reset(self):
        self.x0 = self.y0 = 0
        if self.mode in ['line', 'freehand', 'rectangle', 'oval']:
            # print('cleared line/freehand/rect/oval behaviour')
            self.canvas.bind('<Button-1>', self.dummy_behavior)
            self.canvas.bind('<B1-Motion>', self.dummy_behavior)
            self.canvas.bind('<ButtonRelease-1>', self.dummy_behavior)

        elif self.mode in ['poly']:
            # print('cleared poly behaviour')
            self.canvas.bind('<Button-1>', self.dummy_behavior)
            self.canvas.bind('<Motion>', self.dummy_behavior)
            self.canvas.bind('<Button-3>', self.dummy_behavior)

        elif self.mode in ['cursor']:
            # print('cleared cursor behaviour')
            self.canvas.bind('<Button-1>', self.dummy_behavior)
            self.canvas.bind('<B1-Motion>', self.dummy_behavior)
            self.gui.get_root().bind('<Control-x>', self.dummy_behavior)
            self.gui.get_root().bind('<Control-c>', self.dummy_behavior)
            self.gui.get_root().bind('<Control-v>', self.dummy_behavior)

    def dummy_behavior(self, event):
        pass

    # for debug purpose
    def debug(self):
        print(self.__drawables)
