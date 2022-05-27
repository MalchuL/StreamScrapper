import numpy as np


class DummySR:
    def __init__(self, target_resolution=(1920, 1080)):
        pass

    def super_resolution(self, image: np.ndarray):
        return image
