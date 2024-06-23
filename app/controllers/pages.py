from flask import Blueprint
from .algoritmo_multipropietario.insert_into_multipropietario import HandleAlgoritmoMultipropietario
from .routes.show_home_page import render_home_page
from .routes.create_form import handle_form_submission
from .routes.form_detail import get_form_detail
from .routes.form_list import get_form_list
from .routes.search_multipropietarios import handle_search_multipropietarios
from .routes.json_interpreter import handle_json_form_submission
from .routes.autocomplete import handle_autocomplete

blueprint = Blueprint('pages', __name__)


################
#### routes ####
################


@blueprint.route('/', methods=['GET', 'POST'])
def show_home_page():
    return render_home_page()


@blueprint.route('/form-F2890', methods=['GET', 'POST'])
def form():
    return handle_form_submission()


@blueprint.route('/form-list', methods=['GET', 'POST'])
def form_list():
    return get_form_list()


@blueprint.route('/form-F2890/<int:numero_atencion>')
def form_detail(numero_atencion):
    return get_form_detail(numero_atencion)


@blueprint.route('/buscar_multipropietarios', methods=['GET', 'POST'])
def search_multipropietarios():
    return handle_search_multipropietarios()


@blueprint.route('/json-interpreter', methods=['POST'])
def json_interpreter():
    return handle_json_form_submission()

@blueprint.route('/autocomplete')
def autocomplete():
    return handle_autocomplete()
