import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sistema_de_turnos_medicos.settings')

app = Celery('Sistema_de_turnos_medicos')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()