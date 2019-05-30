# ppds-labs: readers_writers
# Copyright (c) 2019, Milten Plescott. All rights reserved.
# SPDX-License-Identifier: MIT


from ppds import Mutex, Semaphore, Thread
from random import randint
from time import sleep
from lightswitch import Lightswitch

_print = print
print_mutex = Mutex()

green_style = "\u001b[33m"
red_style = "\u001b[31m"
end_style = "\033[0m"


def print(*args, **kwargs):
    print_mutex.lock()
    _print(*args, **kwargs)
    print_mutex.unlock()


readers = 10  # number of readers
writers = 10  # number of writers
pause_lo = 1  # pause between two reading/writing sessions is a random number
pause_hi = 10  # from <pause_lo,pause_hi> interval
read_lo = 1  # reading time is a random number
read_hi = 10  # from <read_lo,read_hi> interval
write_lo = 1  # writing time is a random number
write_hi = 10  # from <write_lo,write_hi> interval


def set_globals(r, w, p_lo, p_hi, r_lo, r_hi, w_lo, w_hi):
    global readers
    global writers
    global pause_lo
    global pause_hi
    global read_lo
    global read_hi
    global write_lo
    global write_hi
    readers = r
    writers = w
    pause_lo = p_lo
    pause_hi = p_hi
    read_lo = r_lo
    read_hi = r_hi
    write_lo = w_lo
    write_hi = w_hi


def pause():
    sleep(randint(pause_lo, pause_hi))


def read():
    sleep(randint(read_lo, read_hi))


def write():
    sleep(randint(write_lo, write_hi))


##################
#     TEST 1     #
##################


def test1():
    set_globals(r=10, w=10, p_lo=1, p_hi=10, r_lo=1, r_hi=10, w_lo=1, w_hi=10)
    shared = Shared1()
    reader_threads = []
    for i in range(readers):
        reader_threads.append(Thread(test1_reader, shared, i))

    writer_threads = []
    for i in range(writers):
        writer_threads.append(Thread(test1_writer, shared, i))

    for t in reader_threads + writer_threads:
        t.join()


class Shared1:
    def __init__(self):
        self.readLS = Lightswitch()
        self.roomEmpty = Semaphore(1)


def test1_reader(shared, t_id):
    while True:
        pause()
        shared.readLS.lock(shared.roomEmpty)
        print("Thread {:2d} starting to ".format(t_id) + green_style + "read" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))
        read()
        shared.readLS.unlock(shared.roomEmpty)
        print("Thread {:2d} finished ".format(t_id) + green_style + "reading" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))


def test1_writer(shared, t_id):
    while True:
        pause()
        shared.roomEmpty.wait()
        print("Thread {:2d} starting to ".format(t_id) + red_style + "write" + end_style
              + ", single writer inside.".format(shared.readLS.count))
        write()
        shared.roomEmpty.signal()
        print("Thread {:2d} finished ".format(t_id) + red_style + "writing" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))


##################
#     TEST 2     #
##################


def test2():
    set_globals(r=10, w=10, p_lo=1, p_hi=10, r_lo=1, r_hi=10, w_lo=1, w_hi=10)
    shared = Shared2()
    reader_threads = []
    for i in range(readers):
        reader_threads.append(Thread(test2_reader, shared, i))

    writer_threads = []
    for i in range(writers):
        writer_threads.append(Thread(test2_writer, shared, i))

    for t in reader_threads + writer_threads:
        t.join()


class Shared2:
    def __init__(self):
        self.readLS = Lightswitch()
        self.roomEmpty = Semaphore(1)
        self.turnstile = Semaphore(1)


def test2_reader(shared, t_id):
    while True:
        pause()
        shared.turnstile.wait()
        shared.turnstile.signal()
        shared.readLS.lock(shared.roomEmpty)
        print("Thread {:2d} starting to ".format(t_id) + green_style + "read" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))
        read()
        shared.readLS.unlock(shared.roomEmpty)
        print("Thread {:2d} finished ".format(t_id) + green_style + "reading" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))


