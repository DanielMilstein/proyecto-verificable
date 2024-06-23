from ...models import BienRaiz, Persona, Formulario, Implicados, CNE, Comuna, db
from ..algoritmo_multipropietario.insert_into_multipropietario import HandleAlgoritmoMultipropietario

def get_formulario_by_numero_atencion(numero_atencion):
    return Formulario.query.filter_by(numero_atencion=numero_atencion).first()

def get_bien_raiz_by_rol(rol):
    return BienRaiz.query.filter_by(rol=rol).first()

def get_comuna_by_codigo(codigo_comuna):
    return Comuna.query.filter_by(codigo_comuna=codigo_comuna).first()

def get_cne_by_codigo(codigo_cne):
    return CNE.query.filter_by(codigo_cne=codigo_cne).first()

def get_implicados_by_numero_atencion(numero_atencion, adquiriente):
    return Implicados.query.filter_by(numero_atencion=numero_atencion, adquiriente=adquiriente).all()

def get_or_create_cne(codigo_cne):
    cne_record = CNE.query.filter_by(codigo_cne=str(codigo_cne)).first()
    if cne_record is None:
        cne_record = CNE(codigo_cne, '')
        db.session.add(cne_record)
        db.session.commit()
    return cne_record

def get_or_create_bien_raiz(comuna_code, manzana, predio):
    bien_raiz = BienRaiz.query.filter_by(
        comuna=comuna_code,
        manzana=manzana,
        predio=predio
    ).first()
    if not bien_raiz:
        bien_raiz = BienRaiz(comuna_code, manzana, predio)
        db.session.add(bien_raiz)
        db.session.commit()
    return bien_raiz

def get_or_create_persona(rut):
    persona = Persona.query.filter_by(rut=rut).first()
    if not persona:
        persona = Persona(rut)
        db.session.add(persona)
        db.session.commit()
    return persona

def create_implicados(form, personas, adquiriente_flag):
    for persona in personas:
        rut = persona['rut']
        porcentaje_derecho = persona['porcentaje_derecho']
        persona_obj = get_or_create_persona(rut)
        implicado = Implicados(
            rut=rut,
            numero_atencion=form.numero_atencion,
            porcentaje_derecho=porcentaje_derecho,
            adquiriente=adquiriente_flag
        )
        db.session.add(implicado)
    db.session.commit()

def upload_to_multipropietario(form_data, processed_entries=None):
    if processed_entries is None:
        processed_entries = set()

    multipropietario = HandleAlgoritmoMultipropietario()
    success = multipropietario.insert_into_multipropietario(form_data, processed_entries)
    if isinstance(success, list):
        for entry in success:
            entry_key = (entry['rol'], entry['fecha_inscripcion'], entry['fojas'], entry['nro_inscripcion'])
            if entry_key not in processed_entries:
                processed_entries.add(entry_key)
                upload_to_multipropietario(entry, processed_entries)
    else:
        if success:
            print("Data inserted into 'multipropietario' successfully.")
        else:
            print("Failed to insert data into 'multipropietario'.")

def create_formulario_and_implicados(form_data, adquirientes, enajenantes):
    cne_code = form_data['cne']
    comuna_code = form_data['comuna']
    manzana = form_data['manzana']
    predio = form_data['predio']

    bien_raiz = get_or_create_bien_raiz(comuna_code, manzana, predio)

    new_form = Formulario(
        cne=cne_code,
        rol=f'{comuna_code}-{manzana}-{predio}',
        fojas=form_data['fojas'],
        fecha_inscripcion=form_data['fecha_inscripcion'],
        numero_inscripcion=form_data['nro_inscripcion']
    )
    db.session.add(new_form)
    db.session.commit()

    create_implicados(new_form, adquirientes, True)
    create_implicados(new_form, enajenantes, False)

    form_data = {
        'cne': cne_code,
        'rol': f'{comuna_code}-{manzana}-{predio}',
        'fecha_inscripcion': form_data['fecha_inscripcion'],
        'nro_inscripcion': form_data['nro_inscripcion'],
        'fojas': form_data['fojas'],
        'enajenantes': enajenantes,
        'adquirientes': adquirientes
    }

    upload_to_multipropietario(form_data)
    db.session.commit()