class ReplayBuffer:

    def __init__(self):

        self.buffer = []

    def add(self, transition):

        if transition is not None:
            self.buffer.append(transition)

    def clear(self):

        self.buffer.clear()

    def size(self):

        return len(self.buffer)

    def get_all(self):

        return self.buffer