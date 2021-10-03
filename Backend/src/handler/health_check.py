import psutil
import nvidia_smi

from src.service.response import *
from src.const import *


def cpu_check(log):
    try:
        processor = {'physicals': psutil.cpu_count(False), 'logicals': psutil.cpu_count(True),
                    'usage': psutil.cpu_percent(), 'usages': psutil.cpu_percent(percpu=True)}
        memory = psutil.virtual_memory()._asdict()
        memory = {'total': memory['total'], 'available': memory['available'],
                'used': memory['used'], 'free': memory['free'], 'percent': memory['percent']}
        storage = psutil.disk_usage(ROOT)._asdict()
        storage = {'total': storage['total'], 'used': storage['used'],
                'free': storage['free'], 'percent': storage['percent']}
        data = {'processor': processor, 'memory': memory, 'storage': storage}
        return DataReponse(message= 'Success!',data=data,code = CODE_DONE)
    except Exception as e:
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def gpu_check(log):
    try:
        nvidia_smi.nvmlInit()

        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        # card id 0 hardcoded here, there is also a call to get all available card ids, so we could iterate

        memInfo = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)

        mem_total = str(memInfo.total / 1024 / 1024) + ' MiB'
        # mem_used = str(memInfo.used / 1024 / 1024) + ' MiB'
        mem_free = str(memInfo.total / 1024 / 1024 - memInfo.used / 1024 / 1024) + ' MiB'
        temp = str(nvidia_smi.nvmlDeviceGetTemperature(handle, nvidia_smi.NVML_TEMPERATURE_GPU)) + ' C'
        device_name =  nvidia_smi.nvmlDeviceGetName(handle).decode("utf-8")
        data = {
            'name' : device_name,
            'total_mem' : mem_total,
            'usaged' : str((memInfo.used/memInfo.total)*100) + '%',
            'free_mem' : mem_free,
            'temperature' : temp
        }
        return  DataReponse(message= 'Success!',data=data,code = CODE_DONE)
    except Exception as e:
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)