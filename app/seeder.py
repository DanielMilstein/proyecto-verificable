import json
from . import db
from .models import CNE, Comuna

NO_COMUNAS = 0
NUMERO_FORMULARIOS = 2

def retrieve_comunas_list():
    comunas_list = []

    with open('app/comunas-region-seed.json', 'r', encoding='utf-8') as json_file:
        comunas_data = json.load(json_file)

        for comuna_data in comunas_data['Comuna']:
            comunas_list.append(Comuna(
                codigo_comuna=comuna_data['codigo_comuna'],
                nombre_comuna=comuna_data['nombre_comuna'],
                codigo_region=comuna_data['codigo_region'],
                nombre_region=comuna_data['nombre_region']
            ))
    
    return comunas_list

def retrieve_formularios_list():
    formularios = [
        CNE(codigo_cne='8', nombre_cne='Compraventa'),
        CNE(codigo_cne='99', nombre_cne='Regularización del Patrimonio'),
    ]
    return formularios

def seed_database():
    db_seeded = False
    print("Running seeder...")

    global NO_COMUNAS
    global NUMERO_FORMULARIOS
    
    if db.session.query(Comuna).count() == NO_COMUNAS:
        print("Seeding database with comunas...")

        comunas_list = retrieve_comunas_list()
        for comuna_obj in comunas_list:
            db.session.add(comuna_obj)
        db_seeded = True
    
    if db.session.query(CNE).count() < NUMERO_FORMULARIOS:
        print("Seeding database with formularios...")
        formularios_list = retrieve_formularios_list()
        for formulario_obj in formularios_list:
            db.session.add(formulario_obj)
        db_seeded = True

    if db_seeded:
        db.session.commit()
        print("Database seeded successfully")
    else:
        print("Database is already seeded")
