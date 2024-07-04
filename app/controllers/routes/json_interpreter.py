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
    except json.JSONDecodeError as e:
        return jsonify({'error': f'Invalid JSON format: {e}'})
    
    forms_to_process = json_data.get('F2890', [])
    forms_to_process.sort(key=lambda x: datetime.strptime(x.get('fechaInscripcion', ''), '%Y-%m-%d'))

    errors, success_messages = process_forms(forms_to_process)
    
    return render_template(
        'json-interpreter/json-interpreter.html', 
        success=True, 
        success_messages=success_messages, 
        errors=errors
    )

def process_forms(forms_to_process):
    errors = []
    success_messages = []

    for form_data in forms_to_process:
        try:
            cne_code = form_data.get('CNE')

            if not is_valid_cne_code(cne_code):
                errors.append(f"Invalid CNE code: {cne_code}")
                continue

            adquirientes = extract_participants(form_data.get('adquirentes', []))
            enajenantes = extract_participants(form_data.get('enajenantes', []))

            processed_form_data = extract_form_data(form_data)

            create_formulario_and_implicados(processed_form_data, adquirientes, enajenantes)
            success_messages.append(f"Form data processed successfully: {processed_form_data}")

        except Exception as e:
            db.session.rollback()
            errors.append(f"Error processing form data: {e}")

    return errors, success_messages

def is_valid_cne_code(cne_code):
    return cne_code in [8, 99]

def extract_participants(participants):
    return [
        {'rut': participant.get('RUNRUT'), 'porcentaje_derecho': participant.get('porcDerecho')}
        for participant in participants
    ]

def extract_form_data(form_data):
    return {
        'cne': form_data.get('CNE'),
        'comuna': form_data['bienRaiz'].get('comuna'),
        'manzana': form_data['bienRaiz'].get('manzana', ''),
        'predio': form_data['bienRaiz'].get('predio', ''),
        'fojas': form_data.get('fojas', ''),
        'fecha_inscripcion': datetime.strptime(form_data.get('fechaInscripcion', ''), '%Y-%m-%d').date(),
        'nro_inscripcion': form_data.get('nroInscripcion', None)
    }
