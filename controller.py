from drawable_list import DrawableList
from drawable import Drawable
import pickle

from tkinter.filedialog import askopenfile, asksaveasfile


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
        self.temp_item_id = None

        # to store a list of temporary canvas items
        self.temp_list = DrawableList(self.canvas)

        # to store the index for selected item(s)
        self.selected_idx = None

        # to store copied or cut item(s)
        self.clipboard = None

        self.is_cut = False

        # used for drawing polygon
        self.first_poly_click = True

        # stores all drawn shapes on screen
        self.__drawables = DrawableList(self.canvas)

        # stores redo steps
        self.__redo_stack = []

        # stores indexes to be grouped
        self.grouping_idx = []

        self.__initialize()

    def __initialize(self):
        # shift key detection for drawing regular shapes (square and circle)
        self.gui.get_root().bind('<KeyPress-Shift_L>', self.set_regular_mode)
        self.gui.get_root().bind('<KeyRelease-Shift_L>', self.reset_regular_mode)

        # undo and redo
        self.gui.get_root().bind('<Control-z>', self.undo)
        self.gui.get_root().bind('<Control-y>', self.redo)

        # set up behaviours for function buttons
        self.btn_list[0].bind('<Button-1>', self.set_freehand_mode)
        self.btn_list[1].bind('<Button-1>', self.set_line_mode)
        self.btn_list[2].bind('<Button-1>', self.set_rect_mode)
        self.btn_list[3].bind('<Button-1>', self.set_oval_mode)
        self.btn_list[4].bind('<Button-1>', self.set_poly_mode)
        self.btn_list[5].bind('<Button-1>', self.set_cursor_mode)
        self.btn_list[6].bind('<Button-1>', self.set_grouping_mode)
        self.btn_list[7].bind('<Button-1>', self.save_file)
        self.btn_list[8].bind('<Button-1>', self.load_file)

    # set regular mode when shift is down
    def set_regular_mode(self, _):
        self.regular = True
        self.gui.get_root().unbind('<KeyPress-Shift_L>')

    # reset regular mode when shift is up
    def reset_regular_mode(self, _):
        self.regular = False
        self.gui.get_root().bind('<KeyPress-Shift_L>', self.set_regular_mode)

    # undo when Control+z
    def undo(self, _):
        if not self.__drawables.get_list():
            return

        item = self.__drawables[-1]
        self.__redo_stack.append(item)
        del self.__drawables[-1]

        self.delete_items_recur(item)

    # redo when Control+y
    def redo(self, _):
        if not self.__redo_stack:
            return

        item = self.__redo_stack[-1]
        del self.__redo_stack[-1]

        self.paste_items(item, self.__drawables, 0)

    def clear_redo(self):
        self.__redo_stack = []

    # canvas behaviour for drawing straight lines
    def set_line_mode(self, _):
        self.reset()
        self.mode = 'line'
        print('line mode')
        self.gui.set_label_text('Line Mode')

        # set interaction behaviours
        self.canvas.bind('<Button-1>', self.line_down)
        self.canvas.bind('<B1-Motion>', self.line_drag)
        self.canvas.bind('<ButtonRelease-1>', self.line_up)

    def line_down(self, event):
        self.x0, self.y0 = event.x, event.y
        self.temp_item_id = self.canvas.create_line(self.x0,
                                                    self.y0,
                                                    self.x0,
                                                    self.y0,
                                                    width=self.width,
                                                    fill=self.gui.get_color(),
                                                    tags='line'
                                                    )

    def line_drag(self, event):
        self.canvas.delete(self.temp_item_id)
        self.temp_item_id = self.canvas.create_line(self.x0,
                                                    self.y0,
                                                    event.x,
                                                    event.y,
                                                    width=self.width,
                                                    fill=self.gui.get_color(),
                                                    tags='line'
                                                    )

    def line_up(self, _):
        self.__drawables.append(self.temp_item_id)
        self.clear_redo()
        self.temp_item_id = None

    # canvas behaviour for freehand drawing
    def set_freehand_mode(self, _):
        self.reset()
        self.mode = 'freehand'
        print('freehand mode')
        self.gui.set_label_text('Scribble Mode')

        # set interaction behaviours
        self.canvas.bind('<Button-1>', self.fh_down)
        self.canvas.bind('<B1-Motion>', self.fh_drag)
        self.canvas.bind('<ButtonRelease-1>', self.fh_up)

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
        self.clear_redo()
        self.temp_list.clear()

        print(self.__drawables)

    # canvas behaviour for drawing rectangles (and squares)
    def set_rect_mode(self, _):
        self.reset()
        self.mode = 'rectangle'
        print('rectangle mode')
        self.gui.set_label_text('Rectangle Mode')

        # set interaction behaviours
        self.canvas.bind('<Button-1>', self.rect_down)
        self.canvas.bind('<B1-Motion>', self.rect_drag)
        self.canvas.bind('<ButtonRelease-1>', self.rect_up)

    def rect_down(self, event):
        self.x0, self.y0 = event.x, event.y
        self.temp_item_id = self.canvas.create_rectangle(self.x0,
                                                         self.y0,
                                                         self.x0,
                                                         self.y0,
                                                         width=self.width,
                                                         outline=self.gui.get_color(),
                                                         tags='rectangle'
                                                         )

    def rect_drag(self, event):
        self.canvas.delete(self.temp_item_id)

        # draw square when regular flag is set
        if self.regular:
            width = event.x - self.x0
            height = event.y - self.y0

            # handle four different cases
            if width >= 0 and height >= 0:
                side = min(width, height)
                self.temp_item_id = self.canvas.create_rectangle(self.x0,
                                                                 self.y0,
                                                                 self.x0 + side,
                                                                 self.y0 + side,
                                                                 width=self.width,
                                                                 outline=self.gui.get_color(),
                                                                 tags='rectangle'
                                                                 )

            elif width >= 0 and height < 0:
                side = min(width, -height)
                self.temp_item_id = self.canvas.create_rectangle(self.x0,
                                                                 self.y0,
                                                                 self.x0 + side,
                                                                 self.y0 - side,
                                                                 width=self.width,
                                                                 outline=self.gui.get_color(),
                                                                 tags='rectangle'
                                                                 )

            elif width < 0 and height >= 0:
                side = min(-width, height)
                self.temp_item_id = self.canvas.create_rectangle(self.x0,
                                                                 self.y0,
                                                                 self.x0 - side,
                                                                 self.y0 + side,
                                                                 width=self.width,
                                                                 outline=self.gui.get_color(),
                                                                 tags='rectangle'
                                                                 )

            else:
                side = min(-width, -height)
                self.temp_item_id = self.canvas.create_rectangle(self.x0,
                                                                 self.y0,
                                                                 self.x0 - side,
                                                                 self.y0 - side,
                                                                 width=self.width,
                                                                 outline=self.gui.get_color(),
                                                                 tags='rectangle'
                                                                 )

        # otherwise draw rectangle
        else:
            self.temp_item_id = self.canvas.create_rectangle(self.x0,
                                                             self.y0,
                                                             event.x,
                                                             event.y,
                                                             width=self.width,
                                                             outline=self.gui.get_color(),
                                                             tags='rectangle'
                                                             )

    def rect_up(self, _):
        self.__drawables.append(self.temp_item_id)
        self.clear_redo()
        self.temp_item_id = None

    # canvas behaviour for drawing ovals (and circles)
    def set_oval_mode(self, _):
        self.reset()
        self.mode = 'oval'
        print('oval mode')
        self.gui.set_label_text('Oval Mode')

        # set interaction behaviours
        self.canvas.bind('<Button-1>', self.oval_down)
        self.canvas.bind('<B1-Motion>', self.oval_drag)
        self.canvas.bind('<ButtonRelease-1>', self.oval_up)

    def oval_down(self, event):
        self.x0, self.y0 = event.x, event.y
        self.temp_item_id = self.canvas.create_oval(self.x0,
                                                    self.y0,
                                                    self.x0,
                                                    self.y0,
                                                    width=self.width,
                                                    outline=self.gui.get_color(),
                                                    tag='oval'
                                                    )

    def oval_drag(self, event):
        self.canvas.delete(self.temp_item_id)

        # draw circle when regular flag is set
        if self.regular:
            width = event.x - self.x0
            height = event.y - self.y0

            # handle four difference cases
            if width >= 0 and height >= 0:
                side = min(width, height)
                self.temp_item_id = self.canvas.create_oval(self.x0,
                                                            self.y0,
                                                            self.x0 + side,
                                                            self.y0 + side,
                                                            width=self.width,
                                                            outline=self.gui.get_color(),
                                                            tag='oval'
                                                            )

            elif width >= 0 and height < 0:
                side = min(width, -height)
                self.temp_item_id = self.canvas.create_oval(self.x0,
                                                            self.y0,
                                                            self.x0 + side,
                                                            self.y0 - side,
                                                            width=self.width,
                                                            outline=self.gui.get_color(),
                                                            tag='oval'
                                                            )

            elif width < 0 and height >= 0:
                side = min(-width, height)
                self.temp_item_id = self.canvas.create_oval(self.x0,
                                                            self.y0,
                                                            self.x0 - side,
                                                            self.y0 + side,
                                                            width=self.width,
                                                            outline=self.gui.get_color(),
                                                            tag='oval'
                                                            )

            else:
                side = min(-width, -height)
                self.temp_item_id = self.canvas.create_oval(self.x0,
                                                            self.y0,
                                                            self.x0 - side,
                                                            self.y0 - side,
                                                            width=self.width,
                                                            outline=self.gui.get_color(),
                                                            tag='oval'
                                                            )

        # otherwise draw oval
        else:
            self.temp_item_id = self.canvas.create_oval(self.x0,
                                                        self.y0,
                                                        event.x,
                                                        event.y,
                                                        width=self.width,
                                                        outline=self.gui.get_color(),
                                                        tag='oval'
                                                        )

    def oval_up(self, _):
        self.__drawables.append(self.temp_item_id)
        self.clear_redo()
        self.temp_item_id = None

    # canvas behaviour for drawing polygons
    def set_poly_mode(self, _):
        self.reset()
        self.mode = 'poly'
        print('polygon mode')
        self.gui.set_label_text('Polygon Mode')

        # set interaction behaviours
        self.canvas.bind('<Button-1>', self.poly_left)
        self.canvas.bind('<Motion>', self.poly_move)
        self.canvas.bind('<Button-3>', self.poly_right)
        self.first_poly_click = True

    def poly_left(self, event):

        if self.first_poly_click:
            # first left click sets the origin
            self.x0, self.y0 = event.x, event.y
            self.temp_item_id = self.canvas.create_line(self.x0,
                                                        self.y0,
                                                        self.x0,
                                                        self.y0,
                                                        width=self.width,
                                                        fill=self.gui.get_color(),
                                                        tag='poly'
                                                        )

            self.first_poly_click = False
        else:
            # subsequent left clicks register line segment and append to polygon list
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

        # draw temporary lines for visual purpose
        if not self.first_poly_click:
            self.canvas.delete(self.temp_item_id)
            self.temp_item_id = self.canvas.create_line(self.x0,
                                                        self.y0,
                                                        event.x,
                                                        event.y,
                                                        width=self.width,
                                                        fill=self.gui.get_color(),
                                                        tag='poly'
                                                        )

    def poly_right(self, _):
        if self.temp_item_id:
            self.temp_list.append(self.temp_item_id)
        if self.temp_list:
            self.__drawables.append(self.temp_list)
            self.clear_redo()
        self.temp_list.clear()
        self.first_poly_click = True

    # canvas behaviour for selecting items
    def set_cursor_mode(self, _):
        self.reset()
        self.mode = 'cursor'
        print('cursor mode')
        self.gui.set_label_text('Cursor Mode')

        # set interaction behaviours
        self.canvas.bind('<Button-1>', self.cursor_single)
        self.canvas.bind('<B1-Motion>', self.cursor_drag)
        self.gui.get_root().bind('<Control-x>', self.cut)
        self.gui.get_root().bind('<Control-c>', self.copy)
        self.gui.get_root().bind('<Control-v>', self.paste)

    def cursor_single(self, event):

        # find the canvas item that the mouse clicked on
        clicked = list(self.canvas.find_withtag('current'))

        if not clicked:
            return

        self.x0, self.y0 = event.x, event.y

        # recursively search for adjacent items
        self.selected_idx = self.search(self.__drawables.get_list(), clicked[0])

    def search(self, container, item):
        # recursive search algorithm to determine the top-level position of the clicked canvas item
        for idx, i in enumerate(container):
            if isinstance(i, Drawable):
                if i.ident == item:
                    return idx

            elif type(i) is list:
                if self.does_contain(i, item):
                    return idx
        return -1

    def does_contain(self, container, item):
        for i in container:
            if isinstance(i, Drawable):
                if i.ident == item:
                    return True
            elif type(i) is list:
                return self.does_contain(i, item)

    def cursor_drag(self, event):
        #continually find the canvas item(s) being clicked on
        clicked = list(self.canvas.find_withtag('current'))
        if not clicked:
            return
        self.selected_idx = self.search(self.__drawables.get_list(), clicked[0])

        if self.selected_idx is not None:
            to_be_moved = self.__drawables[self.selected_idx]
            offset = [event.x - self.x0, event.y - self.y0]

            # recursively move every item
            if type(to_be_moved) is list:
                self.move(to_be_moved, offset)
            else:
                self.canvas.move(to_be_moved.ident, offset[0], offset[1])
                to_be_moved.coords = self.canvas.coords(to_be_moved.ident)

            self.x0, self.y0 = event.x, event.y
            self.selected_idx = None

    def move(self, items, offset):
        # recursive move algorithm
        for i in items:
            if type(i) is list:
                self.move(i, offset)
            else:
                self.canvas.move(i.ident, offset[0], offset[1])
                i.coords = self.canvas.coords(i.ident)

    def cut(self, _):

        if self.selected_idx is None:
            return

        # put canvas item to be cut into clipboard
        self.clipboard = self.__drawables[self.selected_idx]

        # recursively delete the cut items
        self.delete_items_recur(self.__drawables[self.selected_idx])
        del self.__drawables[self.selected_idx]

    def delete_items_recur(self, item):
        if type(item) is list:
            for i in item:
                if type(i) is list:
                    self.delete_items_recur(i)
                else:
                    self.canvas.delete(i.ident)
        else:
            self.canvas.delete(item.ident)

    def copy(self, _):

        if self.selected_idx is None:
            return

        # put canvas item to be cut into clipboard
        self.clipboard = self.__drawables[self.selected_idx]

    def paste(self, _):

        if self.selected_idx is None:
            return

        # recursively paste canvas items with 20 pixel offset in x and y position
        self.paste_items(self.clipboard, self.__drawables, 20)

    def paste_items(self, item, container, offset):
        # recursive paste algorithm
        if type(item) is list:
            inner_container = DrawableList(self.canvas)
            for i in item:
                self.paste_items(i, inner_container, offset)
            container.append(inner_container)
        elif isinstance(item, Drawable):
            container.append(self.paste_item(item, offset))

    def paste_item(self, item, offset):
        coords = [coord + offset for coord in item.coords]

        if item.tag == 'rectangle':
            ident = self.canvas.create_rectangle(coords[0],
                                                 coords[1],
                                                 coords[2],
                                                 coords[3],
                                                 width=self.width,
                                                 outline=item.color,
                                                 tags='rectangle'
                                                 )

        elif item.tag == 'oval':
            ident = self.canvas.create_oval(coords[0],
                                            coords[1],
                                            coords[2],
                                            coords[3],
                                            width=self.width,
                                            outline=item.color,
                                            tags='oval'
                                            )

        else:
            ident = self.canvas.create_line(coords[0],
                                            coords[1],
                                            coords[2],
                                            coords[3],
                                            width=self.width,
                                            fill=item.color,
                                            tags='line'
                                            )
        return Drawable(ident, item.tag, coords, item.color)

    def set_grouping_mode(self, _):
        self.reset()
        self.mode = 'grouping'
        print('grouping mode')
        self.gui.set_label_text('Grouping Mode')
        self.canvas.bind('<Button-1>', self.grouping_click)
        self.gui.get_root().bind('<Control-g>', self.group)
        self.gui.get_root().bind('<Control-u>', self.ungroup)
        self.grouping_idx = []

    def grouping_click(self, _):
        clicked = list(self.canvas.find_withtag('current'))

        if not clicked:
            return

        # add item to be grouped to a list
        self.grouping_idx.append(self.search(self.__drawables.get_list(), clicked[0]))

    def group(self, _):
        if not self.grouping_idx:
            return

        grouped = []
        # remove all duplications
        self.grouping_idx = list(dict.fromkeys(self.grouping_idx))

        # add items to be grouped into a single list and remove them from drawables list
        for i in self.grouping_idx:
            grouped.append(self.__drawables[i])
            self.__drawables[i] = -1

        self.__drawables.remove(-1)

        if grouped:
            # append the group to drawables list
            self.__drawables.get_list().append(grouped)

    def ungroup(self, _):

        # only allow one item to be selected when ungrouping
        if len(self.grouping_idx) != 1:
            return

        grouped = self.__drawables[self.grouping_idx[0]]

        # cannot ungroup primary items
        if isinstance(grouped, Drawable):
            return

        del self.__drawables[self.grouping_idx[0]]

        for i in grouped:
            self.__drawables.get_list().append(i)

    # reset canvas behaviour
    def reset(self):
        self.x0 = self.y0 = 0
        if self.mode in ['line', 'freehand', 'rectangle', 'oval']:
            self.canvas.bind('<Button-1>', self.dummy_behavior)
            self.canvas.bind('<B1-Motion>', self.dummy_behavior)
            self.canvas.bind('<ButtonRelease-1>', self.dummy_behavior)

        elif self.mode in ['poly']:
            self.canvas.bind('<Button-1>', self.dummy_behavior)
            self.canvas.bind('<Motion>', self.dummy_behavior)
            self.canvas.bind('<Button-3>', self.dummy_behavior)

        elif self.mode in ['cursor']:
            self.canvas.bind('<Button-1>', self.dummy_behavior)
            self.canvas.bind('<B1-Motion>', self.dummy_behavior)
            self.gui.get_root().bind('<Control-x>', self.dummy_behavior)
            self.gui.get_root().bind('<Control-c>', self.dummy_behavior)
            self.gui.get_root().bind('<Control-v>', self.dummy_behavior)

        elif self.mode in ['grouping']:
            self.canvas.bind('<Button-1>', self.dummy_behavior)
            self.gui.get_root().bind('<Control-g>', self.dummy_behavior)
            self.gui.get_root().bind('<Control-u>', self.dummy_behavior)

    def dummy_behavior(self, event):
        pass

    def save_file(self, _):
        # open tkinter save as file dialog
        f = asksaveasfile(mode='wb', filetypes=[('pickle files', '.pickle')])
        if f is None:
            return 'break'

        # serialize objects into binary and save to file
        serialized_list = []
        self.serialize(self.__drawables.get_list(), serialized_list)
        f.write(pickle.dumps(serialized_list[0]))
        f.close()
        return 'break'

    def serialize(self, item, container):
        if type(item) is list:
            inner_container = []
            for i in item:
                self.serialize(i, inner_container)
            container.append(inner_container)
        elif isinstance(item, Drawable):
            container.append([item.ident, item.tag, item.coords, item.color])

    def load_file(self, _):
        # open tkinter open file dialog
        f = askopenfile(mode='rb', filetypes=[('pickle files', '.pickle')])
        if f is None:
            return 'break'

        # deserialize binary to objects and load to canvas
        self.clear_canvas(self.__drawables)
        self.__drawables.clear()
        container = []
        self.deserialize(pickle.load(f), container)
        self.__drawables.set_list(container[0])
        f.close()
        return 'break'

    def deserialize(self, item, container):
        if type(item) is list and len(item) == 4 and type(item[1]) is str:
            if item[1] == 'rectangle':
                ident = self.canvas.create_rectangle(item[2][0],
                                                     item[2][1],
                                                     item[2][2],
                                                     item[2][3],
                                                     width=self.width,
                                                     outline=item[3],
                                                     tags='rectangle'
                                                     )

            elif item[1] == 'oval':
                ident = self.canvas.create_oval(item[2][0],
                                                item[2][1],
                                                item[2][2],
                                                item[2][3],
                                                width=self.width,
                                                outline=item[3],
                                                tags='oval'
                                                )

            else:
                ident = self.canvas.create_line(item[2][0],
                                                item[2][1],
                                                item[2][2],
                                                item[2][3],
                                                width=self.width,
                                                fill=item[3],
                                                tags='line'
                                                )

            container.append(Drawable(ident, item[1], item[2], item[3]))

        elif type(item) is list:
            inner_container = []
            for i in item:
                self.deserialize(i, inner_container)
            container.append(inner_container)

    def clear_canvas(self, item):
        if isinstance(item, Drawable):
            self.canvas.delete(item.ident)
        else:
            for i in item:
                self.clear_canvas(i)
