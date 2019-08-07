class Entry:

    def __init__(self, file):
        if not file:
            # TODO: Error, no file given
            return
        self.file = file
        self.uid = None
        self.version = None
        self.last_modified = None

    def update(self):
        """
        Update an already existing log entry
        """
        pass
