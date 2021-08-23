class Drawables:

    def __init__(self, canvas):
        self.__list = []
        self.canvas = canvas

    def append(self, item):
        if isinstance(item, Drawables):
            self.__list.append(item.__get_list())

        else:
            tag = list(self.canvas.gettags(item))
            coords = list(self.canvas.coords(item))
            if 'rectangle' in tag or 'oval' in tag:
                color = self.canvas.itemcget(item, 'outline')
            else:
                color = self.canvas.itemcget(item, 'fill')

            # print(tag, coords, color)

            self.__list.append([item, tag[0], coords[0], coords[1], coords[2], coords[3], color])

    def delete(self, idx):
        del self.__list[idx]

    def __repr__(self):
        return str(self.__list)

    def __getitem__(self, item):
        return self.__list[item]

    def clear(self):
        self.__list = []

    def __get_list(self):
        return self.__list

