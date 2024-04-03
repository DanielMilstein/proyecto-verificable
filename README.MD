# Diseño de software Verificable - Proyecto, Entrega 1
## Como correr la aplicación
**Base de datos:** 
	Nuestra base de datos MySQL está contenerizada dentro de docker. Por lo tanto, para poder utilizarla, se deben seguir los sigueintes pasos: <br>
	`docker pull mysql`<br>
	`docker run --name project -e MYSQL_ROOT_PASSWORD=verificables -e MYSQL_DATABASE=project_app_db -e MYSQL_USER=myuser -e MYSQL_PASSWORD=verificables -p 3306:3306 -d mysql`<br>
	`docker exec -it project mysql -umyuser -pverificables`
**Flask:**
En el direcotrio principal del proyecto, nada más correr el comando:
	`python run.py`

En caso de errores, acá hay dos posibles problemas y sus soluciones:
- Creamos un script para poder rellenar la DB automáticamente con los CNE y las Comunas. Para que este script (y la DB) funcione correctamente, se necesita que el archivo excel 'regionesComunas.xlsx' del enunciado esté en el directorio principal del proyecto.<br>
- Instalar las librerías requeridas para el proyecto:
	`pip install -r requirements.txt`
## Cómo probar tabla Multi propietarios
Debido a que nuestro modelo de datos está basado en la consistencia de los mismos (nos pareció que podría ser útil pensando en el futuro ; quizás nos arrepentimos 🥴), se deben realizar múltiples inserciones para poder probar la tabla Multi propietarios. <br><br>Todo los snippets de código que se ven de aquí en adelante son ejemplos, y sus valores pueden ser modificados con libertad. 
	<br>*Nota: Técnicamente se pueden provocar errores con la base de datos al insertar ciertos atributos con libertad absoluta usando la inserción manual mediante la consola de mysql (por ejemplo, ingresando un RUT/RUN más largo del esperado). Ya que los usuarios no pueden ingresar formularios de esta manera, no pensamos que el cliente se preocupe de este tipo de errores.*<br>
Ahora sí, veamos los pasos a seguir para insertar datos en la tabla Multi propietario.<br>
### 1. Personas
Primero que nada, necesitamos crear las personas que serán dueñas de la propiedad/bien raíz. <br>
	`INSERT INTO persona (rut) VALUES ('12345678-9'), ('18765432-1'), ('5498732-1');` 
<br>La tabla persona aceptará los ruts con puntos entremedio (ej: 12.345.678-9), pero sólo mediante el ingreso manual de los datos mediante la consola de MySQL; en cualquier otro caso, se descartará,. Es decir, que al usar la aplicación, se espera que los ruts se ingresen sin puntos entremedio.
### 2. Bien raíz
Luego, debemos crear el bien raíz en cuestión.<br>
`INSERT INTO bien_raiz (comuna, manzana, predio) VALUES (1,1,1);`

### 3. Multi propietario
Ahora es momento de ingresar filas a la tabla multi propietario, que junta al concepto de propiedad con un rol determinado.

	`INSERT INTO multipropietario(
		id, rol, fojas, fecha_inscripcion, numero_inscripcion, 
		ano_vigencia_inicial, ano_vigencia_final
	) 
	VALUES 
		(1, 1, 10, '2023-05-15', 1001, 2023, 2028), 
		(2, 1, 25, '2023-05-15', 1001, 2020, 2028), 
		(3, 1, 40, '2023-05-15', 1001, 2000, 2030);`

Donde el 'rol' debe ser de la propiedad ingresada anteriormente:
	`SELECT * FROM bien_raiz WHERE manzana=1 AND predio=1 AND comuna=1

Notar cómo ingresamos el atributo 'id' manualmente. Esto es porque nos facilitará su uso en el paso siguiente (nada más, hay que tener cuidado con no ingresar un 'id' que hayamos ingresado previamente).
### 4. Propietario
Finalmente, ingresamos filas a la tabla Propietario, la cuál se encarga de unir a las personas propietarias con sus propiedades (es una tabla intermedia ; relación N x N). 

	`INSERT INTO propietario (rut, multipropietario_id, porcentaje_derecho) VALUES  ('05498732-1', 3, 25), ('12345678-9', 1, 25),  ('18765432-1', 2, 50);`

Donde el 'rut' deben ser los mismos que fueron ingresados durante el paso 1, y los multipropietario_id los mismo que ingresamos en el paso 3.
