# sensor/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import Board, Sensor, Measurement
from .serializers import BoardSerializer, BoardCreateUpdateSerializer, SensorSerializer


def _check_token(request):
    """Проверка токена авторизации."""
    token = request.headers.get('X-SECRET-TOKEN')
    if token != settings.SECRET_TOKEN:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    return None


class TokenAuthentication(BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get('X-SECRET-TOKEN')
        if token != settings.SECRET_TOKEN:
            raise AuthenticationFailed('Invalid token')
        return True


class BoardViewSet(viewsets.ModelViewSet):
    """CRUD для плат. Создание/обновление с вложенными сенсорами."""
    queryset = Board.objects.prefetch_related('sensors').all()
    permission_classes = [TokenAuthentication]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return BoardCreateUpdateSerializer
        return BoardSerializer


class SensorViewSet(viewsets.ModelViewSet):
    """CRUD для сенсоров."""
    queryset = Sensor.objects.select_related('board').all()
    serializer_class = SensorSerializer
    permission_classes = [TokenAuthentication]


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

    queryset = Measurement.objects.select_related('sensor').all()[offset:offset + limit]
    measurements = []
    for m in queryset:
        item = {'id': m.id, 'timestamp': m.timestamp.isoformat(), 'value': m.value}
        if m.sensor_id:
            item['sensor_uuid'] = str(m.sensor_id)
        measurements.append(item)
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


@api_view(['POST'])
def add_board_measurements(request):
    """
    Отправка измерений платой. Авторизация по токену платы (X-SECRET-TOKEN).
    Тело: [{"sensor_uuid": "uuid", "value": 31.5}, ...]
    Если хотя бы один sensor_uuid принадлежит другой плате — 400, но валидные записываются.
    """
    board_token = request.headers.get('X-SECRET-TOKEN')
    if not board_token:
        return Response({'error': 'X-SECRET-TOKEN required'}, status=status.HTTP_401_UNAUTHORIZED)

    board = Board.objects.filter(secret_token=board_token).first()
    if not board:
        return Response({'error': 'Invalid board token'}, status=status.HTTP_401_UNAUTHORIZED)

    if not isinstance(request.data, list):
        return Response({'error': 'Expected array of {sensor_uuid, value}'}, status=status.HTTP_400_BAD_REQUEST)

    created = []
    invalid_sensors = []

    for item in request.data:
        sensor_uuid = item.get('sensor_uuid')
        try:
            value = float(item.get('value'))
        except (TypeError, ValueError):
            invalid_sensors.append({'sensor_uuid': sensor_uuid, 'error': 'value must be a number'})
            continue

        sensor = Sensor.objects.filter(id=sensor_uuid).select_related('board').first()
        if not sensor:
            invalid_sensors.append({'sensor_uuid': str(sensor_uuid), 'error': 'sensor not found'})
            continue
        if sensor.board_id != board.id:
            invalid_sensors.append({'sensor_uuid': str(sensor_uuid), 'error': 'sensor belongs to another board'})
            continue

        m = Measurement.objects.create(sensor=sensor, value=value)
        created.append({
            'id': m.id,
            'sensor_uuid': str(sensor.id),
            'timestamp': m.timestamp.isoformat(),
            'value': m.value,
        })

    if invalid_sensors:
        return Response({
            'status': 'partial',
            'created': created,
            'invalid': invalid_sensors,
            'error': 'Some sensors invalid or belong to another board'
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'status': 'success',
        'created': created
    }, status=status.HTTP_201_CREATED)