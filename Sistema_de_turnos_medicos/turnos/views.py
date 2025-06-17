from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone

from .forms import (
    RegistroForm, TurnoForm, EspecialidadForm,
    DoctorRegistroForm, CrearFichaForm, ReservarTurnoForm, SugerirTurnoForm
)
from .models import Turno, Doctor, Perfil, Paciente, Especialidad


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
        return HttpResponseForbidden("Solo los pacientes pueden agendar turnos.")

    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.paciente = request.user.paciente
            turno.doctor = doctor
            turno.especialidad = doctor.especialidad
            turno.save()
            messages.success(request, "Turno reservado.")
            return redirect('mis_turnos')
    else:
        form = TurnoForm(initial={'doctor': doctor, 'especialidad': doctor.especialidad})

    return render(request, 'turnos/detalle_doctor.html', {'form': form, 'doctor': doctor})


from django.contrib.auth import login

def registrar_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistroForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            user = doctor.user
            # Crear perfil del doctor
            perfil, created = Perfil.objects.get_or_create(user=user)
            perfil.es_doctor = True
            perfil.save()
            # Iniciar sesión automáticamente
            login(request, user)
            messages.success(request, "Doctor registrado y sesión iniciada.")
            return redirect('listar_fichas')
    else:
        form = DoctorRegistroForm()
    return render(request, 'turnos/registrar_doctor.html', {'form': form})

# ---------------------- PACIENTE - TURNOS ----------------------

@login_required
def mis_turnos(request):
    if request.user.perfil.es_paciente:
        turnos = Turno.objects.filter(paciente=request.user.paciente).order_by('fecha', 'hora')
        return render(request, 'turnos/mis_turnos.html', {'turnos': turnos})
    return HttpResponseForbidden("No tienes permiso para ver esta sección.")


@login_required
def confirmar_reserva(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id, reservado=False)

    if not request.user.perfil.es_paciente:
        return HttpResponseForbidden("Acceso denegado.")

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

    return render(request, 'turnos/confirmar_reserva.html', {'form': form, 'turno': turno})


@login_required
def reservar_ficha(request):
    especialidades = Especialidad.objects.all()
    doctores = Doctor.objects.all()
    turnos_disponibles = None

    especialidad_id = request.GET.get('especialidad')
    doctor_id = request.GET.get('doctor')

    if especialidad_id:
        doctores = doctores.filter(especialidad_id=especialidad_id)

    if doctor_id:
        turnos_disponibles = Turno.objects.filter(
            doctor_id=doctor_id,
            reservado=False,
            paciente__isnull=True
        ).order_by('fecha', 'hora')

    return render(request, 'turnos/reservar_ficha.html', {
        'especialidades': especialidades,
        'doctores': doctores,
        'turnos': turnos_disponibles,
        'selected_especialidad': especialidad_id,
        'selected_doctor': doctor_id,
    })


@login_required
def reservar_ficha_confirmar(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id, reservado=False, paciente__isnull=True)

    if not request.user.perfil.es_paciente:
        return HttpResponseForbidden("Acceso denegado.")

    if request.method == 'POST':
        turno.paciente = request.user.paciente
        turno.reservado = True
        turno.save()
        messages.success(request, 'Turno reservado correctamente.')
        return redirect('mis_turnos')

    return render(request, 'turnos/reservar_confirmar.html', {'turno': turno})


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

    if not request.user.perfil.es_paciente:
        return HttpResponseForbidden("Solo los pacientes pueden sugerir turnos.")

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
        return HttpResponseForbidden("Solo los doctores pueden crear fichas.")

    if request.method == 'POST':
        form = CrearFichaForm(request.POST, doctor=request.user.doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Ficha creada correctamente.")
            return redirect('listar_fichas')
    else:
        form = CrearFichaForm(doctor=request.user.doctor)

    return render(request, 'turnos/crear_ficha.html', {'form': form})


@login_required
def listar_fichas(request):
    if not request.user.perfil.es_doctor:
        return HttpResponseForbidden("Solo los doctores pueden ver sus fichas.")
    
    turnos = Turno.objects.filter(doctor=request.user.doctor, paciente__isnull=True).order_by('fecha', 'hora')
    return render(request, 'turnos/listar_fichas.html', {'turnos': turnos})


# ---------------------- ESPECIALIDADES y AJAX ----------------------

@login_required
def crear_especialidad(request):
    if not (request.user.perfil.es_doctor or request.user.is_superuser):
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
