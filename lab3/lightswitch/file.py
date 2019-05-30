# ppds-labs: lightswitch
# Copyright (c) 2019, Milten Plescott. All rights reserved.
# SPDX-License-Identifier: MIT

from ppds import Mutex, Semaphore, Thread
from random import randint
from time import sleep
from lightswitch import Lightswitch

_print = print
print_mutex = Mutex()


def print(*args, **kwargs):
    print_mutex.lock()
    _print(*args, **kwargs)
    print_mutex.unlock()


def lightswitch_test_fnc(lightswitch, semaphore, t_id):
    sleep(randint(2, 10))
    lightswitch.lock_test(semaphore, t_id)
    sleep(randint(2, 10))
    lightswitch.unlock_test(semaphore, t_id)


def main():
    n = 5
    lightswitch = Lightswitch()
    semaphore = Semaphore(1)
    threads = []
    for i in range(n):
        threads.append(Thread(lightswitch_test_fnc, lightswitch, semaphore, i))
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
