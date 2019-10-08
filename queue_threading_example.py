#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
import logging.handlers
import threading
import queue

log_mgr = None
todo_queue = queue.Queue()
done_queue = queue.Queue()


class LogMgr:
    def __init__(self, logpath):
        self.LOG = logging.getLogger('log')
        loghd = logging.handlers.RotatingFileHandler(logpath, "a", 0, 1)
        fmt = logging.Formatter("%(asctime)s %(threadName)-10s %(message)s", "%Y-%m-%d %H:%M:%S")
        loghd.setFormatter(fmt)
        self.LOG.addHandler(loghd)
        self.LOG.setLevel(logging.INFO)

        self.consolelog = logging.StreamHandler()
        self.consolelog.setLevel(logging.DEBUG)
        self.consolelog.setFormatter(fmt)
        self.LOG.addHandler(self.consolelog)

    def info(self, msg):
        if self.LOG is not None:
            self.LOG.info(msg)


class Worker(threading.Thread):
    global log_mgr

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        while True:
            try:
                task = todo_queue.get(False)
                if task:
                    log_mgr.info("HANDLE_TASK: %s" % task)
                    done_queue.put(1)
            except queue.Empty:
                break
        return


def main():
    global log_mgr
    log_mgr = LogMgr("mylog")

    for i in range(30):
        todo_queue.put("data"+str(i))

    workers = []
    for i in range(3):
        w = Worker("worker"+str(i))
        workers.append(w)

    for i in range(3):
        workers[i].start()

    for i in range(3):
        workers[i].join()

    total_num = done_queue.qsize()
    log_mgr.info("TOTAL_HANDLE_TASK: %d" % total_num)
    exit(0)


if __name__ == '__main__':
    main()
