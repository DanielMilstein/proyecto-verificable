from flask import render_template, Blueprint, request, redirect
from app.forms import *
from app.models import formulario, db, multipropietario, persona

blueprint = Blueprint('pages', __name__)



################
#### routes ####
################


@blueprint.route('/')
def home():
    return "Hello World!"

@blueprint.route('/form', methods=['GET', 'POST'])
def form():
    form = MyForm()
    if request.method == 'POST' and form.validate_on_submit():

        # Save form data to the database
        new_form = formulario(
            numero_atencion=form.numero_atencion.data,
            cne=form.cne.data,
            rol=form.rol.data,
            fojas=form.fojas.data,
            fecha_inscripcion=form.fecha_inscripcion.data,
            numero_inscripcion=form.numero_inscripcion.data
        )
        db.session.add(new_form)
        db.session.commit()


        return redirect('/')
    return render_template('forms/form.html', title='Form', form=form)


@blueprint.route('/form_list', methods=['GET', 'POST'])
def form_list():
    # List all the forms in the database
    forms = formulario.query.all()



    return render_template('forms/form_list.html', title='Form List', forms=forms)