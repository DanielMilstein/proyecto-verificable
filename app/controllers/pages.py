from flask import render_template, Blueprint, request, redirect, flash
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
                # Redirect or respond as necessary
                return 'File Uploaded Successfully'
    return render_template('pages/home.html')


@blueprint.route('/form', methods=['GET', 'POST'])
def form():
    form = MyForm()
    if request.method == 'POST' and form.validate_on_submit():

        new_form = formulario(
            cne=form.cne.data,
            rol=form.rol.data,
            fojas=form.fojas.data,
            fecha_inscripcion=form.fecha_inscripcion.data,
            numero_inscripcion=form.numero_inscripcion.data
        )
        db.session.add(new_form)
        flash('Formulario creado con éxito')
        bien_raiz = bienRaiz.query.filter_by(rol=form.rol.data).first()
        if bien_raiz is None:
            bien_raiz = bienRaiz(form.rol.data)
            db.session.add(bien_raiz)
        else:
            pass


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
            else:
                pass

            # adquirienteImplicado = implicados(
            #     rut=adquiriente,
            #     porcentaje_derecho=adquirientesPorcentaje[adquirientesRut.index(adquiriente)],
            #     adquiriente=True
            # )
            # db.session.add(adquirienteImplicado)
            # new_form.implicados.append(adquirienteImplicado)

        for enajenante in enajenantesRut:
            enajenantePersona = persona.query.filter_by(rut=enajenante).first()
            if enajenantePersona is None:
                enajenantePersona = persona(enajenante)
                db.session.add(enajenantePersona)
            else:
                pass

        #     enajenanteImplicado = implicados(
        #         rut=enajenante,
        #         porcentaje_derecho=enajenantesPorcentaje[enajenantesRut.index(enajenante)],
        #         adquiriente=False
        #     )
        #     db.session.add(enajenanteImplicado)
        #     new_form.implicados.append(enajenanteImplicado)
 

            
        
        db.session.commit()


        return redirect('/')
    return render_template('forms/form.html', title='Form', form=form)


@blueprint.route('/form_list', methods=['GET', 'POST'])
def form_list():
    # List all the forms in the database
    forms = formulario.query.all()



    return render_template('forms/form_list.html', title='Form List', forms=forms)