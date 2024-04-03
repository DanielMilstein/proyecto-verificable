from flask import render_template, Blueprint, request, redirect, flash, jsonify
from app.forms import *
from app.models import *
import json


blueprint = Blueprint('pages', __name__)



################
#### routes ####
################


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'upload_file' in request.files:
            file = request.files['upload_file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                return 'File Uploaded Successfully'
    return render_template('home.html')


@blueprint.route('/form-F2890', methods=['GET', 'POST'])
def form():
    form = MyForm()

    cnes = CNE.query.all()
    comunas = Comuna.query.all()

    if request.method == 'POST' and form.validate_on_submit():


        cne_record = CNE.query.filter_by(codigo_cne=str(form.cne.data)).first()
        

        if cne_record is None:
            cne_record = CNE(form.cne.data, '')
            db.session.add(cne_record)
            db.session.commit()
        else:
            pass


        rol_search = f'{form.comuna.data}-{form.manzana.data}-{form.predio.data}'
        print(rol_search)
        bien_raiz = BienRaiz.query.filter_by(rol=rol_search).first()
        if bien_raiz is None:
            bien_raiz = BienRaiz(form.comuna.data, form.manzana.data, form.predio.data)
            db.session.add(bien_raiz)
        else:
            pass



        new_form = Formulario(
            cne=form.cne.data,
            rol=bien_raiz.rol,
            fojas=form.fojas.data,
            fecha_inscripcion=form.fecha_inscripcion.data,
            numero_inscripcion=form.numero_inscripcion.data
        )
        db.session.add(new_form)            



        adquirientesRut = request.form.getlist('adquirientesRut[]')
        adquirientesPorcentaje = request.form.getlist('adquirientesPorcentaje[]')
        try: 
            enajenantesRut = request.form.getlist('enajenantesRut[]')
            enajenantesPorcentaje = request.form.getlist('enajenantesPorcentaje[]')
        except:
            pass


        for adquiriente in adquirientesRut:
            adquirientePersona = Persona.query.filter_by(rut=adquiriente).first()
            if adquirientePersona is None:
                adquirientePersona = Persona(adquiriente)
                db.session.add(adquirientePersona)
                db.session.commit()
            else:
                pass

            adquirienteImplicado = Implicados(
                rut=adquiriente,
                numero_atencion=new_form.numero_atencion,
                porcentaje_derecho=adquirientesPorcentaje[adquirientesRut.index(adquiriente)],
                adquiriente=True
            )
            db.session.add(adquirienteImplicado)


        for enajenante in enajenantesRut:
            enajenantePersona = Persona.query.filter_by(rut=enajenante).first()
            if enajenantePersona is None:
                enajenantePersona = Persona(enajenante)
                db.session.add(enajenantePersona)
                db.session.commit() 
            else:
                pass

            enajenanteImplicado = Implicados(
                rut=enajenante,
                numero_atencion=new_form.numero_atencion,
                porcentaje_derecho=enajenantesPorcentaje[enajenantesRut.index(enajenante)],
                adquiriente=False
            )
            db.session.add(enajenanteImplicado)

 

            
        
        db.session.commit()


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



@blueprint.route('/buscar_multipropietarios', methods=['GET','POST'])
def search_multipropietarios():
    if request.method == 'POST':
        año = request.form.get('año')
        comuna_codigo = request.form.get('comuna')
        manzana = request.form.get('manzana')
        predio = request.form.get('predio')
    elif request.method == 'GET':
        año = request.args.get('año')
        comuna_codigo = request.args.get('comuna')
        manzana = request.args.get('manzana')
        predio = request.args.get('predio')


    if None in (año, comuna_codigo, manzana, predio):
        return render_template('/multipropietario/multipropietario.html', propietarios_info=None)

    comuna_obj = Comuna.query.filter_by(codigo_comuna=comuna_codigo).first()
    comuna_name = comuna_obj.nombre_comuna

    bien_raiz_id = BienRaiz.query.filter(
        BienRaiz.comuna == int(comuna_codigo),
        BienRaiz.manzana == int(manzana),
        BienRaiz.predio == int(predio)
    ).with_entities(BienRaiz.rol).scalar()
    
    query = Multipropietario.query.filter(
        Multipropietario.ano_vigencia_inicial <= año,
        (Multipropietario.ano_vigencia_final >= año) | (Multipropietario.ano_vigencia_final == None),
        Multipropietario.rol.like(bien_raiz_id)
    )
    multipropietarios = query.all()
   
    propietarios_info = []
    for multi_ppropietario in multipropietarios:
        propietarios = Propietario.query.filter_by(multipropietario_id=multi_ppropietario.id).all()
        for propietario in propietarios:
            propietarios_info.append({
                'nombre_propietario': 'Random Name', 
                'rut_run': propietario.rut,
                'porcentaje_derecho': propietario.porcentaje_derecho,
                'comuna': comuna_name,
                'manzana': manzana,
                'predio': predio,
                'año_vigencia_inicial': multi_ppropietario.ano_vigencia_inicial,
                'año_vigencia_final': multi_ppropietario.ano_vigencia_final
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
            error_list_when_uploading_json = []  
            
            for form_data in json_data.get('F2890', []):
                try:
                    cne_code = form_data.get('CNE')
                    
                    
                    if cne_code not in [8, 99]:
                        error_list_when_uploading_json.append(f"Invalid CNE code: {cne_code}")
                        continue 
                    
                    
                    comuna_code = form_data.get('bienRaiz', {}).get('comuna')
                    comuna = Comuna.query.filter_by(codigo_comuna=comuna_code).first()
                    if not comuna:
                        error_list_when_uploading_json.append(f'Comuna with code {comuna_code} not found')
                        continue  
                    
                    bien_raiz_data = form_data.get('bienRaiz', {})
                    manzana = bien_raiz_data.get('manzana', '')
                    predio = bien_raiz_data.get('predio', '')
                    rol_search = f'{comuna_code}-{manzana}-{predio}'
                    bien_raiz = BienRaiz.query.filter_by(rol=rol_search).first()
                    if not bien_raiz:
                        bien_raiz = BienRaiz(comuna=comuna_code, manzana=manzana, predio=predio)
                        db.session.add(bien_raiz)


                    new_form = Formulario(
                        cne=cne_code,
                        rol=bien_raiz.rol,
                        fojas=form_data.get('fojas', ''),
                        fecha_inscripcion=form_data.get('fechaInscripcion', None),
                        numero_inscripcion=form_data.get('nroInscripcion', None)
                    )
                    db.session.add(new_form)


                    for adquirente_data in form_data.get('adquirentes', []):
                        rut = adquirente_data.get('RUNRUT')
                        porcentaje_derecho = adquirente_data.get('porcDerecho')
                        adquiriente = Persona.query.filter_by(rut=rut).first()
                        if not adquiriente:
                            adquiriente = Persona(rut=rut)
                            db.session.add(adquiriente)
                        adquiriente_implicado = Implicados(
                            numero_atencion=new_form.numero_atencion,
                            rut=rut,
                            adquiriente=True,
                            porcentaje_derecho=porcentaje_derecho
                        )
                        db.session.add(adquiriente_implicado)


                    for enajenante_data in form_data.get('enajenantes', []):
                        rut = enajenante_data.get('RUNRUT')
                        porcentaje_derecho = enajenante_data.get('porcDerecho')
                        enajenante = Persona.query.filter_by(rut=rut).first()
                        if not enajenante:
                            enajenante = Persona(rut=rut)
                            db.session.add(enajenante)
                        enajenante_implicado = Implicados(
                            numero_atencion=new_form.numero_atencion,
                            rut=rut,
                            adquiriente=False,
                            porcentaje_derecho=porcentaje_derecho
                        )
                        db.session.add(enajenante_implicado)

                    db.session.commit()

                except Exception as e:
                    db.session.rollback()
                    error_list_when_uploading_json.append(f"Error processing form data: {e}")
            
            if error_list_when_uploading_json:
                return jsonify({'success': False, 'errors': error_list_when_uploading_json})
            else:
                return jsonify({'success': True})
        
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Invalid JSON format: {e}'})

    else:
        return jsonify({'error': 'Invalid file type'})
