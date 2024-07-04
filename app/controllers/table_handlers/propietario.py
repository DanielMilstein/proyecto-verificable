from app.models import Propietario, db

class PropietarioTableHandler:
    def upload_propietario(self, propietario, multipropietario_id):
        nuevo_propietario = Propietario(rut=propietario['rut'], porcentaje_derecho=propietario['porcentaje_derecho'], multipropietario_id=multipropietario_id)
        db.session.add(nuevo_propietario)
        db.session.commit()

    def upload_adquirientes(self, adquirientes, multipropietario_id):
        suma_porcentaje_derecho = self.check_valid_porcentaje_derecho(adquirientes)
        if suma_porcentaje_derecho > 100:
            adquirientes = self._scale_porcentaje_derecho(adquirientes, suma_porcentaje_derecho)

        self._save_adquirientes(adquirientes, multipropietario_id)
        db.session.commit()

    def _scale_porcentaje_derecho(self, adquirientes, suma_porcentaje_derecho):
        scale = 100 / suma_porcentaje_derecho
        for adquiriente in adquirientes:
            adquiriente['porcentaje_derecho'] *= scale
        return adquirientes

    def _save_adquirientes(self, adquirientes, multipropietario_id):
        for adquiriente in adquirientes:
            propietario = self._create_propietario(adquiriente, multipropietario_id)
            db.session.add(propietario)

    def _create_propietario(self, adquiriente, multipropietario_id):
        return Propietario(
            rut=adquiriente['rut'],
            porcentaje_derecho=adquiriente['porcentaje_derecho'],
            multipropietario_id=multipropietario_id
        )

    def check_valid_porcentaje_derecho(self, adquirientes):
        suma_porcentaje_derecho = 0
        for adquiriente in adquirientes:
            suma_porcentaje_derecho += adquiriente['porcentaje_derecho']
        return suma_porcentaje_derecho

    def get_by_multipropietario_id(self, multipropietario_id):
        return Propietario.query.filter_by(multipropietario_id=multipropietario_id).all()

    def delete(self, propietario):
        db.session.delete(propietario)
        db.session.commit()

    def check_if_propietario_exists(self, rut):
        propietarios = Propietario.query.filter_by(rut=rut).all()
        return propietarios