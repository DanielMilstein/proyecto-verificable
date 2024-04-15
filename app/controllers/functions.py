from flask import render_template, Blueprint, request, redirect, flash, jsonify
from app.forms import *
from app.models import *
import json




def refresh_multipropietario():
    Multipropietario.query.delete()
    
    formularios = Formulario.query.all()

    for formulario in formularios:
        formularios_mismo_rol = Formulario.query.filter_by(rol = formulario.rol).all().order_by(Formulario.fecha_inscripcion)

        vigencia_inicial = 0
        vigencia_final = 0

        if formularios_mismo_rol:
            for form in formularios_mismo_rol:
                if form.fecha_inscripcion.year < formulario.fecha_inscripcion.year:
                    formulario.ano_vigencia_inicial = form.fecha_inscripcion.year
                elif form.fecha_inscripcion.year > formulario.fecha_inscripcion.year:
                    formulario.ano_vigencia_final = form.fecha_inscripcion.year


        nueva_entrada = Multipropietario(
            rol = formulario.rol,
            fojas = formulario.fojas,
            fecha_inscripcion = formulario.fecha_inscripcion,
            numero_inscripcion = formulario.numero_inscripcion,
            ano_inscripcion = formulario.fecha_inscripcion.year,
            ano_vigencia_inicial = vigencia_inicial,
            ano_vigencia_final = vigencia_final

        )

        db.session.add(nueva_entrada)
        db.session.commit()
        