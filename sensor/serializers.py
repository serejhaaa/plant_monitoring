import secrets
from rest_framework import serializers
from .models import Board, Sensor, SensorType


def generate_board_token():
    return secrets.token_hex(64)  # 128 hex-символов


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'board', 'sensor_type']

    def validate_sensor_type(self, value):
        if value not in SensorType.values:
            raise serializers.ValidationError(
                f"sensor_type must be one of: {', '.join(SensorType.values)}"
            )
        return value


class SensorWriteSerializer(serializers.ModelSerializer):
    """Для вложенного создания сенсоров (без board — подставится из контекста)."""
    class Meta:
        model = Sensor
        fields = ['id', 'sensor_type']
        read_only_fields = ['id']

    def validate_sensor_type(self, value):
        if value not in SensorType.values:
            raise serializers.ValidationError(
                f"sensor_type must be one of: {', '.join(SensorType.values)}"
            )
        return value


class BoardSerializer(serializers.ModelSerializer):
    sensors = SensorSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'name', 'secret_token', 'sensors']
        read_only_fields = ['id']


class BoardCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор с возможностью создания платы вместе с сенсорами. Токен генерируется автоматически."""
    sensors = SensorWriteSerializer(many=True, required=False)
    secret_token = serializers.CharField(read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'name', 'secret_token', 'sensors']
        read_only_fields = ['id', 'secret_token']

    def to_representation(self, instance):
        return BoardSerializer(instance).data

    def create(self, validated_data):
        sensors_data = validated_data.pop('sensors', [])
        validated_data['secret_token'] = generate_board_token()
        board = Board.objects.create(**validated_data)
        for s in sensors_data:
            Sensor.objects.create(board=board, sensor_type=s['sensor_type'])
        return board

    def update(self, instance, validated_data):
        sensors_data = validated_data.pop('sensors', None)
        validated_data.pop('secret_token', None)  # Токен неизменяем
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if sensors_data is not None:
            instance.sensors.all().delete()
            for s in sensors_data:
                Sensor.objects.create(board=instance, sensor_type=s['sensor_type'])

        return instance
