from ppds import *


class Shared:

    counter = 0

    def __init__(self, end):
        self.end = end
        self.elms = [0] * end

    def print_list(self):
        print(self.elms)

    def print_histogram(self):
        for i in set(self.elms):
            count = self.elms.count(i)
            print("\t{} - {}".format(i, count))


def fnc_1(shared):
    while True:
        if shared.counter >= shared.end:
            break
        try:
            shared.elms[shared.counter] += 1
            shared.counter += 1
        except IndexError:
            print("IndexError on index: {}".format(shared.counter))


def fnc_2(shared, mutex):
    t_count = 0
    mutex.wait()
    while True:
        if shared.counter >= shared.end:
            break
        try:
            shared.elms[shared.counter] += 1
            shared.counter += 1
            t_count += 1
        except IndexError:
            print("IndexError on index: {}".format(shared.counter))
    mutex.signal()
    print("Thread ID {:5d} count: {} - {:.2f}%".format(threading.get_ident(), t_count, 100 * t_count / shared.end))


def fnc_3(shared, mutex):
    t_count = 0
    while True:
        mutex.wait()
        if shared.counter >= shared.end:
            mutex.signal()
            break
        try:
            shared.elms[shared.counter] += 1
            shared.counter += 1
            t_count += 1
        except IndexError:
            print("IndexError on index: {}".format(shared.counter))
            mutex.signal()
        mutex.signal()
    print("Thread ID {:5d} count: {} - {:.2f}%".format(threading.get_ident(), t_count, 100*t_count/shared.end))


def test(fnc_x, array_size, n_threads, use_mutex):
    foo = Shared(array_size)
    mutex = Semaphore()
    threads = []
    if use_mutex:
        for i in range(n_threads):
            threads.append(Thread(fnc_x, foo, mutex))
    else:
        for i in range(n_threads):
            threads.append(Thread(fnc_x, foo))
    for i in range(n_threads):
        threads[i].join()
    print("Histogram:")
    foo.print_histogram()
    print()


def main():
    test(fnc_x=fnc_1, array_size=1000000, n_threads=4, use_mutex=False)
    test(fnc_x=fnc_2, array_size=1000000, n_threads=4, use_mutex=True)
    test(fnc_x=fnc_3, array_size=1000000, n_threads=4, use_mutex=True)


if __name__ == '__main__':
    main()
