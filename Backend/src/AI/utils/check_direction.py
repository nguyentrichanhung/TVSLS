from collections import deque

class VehiclePos(object):
    def __init__(self):
        self.positions = deque(maxlen=2)
        self.frames_since_seen = 0
        self.speed = 0
        self.is_wrong_direction = False

    def add_position(self, new_position):
        self.positions.append(new_position)
        self.frames_since_seen = 0