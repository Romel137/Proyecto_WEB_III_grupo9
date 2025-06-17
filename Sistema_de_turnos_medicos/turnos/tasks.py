<<<<<<< HEAD
from celery import shared_task
from django.utils import timezone
from turnos.models import Turno
from django.core.mail import send_mail

@shared_task
def enviar_recordatorios_turnos():
    ahora = timezone.now()
    manana = ahora + timezone.timedelta(days=1)
    turnos = Turno.objects.filter(
        fecha__range=[ahora.date(), manana.date()]
    )
    for turno in turnos:
        turno_datetime = timezone.make_aware(
            timezone.datetime.combine(turno.fecha, turno.hora)
        )
        horas_antes = (turno_datetime - ahora).total_seconds() / 3600
        if 23 <= horas_antes <= 25 or horas_antes < 24:
            paciente = turno.paciente
            email = paciente.email
            mensaje = (
                f"Hola {paciente.user.get_full_name()},\n\n"
                f"Te recordamos que tienes un turno con el Dr. {turno.doctor.user.get_full_name()} "
                f"el {turno.fecha} a las {turno.hora}.\n\n"
                "¡No faltes!"
            )
            send_mail(
                subject="Recordatorio de turno médico",
                message=mensaje,
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )
=======
from django.utils import timezone
from django.core.mail import send_mail
from .models import Turno

def enviar_recordatorios_doctores():
    hoy = timezone.now().date()
    pendientes = Turno.objects.filter(fecha=hoy, reservado=True, recordatorio_enviado=False)
    for turno in pendientes:
        doctor = turno.doctor
        send_mail(
            "Recordatorio de turno hoy",
            f"Tienes una cita hoy con {turno.paciente} a las {turno.hora}.",
            None,
            [doctor.user.email]
        )
        turno.recordatorio_enviado = True
        turno.save()
>>>>>>> 159897e375c1e5a0bed2799ad47f73d4a7625613
