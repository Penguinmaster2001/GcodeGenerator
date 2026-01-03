class GcodePoint:
    def __init__(self, x: float, y: float, layer: int, extrude: bool):
        self.x = x
        self.y = y
        self.layer = layer
        self.extrude = extrude
