# ppds-labs: dining_philosophers
# Copyright (c) 2019, Milten Plescott. All rights reserved.
# SPDX-License-Identifier: MIT

from ppds import Mutex, Semaphore, Thread
from random import randint
from time import sleep

_print = print
print_mutex = Mutex()

green_style = "\033[32m"
end_style = "\033[0m"


def print(*args, **kwargs):
    print_mutex.lock()
    _print(*args, **kwargs)
    print_mutex.unlock()


class Shared:

    def __init__(self, n, eat_coef):
        self.n = n
        self.eat_coef = eat_coef
        self.forks = [Semaphore(1) for _ in range(n)]

    def get_right(self, i):
        print("Philosopher {:2d} is getting right fork.".format(i))
        self.forks[i].wait()

    def get_left(self, i):
        print("Philosopher {:2d} is getting left fork.".format(i))
        self.forks[(i + 1) % self.n].wait()

    def put_right(self, i):
        print("Philosopher {:2d} is putting right fork.".format(i))
        self.forks[i].signal()

    def put_left(self, i):
        print("Philosopher {:2d} is putting left fork.".format(i))
        self.forks[(i + 1) % self.n].signal()


def dine(shared, eat_coef, philosopher_id):
    sleep(randint(1, 10) / 10)
    while True:
        print("Philosopher {:2d} has no forks.".format(philosopher_id))
        get_forks(shared, philosopher_id)
        print("Philosopher {:2d} has both forks.".format(philosopher_id))
        print(green_style + "Philosopher {:2d} is starting to eat.".format(philosopher_id) + end_style)
        eat(eat_coef)
        print("Philosopher {:2d} has finished eating.".format(philosopher_id))
        put_forks(shared, philosopher_id)


def get_forks(shared, philosopher_id):
    if philosopher_id % 2 == 0:
        shared.get_right(philosopher_id)
        shared.get_left(philosopher_id)
    else:
        shared.get_left(philosopher_id)
        shared.get_right(philosopher_id)


def eat(eat_coef):
    sleep(randint(1, 5) * eat_coef)


def put_forks(shared, philosopher_id):
    shared.put_right(philosopher_id)
    shared.put_left(philosopher_id)


def main():
    n = 5  # n philosophers, n forks
    eat_coef = 1.0
    shared = Shared(n, eat_coef)
    threads = []
    for i in range(n):
        threads.append(Thread(dine, shared, eat_coef, i))
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
