from drawable import Drawable


class DrawableList:

    def __init__(self, canvas):
        self.__list = []
        self.canvas = canvas

    def append(self, item):
        if isinstance(item, DrawableList):
            self.__list.append(item.get_list())

        else:
            tag = list(self.canvas.gettags(item))
            coords = list(self.canvas.coords(item))
            if 'rectangle' in tag or 'oval' in tag:
                color = self.canvas.itemcget(item, 'outline')
            else:
                color = self.canvas.itemcget(item, 'fill')

            self.__list.append(Drawable(item, tag[0], coords, color))

    def __delitem__(self, key):
        del self.__list[key]

    def __repr__(self):
        return str(self.__list)

    def __getitem__(self, item):
        return self.__list[item]

    def __iter__(self):
        return self.__list.__iter__()

    def __len__(self):
        return len(self.__list)

    def clear(self):
        self.__list = []

    def get_list(self):
        return self.__list

