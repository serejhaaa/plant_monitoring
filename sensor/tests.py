from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status

from .models import Board, Sensor, SensorModel, Measurement, MeasurementType

ADMIN_HEADERS = {'X-SECRET-TOKEN': 'test-admin-token', 'Content-Type': 'application/json'}


@override_settings(SECRET_TOKEN='test-admin-token')
class MeasurementTypeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_measurement_type(self):
        r = self.client.post(
            '/api/measurement-types/',
            {'name': 'Air Temperature', 'code': 'air_temp'},
            format='json',
            HTTP_X_SECRET_TOKEN='test-admin-token'
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', r.data)
        self.assertEqual(r.data['name'], 'Air Temperature')
        self.assertEqual(r.data['code'], 'air_temp')

    def test_list_measurement_types(self):
        MeasurementType.objects.create(name='Test', code='test')
        r = self.client.get('/api/measurement-types/', HTTP_X_SECRET_TOKEN='test-admin-token')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(r.data), 1)

    def test_measurement_type_unauthorized(self):
        r = self.client.get('/api/measurement-types/')
        self.assertIn(r.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


@override_settings(SECRET_TOKEN='test-admin-token')
class SensorModelAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.mt = MeasurementType.objects.create(name='air_temp', code='air_temp')

    def test_create_sensor_model(self):
        r = self.client.post(
            '/api/sensor-models/',
            {
                'name': 'DHT11',
                'description': 'Temp/humidity sensor',
                'default_config': {'PIN_DHT': 0},
                'measurement_type_ids': [str(self.mt.id)]
            },
            format='json',
            HTTP_X_SECRET_TOKEN='test-admin-token'
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['name'], 'DHT11')
        self.assertIn('measurement_types', r.data)

    def test_list_sensor_models(self):
        r = self.client.get('/api/sensor-models/', HTTP_X_SECRET_TOKEN='test-admin-token')
        self.assertEqual(r.status_code, status.HTTP_200_OK)


@override_settings(SECRET_TOKEN='test-admin-token')
class BoardAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.sm = SensorModel.objects.create(
            name='DHT11',
            default_config={'PIN_DHT': 0}
        )

    def test_create_board_with_sensors(self):
        r = self.client.post(
            '/api/boards/',
            {
                'name': 'Test Board',
                'serial_number': 'abc123',
                'rgb_config': {'PIN_R': 26, 'PIN_G': 27, 'PIN_B': 25},
                'sensors': [
                    {'sensor_model_id': str(self.sm.id), 'config': {'PIN_DHT': 4}}
                ]
            },
            format='json',
            HTTP_X_SECRET_TOKEN='test-admin-token'
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn('secret_token', r.data)
        self.assertEqual(len(r.data['secret_token']), 128)
        self.assertEqual(len(r.data['sensors']), 1)
        self.assertEqual(r.data['sensors'][0]['config'], {'PIN_DHT': 4})

    def test_list_boards(self):
        r = self.client.get('/api/boards/', HTTP_X_SECRET_TOKEN='test-admin-token')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_board_unauthorized(self):
        r = self.client.post('/api/boards/', {'name': 'X', 'serial_number': 'x'}, format='json')
        self.assertIn(r.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


@override_settings(SECRET_TOKEN='test-admin-token')
class SensorAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.board = Board.objects.create(name='B1', serial_number='sn1', secret_token='t1')
        self.sm = SensorModel.objects.create(name='DHT11', default_config={})

    def test_create_sensor(self):
        r = self.client.post(
            '/api/sensors/',
            {
                'board': str(self.board.id),
                'sensor_model_id': str(self.sm.id),
                'config': {'PIN_DHT': 5}
            },
            format='json',
            HTTP_X_SECRET_TOKEN='test-admin-token'
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['config'], {'PIN_DHT': 5})


@override_settings(SECRET_TOKEN='test-admin-token')
class BoardConfigTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_config_not_found(self):
        r = self.client.get('/api/board/config/nonexistent/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_config_success(self):
        board = Board.objects.create(
            name='B1',
            serial_number='sn-config-test',
            secret_token='token123',
            is_activated=False
        )
        sm = SensorModel.objects.create(name='DHT11', default_config={'PIN_DHT': 0})
        Sensor.objects.create(board=board, sensor_model=sm, config={'PIN_DHT': 4})

        r = self.client.get('/api/board/config/sn-config-test/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['name'], 'B1')
        self.assertEqual(r.data['token'], 'token123')
        self.assertEqual(len(r.data['sensors']), 1)
        self.assertEqual(r.data['sensors'][0]['config'], {'PIN_DHT': 4})

        board.refresh_from_db()
        self.assertTrue(board.is_activated)

    def test_config_already_activated(self):
        board = Board.objects.create(
            name='B2',
            serial_number='sn-activated',
            secret_token='t2',
            is_activated=True
        )
        r = self.client.get('/api/board/config/sn-activated/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(SECRET_TOKEN='test-admin-token')
class MeasurementsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.board = Board.objects.create(
            name='B1',
            serial_number='sn1',
            secret_token='board-token-123'
        )
        self.sm = SensorModel.objects.create(name='DHT11', default_config={})
        self.sensor = Sensor.objects.create(
            board=self.board,
            sensor_model=self.sm,
            config={'PIN_DHT': 0}
        )
        self.mt = MeasurementType.objects.create(name='air_temp', code='air_temp')

    def test_add_measurement_admin(self):
        r = self.client.post(
            '/api/measure/',
            {'value': 25.5},
            format='json',
            HTTP_X_SECRET_TOKEN='test-admin-token'
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['value'], 25.5)

    def test_add_board_measurements(self):
        r = self.client.post(
            '/api/board/measure/',
            [
                {'sensor_uuid': str(self.sensor.id), 'value': 23.0},
                {'sensor_uuid': str(self.sensor.id), 'value': 65.0, 'measurement_type_uuid': str(self.mt.id)}
            ],
            format='json',
            HTTP_X_SECRET_TOKEN='board-token-123'
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(r.data['created']), 2)

    def test_add_board_measurements_invalid_sensor(self):
        r = self.client.post(
            '/api/board/measure/',
            [{'sensor_uuid': '00000000-0000-0000-0000-000000000000', 'value': 1.0}],
            format='json',
            HTTP_X_SECRET_TOKEN='board-token-123'
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('invalid', r.data)

    def test_list_measurements(self):
        r = self.client.get('/api/measurements/', HTTP_X_SECRET_TOKEN='test-admin-token')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('total', r.data)
        self.assertIn('results', r.data)
