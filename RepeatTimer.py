from MacsOpener import MacsOpener
from MacOpener import MacOpener
from MacStore import *
import sys
import sched, time
from threading import Timer, Thread, Event


# class RepeatTimer:
#     def __init__(self, action, interval):
#         self.interval = interval
#         self.action = action
#         self.timer = Timer(interval, self.start)
#
#     def start(self):
#         self.timer = Timer(self.interval, self.start)
#         self.timer.start()
#         self.action.do()
#
#     def cancel(self):
#         self.timer.cancel()


class RepeatTimer(Thread):
    """Call a function after a specified number of seconds:

            t = Timer(30.0, f, args=None, kwargs=None)
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting

    """

    def __init__(self, interval, function, delay=None, args=None, kwargs=None):
        Thread.__init__(self)
        self.delay = delay
        if delay is None:
            self.delay = interval
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def _wait_and_do(self, interval):
        self.finished.wait(interval)
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)

    def run(self):
        self._wait_and_do(self.delay)
        while not self.finished.is_set():
            self._wait_and_do(self.interval)


def _debug():
    print(sys.argv)
    action = MacsOpener(MacStoreByCsv(), MacOpener(local_ip='10.21.124.111'))
    # timer = RepeatTimer(action, 2)
    timer = RepeatTimer(2, action.do, 0.0)
    print('sched start', time.time())
    timer.start()
    time.sleep(3)
    timer.cancel()
    print('sched end', time.time())


if __name__ == '__main__':
    _debug()
