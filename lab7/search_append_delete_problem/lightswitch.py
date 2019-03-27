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
