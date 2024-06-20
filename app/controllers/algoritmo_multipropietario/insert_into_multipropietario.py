from .algoritmos.regularizacion_patrimonio.algoritmo_regularizacion_patrimonio import AlgoritmoRegularizacionPatrimonio
from .algoritmos.compraventa.algoritmo_compraventa import AlgoritmoCompraventa
from ...models import Formulario, Implicados

REGULARIZACION_DE_PATRIMONIO = 99
COMPRAVENTA = 8
class ExecutelgoritmoMultipropietario:
    def __init__(self):
        self.regularizacion_algorithm = AlgoritmoRegularizacionPatrimonio()
        self.compraventa_algorithm = AlgoritmoCompraventa()

    def execute(self, cne_code, form_data, processed_entries):
        if cne_code == REGULARIZACION_DE_PATRIMONIO:
            return self.regularizacion_algorithm.apply_algorithm_on(form_data, processed_entries)
        elif cne_code == COMPRAVENTA:
            return self.compraventa_algorithm.apply_algorithm_on(form_data)
        else:
            return False

class HandleAlgoritmoMultipropietario:
    def __init__(self):
        self.algorithm_executor = ExecutelgoritmoMultipropietario()

    def insert_into_multipropietario(self, form_data, processed_entries):
        return self.execute_algorithm_on(form_data, processed_entries)

    def execute_algorithm_on(self, form_data, processed_entries):
        cne_code = form_data.get('cne', None)

        if cne_code is None:
            matching_formulario = fetch_matching_formulario(form_data)

            if matching_formulario:
                form_data['cne'] = matching_formulario.cne
                if matching_formulario.cne in [COMPRAVENTA, REGULARIZACION_DE_PATRIMONIO]:
                    numero_atencion = matching_formulario.numero_atencion
                    adquirientes, enajenantes = fetch_and_parse_implicados(numero_atencion)
                    form_data['adquirientes'] = adquirientes
                    form_data['enajenantes'] = enajenantes

        cne_code = form_data.get('cne', None)
        return self.algorithm_executor.execute(cne_code, form_data, processed_entries)

def fetch_matching_formulario(form_data):
    return Formulario.query.filter_by(
        fecha_inscripcion=form_data['fecha_inscripcion'],
        rol=form_data['rol'],
        fojas=form_data['fojas'],
        numero_inscripcion=form_data['nro_inscripcion']
    ).first()

def fetch_and_parse_implicados(numero_atencion):
    implicados = Implicados.query.filter_by(numero_atencion=numero_atencion).all()
    adquirientes = []
    enajenantes = []

    for implicado in implicados:
        implicado_dict = {
            'rut': implicado.rut,
            'porcentaje_derecho': implicado.porcentaje_derecho
        }
        if implicado.adquiriente == 1:
            adquirientes.append(implicado_dict)
        else:
            enajenantes.append(implicado_dict)

    return adquirientes, enajenantes