from flask import render_template
from ...models import Formulario, BienRaiz, Comuna, CNE, Implicados
from .form_utils import get_formulario_by_numero_atencion, get_bien_raiz_by_rol, get_comuna_by_codigo, get_cne_by_codigo, get_implicados_by_numero_atencion

def get_form_detail(numero_atencion):
    formulario = get_formulario_by_numero_atencion(numero_atencion)

    if not formulario:
        return render_template('404.html'), 404

    bien_raiz = get_bien_raiz_by_rol(formulario.rol)
    comuna = get_comuna_by_codigo(bien_raiz.comuna)
    cne = get_cne_by_codigo(formulario.cne)
    adquirientes = get_implicados_by_numero_atencion(numero_atencion, adquiriente=True)
    enajenantes = get_implicados_by_numero_atencion(numero_atencion, adquiriente=False)

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

    return render_template('form-list/form-detail.html', form_details=form_details)
