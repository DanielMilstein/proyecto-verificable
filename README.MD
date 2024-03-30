For each insert, you must be sure the personas exist. 
INSERT INTO persona (rut) VALUES ('12.345.678-9'), ('18.765.432-1'), ('5.498.732-1');

Then, you must add multipropietario:
-- Data for multipropietario table (based on the rol values used above)
INSERT INTO multipropietario (id, rol, fojas, fecha_inscripcion, numero_inscripcion, ano_vigencia_inicial, ano_vigencia_final) VALUES 
(1, '1/1/1', 10, '2023-05-15', 1001, 2023, 2028),
(2, '1/1/1', 25, '2023-05-15', 1001, 2020, 2028),
(3, '1/1/1', 40, '2023-05-15', 1001, 2000, 2030),



And lastly, the middle table:
-- For the first propiedad
INSERT INTO propietario (rut, multipropietario_id, rol, porcentaje_derecho) VALUES ('12.345.678-9', 1, '1/1/1', 25),('18.765.432-1', 2, '1/1/1', 50), ('5.498.732-1', 3, '1/1/1', 25);