# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.core.mail import send_mail

from .forms import (
    RegistroForm, TurnoForm, EspecialidadForm,
    DoctorRegistroForm, CrearFichaForm, ReservarTurnoForm, SugerirTurnoForm
)
from .models import Turno, Doctor, Perfil, Paciente

# ---------------------- VISTAS GENERALES ----------------------

def inicio(request):
    context = {
        'total_turnos': Turno.objects.count(),
        'total_doctores': Doctor.objects.count(),
        'total_pacientes': Paciente.objects.count(),
        'proximo_turno': Turno.objects.filter(fecha__gte=timezone.now()).order_by('fecha').first()
    }
    return render(request, 'turnos/inicio.html', context)

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            perfil = Perfil.objects.create(user=user)
            rol = form.cleaned_data['rol']
            if rol == 'paciente':
                perfil.es_paciente = True
                Paciente.objects.create(user=user, email=user.email or '', telefono='')
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
            login(request, form.get_user())
            messages.success(request, "Inicio de sesión exitoso.")
            return redirect('inicio')
        messages.error(request, "Credenciales inválidas.")
    else:
        form = AuthenticationForm()
    return render(request, 'turnos/login.html', {'form': form})

def cerrar_sesion(request):
    logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('inicio')

# ---------------------- DOCTORES ----------------------

def listar_doctores(request):
    doctores = Doctor.objects.all()
    return render(request, 'turnos/listar_doctores.html', {'doctores': doctores})

@login_required
def detalle_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if not request.user.perfil.es_paciente:
        return HttpResponseForbidden("Solo pacientes pueden agendar.")
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.paciente = request.user.paciente
            turno.doctor = doctor
            turno.especialidad = doctor.especialidad
            turno.save()
            return redirect('listar_turnos')
    else:
        form = TurnoForm(initial={'doctor': doctor, 'especialidad': doctor.especialidad})
    return render(request, 'turnos/detalle_doctor.html', {'form': form, 'doctor': doctor})

@login_required
<<<<<<< HEAD
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
            turno.paciente, _ = Paciente.objects.get_or_create(user=request.user, defaults={
                'telefono': '',  # o datos por defecto válidos
                'email': request.user.email or ''
            })
            turno.save()
            mensaje = f"Hola {turno.paciente.user.username}, tu turno con el Dr. {turno.doctor.user.get_full_name()} ha sido confirmado para el {turno.fecha} a las {turno.hora}."
            send_mail(
                subject="Confirmación de Turno Médico",
                message=mensaje,
                from_email=None,
                recipient_list=[turno.paciente.email],
                fail_silently=False,
            )
            return redirect('listar_turnos')
    else:
        form = TurnoForm(request.GET)
    return render(request, 'turnos/crear_turno.html', {
        'form': form,
    'especialidad_seleccionada': request.GET.get('especialidad') or request.POST.get('especialidad')
        })

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

=======
>>>>>>> 159897e375c1e5a0bed2799ad47f73d4a7625613
def registrar_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('iniciar_sesion')
    else:
        form = DoctorRegistroForm()
    return render(request, 'turnos/registrar_doctor.html', {'form': form})

# ---------------------- PACIENTE - TURNOS ----------------------

@login_required
def listar_turnos(request):
    if not request.user.perfil.es_paciente:
        return HttpResponseForbidden("Solo los pacientes pueden ver sus turnos.")
    turnos = Turno.objects.filter(paciente=request.user.paciente)
    return render(request, 'turnos/listar_turnos.html', {'turnos': turnos})

@login_required
def mis_turnos(request):
    if request.user.perfil.es_paciente:
        turnos = Turno.objects.filter(paciente=request.user.paciente).order_by('fecha', 'hora')
        return render(request, 'turnos/mis_turnos.html', {'turnos': turnos})
    return redirect('inicio')

@login_required
def reservar_ficha(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id, reservado=False)
    if not request.user.perfil.es_paciente:
        return redirect('inicio')
    if request.method == 'POST':
        form = ReservarTurnoForm(request.POST, instance=turno)
        if form.is_valid():
            turno.paciente = request.user.paciente
            turno.reservado = True
            turno.save()
            messages.success(request, "Turno reservado con éxito.")
            return redirect('mis_turnos')
    else:
        form = ReservarTurnoForm(instance=turno)
    return render(request, 'turnos/reservar_ficha.html', {'form': form, 'turno': turno})

@login_required
def cancelar_turno(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id)
    if turno.paciente != request.user.paciente:
        messages.error(request, "No puedes cancelar un turno ajeno.")
        return redirect('mis_turnos')
    turno.delete()
    messages.success(request, "Turno cancelado.")
    return redirect('mis_turnos')

@login_required
def sugerir_turno(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    paciente = get_object_or_404(Paciente, user=request.user)

    if request.method == 'POST':
        form = SugerirTurnoForm(request.POST, doctor=doctor, paciente=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, "Has sugerido un turno al doctor.")
            return redirect('mis_turnos')
    else:
        form = SugerirTurnoForm(doctor=doctor, paciente=paciente)

    return render(request, 'turnos/sugerir_turno.html', {
        'form': form,
        'doctor': doctor
    })

# ---------------------- DOCTOR - FICHAS ----------------------

@login_required
def crear_ficha(request):
    if not request.user.perfil.es_doctor:
        return redirect('inicio')
    if request.method == 'POST':
        form = CrearFichaForm(request.POST, doctor=request.user.doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Ficha creada.")
            return redirect('listar_fichas')
    else:
        form = CrearFichaForm(doctor=request.user.doctor)
    return render(request, 'turnos/crear_ficha.html', {'form': form})

@login_required
def listar_fichas(request):
    if not request.user.perfil.es_doctor:
        return redirect('inicio')
    turnos = Turno.objects.filter(doctor=request.user.doctor, paciente__isnull=True).order_by('fecha', 'hora')
    return render(request, 'turnos/listar_fichas.html', {'turnos': turnos})

# ---------------------- ESPECIALIDADES y AJAX ----------------------

@login_required
def crear_especialidad(request):
    if not request.user.perfil.es_doctor and not request.user.is_superuser:
        return HttpResponseForbidden("Sin permiso.")
    if request.method == 'POST':
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Especialidad creada.")
            return redirect('inicio')
    else:
        form = EspecialidadForm()
    return render(request, 'turnos/crear_especialidad.html', {'form': form})

def obtener_doctores_por_especialidad(request):
    especialidad_id = request.GET.get('especialidad_id')
    doctores = Doctor.objects.filter(especialidad_id=especialidad_id)
    data = [{'id': d.id, 'nombre': f'{d.user.first_name} {d.user.last_name}'} for d in doctores]
    return JsonResponse(data, safe=False)