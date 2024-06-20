import unittest
from app.models import Formulario, Implicados, Multipropietario, Propietario
from app import create_app, db
from app.controllers.table_handlers.multipropietario import MultipropietarioTableHandler
from app.controllers.table_handlers.propietario import PropietarioTableHandler
from unittest.mock import patch, MagicMock
from wtforms import Form, StringField, IntegerField, DateField
from app.forms import rol_validator, rut_validator, porcentaje_validator, positive_integer_validator, validate_past_date
from wtforms.validators import ValidationError
import json
from datetime import date

from config.test_config import TestConfig  # Ensure this points to your test configuration

class TestMultipropietarioTableHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_object=TestConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def setUp(self):
        self.handler = MultipropietarioTableHandler()
        self.handler.propietario_handler = MagicMock()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @patch('app.models.db.session', autospec=True)
    def test_upload_form(self, mock_session):
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()

        form_id = self.handler.upload_form('test_rol', date(2023, 1, 1), 'fojas', 'nro_inscripcion', 2023, 2023, 2025)

        self.assertTrue(mock_session.add.called)
        self.assertTrue(mock_session.commit.called)
        # self.assertIsNotNone(form_id)

    def test_get_forms_by_rol(self):
        with patch.object(Multipropietario.query, 'filter_by', return_value=MagicMock(all=MagicMock(return_value=[]))) as mock_filter_by:
            forms = self.handler.get_forms_by_rol('test_rol')
            self.assertEqual(forms, [])
            

    def test_upload_propietario(self):
        self.handler.propietario_handler.upload_propietario = MagicMock()
        self.handler.upload_propietario('test_propietario', 1)
        self.handler.propietario_handler.upload_propietario.assert_called_with('test_propietario', 1)

    def test_check_if_propietario_exists(self):
        self.handler.propietario_handler.check_if_propietario_exists = MagicMock(return_value=[])
        result = self.handler.check_if_propietario_exists('test_rut', 'test_rol', 2023)
        self.assertFalse(result)

    def test_upload_adquirientes(self):
        self.handler.propietario_handler.upload_adquirientes = MagicMock()
        self.handler.upload_adquirientes('test_adquirientes', 1)
        self.handler.propietario_handler.upload_adquirientes.assert_called_with('test_adquirientes', 1)

    @patch('app.models.db.session', autospec=True)
    def test_delete(self, mock_session):
        self.handler.delete_linked_propietarios = MagicMock()
        self.handler.delete_multipropietario = MagicMock()
        self.handler.delete(1)
        self.handler.delete_linked_propietarios.assert_called_with(1)
        self.handler.delete_multipropietario.assert_called_with(1)

    def test_get_linked_propietarios(self):
        self.handler.propietario_handler.get_by_multipropietario_id = MagicMock(return_value=[])
        result = self.handler.get_linked_propietarios(1)
        self.assertEqual(result, [])

    def test_get_pctje_derecho_propietario(self):
        self.handler.propietario_handler.check_if_propietario_exists = MagicMock(return_value=[])
        result = self.handler.get_pctje_derecho_propietario('test_rut', 'test_rol')
        self.assertEqual(result, 0)

    def test_get_posterior_forms(self):
        with patch.object(Multipropietario.query, 'filter', return_value=MagicMock(all=MagicMock(return_value=[]))) as mock_filter:
            forms = self.handler.get_posterior_forms({'fecha_inscripcion': date(2023, 1, 1), 'rol': 'test_rol'})
            self.assertEqual(forms, [])

    def test_multipropietario_to_dict(self):
        multipropietario = Multipropietario(rol='test_rol', fecha_inscripcion=date(2023, 1, 1), ano_inscripcion=2023, fojas='fojas', numero_inscripcion='nro_inscripcion', ano_vigencia_inicial=2023, ano_vigencia_final=2025)
        result = self.handler.multipropietario_to_dict(multipropietario)
        expected = {
            'id': multipropietario.id,
            'rol': 'test_rol',
            'fecha_inscripcion': date(2023, 1, 1),
            'ano_inscripcion': 2023,
            'fojas': 'fojas',
            'nro_inscripcion': 'nro_inscripcion',
            'ano_vigencia_inicial': 2023,
            'ano_vigencia_final': 2025
        }
        self.assertEqual(result, expected)

    @patch('app.models.db.session', autospec=True)
    def test_delete_multipropietario(self, mock_session):
        mock_session.commit = MagicMock()
        self.handler.delete_multipropietario(1)
        self.assertTrue(mock_session.commit.called)

    @patch('app.models.db.session', autospec=True)
    def test_delete_linked_propietarios(self, mock_session):
        mock_session.commit = MagicMock()
        self.handler.propietario_handler.get_by_multipropietario_id = MagicMock(return_value=[])
        self.handler.delete_linked_propietarios(1)
        self.assertTrue(self.handler.propietario_handler.get_by_multipropietario_id.called)




if __name__ == '__main__':
    unittest.main()