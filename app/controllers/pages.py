from flask import render_template, Blueprint, request, redirect, flash, jsonify
from app.forms import *
from app.models import *
import json
from datetime import datetime
from .algoritmo_multipropietario.insert_into_multipropietario import HandleAlgoritmoMultipropietario

blueprint = Blueprint('pages', __name__)


################
#### routes ####
################


@blueprint.route('/', methods=['GET', 'POST'])
def show_home_page():
    if is_file_upload_request():
        return handle_file_upload()
    return render_template('home.html')

def is_file_upload_request():
    return request.method == 'POST' and 'upload_file' in request.files

def handle_file_upload():
    file = request.files['upload_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        save_uploaded_file(file)
        return 'File Uploaded Successfully'
    flash('No file uploaded')
    return redirect(request.url)

def save_uploaded_file(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

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

from datetime import datetime

from datetime import datetime

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


@blueprint.route('/form-F2890', methods=['GET', 'POST'])
def form():
    form = MyForm()

    if request.method == 'POST' and form.validate_on_submit():
        cne_record = CNE.query.filter_by(codigo_cne=str(form.cne.data.codigo_cne)).first()
        if cne_record is None:
            cne_record = CNE(form.cne.data, '')
            db.session.add(cne_record)
            db.session.commit()

        form_data = {
            'cne': form.cne.data.codigo_cne,
            'comuna': form.comuna.data.codigo_comuna,
            'manzana': form.manzana.data,
            'predio': form.predio.data,
            'fojas': form.fojas.data,
            'fecha_inscripcion':form.fecha_inscripcion.data,
            'nro_inscripcion': form.numero_inscripcion.data,
        }

        adquirientes = [{'rut': rut, 'porcentaje_derecho': float(pctje)} for rut, pctje in zip(
            request.form.getlist('adquirientesRut[]'), 
            request.form.getlist('adquirientesPorcentaje[]')
        )]
        print(request.form)
        enajenantes = [{'rut': rut, 'porcentaje_derecho': float(pctje)} for rut, pctje in zip(
            request.form.getlist('enajenantesRut[]'), 
            request.form.getlist('enajenantesPorcentaje[]')
        )]

        create_formulario_and_implicados(form_data, adquirientes, enajenantes)
        return redirect('/')
    return render_template('form-F2890/form-F2890.html', title='Form', form=form)


@blueprint.route('/form-list', methods=['GET', 'POST'])
def form_list():
    forms = Formulario.query.all()
    for form in forms:
        nombre_cne = CNE.query.filter_by(codigo_cne=form.cne).first().nombre_cne
        form.nombre_cne = nombre_cne

    return render_template('form-list/form-list.html', title='Form List', forms=forms)


@blueprint.route('/autocomplete')
def autocomplete():
    search = request.args.get('q', '')
    suggestions = [{'id': item.codigo_comuna, 'text': item.nombre_comuna} for item in Comuna.query.filter(Comuna.nombre_comuna.contains(search)).all()]
    return jsonify(results=suggestions)


@blueprint.route('/form-F2890/<int:numero_atencion>')
def form_detail(numero_atencion):
    formulario = Formulario.query.filter_by(numero_atencion=numero_atencion).first()

    bien_raiz = BienRaiz.query.filter_by(rol=formulario.rol).first()
    comuna = Comuna.query.filter_by(codigo_comuna=bien_raiz.comuna).first()

    cne = CNE.query.filter_by(codigo_cne=formulario.cne).first()

    adquirientes = Implicados.query.filter_by(numero_atencion=numero_atencion, adquiriente=1).all()
    enajenantes = Implicados.query.filter_by(numero_atencion=numero_atencion, adquiriente=0).all()

    form_details = {
        'numero_atencion': formulario.numero_atencion,
        'fojas': formulario.fojas,
        'fecha_inscripcion': formulario.fecha_inscripcion,
        'numero_inscripcion': formulario.numero_inscripcion,
        'bien_raiz': bien_raiz,
        'nombre_comuna': comuna.nombre_comuna,
        'cne': cne,
        'adquirientes': adquirientes,
        'enajenantes': enajenantes
    }

    if formulario:
        return render_template('form-list/form-detail.html', form_details=form_details)
    else:
        return render_template('404.html'), 404

@blueprint.route('/buscar_multipropietarios', methods=['GET','POST'])
def search_multipropietarios():
    if request.method == 'POST':
        year = request.form.get('año')
        comuna_codigo = request.form.get('comuna')
        manzana = request.form.get('manzana')
        predio = request.form.get('predio')
    elif request.method == 'GET':
        year = request.args.get('año')
        comuna_codigo = request.args.get('comuna')
        manzana = request.args.get('manzana')
        predio = request.args.get('predio')

    if None in (year, comuna_codigo, manzana, predio):
        return render_template('/multipropietario/multipropietario.html', propietarios_info=None)
    elif '' in (year, comuna_codigo, manzana, predio):
        return render_template('/multipropietario/multipropietario.html', propietarios_info=None)

    comuna_obj = Comuna.query.filter_by(codigo_comuna=comuna_codigo).first()
    comuna_name = comuna_obj.nombre_comuna

    bien_raiz_id = BienRaiz.query.filter(
        BienRaiz.comuna == int(comuna_codigo),
        BienRaiz.manzana == int(manzana),
        BienRaiz.predio == int(predio)
    ).with_entities(BienRaiz.rol).scalar()
    
    if not bien_raiz_id:
        return render_template('/multipropietario/multipropietario.html', propietarios_info=None)
    query = Multipropietario.query.filter(
        Multipropietario.ano_vigencia_inicial <= year,
        (Multipropietario.ano_vigencia_final >= year) | (Multipropietario.ano_vigencia_final == None),
        Multipropietario.rol.like(bien_raiz_id)
    )
    multipropietarios = query.all()
   
    propietarios_info = []
    for multi_propietario in multipropietarios:
        propietarios = Propietario.query.filter_by(multipropietario_id=multi_propietario.id).all()
        for propietario in propietarios:
            propietarios_info.append({
                'nombre_propietario': 'Random Name', 
                'rut_run': propietario.rut,
                'porcentaje_derecho': propietario.porcentaje_derecho,
                'comuna': comuna_name,
                'manzana': manzana,
                'predio': predio,
                'fecha_inscripcion': multi_propietario.fecha_inscripcion,
                'ano_inscripcion': multi_propietario.ano_inscripcion,
                'numero_inscripcion': multi_propietario.numero_inscripcion,
                'fojas': multi_propietario.fojas,
                'año_vigencia_inicial': multi_propietario.ano_vigencia_inicial,
                'año_vigencia_final': multi_propietario.ano_vigencia_final
            })
    return render_template('/multipropietario/multipropietario.html', propietarios_info=propietarios_info)

@blueprint.route('/json-interpreter', methods=['POST'])
def json_interpreter():
    if 'upload_file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['upload_file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and file.filename.endswith('.json'):
        try:
            json_data = json.loads(file.read())
            errors = []
            success_messages = []

            forms_to_process = json_data.get('F2890', [])
            forms_to_process.sort(key=lambda x: datetime.strptime(x.get('fechaInscripcion', ''), '%Y-%m-%d'))

            for form_data in forms_to_process:
                try:
                    cne_code = form_data.get('CNE')

                    if cne_code not in [8, 99]:
                        errors.append(f"Invalid CNE code: {cne_code}")
                        continue

                    adquirientes = [
                        {'rut': a.get('RUNRUT'), 'porcentaje_derecho': a.get('porcDerecho')}
                        for a in form_data.get('adquirentes', [])
                    ]

                    enajenantes = [
                        {'rut': e.get('RUNRUT'), 'porcentaje_derecho': e.get('porcDerecho')}
                        for e in form_data.get('enajenantes', [])
                    ]

                    form_data = {
                        'cne': form_data.get('CNE'),
                        'comuna': form_data['bienRaiz'].get('comuna'),
                        'manzana': form_data['bienRaiz'].get('manzana', ''),
                        'predio': form_data['bienRaiz'].get('predio', ''),
                        'fojas': form_data.get('fojas', ''),
                        'fecha_inscripcion': datetime.strptime(form_data.get('fechaInscripcion', ''), '%Y-%m-%d').date(),
                        'nro_inscripcion': form_data.get('nroInscripcion', None)
                    }

                    create_formulario_and_implicados(form_data, adquirientes, enajenantes)

                    success_messages.append(f"Form data processed successfully: {form_data}")

                except Exception as e:
                    db.session.rollback()
                    errors.append(f"Error processing form data: {e}")

            return render_template('json-interpreter/json-interpreter.html', success=True, success_messages=success_messages, errors=errors)

        except json.JSONDecodeError as e:
            return jsonify({'error': f'Invalid JSON format: {e}'})

    else:
        return jsonify({'error': 'Invalid file type'})