from .models import Paciente, Doctor

def perfil_context(request):
    if request.user.is_authenticated:
        try:
            if hasattr(request.user, 'paciente'):
                return {'perfil': {'es_paciente': True, 'es_doctor': False}}
            elif hasattr(request.user, 'doctor'):
                return {'perfil': {'es_paciente': False, 'es_doctor': True}}
        except:
            pass
    return {'perfil': {'es_paciente': False, 'es_doctor': False}}
