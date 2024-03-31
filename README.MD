# How to test the Multipropietarios table
For each insert, you must be sure the personas exist. 
INSERT INTO persona (rut) VALUES ('12.345.678-9'), ('18.765.432-1'), ('5.498.732-1');

Insert bien raiz to be used.
INSERT INTO bien_raiz (comuna, manzana, predio) VALUES (1,1,1);

Then, you must add a multipropietario entry:
-- Data for multipropietario table (based on the rol values used above)
INSERT INTO multipropietario (id, rol, fojas, fecha_inscripcion, numero_inscripcion, ano_vigencia_inicial, ano_vigencia_final) 
VALUES 
(1, 1, 10, '2023-05-15', 1001, 2023, 2028),
 (2, 1, 25, '2023-05-15', 1001, 2020, 2028), 
 (3, 1, 40, '2023-05-15', 1001, 2000, 2030);

And lastly, the middle table to lnik the 'multipropietarios' to actual people:
-- For the first propiedad
NSERT INTO propietario (rut, multipropietario_id, porcentaje_derecho)  
VALUES  
('05498732-1', 3, 25), ('12345678-9', 1, 25),  ('18765432-1', 2, 50);