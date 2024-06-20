# Diseño de software Verificable - Proyecto, Entrega 2

## Cómo correr la aplicación

Nuestra base de datos MySQL está contenerizada dentro de Docker. Para utilizarla, sigue estos pasos:

1. Asegúrate de tener Docker instalado en tu sistema.

2. Luego, crea y ejecuta el contenedor de MySQL con el siguiente comando:

```bash
docker compose up
```

Este archivo `compose.yml` define dos servicios: `sii-mysql-db` y `sii-flask-app`. Aquí está la explicación de lo que hace cada uno de ellos:

### Servicio `sii-mysql-db`:
- **Imagen:** Utiliza la imagen oficial de MySQL versión 8.0.
- **Variables de entorno:** Establece las siguientes variables de entorno para la configuración de MySQL:
  - `MYSQL_ROOT_PASSWORD`: Contraseña para el usuario root de MySQL.
  - `MYSQL_DATABASE`: Nombre de la base de datos que se creará dentro del contenedor.
  - `MYSQL_USER`: Nombre de usuario de MySQL.
  - `MYSQL_PASSWORD`: Contraseña del usuario de MySQL.
- **Puertos:** Mapea el puerto 3306 del contenedor al puerto 3306 del host, lo que permite que otras aplicaciones se conecten al servidor MySQL.
- **Healthcheck:** Define un comando de verificación de salud para asegurarse de que el servicio MySQL esté en funcionamiento. El healthcheck intenta ejecutar el comando `mysqladmin ping -h localhost` cada 5 segundos y reintentará hasta 10 veces si falla.

### Servicio `sii-flask-app`:
- **Construcción de la imagen:** Usa el Dockerfile en el directorio actual (`.`) para construir la imagen del servicio Flask. Esto significa que el Dockerfile debe estar en el mismo directorio que el archivo `compose.yml`.
- **Puertos:** Mapea el puerto 5000 del contenedor al puerto 5000 del host, permitiendo acceder a la aplicación Flask desde el navegador u otras aplicaciones.
- **Dependencias:** Especifica que este servicio depende del servicio `sii-mysql-db` y se asegura de que el servicio `sii-mysql-db` esté en un estado saludable (`service_healthy`) antes de iniciar este servicio. Esto garantiza que la base de datos esté disponible antes de que la aplicación Flask intente conectarse a ella.

Este archivo `compose.yml` proporciona una forma de definir, construir y orquestar múltiples servicios Docker para facilitar el desarrollo y la implementación de aplicaciones complejas. En este caso, se utiliza para gestionar la base de datos MySQL y la aplicación Flask de manera conjunta.


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
`INSERT INTO bien_raiz (comuna, manzana, predio, rol) VALUES (1,1,1 "1,1,1");`

### 3. Multi propietario
Ahora es momento de ingresar filas a la tabla multi propietario, que junta al concepto de propiedad con un rol determinado.

	`INSERT INTO multipropietario(
		id, rol, fojas, fecha_inscripcion, numero_inscripcion, ano_inscripcion,
		ano_vigencia_inicial, ano_vigencia_final
	) 
	VALUES 
		(1, "1-1-1", 10, '2023-05-15', 1001, 1900, 2023, 2028), 
		(2, "1-1-1", 25, '2023-05-15', 1001, 1900, 2020, 2028), 
		(3, "1-1-1", 40, '2023-05-15', 1001, 1900, 2000, 2030);`

Donde el 'rol' debe ser de la propiedad ingresada anteriormente:
	`SELECT * FROM bien_raiz WHERE manzana=1 AND predio=1 AND comuna=1

Notar cómo ingresamos el atributo 'id' manualmente. Esto es porque nos facilitará su uso en el paso siguiente (nada más, hay que tener cuidado con no ingresar un 'id' que hayamos ingresado previamente).
### 4. Propietario
Finalmente, ingresamos filas a la tabla Propietario, la cuál se encarga de unir a las personas propietarias con sus propiedades (es una tabla intermedia ; relación N x N). 

	`INSERT INTO propietario (rut, multipropietario_id, porcentaje_derecho) VALUES  ('5498732-1', 3, 25), ('12345678-9', 1, 25),  ('18765432-1', 2, 50);`

Donde el 'rut' deben ser los mismos que fueron ingresados durante el paso 1, y los multipropietario_id los mismo que ingresamos en el paso 3.




## Tests

Para correr los tests, primero debes instalar las dependencias necesarias. Puedes hacerlo ejecutando el siguiente comando:

```bash
pip install -r requirements.txt
```

Una vez instaladas las dependencias, puedes ejecutar los tests con el siguiente comando:

```bash
coverage run -m unittest discover
```

Este comando ejecutará todos los tests unitarios definidos en el directorio `tests` y generará un reporte de cobertura. Para ver el reporte de cobertura, puedes ejecutar el siguiente comando:

```bash
coverage report
```

