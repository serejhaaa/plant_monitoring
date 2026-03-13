import secrets
from rest_framework import serializers
from .models import (
    Board,
    Sensor,
    SensorModel,
    SensorModelMeasurementType,
    MeasurementType,
)


def generate_board_token():
    return secrets.token_hex(64)  # 128 hex-символов


class MeasurementTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementType
        fields = ['id', 'name', 'code']


class SensorModelMeasurementTypeSerializer(serializers.ModelSerializer):
    measurement_type = MeasurementTypeSerializer(read_only=True)

    class Meta:
        model = SensorModelMeasurementType
        fields = ['measurement_type']


class SensorModelSerializer(serializers.ModelSerializer):
    measurement_types = MeasurementTypeSerializer(many=True, read_only=True)

    class Meta:
        model = SensorModel
        fields = ['id', 'name', 'description', 'default_config', 'measurement_types']


class SensorModelCreateUpdateSerializer(serializers.ModelSerializer):
    measurement_type_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = SensorModel
        fields = ['id', 'name', 'description', 'default_config', 'measurement_type_ids']

    def create(self, validated_data):
        mt_ids = validated_data.pop('measurement_type_ids', [])
        obj = SensorModel.objects.create(**validated_data)
        for mt_id in mt_ids:
            SensorModelMeasurementType.objects.create(
                sensor_model=obj,
                measurement_type_id=mt_id
            )
        return obj

    def update(self, instance, validated_data):
        mt_ids = validated_data.pop('measurement_type_ids', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if mt_ids is not None:
            SensorModelMeasurementType.objects.filter(sensor_model=instance).delete()
            for mt_id in mt_ids:
                SensorModelMeasurementType.objects.create(
                    sensor_model=instance,
                    measurement_type_id=mt_id
                )
        return instance

    def to_representation(self, instance):
        return SensorModelSerializer(instance).data


class SensorSerializer(serializers.ModelSerializer):
    sensor_model = SensorModelSerializer(read_only=True)

    class Meta:
        model = Sensor
        fields = ['id', 'board', 'sensor_model', 'config']


class SensorCreateUpdateSerializer(serializers.ModelSerializer):
    sensor_model = SensorModelSerializer(read_only=True)
    sensor_model_id = serializers.PrimaryKeyRelatedField(
        queryset=SensorModel.objects.all(),
        source='sensor_model',
        write_only=True
    )

    class Meta:
        model = Sensor
        fields = ['id', 'board', 'sensor_model', 'sensor_model_id', 'config']


class SensorWriteSerializer(serializers.ModelSerializer):
    """Для вложенного создания сенсоров при создании платы."""
    sensor_model_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Sensor
        fields = ['id', 'sensor_model_id', 'config']
        read_only_fields = ['id']


class BoardSerializer(serializers.ModelSerializer):
    sensors = SensorSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 'name', 'secret_token', 'serial_number',
            'rgb_config', 'is_activated', 'sensors'
        ]
        read_only_fields = ['id', 'secret_token']


class BoardCreateUpdateSerializer(serializers.ModelSerializer):
    sensors = SensorWriteSerializer(many=True, required=False)
    secret_token = serializers.CharField(read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 'name', 'secret_token', 'serial_number',
            'rgb_config', 'is_activated', 'sensors'
        ]
        read_only_fields = ['id', 'secret_token']

    def to_representation(self, instance):
        return BoardSerializer(instance).data

    def create(self, validated_data):
        sensors_data = validated_data.pop('sensors', [])
        validated_data['secret_token'] = generate_board_token()
        board = Board.objects.create(**validated_data)
        for s in sensors_data:
            Sensor.objects.create(
                board=board,
                sensor_model_id=s['sensor_model_id'],
                config=s.get('config', {})
            )
        return board

    def update(self, instance, validated_data):
        sensors_data = validated_data.pop('sensors', None)
        validated_data.pop('secret_token', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if sensors_data is not None:
            instance.sensors.all().delete()
            for s in sensors_data:
                Sensor.objects.create(
                    board=instance,
                    sensor_model_id=s['sensor_model_id'],
                    config=s.get('config', {})
                )
        return instance
