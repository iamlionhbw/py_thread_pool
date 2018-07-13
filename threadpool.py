# -*- coding:utf-8 -*-

import concurrent.futures
import threading
import uuid
import functools
from multiprocessing import cpu_count


def hook_user_func(user_func):

    @functools.wraps(user_func)
    def actual_user_func(tp_instance, uid, *args, **kwargs):
        tp_instance.put_to_work()
        ret = user_func(*args, **kwargs)
        if not tp_instance.keep_task_history:
            del tp_instance.task_dict[uid]
        tp_instance.finish_work()
        return ret
    return actual_user_func


class ThreadPool(object):

    def __init__(self, thread_counts=None, keep_task_history=True, mul_times=1):
        # Pay attention to the param:keep_task_history
        # You can set it to False which means that
        # the thread pool would drop the task when the it is finished.
        # But, if the keep_task_history is False,
        # the result() method and all the methods which starts with the prefix:is_task_* would
        # make no sense, and invoke them would just get the False as the return value, but
        # keep in mind that the False has no meaning.

        super().__init__()

        tc = thread_counts if thread_counts is not None else cpu_count()
        tc *= mul_times
        tc = tc if tc <= cpu_count() * 2 else cpu_count() * 2

        self._worker_thread_count = tc
        self._idle_count = self._worker_thread_count
        self._busy_count = 0
        self._count_lock = threading.Lock()

        self._tpExecutor = concurrent.futures.ThreadPoolExecutor(self._worker_thread_count)
        self.task_dict = {}

        self.keep_task_history = keep_task_history

    @property
    def idle_count(self):
        return self._idle_count

    @property
    def busy_count(self):
        return self._busy_count

    def put_to_work(self):
        self._count_lock.acquire()
        self._idle_count -= 1
        self._busy_count += 1
        self._count_lock.release()

    def finish_work(self):
        self._count_lock.acquire()
        self._idle_count += 1
        self._busy_count -= 1
        self._count_lock.release()

    def submit_task(self, func, *args, **kwargs):
        uid = uuid.uuid1()
        hk_func = hook_user_func(func)
        self.task_dict[uid] = self._tpExecutor.submit(hk_func, self, uid, *args, **kwargs)
        return uid

    def cancel_task(self, UUID):
        # return True if the task is cancelled successfully, otherwise False
        if UUID not in self.task_dict:
            return False
        _flg = self.task_dict[UUID].cancel()
        if _flg and not self.keep_task_history:
            del self.task_dict[UUID]
        return _flg

    def result(self, UUID, timeout=None):
        # force to get the result, but maybe return an exception
        if not self.keep_task_history and UUID not in self.task_dict:
            return False
        try:
            ret = self.task_dict[UUID].result()
        except Exception as e:
            ret = e
        return ret

    def is_task_finished(self, UUID):
        if not self.keep_task_history and UUID not in self.task_dict:
            return False
        return self.task_dict[UUID].done() and not self.task_dict[UUID].cancelled()

    def is_task_running(self, UUID):
        if not self.keep_task_history and UUID not in self.task_dict:
            return False
        return self.task_dict[UUID].running()

    def is_task_pending(self, UUID):
        if not self.keep_task_history and UUID not in self.task_dict:
            return False
        return not (self.task_dict[UUID].done() or self.task_dict[UUID].cancelled() or self.task_dict[UUID].running())

    def is_task_cancelled(self, UUID):
        if not self.keep_task_history and UUID not in self.task_dict:
            return False
        return self.task_dict[UUID].cancelled()
