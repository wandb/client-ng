import logging
import os
import threading

try:
    from tensorflow.python.distribute.cluster_resolver import tpu_cluster_resolver  # type: ignore
    from tensorflow.python.profiler import profiler_client  # type: ignore
except ImportError:
    tpu_cluster_resolver = None
    profiler_client = None
    pass


logger = logging.getLogger(__name__)


class TPUProfiler(object):
    def __init__(
        self,
        service_addr=None,
        tpu=None,
        tpu_zone=None,
        gcp_project=None,
        duration_ms=500,
    ):
        if service_addr:
            if tpu:
                logger.warn(
                    "Both service_addr and tpu arguments provided. "
                    "Ignoring tpu and using service_addr."
                )
        else:
            if not tpu:
                tpu = os.environ["TPU_NAME"]
            try:
                service_addr = tpu_cluster_resolver.TPUClusterResolver(
                    [tpu], zone=tpu_zone, project=gcp_project
                ).get_master()
            except (ValueError, TypeError):
                raise Exception(
                    "Failed to find TPU. Use tpu_zone and gcp_project "
                    "arguments to specify zone and project for your TPU."
                )
        service_addr = service_addr.replace("grpc://", "").replace(":8470", ":8466")
        self.service_addr = service_addr
        self.duration_ms = duration_ms
        self._tpu_utilization = 0.0
        # self._thread = threading.Thread(target=self._thread_body, daemon=True)
        # self._thread.start()

    def _get_tpu_utilization(self):
        # this call blocks for duration_ms milliseconds
        res = profiler_client.monitor(
            self.service_addr, duration_ms=self.duration_ms, level=2
        )
        return float(res.split("Utilization ")[1].split(": ")[1].split("%")[0])

    def _thread_body(self):
        while True:
            try:
                self._tpu_utilization = self._get_tpu_utilization()
            except Exception:
                # Happens when previous profiler session is still active.
                pass

    def get_tpu_utilization(self):
        return self._get_tpu_utilization()
        # return self._tpu_utilization


def is_tpu_available():
    return profiler_client is not None and "TPU_NAME" in os.environ
