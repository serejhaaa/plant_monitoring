# sensor/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import Board, Sensor, SensorModel, Measurement, MeasurementType
from .serializers import (
    MeasurementTypeSerializer,
    BoardSerializer,
    BoardCreateUpdateSerializer,
    SensorSerializer,
    SensorCreateUpdateSerializer,
    SensorModelSerializer,
    SensorModelCreateUpdateSerializer,
)


def _check_token(request):
    token = request.headers.get('X-SECRET-TOKEN')
    if token != settings.SECRET_TOKEN:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    return None


class AdminTokenAuthentication(BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get('X-SECRET-TOKEN')
        if token != settings.SECRET_TOKEN:
            raise AuthenticationFailed('Invalid token')
        return True


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.prefetch_related('sensors').all()
    permission_classes = [AdminTokenAuthentication]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return BoardCreateUpdateSerializer
        return BoardSerializer


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.select_related('board', 'sensor_model').all()
    permission_classes = [AdminTokenAuthentication]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return SensorCreateUpdateSerializer
        return SensorSerializer


class MeasurementTypeViewSet(viewsets.ModelViewSet):
    queryset = MeasurementType.objects.all()
    serializer_class = MeasurementTypeSerializer
    permission_classes = [AdminTokenAuthentication]


class SensorModelViewSet(viewsets.ModelViewSet):
    queryset = SensorModel.objects.prefetch_related('model_measurement_types__measurement_type').all()
    permission_classes = [AdminTokenAuthentication]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return SensorModelCreateUpdateSerializer
        return SensorModelSerializer


@api_view(['GET'])
def board_config(request, serial_number):
    """
    Получение конфига платы по серийному номеру. Без авторизации.
    Возвращает конфиг только если is_activated=False, затем ставит is_activated=True.
    """
    board = Board.objects.filter(serial_number=serial_number).prefetch_related(
        'sensors__sensor_model'
    ).first()
    if not board:
        return Response(
            {'error': 'Board not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    if board.is_activated:
        return Response(
            {'error': 'Board already activated'},
            status=status.HTTP_403_FORBIDDEN
        )
    board.is_activated = True
    board.save(update_fields=['is_activated'])

    sensors_payload = []
    for s in board.sensors.all():
        sensors_payload.append({
            'id': str(s.id),
            'model': s.sensor_model.name,
            'config': s.config or s.sensor_model.default_config or {},
        })

    config = {
        'id': str(board.id),
        'name': board.name,
        'token': board.secret_token,
        'rgb_config': board.rgb_config or {},
        'sensors': sensors_payload,
    }
    return Response(config)


@api_view(['GET'])
def list_measurements(request):
    auth_error = _check_token(request)
    if auth_error:
        return auth_error

    try:
        limit = min(int(request.query_params.get('limit', 100)), 1000)
        offset = max(int(request.query_params.get('offset', 0)), 0)
    except (TypeError, ValueError):
        limit = 100
        offset = 0

    queryset = Measurement.objects.select_related(
        'sensor', 'measurement_type'
    ).all()[offset:offset + limit]
    measurements = []
    for m in queryset:
        item = {'id': m.id, 'timestamp': m.timestamp.isoformat(), 'value': m.value}
        if m.sensor_id:
            item['sensor_uuid'] = str(m.sensor_id)
        if m.measurement_type_id:
            item['measurement_type_uuid'] = str(m.measurement_type_id)
        measurements.append(item)
    total = Measurement.objects.count()

    return Response({
        'count': len(measurements),
        'total': total,
        'results': measurements
    })


@api_view(['POST'])
def add_measurement(request):
    auth_error = _check_token(request)
    if auth_error:
        return auth_error

    try:
        value = float(request.data.get('value'))
    except (TypeError, ValueError):
        return Response({'error': 'Value must be a number'}, status=status.HTTP_400_BAD_REQUEST)

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
    Отправка измерений платой. Авторизация по токену платы.
    Тело: [{"sensor_uuid": "uuid", "measurement_type_uuid": "uuid", "value": 31.5}, ...]
    measurement_type_uuid опционален.
    """
    board_token = request.headers.get('X-SECRET-TOKEN')
    if not board_token:
        return Response({'error': 'X-SECRET-TOKEN required'}, status=status.HTTP_401_UNAUTHORIZED)

    board = Board.objects.filter(secret_token=board_token).first()
    if not board:
        return Response({'error': 'Invalid board token'}, status=status.HTTP_401_UNAUTHORIZED)

    if not isinstance(request.data, list):
        return Response(
            {'error': 'Expected array of {sensor_uuid, value [, measurement_type_uuid]}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    created = []
    invalid_sensors = []

    for item in request.data:
        sensor_uuid = item.get('sensor_uuid')
        mt_uuid = item.get('measurement_type_uuid')
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
            invalid_sensors.append({
                'sensor_uuid': str(sensor_uuid),
                'error': 'sensor belongs to another board'
            })
            continue

        m = Measurement.objects.create(
            sensor=sensor,
            value=value,
            measurement_type_id=mt_uuid if mt_uuid else None
        )
        created.append({
            'id': m.id,
            'sensor_uuid': str(sensor.id),
            'measurement_type_uuid': str(m.measurement_type_id) if m.measurement_type_id else None,
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
