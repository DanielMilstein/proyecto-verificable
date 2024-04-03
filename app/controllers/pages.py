from flask import render_template, Blueprint, request, redirect, flash, jsonify
from app.forms import *
from app.models import *


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


        cne_record = CNE.query.filter_by(codigo_cne=str(form.cne.data.codigo_cne)).first()

        if cne_record is None:
            cne_record = CNE(form.cne.data, '')
            db.session.add(cne_record)
            db.session.commit()
        else:
            pass


        existing_bien_raiz = BienRaiz.query.filter_by(
            comuna=form.comuna.data.codigo_comuna,
            manzana=form.manzana.data,
            predio=form.predio.data
        ).first()

        if existing_bien_raiz is None:
            bien_raiz = BienRaiz(form.comuna.data.codigo_comuna, form.manzana.data, form.predio.data)
            db.session.add(bien_raiz)
            db.session.commit()
        else:
            bien_raiz = existing_bien_raiz


        new_form = Formulario(
            cne=form.cne.data.codigo_cne,
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
    elif '' in (año, comuna_codigo, manzana, predio):
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
        Multipropietario.ano_vigencia_inicial <= año,
        (Multipropietario.ano_vigencia_final >= año) | (Multipropietario.ano_vigencia_final == None),
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
                'año_vigencia_inicial': multi_propietario.ano_vigencia_inicial,
                'año_vigencia_final': multi_propietario.ano_vigencia_final
            })

    return render_template('/multipropietario/multipropietario.html', propietarios_info=propietarios_info)
