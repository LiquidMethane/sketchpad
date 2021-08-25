from drawable import Drawable


class DrawableList:

    def __init__(self, canvas):
        self.__list = []
        self.canvas = canvas

    def append(self, item):
        if isinstance(item, DrawableList):
            self.__list.append(item.get_list())

        elif isinstance(item, Drawable):
            self.__list.append(item)

        else:
            tag = list(self.canvas.gettags(item))
            coords = list(self.canvas.coords(item))
            if 'rectangle' in tag or 'oval' in tag:
                color = self.canvas.itemcget(item, 'outline')
            else:
                color = self.canvas.itemcget(item, 'fill')

            self.__list.append(Drawable(item, tag[0], coords, color))

    # define delete item by index
    def __delitem__(self, key):
        del self.__list[key]

    # define to string
    def __repr__(self):
        return str(self.__list)

    # define get item by index
    def __getitem__(self, item):
        return self.__list[item]

    # define set item by index
    def __setitem__(self, key, value):
        self.__list[key] = value

    # define iterable behaviour
    def __iter__(self):
        return self.__list.__iter__()

    # define length
    def __len__(self):
        return len(self.__list)

    def clear(self):
        self.__list = []

    def get_list(self):
        return self.__list

    def set_list(self, container):
        self.__list = container

    def remove(self, val):
        self.__list = [i for i in self.__list if i != val]
