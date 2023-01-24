class MessageHandler(object):

    def is_open(self):
        raise NotImplementedError("is_open is not implemented")

    def is_busy(self):
        raise NotImplementedError("is_open is not implemented")

    def open(self):
        raise NotImplementedError("is_open is not implemented")

    def close(self):
        raise NotImplementedError("is_open is not implemented")

    def write(self, command):
        raise NotImplementedError("is_open is not implemented")

    def read(self):
        raise NotImplementedError("is_open is not implemented")
