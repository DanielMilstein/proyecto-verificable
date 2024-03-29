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
    return render_template('home.html')


@blueprint.route('/form-F2890', methods=['GET', 'POST'])
def form():
    form = MyForm()
    if request.method == 'POST' and form.validate_on_submit():


        cne_record = CNE.query.filter_by(codigo_cne=form.cne.data).first()

        if cne_record is None:
            cne_record = CNE(form.cne.data, '')
            db.session.add(cne_record)
            db.session.commit()
        else:
            pass

        comuna_record = comuna.query.filter_by(codigo_comuna=form.rol.data.split('-')[0]).first()

        if comuna_record is None:
            comuna_record = comuna(form.rol.data.split('-')[0], '')
            db.session.add(comuna_record)
            db.session.commit()
        else:
            pass

        bien_raiz = bienRaiz.query.filter_by(rol=form.rol.data).first()
        if bien_raiz is None:
            bien_raiz = bienRaiz(form.rol.data)
            db.session.add(bien_raiz)
        else:
            pass



        new_form = formulario(
            cne=form.cne.data,
            rol=form.rol.data,
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



    return render_template('forms/form_list.html', title='Form List', forms=forms)