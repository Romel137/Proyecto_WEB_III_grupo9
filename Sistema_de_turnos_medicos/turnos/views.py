from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroForm, TurnoForm
from .models import Turno, Doctor, Perfil, Paciente
from django.core.mail import send_mail
from .forms import DoctorRegistroForm
from django.contrib.auth.models import User
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
            turno.especialidad = turno.doctor.especialidad  # importante
            turno.save()
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
            doctor = Doctor.objects.get(user=request.user)
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
    if not request.user.perfil.es_paciente:
        return HttpResponseForbidden("Solo los pacientes pueden crear turnos.")

    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.paciente = Paciente.objects.get(user=request.user)
            turno.especialidad = turno.doctor.especialidad  # Se asigna automáticamente
            turno.save()
            return redirect('listar_turnos')
    else:
        form = TurnoForm()
    
    return render(request, 'reservar_turno.html', {'form': form})

@login_required
def mis_pacientes(request):
    pacientes = Paciente.objects.all()

    
    pacientes_con_doctores = []
    for paciente in pacientes:
        turnos = Turno.objects.filter(paciente=paciente)
        doctores = [turno.doctor.user.get_full_name() for turno in turnos]
        pacientes_con_doctores.append({
            'paciente': paciente,
            'doctores': list(set(doctores))  # lista sin duplicados
        })

    return render(request, 'turnos/mis_pacientes.html', {'pacientes_con_doctores': pacientes_con_doctores})