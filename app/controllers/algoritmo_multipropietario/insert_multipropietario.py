from .algoritmos.regularizacion_patrimonio.algoritmo_regularizacion_patrimonio import AlgoritmoRegularizacionPatrimonio
from .algoritmos.compraventa.algoritmo_compraventa import AlgoritmoCompraventa

REGULARIZACION_DE_PATRIMONIO = 99
COMPRAVENTA = 8
class AlgoritmoMultipropietario:
    def insert_into_multipropietario(self, form_data):
        self.execute_algorithm_on(form_data)

    def execute_algorithm_on(self, form_data):
        cne_code = form_data.get('cne', None)
        if cne_code == REGULARIZACION_DE_PATRIMONIO:  
            regularizacion_algorithm = AlgoritmoRegularizacionPatrimonio()
            regularizacion_algorithm.apply_algorithm_on(form_data)
        elif cne_code == COMPRAVENTA: 
            compraventa_algorithm = AlgoritmoCompraventa()
            compraventa_algorithm.apply_algorithm_on(form_data)
        return True