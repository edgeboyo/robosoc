class dist_queue:
    def __init__(self):
        self.q = []
    def add(self, d1, d2, d3):
        if len(self.q) == 3:
            self.q.pop(0)
        self.q.append((d1, d2, d3))
    def get(self, n):
        if n >= 3:
            return (0, 0, 0)
        return self.q[n]
    def getLast(self):
        return self.q[len(self.q)-1]
    def size(self):
        return len(self.q)

