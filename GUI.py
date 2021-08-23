import tkinter as tk
from tkinter.colorchooser import askcolor
from controller import Controller


class GUI:

    def start_gui(self):
        self.__root.mainloop()

    def __init__(self):
        # top level
        self.__root = tk.Tk()

        # color for drawing shapes
        self.__color = '#000000'

        self.__txtvar = tk.StringVar()

        # icons for icon buttons
        self.__icons = [
            tk.PhotoImage(file='freehand.png'),
            tk.PhotoImage(file='line.png'),
            tk.PhotoImage(file='rectangle.png'),
            tk.PhotoImage(file='oval.png'),
            tk.PhotoImage(file='polygon.png'),
            tk.PhotoImage(file='cursor.png')
        ]

        # configure tkinter window
        self.__root.title('Sketchpad')
        self.__root.geometry('1280x805')
        self.__root.resizable(0, 0)

        # function buttons
        self.__btn_list = []

        # put buttons on window
        for i in range(0, 6):
            self.__btn_list.append(
                tk.Button(
                    master=self.__root,
                    width=75,
                    height=75,
                    image=self.__icons[i]
                )
            )
            self.__btn_list[i].place(x=i * 85, y=5)

        # color picker button
        self.__frm_color = tk.Frame(
            master=self.__root,
            width=40,
            height=40,
            bg='black'
        )
        self.__frm_color.bind('<Button-1>', lambda e: self.__pick_color())
        self.__frm_color.place(x=535, y=25)

        # label
        self.__lbl = tk.Label(
            master=self.__root,
            font=('TkDefaultFont', 30),
            textvariable=self.__txtvar
        )
        self.__lbl.place(x=700, y=20)

        # canvas
        self.__canvas = tk.Canvas(
            master=self.__root,
            bg='gray88',
            width=1280,
            height=720
        )
        self.__canvas.place(x=0, y=85, width=1280, height=720)

    # getter method for canvas
    def get_canvas(self):
        return self.__canvas

    # getter method for function button list
    def get_btn_list(self):
        return self.__btn_list

    # getter method for top level
    def get_root(self):
        return self.__root

    # getter method for color
    def get_color(self):
        return self.__color

    # launches color picker dialog window
    def __pick_color(self):
        self.__color = askcolor()[1]
        self.__frm_color.config(bg=self.__color)

    def set_label_text(self, txt):
        self.__txtvar.set(txt)


def main():
    gui = GUI()
    controller = Controller(gui)
    gui.start_gui()
    return


if __name__ == '__main__':
    main()
