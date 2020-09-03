import logging
import os

from tensorflow.python.distribute.cluster_resolver import tpu_cluster_resolver
from tensorflow.python.profiler import profiler_client


logger = logging.getLogger(__name__)


class TPUProfiler(object):

    def __init__(self,
                 service_addr=None,
                 tpu=None,
                 tpu_zone=None,
                 gcp_project=None):
        if service_addr:
            if tpu:
                logger.warn("Both service_addr and tpu arguments provided. "
                            "Ignoring tpu and using service_addr.")
        else:
            if not tpu:
                tpu = os.environ['TPU_NAME']
            try:
                service_addr = tpu_cluster_resolver.TPUClusterResolver(
                    [tpu], zone=tpu_zone, project=gcp_project
                ).get_master()
            except(ValueError, TypeError):
                raise Exception("Failed to find TPU. Use tpu_zone and gcp_project "
                                "arguments to specify zone and project for your TPU.")
        service_addr = service_addr.replace('grpc://', '').replace(':8470', ':8466')
        self.service_addr = service_addr

    def get_tpu_utilization(self):
        res = profiler_client.monitor(self.service_addr, duration_ms=500, level=2)
        return float(res.split("Utilization ")[1].split(': ')[1].split('%')[0])


def is_tpu_available():
    return 'TPU_NAME' in os.environ
