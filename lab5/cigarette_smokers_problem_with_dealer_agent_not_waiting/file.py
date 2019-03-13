# ppds-labs: cigarette_smokers_problem_with_dealer_agent_not_waiting
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
    def __init__(self):
        self.mutex = Mutex()

        # signal smoker that he can smoke
        self.smoker_tobacco = Semaphore(0)
        self.smoker_paper = Semaphore(0)
        self.smoker_match = Semaphore(0)

        # signal dealer that he can deal
        self.dealer_tobacco = Semaphore(0)
        self.dealer_paper = Semaphore(0)
        self.dealer_match = Semaphore(0)

        self.is_tobacco = 0
        self.is_paper = 0
        self.is_match = 0

    def print_materials_state(self):
        print("Tobacco: {}, Paper: {}, Match: {}.".format(self.is_tobacco, self.is_paper, self.is_match))


def smoke():
    sleep(randint(1, 10) / 10)


def agent_tobacco(shared):
    while True:
        sleep(randint(1, 5) / 10)
        print("Agent without tobacco signaling paper and match dealers.")
        shared.dealer_paper.signal()
        shared.dealer_match.signal()


def agent_paper(shared):
    while True:
        sleep(randint(1, 5) / 10)
        print("Agent without papers signaling tobacco and match dealers.")
        shared.dealer_tobacco.signal()
        shared.dealer_match.signal()


def agent_match(shared):
    while True:
        sleep(randint(1, 5) / 10)
        print("Agent without matches signaling tobacco and paper dealers.")
        shared.dealer_tobacco.signal()
        shared.dealer_paper.signal()


def dealer_tobacco(shared):
    while True:
        shared.dealer_tobacco.wait()
        shared.mutex.lock()
        print("Tobacco dealer recieved material.")
        shared.print_materials_state()
        if shared.is_paper:
            shared.is_paper -= 1
            print("Tobacco dealer signaling smoker without match to smoke.")
            shared.smoker_match.signal()
        elif shared.is_match:
            shared.is_match -= 1
            print("Tobacco dealer signaling smoker without paper to smoke.")
            shared.smoker_paper.signal()
        else:
            shared.is_tobacco += 1
        shared.mutex.unlock()


def dealer_paper(shared):
    while True:
        shared.dealer_paper.wait()
        shared.mutex.lock()
        print("Paper dealer recieved material.")
        shared.print_materials_state()
        if shared.is_tobacco:
            shared.is_tobacco -= 1
            print("Paper dealer signaling smoker without match to smoke.")
            shared.smoker_match.signal()
        elif shared.is_match:
            shared.is_match -= 1
            print("Paper dealer signaling smoker without tobacco to smoke.")
            shared.smoker_tobacco.signal()
        else:
            shared.is_paper += 1
        shared.mutex.unlock()


def dealer_match(shared):
    while True:
        shared.dealer_match.wait()
        shared.mutex.lock()
        print("Match dealer recieved material.")
        shared.print_materials_state()
        if shared.is_tobacco:
            shared.is_tobacco -= 1
            print("Match dealer signaling smoker without paper to smoke.")
            shared.smoker_paper.signal()
        elif shared.is_paper:
            shared.is_paper -= 1
            print("Match dealer signaling smoker without tobacco to smoke.")
            shared.smoker_tobacco.signal()
        else:
            shared.is_match += 1
        shared.mutex.unlock()


def smoker_tobacco(shared):
    while True:
        sleep(randint(1, 10) / 10)
        shared.smoker_tobacco.wait()
        print(green_style + "Smoker without tobacco smoking." + end_style)
        smoke()


def smoker_paper(shared):
    while True:
        sleep(randint(1, 10) / 10)
        shared.smoker_paper.wait()
        print(green_style + "Smoker without paper smoking." + end_style)
        smoke()


def smoker_match(shared):
    while True:
        sleep(randint(1, 10) / 10)
        shared.smoker_match.wait()
        print(green_style + "Smoker without match smoking." + end_style)
        smoke()


def main():
    shared = Shared()
    agents = []
    agents.append(Thread(agent_tobacco, shared))
    agents.append(Thread(agent_paper, shared))
    agents.append(Thread(agent_match, shared))

    dealers = []
    dealers.append(Thread(dealer_tobacco, shared))
    dealers.append(Thread(dealer_paper, shared))
    dealers.append(Thread(dealer_match, shared))

    smokers = []
    smokers.append(Thread(smoker_tobacco, shared))
    smokers.append(Thread(smoker_paper, shared))
    smokers.append(Thread(smoker_match, shared))

    for t in agents + dealers + smokers:
        t.join()


if __name__ == '__main__':
    main()
