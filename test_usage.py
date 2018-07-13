# -*- coding:utf-8 -*-

import threading
import time
from threadpool import ThreadPool


def thread_func(iden):
    c = 5
    while c:
        print("This is from", iden, threading.current_thread().ident)
        c -= 1
        time.sleep(1)
    return iden


if __name__ == '__main__':

    tp = ThreadPool(2)
    auid = tp.submit_task(thread_func, "A")
    buid = tp.submit_task(thread_func, "B")
    cuid = tp.submit_task(thread_func, "C")
    duid = tp.submit_task(thread_func, "D")
    time.sleep(2)
    f = tp.cancel_task(duid)
    print(f)
    time.sleep(4)
    print("----------a---------------")
    print(tp.is_task_cancelled(auid))
    print(tp.is_task_finished(auid))
    print(tp.is_task_pending(auid))
    print(tp.is_task_running(auid))
    print("----------b---------------")
    print(tp.is_task_cancelled(buid))
    print(tp.is_task_finished(buid))
    print(tp.is_task_pending(buid))
    print(tp.is_task_running(buid))
    print("----------c---------------")
    print(tp.is_task_cancelled(cuid))
    print(tp.is_task_finished(cuid))
    print(tp.is_task_pending(cuid))
    print(tp.is_task_running(cuid))
    print("----------d---------------")
    print(tp.is_task_cancelled(duid))
    print(tp.is_task_finished(duid))
    print(tp.is_task_pending(duid))
    print(tp.is_task_running(duid))
