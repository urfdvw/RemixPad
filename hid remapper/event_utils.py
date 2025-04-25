from collections import deque

class EventQueue:
    def __init__(self):
        self._events = []

    def append(self, given):
        self._events.append(given)

    def get(self):
        if self._events:
            return self._events.pop(0)
        else:
            return None

    def clear(self):
        self._events = []

    def __len__(self):
        return len(self._events)

    def __bool__(self):
        return bool(self._events)
        
class EventDeque:
    def __init__(self):
        self.N = 8
        self._events = deque([], self.N)

    def append(self, given):
        if len(self._events) == self.N:
            self.N *= 2
            self._events = deque(list(self._events), self.N)
        self._events.append(given)

    def get(self):
        if self._events:
            return self._events.popleft()
        else:
            return None

    def clear(self):
        self._events = []

    def __len__(self):
        return len(self._events)

    def __bool__(self):
        return bool(self._events)
    
class TestEventQueue:
    def __init__(self, implementation):
        self.implementation = implementation
    def factory(self, *args, **kwargs):
        return self.implementation( *args, **kwargs)
    def test_operations(self):
        # given
        queue = self.factory()
        # when
        queue.append(1)
        queue.append(2)
        queue.append(3)
        # then
        assert list(queue._events) == [1, 2, 3]
        assert len(queue) == 3
        assert bool(queue)
        assert queue.get() == 1
        assert queue.get() == 2
        # when
        queue.clear()
        # then
        assert list(queue._events) == []
        assert not bool(queue)
    def test_capacity(self):
        N = 100
        queue = self.factory()
        for i in range(N):
            queue.append(i)
        assert len(queue) == N
    def test_get_from_empty_queue(self):
        queue = self.factory()
        assert queue.get() is None
        
        
class ProfileEventQueue:
    def __init__(self, implementation, N):
        self.implementation = implementation
        self.N = N
        
    def factory(self, *args, **kwargs):
        return self.implementation( *args, **kwargs)
        
    def setup_append(self):
        queue = self.factory()
        return queue
        
    def profile_append(self, queue):
        for i in range(self.N):
            queue.append(i)
            
    def setup_get(self):
        queue = self.factory()
        for i in range(self.N):
            queue.append(i)
        return queue
        
    def profile_get(self, queue):
        while True:
            if queue.get() is None:
                break
        
    def profile_append(self, queue):
        for i in range(self.N):
            queue.append(i)

    def setup_append_then_get(self):
        queue = self.factory()
        return queue
        
    def profile_append_then_get(self, queue):
        for i in range(self.N):
            queue.append(i)
            queue.get()