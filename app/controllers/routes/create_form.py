from flask import render_template, request, redirect, flash
from ...forms import MyForm
from .form_utils import create_formulario_and_implicados, get_or_create_cne

def handle_form_submission():
    form = MyForm()

    if request.method == 'POST' and form.validate_on_submit():
        return process_form_submission(form)
    
    return render_template('form-F2890/form-F2890.html', title='Form', form=form)

def process_form_submission(form):
    cne_record = get_or_create_cne(form.cne.data.codigo_cne)

    form_data = {
        'cne': form.cne.data.codigo_cne,
        'comuna': form.comuna.data.codigo_comuna,
        'manzana': form.manzana.data,
        'predio': form.predio.data,
        'fojas': form.fojas.data,
        'fecha_inscripcion': form.fecha_inscripcion.data,
        'nro_inscripcion': form.numero_inscripcion.data,
    }

    adquirientes = [{'rut': rut, 'porcentaje_derecho': float(porcentaje)} for rut, porcentaje in zip(
        request.form.getlist('adquirientesRut[]'), 
        request.form.getlist('adquirientesPorcentaje[]')
    )]
    enajenantes = [{'rut': rut, 'porcentaje_derecho': float(porcentaje)} for rut, porcentaje in zip(
        request.form.getlist('enajenantesRut[]'), 
        request.form.getlist('enajenantesPorcentaje[]')
    )]

    create_formulario_and_implicados(form_data, adquirientes, enajenantes)
    return redirect('/')
