from flask import render_template, Blueprint, request
from app.forms import *

blueprint = Blueprint('pages', __name__)



################
#### routes ####
################


@blueprint.route('/')
def home():
    return "Hello World!"

@blueprint.route('/form')
def form():
    form = MyForm()
    if form.validate_on_submit():
        # Here, you can process form data
        flash(f'Form submitted with name: {form.name.data}')

        # Transform to json



        return redirect('/')
    return render_template('form.html', title='Form', form=form)