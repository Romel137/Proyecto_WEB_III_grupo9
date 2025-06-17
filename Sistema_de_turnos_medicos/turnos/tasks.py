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
