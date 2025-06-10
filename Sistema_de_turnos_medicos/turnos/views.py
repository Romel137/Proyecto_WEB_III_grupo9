from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroForm, TurnoForm
from .models import Turno, Doctor, Perfil, Paciente
from django.core.mail import send_mail
from .forms import DoctorRegistroForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from .forms import EspecialidadForm

def inicio(request):
    return render(request, 'turnos/inicio.html')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            rol = form.cleaned_data['rol']
            perfil = Perfil.objects.create(user=user)
            if rol == 'paciente':
                perfil.es_paciente = True
                Paciente.objects.create(user=user, email=user.email, telefono='000000000')
            elif rol == 'doctor':
                perfil.es_doctor = True
            perfil.save()
            login(request, user)
            return redirect('inicio')
    else:
        form = RegistroForm()
    return render(request, 'turnos/registro.html', {'form': form})

def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('inicio')
    else:
        form = AuthenticationForm()
    return render(request, 'turnos/login.html', {'form': form})

def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')

def listar_doctores(request):
    doctores = Doctor.objects.all()
    return render(request, 'turnos/listar_doctores.html', {'doctores': doctores})


@login_required
def detalle_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if not request.user.perfil.es_paciente:
        return HttpResponseForbidden("Solo los pacientes pueden agendar turnos.")
    
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.paciente = Paciente.objects.get(user=request.user)
            turno.doctor = doctor
            turno.especialidad = doctor.especialidad  # ahora es una instancia válida
            turno.save()
            return redirect('listar_turnos')
    else:
        form = TurnoForm(initial={
            'doctor': doctor,
            'especialidad': doctor.especialidad
        })
    
    return render(request, 'turnos/detalle_doctor.html', {'form': form, 'doctor': doctor})

@login_required
def listar_turnos(request):
    if not request.user.perfil.es_paciente:
        return HttpResponseForbidden("Solo los pacientes pueden ver sus turnos.")
    paciente = Paciente.objects.get(user=request.user)
    turnos = Turno.objects.filter(paciente=paciente)
    return render(request, 'turnos/listar_turnos.html', {'turnos': turnos})

@login_required
def crear_turno(request):
    if not request.user.perfil.es_paciente:
        return HttpResponseForbidden("Solo los pacientes pueden crear turnos.")
    
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.paciente = Paciente.objects.get(user=request.user)
            turno.save()

            mensaje = f"Hola {turno.paciente.user.username}, tu turno con el Dr. {turno.doctor.nombre} ha sido confirmado para el {turno.fecha} a las {turno.hora}."
            send_mail(
                subject="Confirmación de Turno Médico",
                message=mensaje,
                from_email=None,  # Usa DEFAULT_FROM_EMAIL
                recipient_list=[turno.paciente.email],
                fail_silently=False,
            )

            return redirect('listar_turnos')
    else:
        form = TurnoForm()
    return render(request, 'turnos/crear_turno.html', {'form': form})

@login_required
def mis_turnos(request):
    try:
        if request.user.perfil.es_paciente:
            paciente = Paciente.objects.get(user=request.user)
            turnos = Turno.objects.filter(paciente=paciente)
        elif request.user.perfil.es_doctor:
            doctor = Doctor.objects.get(nombre=request.user.username)
            turnos = Turno.objects.filter(doctor=doctor)
        else:
            turnos = Turno.objects.none()
    except:
        turnos = Turno.objects.none()

    return render(request, 'turnos/listar_turnos.html', {'turnos': turnos})

def registrar_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('iniciar_sesion')  # o a donde quieras redirigir
    else:
        form = DoctorRegistroForm()
    return render(request, 'turnos/registrar_doctor.html', {'form': form})

@login_required
def reservar_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.paciente = request.user
            turno.save()
            return redirect('lista_turnos')  # Cambia por tu URL real
    else:
        form = TurnoForm()
    return render(request, 'reservar_turno.html', {'form': form})

from django.utils import timezone

def inicio(request):
    total_turnos = Turno.objects.count()
    total_doctores = Doctor.objects.count()
    total_pacientes = Paciente.objects.count()
    proximo_turno = Turno.objects.filter(fecha__gte=timezone.now()).order_by('fecha').first()

    context = {
        'total_turnos': total_turnos,
        'total_doctores': total_doctores,
        'total_pacientes': total_pacientes,
        'proximo_turno': proximo_turno
    }

    return render(request, 'turnos/inicio.html', context)

@login_required
def crear_especialidad(request):
    
    if not request.user.perfil.es_doctor and not request.user.is_superuser:
        return HttpResponseForbidden("No tienes permiso para crear especialidades.")

    if request.method == 'POST':
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Especialidad creada correctamente.")
            return redirect('inicio')
    else:
        form = EspecialidadForm()

    return render(request, 'turnos/crear_especialidad.html', {'form': form})