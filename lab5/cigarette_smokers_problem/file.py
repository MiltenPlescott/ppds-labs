# ppds-labs: cigarette_smokers_problem
# Copyright (c) 2019, Milten Plescott. All rights reserved.
# SPDX-License-Identifier: MIT

from ppds import Mutex, Semaphore, Thread
from random import randint
from time import sleep

_print = print
print_mutex = Mutex()


def print(*args, **kwargs):
    print_mutex.lock()
    _print(*args, **kwargs)
    print_mutex.unlock()


class Shared:
    def __init__(self):
        self.agent = Semaphore(1)
        self.tabacco = Semaphore(0)
        self.paper = Semaphore(0)
        self.match = Semaphore(0)


def agent_tabacco(shared):
    while True:
        sleep(randint(1, 10) / 10)
        shared.agent.wait()
        shared.paper.signal()
        shared.match.signal()


def agent_paper(shared):
    while True:
        sleep(randint(1, 10) / 10)
        shared.agent.wait()
        shared.tabacco.signal()
        shared.match.signal()


def agent_match(shared):
    while True:
        sleep(randint(1, 10) / 10)
        shared.agent.wait()
        shared.paper.signal()
        shared.tabacco.signal()


def smoker_tabacco(shared):
    while True:
        sleep(randint(1, 10) / 10)
        shared.paper.wait()
        shared.match.wait()
        print("Smoker without tabacco smoking.")
        shared.agent.signal()


def smoker_paper(shared):
    while True:
        sleep(randint(1, 10) / 10)
        shared.tabacco.wait()
        shared.match.wait()
        print("Smoker without paper smoking.")
        shared.agent.signal()


def smoker_match(shared):
    while True:
        sleep(randint(1, 10) / 10)
        shared.paper.wait()
        shared.tabacco.wait()
        print("Smoker without match smoking.")
        shared.agent.signal()


def main():

    # DEADLOCK

    shared = Shared()
    agents = []
    agents.append(Thread(agent_tabacco, shared))
    agents.append(Thread(agent_paper, shared))
    agents.append(Thread(agent_match, shared))

    smokers = []
    smokers.append(Thread(smoker_tabacco, shared))
    smokers.append(Thread(smoker_paper, shared))
    smokers.append(Thread(smoker_match, shared))

    for t in agents + smokers:
        t.join()


if __name__ == '__main__':
    main()
