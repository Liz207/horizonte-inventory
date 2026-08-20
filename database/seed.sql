-- ============================================================
-- Horizonte Inventory - datos de prueba
-- 24 productos (el enunciado exige un minimo de 20).
-- Incluye productos agotados a proposito para probar el filtro
-- "Productos sin existencias".
--   sudo -u postgres psql -d horizonte -f database/seed.sql
-- ============================================================

TRUNCATE TABLE products RESTART IDENTITY;

INSERT INTO products (code, name, category, price, quantity) VALUES
-- Libros
('BOOK-001', 'Cien anos de soledad',                    'Libros',     12500.00, 14),
('BOOK-002', 'El principito',                           'Libros',      6800.00, 32),
('BOOK-003', 'Cuentos de angustias y paisajes',         'Libros',      9200.00,  7),
('BOOK-004', 'Diccionario de la lengua espanola',       'Libros',     23500.00,  4),
('BOOK-005', 'La isla de los hombres solos',            'Libros',      8700.00,  0),
('BOOK-006', 'Atlas geografico de Costa Rica',          'Libros',     18400.00,  9),
-- Material educativo
('EDU-001',  'Set de geometria escolar',                'Educativo',   3200.00, 45),
('EDU-002',  'Calculadora cientifica 240 funciones',    'Educativo',  14900.00, 18),
('EDU-003',  'Mapa mudo de America (paquete de 10)',    'Educativo',   2500.00, 60),
('EDU-004',  'Abaco de madera 100 cuentas',             'Educativo',   5400.00,  0),
('EDU-005',  'Tabla periodica plastificada',            'Educativo',   1800.00, 75),
('EDU-006',  'Microscopio escolar 400x',                'Educativo',  48900.00,  3),
-- Papeleria
('PAP-001',  'Cuaderno universitario 100 hojas',        'Papeleria',   1450.00, 210),
('PAP-002',  'Resma de papel bond carta',               'Papeleria',   4750.00,  38),
('PAP-003',  'Block de dibujo tamano carta',            'Papeleria',   2300.00,  26),
('PAP-004',  'Cartulina blanca (unidad)',               'Papeleria',    450.00, 150),
('PAP-005',  'Sobres manila carta (paquete de 25)',     'Papeleria',   3100.00,   0),
-- Oficina
('OFI-001',  'Engrapadora metalica de escritorio',      'Oficina',     6900.00,  12),
('OFI-002',  'Perforadora de dos huecos',               'Oficina',     5600.00,   8),
('OFI-003',  'Archivador de palanca oficio',            'Oficina',     3800.00,  40),
('OFI-004',  'Caja de clips metalicos (100 u.)',        'Oficina',      650.00, 120),
('OFI-005',  'Pizarra acrilica 60x40 cm',               'Oficina',    17800.00,   5),
-- Escritura
('ESC-001',  'Boligrafo azul (caja de 12)',             'Escritura',   3600.00,  55),
('ESC-002',  'Marcadores permanentes surtidos (4 u.)',  'Escritura',   4200.00,   2);

-- Verificacion rapida
SELECT COUNT(*) AS total_productos FROM products;
