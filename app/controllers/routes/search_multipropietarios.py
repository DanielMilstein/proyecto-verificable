from flask import request, render_template
from ...models import Comuna, BienRaiz, Multipropietario, Propietario

def handle_search_multipropietarios():
    year, comuna_codigo, manzana, predio = get_search_parameters()
    endpoint = '/multipropietario/multipropietario.html'
    if not validate_search_parameters(year, comuna_codigo, manzana, predio):
        return render_template(endpoint, propietarios_info=None)

    comuna_name = get_comuna_name(comuna_codigo)
    bien_raiz_id = get_bien_raiz_id(comuna_codigo, manzana, predio)

    if not bien_raiz_id:
        return render_template(endpoint, propietarios_info=None)

    multipropietarios = get_multipropietarios(year, bien_raiz_id)
    propietarios_info = get_propietarios_info(multipropietarios, comuna_name, manzana, predio)

    return render_template(endpoint, propietarios_info=propietarios_info)

def get_search_parameters():
    if request.method == 'POST':
        return (
            request.form.get('año'),
            request.form.get('comuna'),
            request.form.get('manzana'),
            request.form.get('predio')
        )
    return (
        request.args.get('año'),
        request.args.get('comuna'),
        request.args.get('manzana'),
        request.args.get('predio')
    )

def validate_search_parameters(year, comuna_codigo, manzana, predio):
    return None not in (year, comuna_codigo, manzana, predio) and '' not in (year, comuna_codigo, manzana, predio)

def get_comuna_name(comuna_codigo):
    comuna_obj = Comuna.query.filter_by(codigo_comuna=comuna_codigo).first()
    return comuna_obj.nombre_comuna if comuna_obj else 'Unknown'

def get_bien_raiz_id(comuna_codigo, manzana, predio):
    return BienRaiz.query.filter(
        BienRaiz.comuna == int(comuna_codigo),
        BienRaiz.manzana == int(manzana),
        BienRaiz.predio == int(predio)
    ).with_entities(BienRaiz.rol).scalar()

def get_multipropietarios(year, bien_raiz_id):
    return Multipropietario.query.filter(
        Multipropietario.ano_vigencia_inicial <= year,
        (Multipropietario.ano_vigencia_final >= year) | (Multipropietario.ano_vigencia_final == None),
        Multipropietario.rol.like(bien_raiz_id)
    ).all()

def get_propietarios_info(multipropietarios, comuna_name, manzana, predio):
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
    return propietarios_info
