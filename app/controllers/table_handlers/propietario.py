from app.models import Propietario, db

class PropietarioTableHandler:
    def upload_propietario(self, propietario, multipropietario_id):
        nuevo_propietario = Propietario(rut=propietario['rut'], porcentaje_derecho=propietario['porcentaje_derecho'], multipropietario_id=multipropietario_id)
        db.session.add(nuevo_propietario)
        db.session.commit()

    def upload_adquirientes(self, adquirientes, multipropietario_id):
        for adquiriente in adquirientes:
            propietario = Propietario(rut=adquiriente['rut'], porcentaje_derecho=adquiriente['porcentaje_derecho'], multipropietario_id=multipropietario_id)
            db.session.add(propietario)
        db.session.commit()

    def get_by_multipropietario_id(self, multipropietario_id):
        return Propietario.query.filter_by(multipropietario_id=multipropietario_id).all()

    def delete(self, propietario):
        db.session.delete(propietario)
        db.session.commit()

    def check_if_propietario_exists(self, rut):
        propietarios = Propietario.query.filter_by(rut=rut).all()
        return propietarios