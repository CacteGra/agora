from celery.result import AsyncResult
from time import sleep

from django.core.exceptions import ObjectDoesNotExist

from agora.celery import app

from .models import LocalServices
from .models import Miband
from .tasks import miband

def main(miband_user):
    print('gonna try')
    try:
        miband_device = Miband.objects.get(user=miband_user)
    except ObjectDoesNotExist:
        print('Did not find device by user... creating user...')
        Miband.objects.create(user=miband_user)
        return True
    miband_address = miband_device.mac_address
    print(miband_address)
    worker_id = LocalServices.objects.filter(miband=miband_device)
    if worker_id.count() > 0:
        local_services = LocalServices.objects.get(miband=miband_device)
        i = app.control.inspect()
        active_workers = i.active()
        if not local_services.worker_number:
            print('did get')
            miband_sched = miband.delay(miband_address)
            local_services.service_id = miband_sched.id
            for worker, profile in active_workers.items():
                for value in profile:
                    if local_services.service_id == value['id']:
                        local_services.worker_number = value['hostname'].strip('worker@rapsberrypi')
                        print(value['hostname'].strip('worker@rapsberrypi'))
            local_services.save()
        elif not ((['oikos.tasks.twitter_profile' in profile['type'] for profile in active_workers['worker{}@raspberrypi'.format(local_services.worker_number)]]) and ([worker_id in profile['id'] for profile in active_workers['worker{}@raspberrypi'.format(local_services.worker_number)]])):
            miband_sched = miband.delay(miband_address)
            local_services.service_id = miband_sched.id
            print('not in type and args')
            active_workers = i.active()
            for worker, profile in active_workers.items():
                for value in profile:
                    if local_services.service_id == value['id']:
                        local_services.worker_number = worker.strip('worker@rapsberrypi')
            local_services.save()
        elif not i:
            miband_sched = miband.delay(miband_address)
            local_services.service_id = miband_sched.id
            for worker, profile in active_workers.items():
                for value in profile:
                    if local_services.service_id == value['id']:
                        local_services.worker_number = worker.strip('workerr@raspberry')
            local_services.save()
        else:
            print('task already active')
    else:
        miband_sched = miband.delay(miband_address)
        LocalServices.objects.create(miband=miband_device,name='miband',service_id=miband_sched.id)
        i = app.control.inspect()
        active_workers = i.active()
        for worker, profile in active_workers.items():
            for value in profile:
                if local_services.service_id == value['id']:
                    local_services.worker_number = value['hostname'].strip('worker@raspberry')
        local_services.save()
        local_services = LocalServices.objects.filter(miband=miband_device)
        if local_services.count() > 0:
            local_services.miband = miband_sched.id
            local_services.save()
