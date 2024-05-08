from app.models import *
from datetime import datetime

REGULARIZACION_DE_PATRIMONIO = 99
COMPRAVENTA = 8

class AlgoritmoMultipropietario:
    def __init__(self):
        pass

    def insert_into_multipropietario(self, form_data):
        self.execute_algoritmo_on(form_data)
        
    
    def execute_algoritmo_on(self, form_data):
        cne_code = form_data.get('cne', None)
        if cne_code == REGULARIZACION_DE_PATRIMONIO:
            self.algortimo_for_REGULARIZACION_PATRIMONIO(form_data)
        elif cne_code == COMPRAVENTA:
            # Logic for other CNE codes
            pass
        return True  
    
    
    
    def algortimo_for_REGULARIZACION_PATRIMONIO(self, form_data):
        rol = form_data.get('rol', None)
        fecha_inscripcion = form_data.get('fecha_inscripcion', None)
        nro_inscripcion = form_data.get('nro_inscripcion', None)
        fojas = form_data.get('fojas', None)

        enajenantes = form_data.get('enajenantes', [])
        adquirientes = form_data.get('adquirientes', [])
        
        existing_forms = self.get_existing_forms(rol)
        if not existing_forms:
            self.upload_form99(rol, fecha_inscripcion, fojas, nro_inscripcion, adquirientes)
        else:
            latest_form = max(existing_forms, key=lambda x: x.fecha_inscripcion)
            if fecha_inscripcion > latest_form.fecha_inscripcion:
                # If uploaded form is later, update ano_vigencia_final of previous form
                ano_vigencia_final = fecha_inscripcion.year - 1
                self.update_form(latest_form.id, ano_vigencia_final)
                self.upload_form99(rol, fecha_inscripcion, fojas, nro_inscripcion, adquirientes)
            else:
                # If uploaded form is earlier, reupload forms
                self.reupload_forms(form_data)
    
    def upload_form99(self, rol, fecha_inscripcion, fojas, nro_inscripcion, adquirientes):
        # No previous forms, upload normally
        ano_vigencia_inicial = fecha_inscripcion.year
        ano_inscripcion = fecha_inscripcion.year
        ano_vigencia_final = None
        # Upload the form normally and get the ID
        multipropietario_id = self.upload_form(rol, fecha_inscripcion, fojas, nro_inscripcion, ano_inscripcion, ano_vigencia_inicial, ano_vigencia_final, adquirientes)
        # Upload adquirientes using multipropietario_id
        self.upload_propietario(adquirientes, multipropietario_id)
    
    def get_existing_forms(self, rol):
        existing_forms = Multipropietario.query.filter_by(rol=rol).all()
        return existing_forms
    
    def upload_form(self, rol, fecha_inscripcion, fojas, nro_inscripcion, ano_inscripcion, ano_vigencia_inicial, ano_vigencia_final, adquirientes):
        new_form = Multipropietario(rol=rol, fecha_inscripcion=fecha_inscripcion, fojas=fojas, numero_inscripcion=nro_inscripcion, ano_inscripcion=ano_inscripcion, ano_vigencia_inicial=ano_vigencia_inicial, ano_vigencia_final=ano_vigencia_final)
        db.session.add(new_form)
        db.session.commit()
        return new_form.id  # Return the ID of the newly created Multipropietario entry
    
    def upload_propietario(self, adquirientes, multipropietario_id):
        for adquiriente in adquirientes:
            propietario = Propietario(rut=adquiriente['rut'], porcentaje_derecho=adquiriente['pctje_derecho'], multipropietario_id=multipropietario_id)
            db.session.add(propietario)
        db.session.commit()
    
    def update_form(self, form_id, ano_vigencia_final):
        form = Multipropietario.query.get(form_id)
        form.ano_vigencia_final = ano_vigencia_final
        db.session.commit()
    
    def reupload_forms(self, new_form_data):
        new_form_data['id'] = 0

        # Retrieve all forms with the same rol that are posterior to the new form being uploaded
        posterior_forms = Multipropietario.query.filter(
            (Multipropietario.fecha_inscripcion > new_form_data['fecha_inscripcion']) &
            (Multipropietario.rol == new_form_data['rol'])
        ).all()
        new_form_data
        # Append the new form to the list of posterior forms
        forms_to_reupload = [new_form_data] + [self.multipropietario_to_dict(form) for form in posterior_forms]
        print(forms_to_reupload)

        forms_to_reupload.sort(key=lambda x: x['fecha_inscripcion'])

        for form_data in forms_to_reupload:
            form_id = form_data['id']
            
            if form_id:
                adquirientes = []
                propietarios = Propietario.query.filter_by(multipropietario_id=form_id).all()
                for propietario in propietarios:
                    adquiriente = {}
                    adquiriente['rut'] = propietario.rut
                    adquiriente['pctje_derecho'] = propietario.porcentaje_derecho
                    adquirientes.append(adquiriente)
                    db.session.delete(propietario)
                db.session.commit()

                form_data['adquirientes'] = adquirientes

                form = Multipropietario.query.get(form_id)
                db.session.delete(form)
                db.session.commit()

        for form_data in forms_to_reupload:
            self.algortimo_for_REGULARIZACION_PATRIMONIO(form_data)
            db.session.commit()

    def multipropietario_to_dict(self, multipropietario):
        return {
            'id': multipropietario.id,
            'rol': multipropietario.rol,
            'fecha_inscripcion': multipropietario.fecha_inscripcion,
            'ano_inscripcion': multipropietario.ano_inscripcion,
            'fojas': multipropietario.fojas,
            'nro_inscripcion': multipropietario.numero_inscripcion
        }






