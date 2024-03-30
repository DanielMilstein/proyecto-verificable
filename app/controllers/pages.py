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
    comunas = comuna.query.all()

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
        bien_raiz = bienRaiz.query.filter_by(rol=rol_search).first()
        if bien_raiz is None:
            bien_raiz = bienRaiz(form.comuna.data, form.manzana.data, form.predio.data)
            db.session.add(bien_raiz)
        else:
            pass



        new_form = formulario(
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
            adquirientePersona = persona.query.filter_by(rut=adquiriente).first()
            if adquirientePersona is None:
                adquirientePersona = persona(adquiriente)
                db.session.add(adquirientePersona)
                db.session.commit()
            else:
                pass

            adquirienteImplicado = implicados(
                rut=adquiriente,
                numero_atencion=new_form.numero_atencion,
                porcentaje_derecho=adquirientesPorcentaje[adquirientesRut.index(adquiriente)],
                adquiriente=True
            )
            db.session.add(adquirienteImplicado)
            # new_form.implicados.append(adquirienteImplicado)

        for enajenante in enajenantesRut:
            enajenantePersona = persona.query.filter_by(rut=enajenante).first()
            if enajenantePersona is None:
                enajenantePersona = persona(enajenante)
                db.session.add(enajenantePersona)
                db.session.commit() 
            else:
                pass

            enajenanteImplicado = implicados(
                rut=enajenante,
                numero_atencion=new_form.numero_atencion,
                porcentaje_derecho=enajenantesPorcentaje[enajenantesRut.index(enajenante)],
                adquiriente=False
            )
            db.session.add(enajenanteImplicado)
            # new_form.implicados.append(enajenanteImplicado)
 

            
        
        db.session.commit()


        return redirect('/')
    return render_template('form-F2890/form-F2890.html', title='Form', form=form)


@blueprint.route('/form_list', methods=['GET', 'POST'])
def form_list():
    # List all the forms in the database
    forms = formulario.query.all()



    return render_template('form-list/form-list.html', title='Form List', forms=forms)


@blueprint.route('/autocomplete')
def autocomplete():
    search = request.args.get('q', '')
    # Query your database for search suggestions based on the `search` term
    # This is a simplified example; adapt it to your actual data source
    suggestions = [{'id': item.codigo_comuna, 'text': item.nombre_comuna} for item in comuna.query.filter(comuna.nombre_comuna.contains(search)).all()]
    return jsonify(results=suggestions)



@blueprint.route('/buscar_multipropietarios', methods=['GET','POST'])
def search_multipropietarios():
    # Get inputs from the form
    año = request.form.get('año')
    comuna_name = request.form.get('comuna')
    manzana = request.form.get('manzana')
    predio = request.form.get('predio')

    # Check if any of the inputs are None
    if None in (año, comuna_name, manzana, predio):
        # If any input is None, render the template without performing the search
        return render_template('/multipropietario/multipropietario.html', propietarios_info=None)
    
    
    # Find comuna based on comuna_name
    comuna_obj = comuna.query.filter_by(nombre_comuna=comuna_name).first()
    comuna_codigo = comuna_obj.codigo_comuna

    # Query multipropietario table based on the given inputs
    query = multipropietario.query.filter(
        multipropietario.ano_vigencia_inicial <= año,
        (multipropietario.ano_vigencia_final >= año) | (multipropietario.ano_vigencia_final == None),
        multipropietario.rol.like(f'%{comuna_codigo}/{manzana}/{predio}%')
    )
    multipropietarios = query.all()

    # Retrieve extra information from propietario table using multipropietario_id's
    propietarios_info = []
    for mp in multipropietarios:
        propietarios = propietario.query.filter_by(multipropietario_id=mp.id).all()
        for prop in propietarios:
            propietarios_info.append({
                'nombre_propietario': 'Random Name',  # You can generate random names here
                'rut_run': prop.rut,
                'porcentaje_derecho': prop.porcentaje_derecho,
                'comuna': comuna_name,
                'manzana': manzana,
                'predio': predio,
                'año_vigencia_inicial': mp.ano_vigencia_inicial,
                'año_vigencia_final': mp.ano_vigencia_final
            })

    return render_template('/multipropietario/multipropietario.html', propietarios_info=propietarios_info)
