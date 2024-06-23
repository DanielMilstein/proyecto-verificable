from flask import render_template
from ...models import Formulario, CNE

def get_form_list():
    forms = Formulario.query.all()
    for form in forms:
        nombre_cne = get_cne_name(form.cne)
        form.nombre_cne = nombre_cne

    return render_template('form-list/form-list.html', title='Form List', forms=forms)

def get_cne_name(codigo_cne):
    cne_record = CNE.query.filter_by(codigo_cne=codigo_cne).first()
    return cne_record.nombre_cne if cne_record else 'Unknown'
