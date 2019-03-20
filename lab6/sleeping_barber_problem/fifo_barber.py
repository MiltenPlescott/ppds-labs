# ppds-labs: sleeping_barber_problem
# Copyright (c) 2019, Milten Plescott. All rights reserved.
# SPDX-License-Identifier: MIT

from ppds import Mutex, Semaphore, Thread
from queue import Queue
from random import randint
from time import sleep

_print = print
print_mutex = Mutex()

end_style = "\033[0m"
background_style = "\u001b[40m\u001b[37;1m"


def print(*args, **kwargs):
    print_mutex.lock()
    _print(*args, **kwargs)
    print_mutex.unlock()


class Shared:
    def __init__(self, n):
        self.n = n  # number of chairs in the waiting room
        self.customers_count = 0  # number of customers in the waiting room
        self.customers_cut = 0  # number of customers that received their haircut
        self.mutex = Mutex()  # protects access to the customer_count shared variable
        self.customer = Semaphore(0)  # customer signals that he is ready to get his hair cut
        self.barber_done = Semaphore(0)  # barber signals when the haircut is done
        self.customer_done = Semaphore(0)  # customer signals when he is satisfied with the haircut
        self.queue = Queue()  # for queueing customers; each customer puts his semaphore into this FIFO queue


def customer(shared, barber_semaphore, thread_id, color):
    sleep(randint(1, 100) / 10)
    shared.mutex.lock()
    if shared.customers_count == shared.n:
        shared.mutex.unlock()
        print(color + "{:2d}: It's full! I'm leaving!".format(thread_id) + end_style)
        return
    shared.customers_count += 1
    shared.mutex.unlock()
    print(color + "{:2d}: I just got in and I'm sitting in the waiting room!".format(thread_id) + end_style)
    print(color + "{:2d}: There are {} chair left!".format(thread_id, shared.n - shared.customers_count) + end_style)
    shared.queue.put(barber_semaphore)
    shared.customer.signal()
    print(color + "{:2d}: I'm waiting for the barber to call me in!".format(thread_id) + end_style)
    sleep(randint(1, 10) / 10)
    barber_semaphore.wait()
    shared.mutex.lock()
    shared.customers_count -= 1
    print(color + "{:2d}: Walking in the other room! There are {} chair left!".format(thread_id, shared.n - shared.customers_count) + end_style)
    shared.mutex.unlock()
    print(color + "{:2d}: My hair is being cut!".format(thread_id) + end_style)
    get_hair_cut()
    print(color + "{:2d}: My haircut is finished!".format(thread_id) + end_style)
    shared.customer_done.signal()
    shared.barber_done.wait()
    print(color + "{:2d}: I'm leaving with a new haircut!".format(thread_id) + end_style)


def barber(shared):
    barb = "Barber"
    while True:
        print(background_style + "{}: I'm sleeping!".format(barb) + end_style)
        shared.customer.wait()
        barber_semaphore = shared.queue.get()
        print(background_style + "{}: I'm awake and calling in a new customer!".format(barb) + end_style)
        barber_semaphore.signal()
        print(background_style + "{}: I'm cutting customer's hair!".format(barb) + end_style)
        cut_hair()
        shared.customer_done.wait()
        print(background_style + "{}: The haircut is finished!".format(barb) + end_style)
        shared.barber_done.signal()
        shared.customers_cut += 1
        print(background_style + "{}: I've finished {} haircuts already!".format(barb, shared.customers_cut))


def cut_hair():
    sleep(randint(1, 10) / 10)


def get_hair_cut():
    sleep(randint(1, 10) / 10)


def main():
    n = 5  # number of chairs in the waiting room
    shared = Shared(n)

    colors = []
    for i in range(8):
        colors.append("\u001b[{}m".format(30 + i))
    for i in range(8):
        colors.append("\u001b[{};1m".format(30 + i))

    Thread(barber, shared)
    i = 0
    while True:
        sleep(randint(1, 8) / 10)
        Thread(customer, shared, Semaphore(0), i, colors[i % len(colors)])
        i += 1


if __name__ == '__main__':
    main()
