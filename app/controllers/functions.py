from flask import render_template, Blueprint, request, redirect, flash, jsonify
from app.forms import *
from app.models import *
import json




def refresh_multipropietario():
    Multipropietario.query.delete()
    
    formularios = Formulario.query.order_by(Formulario.fecha_inscripcion).all()

    for formulario in formularios:
        formularios_mismo_rol = Formulario.query.filter_by(rol = formulario.rol).order_by(Formulario.fecha_inscripcion).all()

        vigencia_inicial = formulario.fecha_inscripcion.year
        vigencia_final = 0

        if formularios_mismo_rol:
            for form in formularios_mismo_rol:
                if form.fecha_inscripcion.year < formulario.fecha_inscripcion.year:
                    # Search form in multipropietario and set vigencia final
                    if formulario.fecha_inscripcion.year < vigencia_final:
                        Multipropietario.query.filter_by(numero_inscripcion = form.numero_inscripcion).update(dict(ano_vigencia_final = formulario.fecha_inscripcion.year-1))
                elif form.fecha_inscripcion.year == formulario.fecha_inscripcion.year:
                    # Check if adquirientes are the same (with numero inscripcion?)
                    if form.numero_inscripcion != formulario.numero_inscripcion:
                        # Search form in multipropietario and set vigencia final
                        Multipropietario.query.filter_by(numero_inscripcion = form.numero_inscripcion).delete()
                elif form.fecha_inscripcion.year > formulario.fecha_inscripcion.year:
                    if vigencia_final == 0:
                        vigencia_final = max(form.fecha_inscripcion.year-1, formulario.fecha_inscripcion.year)
                    else:
                        if form.fecha_inscripcion.year-1 < vigencia_final:
                            vigencia_final = form.fecha_inscripcion.year-1

        
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
