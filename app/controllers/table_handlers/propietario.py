from app.models import Propietario, db

class PropietarioTableHandler:
    def upload_propietario(self, adquirientes, multipropietario_id):
        for adquiriente in adquirientes:
            propietario = Propietario(rut=adquiriente['rut'], porcentaje_derecho=adquiriente['pctje_derecho'], multipropietario_id=multipropietario_id)
            db.session.add(propietario)
        db.session.commit()

    def get_by_multipropietario_id(self, multipropietario_id):
        return Propietario.query.filter_by(multipropietario_id=multipropietario_id).all()

    def delete(self, propietario):
        db.session.delete(propietario)
        db.session.commit()