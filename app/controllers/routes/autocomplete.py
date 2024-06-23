from flask import request, jsonify
from ...models import Comuna

def handle_autocomplete():
    search = request.args.get('q', '')
    suggestions = get_suggestions(search)
    return jsonify(results=suggestions)

def get_suggestions(search):
    return [
        {'id': item.codigo_comuna, 'text': item.nombre_comuna}
        for item in Comuna.query.filter(Comuna.nombre_comuna.contains(search)).all()
    ]
