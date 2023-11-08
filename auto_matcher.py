class AutoMatcher:
    def __init__(self, directory, camera, limit=150, window_size=1700):
        self.directory = directory
        self.h = window_size
        self.limit = limit
        if camera == "Basler":
            self.camera = 0
        elif camera == "Cognex":
            self.camera = 1
        else:
            self.camera = 1

