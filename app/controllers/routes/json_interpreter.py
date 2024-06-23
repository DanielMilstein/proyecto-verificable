from flask import render_template, request, jsonify
import json
from datetime import datetime
from ...models import db
from .form_utils import create_formulario_and_implicados

def handle_json_form_submission():
    if 'upload_file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['upload_file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and file.filename.endswith('.json'):
        return process_json_file(file)
    
    return jsonify({'error': 'Invalid file type'})

def process_json_file(file):
    try:
        json_data = json.loads(file.read())
        errors = []
        success_messages = []

        forms_to_process = json_data.get('F2890', [])
        forms_to_process.sort(key=lambda x: datetime.strptime(x.get('fechaInscripcion', ''), '%Y-%m-%d'))

        for form_data in forms_to_process:
            try:
                cne_code = form_data.get('CNE')

                if cne_code not in [8, 99]:
                    errors.append(f"Invalid CNE code: {cne_code}")
                    continue

                adquirientes = [
                    {'rut': a.get('RUNRUT'), 'porcentaje_derecho': a.get('porcDerecho')}
                    for a in form_data.get('adquirentes', [])
                ]

                enajenantes = [
                    {'rut': e.get('RUNRUT'), 'porcentaje_derecho': e.get('porcDerecho')}
                    for e in form_data.get('enajenantes', [])
                ]

                form_data = {
                    'cne': form_data.get('CNE'),
                    'comuna': form_data['bienRaiz'].get('comuna'),
                    'manzana': form_data['bienRaiz'].get('manzana', ''),
                    'predio': form_data['bienRaiz'].get('predio', ''),
                    'fojas': form_data.get('fojas', ''),
                    'fecha_inscripcion': datetime.strptime(form_data.get('fechaInscripcion', ''), '%Y-%m-%d').date(),
                    'nro_inscripcion': form_data.get('nroInscripcion', None)
                }

                create_formulario_and_implicados(form_data, adquirientes, enajenantes)

                success_messages.append(f"Form data processed successfully: {form_data}")

            except Exception as e:
                db.session.rollback()
                errors.append(f"Error processing form data: {e}")

        return render_template('json-interpreter/json-interpreter.html', success=True, success_messages=success_messages, errors=errors)

    except json.JSONDecodeError as e:
        return jsonify({'error': f'Invalid JSON format: {e}'})
