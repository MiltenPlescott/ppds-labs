# ppds-labs: barrier
# Copyright (c) 2019, Milten Plescott. All rights reserved.
# SPDX-License-Identifier: MIT

from ppds import Event, Mutex, Semaphore, Thread
from random import randint
import threading
from time import sleep

_print = print
print_mutex = Mutex()


def print(*args, **kwargs):
    print_mutex.lock()
    _print(*args, **kwargs)
    print_mutex.unlock()


def rendezvous(thread_id):
    sleep(randint(1, 10) / 10)
    print("rendezvous: {:2d}".format(thread_id))


def ko(thread_id):
    print("ko: {:2d}".format(thread_id))
    sleep(randint(1, 10) / 10)


class SimpleBarrier:
    """
    ADT, use only barrier()
    """

    def __init__(self, n):
        self.n = n
        self.count = 0
        self.mutex = Mutex()
        self.turnstile = Semaphore(0)

    def barrier(self):
        self.mutex.lock()
        self.count += 1
        if self.count == self.n:
            self.count = 0
            self.turnstile.signal(self.n)
        self.mutex.unlock()
        self.turnstile.wait()


class EventBarrier:
    """
    ADT, use only barrier()
    """

    def __init__(self, n):
        self.n = n
        self.count = 0
        self.mutex = Mutex()
        self.event = Event()

    def barrier(self):
        self.mutex.lock()
        self.count += 1
        if self.count == self.n:
            self.event.signal()
        self.mutex.unlock()
        self.event.wait()

        self.mutex.lock()
        self.count -= 1
        if self.count == 0:
            self.event.clear()
        self.mutex.unlock()


class EventBarrierOptimized:
    """
    ADT, use only barrier()
    """

    def __init__(self, n):
        self.n = n
        self.count = 0
        self.mutex = Mutex()
        self.event = Event()

    def barrier(self):
        self.mutex.lock()
        if self.count == 0:
            self.event.clear()
        self.count += 1
        if self.count == self.n:
            self.count = 0
            self.event.signal()
        self.mutex.unlock()
        self.event.wait()


class ReusableBarrier:
    """
    initialized semaphores, manual usage
    """

    def __init__(self, n):
        self.n = n
        self.count = 0
        self.mutex = Mutex()
        self.turnstile1 = Semaphore(0)
        self.turnstile2 = Semaphore(1)


class PreloadedReusableBarrier:
    """
    initialized semaphores, manual usage
    """

    def __init__(self, n):
        self.n = n
        self.count = 0
        self.mutex = Mutex()
        self.turnstile1 = Semaphore(0)
        self.turnstile2 = Semaphore(0)


def ADT_barrier_example(t_id, barrier):
    sleep(randint(1, 10) / 10)
    print("thread {:2d} before barrier".format(t_id))
    barrier.barrier()
    print("thread {:2d} after barrier".format(t_id))


def reusable_manual_barrier_example(t_id, barrier):
    while True:
        rendezvous(t_id)

        barrier.mutex.lock()
        barrier.count += 1
        if barrier.count == barrier.n:
            barrier.turnstile2.wait()
            barrier.turnstile1.signal()
        barrier.mutex.unlock()
        barrier.turnstile1.wait()
        barrier.turnstile1.signal()

        ko(t_id)

        barrier.mutex.lock()
        barrier.count -= 1
        if barrier.count == 0:
            barrier.turnstile1.wait()
            barrier.turnstile2.signal()
        barrier.mutex.unlock()
        barrier.turnstile2.wait()
        barrier.turnstile2.signal()


def preloaded_reusable_manual_barrier_example(barrier):
    while True:
        rendezvous(threading.get_ident())

        barrier.mutex.lock()
        barrier.count += 1
        if barrier.count == barrier.n:
            barrier.turnstile1.signal(barrier.n)
        barrier.mutex.unlock()
        barrier.turnstile1.wait()

        ko(threading.get_ident())

        barrier.mutex.lock()
        barrier.count -= 1
        if barrier.count == 0:
            barrier.turnstile2.signal(barrier.n)
        barrier.mutex.unlock()
        barrier.turnstile2.wait()


def reusable_ADT_barrier_example(t_id, barrier1, barrier2):
    while True:
        rendezvous(t_id)
        barrier1.barrier()
        ko(t_id)
        barrier2.barrier()


def main():
    n = 10
    print("\nADT SIMPLE BARRIER\n")
    sb = SimpleBarrier(n)
    threads = []
    for i in range(n):
        threads.append(Thread(ADT_barrier_example, i, sb))
    for t in threads:
        t.join()

    print("\nADT EVENT BARRIER\n")
    eb = EventBarrier(n)
    threads = []
    for i in range(n):
        threads.append(Thread(ADT_barrier_example, i, eb))
    for t in threads:
        t.join()

    print("\nADT EVENT BARRIER\n")
    eb = EventBarrierOptimized(n)
    threads = []
    for i in range(n):
        threads.append(Thread(ADT_barrier_example, i, eb))
    for t in threads:
        t.join()

    print("\nREUSABLE BARRIER\n")
    # rb = ReusableBarrier(n)
    # threads = []
    # for i in range(n):
    #     threads.append(Thread(reusable_manual_barrier_example, i, rb))
    # for t in threads:
    #     t.join()

    print("\nPRELOADED REUSABLE BARRIER\n")
    # prb = PreloadedReusableBarrier(n)
    # threads = []
    # for i in range(n):
    #     threads.append(Thread(preloaded_reusable_manual_barrier_example, i, prb))
    # for t in threads:
    #     t.join()

    print("\nREUSABLE BARRIER using ADT SIMPLE BARRIER implemented using SEMAPHORES\n")
    # rsb1 = SimpleBarrier(n)
    # rsb2 = SimpleBarrier(n)
    # threads = []
    # for i in range(n):
    #     threads.append(Thread(reusable_ADT_barrier_example, i, rsb1, rsb2))
    # for t in threads:
    #     t.join()

    print("\nREUSABLE BARRIER using ADT EVENT BARRIER implemented using EVENTS\n")
    # reb1 = EventBarrier(n)
    # reb2 = EventBarrier(n)
    # threads = []
    # for i in range(n):
    #     threads.append(Thread(reusable_ADT_barrier_example, i, reb1, reb2))
    # for t in threads:
    #     t.join()

    print("\nREUSABLE BARRIER using ADT EVENT BARRIER implemented using EVENTS optimized\n")
    # reb1 = EventBarrierOptimized(n)
    # reb2 = EventBarrierOptimized(n)
    # threads = []
    # for i in range(n):
    #     threads.append(Thread(reusable_ADT_barrier_example, i, reb1, reb2))
    # for t in threads:
    #     t.join()


if __name__ == '__main__':
    main()
