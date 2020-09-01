import logging
import os
from subprocess import PIPE, Popen, STDOUT
import threading
import time


logger = logging.getLogger(__name__)


class TPUProfiler(object):

    def __init__(self, duration_ms=1000):
        try:
            import cloud_tpu_profiler
            del cloud_tpu_profiler  # flake8
            self._enabled = True
        except ImportError:
            logger.warn("cloud_tpu_profiler is not installed. "
                        "TPU stats will not be captured.")
            self._enabled = False
            return
        self._tpu_utilization = 0.
        self._time = time.time()
        self._running = False
        self.duration_ms = duration_ms

    def start(self):
        if not self._enabled or self._running:
            return
        self._running = True
        self._start_capture_process()
        self._stop_thread = False
        self._thread = threading.Thread(target=self._thread_body)
        self._thread.start()

    def _start_capture_process(self):
        args = ["capture_tpu_profile",
                "--tpu=" + os.environ['TPU_NAME'],
                "--num_queries=100000",
                "--duration_ms=" + str(self.duration_ms),
                "--monitoring_level=2"]
        self._capture_process = Popen(args,
                                      stdout=PIPE,
                                      stderr=STDOUT,
                                      universal_newlines=True)

    def _is_capture_process_alive(self):
        return self._capture_process.poll() is None

    def _kill_capture_process(self):
        try:
            self._capture_process.kill()
        except Exception:
            pass

    def _readline(self):
        if not self._is_capture_process_alive():
            self._start_capture_process()
        line = self._capture_process.stdout.readline()
        return line

    def _thread_body(self):
        while not self._stop_thread:
            line = self._readline()
            if line.strip().startswith("Utilization "):
                self._tpu_utilization = float(line.split(': ')[1].split('%')[0])
                self._time = time.time()
            time.sleep(0.5)

    def get_tpu_utilization(self):
        if self._enabled:
            return self._tpu_utilization
        return 0.

    def stop(self):
        if self._enabled and self._running:
            self._stop_thread = True
            self._thread.join()
            self._kill_capture_process()
            self._running = False

    def is_enabled(self):
        return self._enabled

    def is_running(self):
        return self._running


def is_tpu_available():
    return 'TPU_NAME' in os.environ
