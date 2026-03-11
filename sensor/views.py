# sensor/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Measurement


def _check_token(request):
    """Проверка токена авторизации."""
    token = request.headers.get('X-SECRET-TOKEN')
    if token != settings.SECRET_TOKEN:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    return None


@api_view(['GET'])
def list_measurements(request):
    """Возвращает список измерений с пагинацией."""
    auth_error = _check_token(request)
    if auth_error:
        return auth_error

    try:
        limit = min(int(request.query_params.get('limit', 100)), 1000)
        offset = max(int(request.query_params.get('offset', 0)), 0)
    except (TypeError, ValueError):
        limit = 100
        offset = 0

    queryset = Measurement.objects.all()[offset:offset + limit]
    measurements = [
        {'id': m.id, 'timestamp': m.timestamp.isoformat(), 'value': m.value}
        for m in queryset
    ]
    total = Measurement.objects.count()

    return Response({
        'count': len(measurements),
        'total': total,
        'results': measurements
    })


@api_view(['POST'])
def add_measurement(request):
    # 1. Авторизация по токену в заголовке
    auth_error = _check_token(request)
    if auth_error:
        return auth_error

    # 2. Получение и валидация числового значения
    try:
        value = float(request.data.get('value'))
    except (TypeError, ValueError):
        return Response({'error': 'Value must be a number'}, status=status.HTTP_400_BAD_REQUEST)

    # 3. Сохранение в БД
    measurement = Measurement.objects.create(value=value)

    return Response({
        'status': 'success',
        'id': measurement.id,
        'timestamp': measurement.timestamp,
        'value': measurement.value
    }, status=status.HTTP_201_CREATED)