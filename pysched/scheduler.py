import os
import threading
import tqdm
import multiprocessing as mp
import time
import queue


_QUEUE_COMMAND = queue.Queue()
_MAX_PROCESS = 1
_RLOCK = threading.RLock()
_T = None
_STOP = False
_STOP_IF_EMPTY = True
_NB_EXECUTED = 0


def register_command(cmd, weight=1, priority=1):
    """Priority shall be added with https://docs.python.org/3/library/heapq.html"""
    _QUEUE_COMMAND.put((cmd, weight, priority))

def get_max_processes():
    return _MAX_PROCESS

def set_max_processes(m):
    global _MAX_PROCESS
    _MAX_PROCESS = m

def stop():
    global _STOP
    _STOP = True

def launch():
    global _STOP, _T
    _STOP = False
    _T = tqdm.tqdm()
    for p in range(_MAX_PROCESS):
        thr = threading.Thread(target=_thread)
        thr.start()

def _thread():
    global _NB_EXECUTED, _T, _STOP, _STOP_IF_EMPTY
    while True:
        with _RLOCK:
            try:
                res = _QUEUE_COMMAND.get_nowait()
            except queue.Empty:
                res = None
                if _STOP_IF_EMPTY:
                    _STOP = True
            except:
                res = None
        if res is not None:
            cmd, weight, priority = res
            p = mp.Process(target=_process, args=(cmd,))
            p.start()
            p.join()
            _NB_EXECUTED += 1
            _T.update(weight)
            # print(f"{_NB_EXECUTED} were executed")
        if _STOP:
            return
        time.sleep(0.01)

def _process(cmd):
    os.system(cmd)
