# ppds-labs: lightswitch
# Copyright (c) 2019, Milten Plescott. All rights reserved.
# SPDX-License-Identifier: MIT

from ppds import Mutex


class Lightswitch:
    def __init__(self):
        self.count = 0
        self.mutex = Mutex()

    def lock(self, semaphore):
        self.mutex.lock()
        self.count += 1
        if self.count == 1:
            semaphore.wait()
        self.mutex.unlock()

    def unlock(self, semaphore):
        self.mutex.lock()
        self.count -= 1
        if self.count == 0:
            semaphore.signal()
        self.mutex.unlock()

    def lock_test(self, semaphore, t_id):
        self.mutex.lock()
        self.count += 1
        if self.count == 1:
            print("First thread walked in and turned on the light!")
            print("thread_id = {:2d}, number of threads inside = {:2d}\n".format(t_id, self.count))
            semaphore.wait()
        else:
            print("A thread walked in, but there already were some threads inside.")
            print("thread_id = {:2d}, number of threads inside = {:2d}\n".format(t_id, self.count))
        self.mutex.unlock()

    def unlock_test(self, semaphore, t_id):
        self.mutex.lock()
        self.count -= 1
        if self.count == 0:
            print("Last thread walked out and turned off the light!")
            print("thread_id = {:2d}, number of threads inside = {:2d}\n".format(t_id, self.count))
            semaphore.signal()
        else:
            print("A thread walked out, but there are still some threads inside.")
            print("thread_id = {:2d}, number of threads inside = {:2d}\n".format(t_id, self.count))
        self.mutex.unlock()
