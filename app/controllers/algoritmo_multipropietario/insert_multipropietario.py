from .algoritmos.regularizacion_patrimonio.algoritmo_regularizacion_patrimonio import AlgoritmoRegularizacionPatrimonio
from .algoritmos.compraventa.algoritmo_compraventa import AlgoritmoCompraventa
from ...models import Formulario, Implicados

REGULARIZACION_DE_PATRIMONIO = 99
COMPRAVENTA = 8

class AlgoritmoMultipropietario:
    def insert_into_multipropietario(self, form_data, processed_entries):
        return self.execute_algorithm_on(form_data, processed_entries)

    def execute_algorithm_on(self, form_data, processed_entries):
        cne_code = form_data.get('cne', None)

        if cne_code is None:
            matching_formulario = Formulario.query.filter_by(
                fecha_inscripcion=form_data['fecha_inscripcion'],
                rol=form_data['rol'],
                fojas=form_data['fojas'],
                numero_inscripcion=form_data['nro_inscripcion']
            ).first()

            if matching_formulario:
                form_data['cne'] = matching_formulario.cne
                if  matching_formulario.cne == COMPRAVENTA:
                    numero_atencion = matching_formulario.numero_atencion

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

                    form_data['adquirientes'] = adquirientes
                    form_data['enajenantes'] = enajenantes

        cne_code = form_data.get('cne', None)
        success = True
        if cne_code == REGULARIZACION_DE_PATRIMONIO:  
            regularizacion_algorithm = AlgoritmoRegularizacionPatrimonio()
            success = regularizacion_algorithm.apply_algorithm_on(form_data, processed_entries)
        elif cne_code == COMPRAVENTA: 
            compraventa_algorithm = AlgoritmoCompraventa()
            compraventa_algorithm.apply_algorithm_on(form_data)
        else:
            success = False

        return success
