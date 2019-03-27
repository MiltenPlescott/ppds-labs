# ppds-labs: search_append_delete_problem
# Copyright (c) 2019, Milten Plescott. All rights reserved.
# SPDX-License-Identifier: MIT

from lightswitch import Lightswitch
from ppds import Mutex, Semaphore, Thread
from random import randint
from time import sleep

_print = print
print_mutex = Mutex()

op_time = 1 / 1000  # sleep time of O(1) operation

red = "\u001b[31m"
green = "\u001b[33m"
blue = "\u001b[34m"
end_style = "\033[0m"


def print(*args, **kwargs):
    print_mutex.lock()
    _print(*args, **kwargs)
    print_mutex.unlock()


class Shared:
    def __init__(self, list_size):
        self.list_size = list_size  # number of items in the singly linked list
        self.append_mutex = Mutex()
        self.no_search = Semaphore(1)
        self.no_append = Semaphore(1)
        self.search_LS = Lightswitch()
        self.append_LS = Lightswitch()


# search for an item at any position in the list
# multiple threads can search concurrently
def searcher(shared, searcher_id, color):
    while True:
        sleep(randint(1, 50) / 10)
        shared.search_LS.lock(shared.no_search)
        print(color + "Searcher " + str(searcher_id) + " searching." + end_style)
        search(randint(1, shared.list_size))  # search for random item
        print(color + "Searcher " + str(searcher_id) + " finished searching." + end_style)
        shared.search_LS.unlock(shared.no_search)


# append at the end of the list
# only one thread can append at a time
# can be run concurrently with searching threads
def appender(shared, appender_id, color):
    while True:
        sleep(randint(1, 50) / 10)
        shared.append_LS.lock(shared.no_append)
        shared.append_mutex.lock()
        print(color + "Appender " + str(appender_id) + " appending." + end_style)
        append(shared.list_size)  # append an item at the end of the list
        print(color + "Appender " + str(appender_id) + " finished appending." + end_style)
        shared.append_mutex.unlock()
        shared.append_LS.unlock(shared.no_append)


# delete an item at position
# deleter thread can delete an item from the list only when there are no
# searching or appending threads accessing the list
def deleter(shared, deleter_id, color):
    while True:
        sleep(randint(1, 50) / 10)
        shared.no_search.wait()
        shared.no_append.wait()
        print(color + "Deleter  " + str(deleter_id) + " deleting." + end_style)
        delete(randint(1, shared.list_size))  # delete random item
        print(color + "Deleter  " + str(deleter_id) + " finished deleting." + end_style)
        shared.no_append.signal()
        shared.no_search.signal()


# simulate list searching time
def search(pos):
    sleep(pos * op_time)


# simulate list appending time
def append(pos):
    randomness_coef = randint(-1, 1) / 10  # introduce some randomness to simulate the changing of the list length
    sleep(pos * op_time + randomness_coef)


# simulate list deleting time
def delete(pos):
    sleep(pos * op_time)


def main():
    n = 5  # number of threads of the searching and appending type
    list_size = 500  # number of items the list
    shared = Shared(list_size)

    threads = []
    for i in range(n):
        threads.append(Thread(searcher, shared, i, blue))
        threads.append(Thread(appender, shared, i, green))
    threads.append(Thread(deleter, shared, 0, red))  # single deleter thread

    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
