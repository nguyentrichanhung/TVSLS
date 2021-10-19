import psutil
# import nvidia_smi

from src.service.response import *
from src.const import *



def cpu_check(log):
    try:
        list_cpus = psutil.cpu_percent(percpu=True,interval=1)
        usages = {}
        for x in range(len(list_cpus)):
            usages["core {}".format(x)] = list_cpus[x]
        processor = {'physicals': psutil.cpu_count(False), 'logicals': psutil.cpu_count(True),
                    'usage': psutil.cpu_percent(interval=1), 'usages': usages}
        memory = psutil.virtual_memory()._asdict()
        memory = {'total': round(memory['total']/GB,2), 'available': round(memory['available']/GB,2),
                'used': round(memory['used']/GB,2), 'free': round(memory['free']/GB,2), 'percent': memory['percent']}
        storage = psutil.disk_usage(ROOT)._asdict()
        storage = {'total': round(storage['total']/GB,2), 'used': round(storage['used']/GB,2),
                'free': round(storage['free']/GB,2), 'percent': storage['percent']}
        data = {'processor': processor, 'memory': memory, 'storage': storage}
        return DataReponse(message= 'Success!',data=data,code = CODE_DONE)
    except Exception as e:
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def gpu_check(log):
    pass
#     try:
#         nvidia_smi.nvmlInit()

#         handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
#         # card id 0 hardcoded here, there is also a call to get all available card ids, so we could iterate

#         memInfo = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)

#         mem_total = str(memInfo.total / 1024 / 1024) + ' MiB'
#         # mem_used = str(memInfo.used / 1024 / 1024) + ' MiB'
#         mem_free = str(memInfo.total / 1024 / 1024 - memInfo.used / 1024 / 1024) + ' MiB'
#         temp = str(nvidia_smi.nvmlDeviceGetTemperature(handle, nvidia_smi.NVML_TEMPERATURE_GPU)) + ' C'
#         device_name =  nvidia_smi.nvmlDeviceGetName(handle).decode("utf-8")
#         data = {
#             'name' : device_name,
#             'total_mem' : mem_total,
#             'usaged' : str((memInfo.used/memInfo.total)*100) + '%',
#             'free_mem' : mem_free,
#             'temperature' : temp
#         }
#         return  DataReponse(message= 'Success!',data=data,code = CODE_DONE)
#     except Exception as e:
#         log.error(e)
#         return DataReponse(message = 'System error!!!',code= CODE_FAIL)