# sensor/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Measurement

@api_view(['POST'])
def add_measurement(request):
    # 1. Авторизация по токену в заголовке
    token = request.headers.get('X-SECRET-TOKEN')
    if token != settings.SECRET_TOKEN:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

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