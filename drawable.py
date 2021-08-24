class Drawable:
    def __init__(self, ident, tag, coords, color):
        self.ident = ident
        self.tag = tag
        self.coords = coords
        self.color = color

    def __repr__(self):
        # return f'ID: {self.ident}  tag: {self.tag}  coords: {self.coords}, color: {self.color}'
        return str([self.ident, self.tag, self.coords, self.color])
