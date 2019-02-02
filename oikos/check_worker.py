from celery.result import AsyncResult
from time import sleep

from django.core.exceptions import ObjectDoesNotExist

from agora.celery import app

from .models import LocalServices
