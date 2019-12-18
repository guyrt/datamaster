
class DMEvents(object):

    FileRead = "FileRead"


class _DMEventHandler(object):
    """Event handler singleton tracks operations across a file."""

    def __init__(self):
        self._events = dict()

    def fire(self, key, value):
        if key not in self._events:
            self._events[key] = list()
        self._events[key].append(value)

    def fire_fileread(self, value):
        self.fire(DMEvents.FileRead, value)

    def get(self, key):
        return self._events.get(key)

    def get_fileread(self):
        return self._events.get(DMEvents.FileRead)


global_event_handler = _DMEventHandler()