def test2_writer(shared, t_id):
    while True:
        pause()
        shared.turnstile.wait()
        shared.roomEmpty.wait()
        print("Thread {:2d} starting to ".format(t_id) + red_style + "write" + end_style
              + ", single writer inside.".format(shared.readLS.count))
        write()
        shared.roomEmpty.signal()
        shared.turnstile.signal()
        print("Thread {:2d} finished ".format(t_id) + red_style + "writing" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))


##################
#     TEST 3     #
##################


def test3():
    set_globals(r=10, w=10, p_lo=1, p_hi=10, r_lo=1, r_hi=10, w_lo=1, w_hi=10)
    shared = Shared3()
    reader_threads = []
    for i in range(readers):
        reader_threads.append(Thread(test3_reader, shared, i))

    writer_threads = []
    for i in range(writers):
        writer_threads.append(Thread(test3_writer, shared, i))

    for t in reader_threads + writer_threads:
        t.join()


class Shared3:
    def __init__(self):
        self.readLS = Lightswitch()
        self.noWriters = Semaphore(1)
        self.noReaders = Semaphore(1)


def test3_reader(shared, t_id):
    while True:
        pause()
        shared.noReaders.wait()
        shared.noReaders.signal()
        shared.readLS.lock(shared.noWriters)
        print("Thread {:2d} starting to ".format(t_id) + green_style + "read" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))
        read()
        shared.readLS.unlock(shared.noWriters)
        print("Thread {:2d} finished ".format(t_id) + green_style + "reading" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))


def test3_writer(shared, t_id):
    while True:
        pause()
        shared.noReaders.wait()
        shared.noWriters.wait()
        print("Thread {:2d} starting to ".format(t_id) + red_style + "write" + end_style
              + ", single writer inside.".format(shared.readLS.count))
        write()
        shared.noWriters.signal()
        shared.noReaders.signal()
        print("Thread {:2d} finished ".format(t_id) + red_style + "writing" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))


##################
#     TEST 4     #
##################


def test4():
    set_globals(r=10, w=10, p_lo=1, p_hi=10, r_lo=1, r_hi=10, w_lo=1, w_hi=10)
    shared = Shared4()
    reader_threads = []
    for i in range(readers):
        reader_threads.append(Thread(test4_reader, shared, i))

    writer_threads = []
    for i in range(writers):
        writer_threads.append(Thread(test4_writer, shared, i))

    for t in reader_threads + writer_threads:
        t.join()


class Shared4:
    def __init__(self):
        self.readLS = Lightswitch()
        self.writeLS = Lightswitch()
        self.noWriters = Semaphore(1)
        self.noReaders = Semaphore(1)


def test4_reader(shared, t_id):
    while True:
        pause()
        shared.noReaders.wait()
        shared.noReaders.signal()
        shared.readLS.lock(shared.noWriters)
        print("Thread {:2d} starting to ".format(t_id) + green_style + "read" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))
        read()
        shared.readLS.unlock(shared.noWriters)
        print("Thread {:2d} finished ".format(t_id) + green_style + "reading" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))


def test4_writer(shared, t_id):
    while True:
        pause()
        shared.writeLS.lock(shared.noReaders)
        shared.noWriters.wait()
        print("Thread {:2d} starting to ".format(t_id) + red_style + "write" + end_style
              + ", single writer inside.".format(shared.readLS.count))
        write()
        shared.noWriters.signal()
        shared.writeLS.unlock(shared.noReaders)
        print("Thread {:2d} finished ".format(t_id) + red_style + "writing" + end_style
              + ", {:2d} threads inside.".format(shared.readLS.count))


def main():
    # test1()  # readers priority;  writers starvation
    # test2()  # writers blocking turnstile
    # test3()  # writers priority, but FIFO queue
    test4()  # FIFO queue fixed using second lightswitch;  readers starvation


if __name__ == '__main__':
    main()
