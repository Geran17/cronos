-- =========================================================
-- ASIGNATURAS
-- =========================================================
INSERT OR IGNORE INTO Asignatura (codigo, nombre, credito) VALUES
-- Biología
('CBM08C5', 'Álgebra y Geometría Analítica', 8), ('CPB01B5', 'Anatomía Funcional de Vertebrados', 8),
('CPB03B5', 'Biofísica', 8), ('CPB04B5', 'Biogeografía', 8), ('CPB05B5', 'Biología Celular', 8),
('CPB07B5', 'Biología del Desarrollo Animal', 8), ('CBB08C5', 'Biología General', 8),
('CPB09B5', 'Biología Molecular', 8), ('CPB13B5', 'Bioquímica', 8), ('CBM22C5', 'Cálculo Diferencial e Integral', 8),
('CCD26C5', 'Cultura Nacional', 8), ('CPB14B5', 'Ecología de Poblaciones y Comunidades', 8),
('CPB15B5', 'Ecología General', 8), ('COO0105', 'Electiva I', 8), ('COO0205', 'Electiva II', 8),
('COO0305', 'Electiva III', 8), ('CBE09C5', 'Estadística Aplicada', 8), ('CBF19C5', 'Física General', 8),
('CPB16B5', 'Fisiología Vegetal', 8), ('CPB18B5', 'Genética Evolutiva', 8), ('CPB19B5', 'Genética General', 8),
('CCD27C5', 'Guaraní', 8), ('CPB21B5', 'Hidrobiología', 8), ('CPB22B5', 'Histología Vegetal', 8),
('CCD28C5', 'Inglés', 8), ('CPB23B5', 'Inmunología', 8), ('CBG16C5', 'Introducción a la Geología', 8),
('CCB24C5', 'Metodología de la Investigación y Redacción Científica', 8), ('CPB25B5', 'Micología', 8),
('CPB26B5', 'Microbiología', 8), ('CPB28B5', 'Morfología Vegetal', 8), ('CPB29B5', 'Pasantía', 8),
('CBQ17C5', 'Química General', 8), ('CBQ23C5', 'Química Orgánica', 8), ('CPB30B5', 'Sistemática Vegetal', 8),
('TGB31B5', 'Trabajo de Grado', 8), ('CPB32B5', 'Virología', 8), ('CPB33B5', 'Zoología de Artrópodos', 8),
('CPB34B5', 'Zoología de Cordados', 8), ('CPB35B5', 'Zoología de Invertebrados', 8),

-- Matemática Estadística
('CBM05C5', 'Álgebra Lineal I', 8), ('CPM06C5', 'Álgebra Lineal II', 8), ('CBM09C5', 'Álgebra y Trigonometría', 8),
('CPE01E5', 'Análisis de Datos', 8), ('CPE02E5', 'Análisis de Regresión', 8), ('CPE03E5', 'Análisis de Series Temporales', 8),
('CBM15C5', 'Análisis Matemático I', 8), ('CPM16C5', 'Análisis Matemático II', 8), ('CPE04E5', 'Análisis Multivariante', 8),
('CPM18C5', 'Análisis Numérico', 8), ('CPE06E5', 'Diseño de Encuestas', 8), ('CPE07E5', 'Diseño de Experimentos', 8),
('CPE08E5', 'Econometría', 8), ('COO01O5', 'Electiva I', 8), ('COO02O5', 'Electiva II', 8), ('COO03O5', 'Electiva III', 8),
('CPE10E5', 'Estadísticas Demográficas y Socioeconómicas', 8), ('CBM33C5', 'Geometría Analítica', 8),
('CPE11E5', 'Inferencia Bayesiana', 8), ('CPE12E5', 'Inferencia Estadística', 8), ('CCE13E5', 'Introducción a la Ciencia de Datos', 8),
('CBM36C5', 'Introducción a la Matemática Discreta', 8), ('CCE14E5', 'Introducción a la Programación y Gestión de Base de Datos', 8),
('CPE15C5', 'Investigación Operativa', 8), ('CPB24C5', 'Metodología de la Investigación y Redacción Científica', 8),
('CPE16E5', 'Métodos No Paramétricos', 8), ('CPE17E5', 'Modelos Lineales', 8), ('CPE18E5', 'Modelos Lineales Generalizados', 8),
('PE19E5', 'Pasantía', 8), ('CPE20C5', 'Probabilidad y Estadística', 8), ('CPE21E5', 'Procesos Estocásticos y Simulación', 8),
('CPE22E5', 'Técnica de Muestreo Estadístico', 8), ('TGE23E5', 'Trabajo de Grado', 8),

-- Física
('CBM04CS', 'Álgebra Lineal', 8), ('CBM08CS', 'Álgebra y Geometría Analítica', 8), ('CBM15CS', 'Análisis Matemático I', 8),
('CBM16CS', 'Análisis Matemático II', 8), ('CCM17CS', 'Análisis Matemático III', 8), ('CBM22CS', 'Cálculo Diferencial e Integral', 8),
('CBM27CS', 'Ecuaciones Diferenciales', 8), ('COO010S', 'Electiva I', 8), ('COO020S', 'Electiva II', 8), ('COO030S', 'Electiva III', 8),
('CBF02CS', 'Electricidad y Magnetismo', 8), ('CPF04FS', 'Elementos de la Física Teórica I', 8), ('CPF05FS', 'Elementos de la Física Teórica II', 8),
('CBE09CS', 'Estadística Aplicada', 8), ('CPF08CS', 'Física Computacional I', 8), ('CPF09CS', 'Física Computacional II', 8),
('CPF13FS', 'Física del Estado Sólido', 8), ('CPF17FS', 'Física Teórica', 8), ('CPF23FS', 'Física Moderna I', 8),
('CPF24FS', 'Física Moderna II', 8), ('CPF26FS', 'Física Térmica y Termodinámica', 8), ('CPF30FS', 'Laboratorio de Electricidad y Magnetismo', 8),
('CCF31FS', 'Laboratorio de Electrónica', 8), ('CPF34FS', 'Laboratorio de Mecánica y Calor', 8), ('CPF35FS', 'Laboratorio de Ondas y Óptica', 8),
('CBF37CS', 'Mecánica', 8), ('CPF38FS', 'Mecánica Clásica I', 8), ('CPF39FS', 'Mecánica Clásica II', 8), ('CPF41FS', 'Mecánica Cuántica I', 8),
('CPF42FS', 'Mecánica Cuántica II', 8), ('CPF45FS', 'Ondas', 8), ('CPF47FS', 'Óptica Física', 8), ('PF49FS', 'Práctica Profesional', 8),
('CBQ18CS', 'Química General I', 8), ('CPF52FS', 'Teoría Electromagnética I', 8), ('CPF53FS', 'Teoría Electromagnética II', 8),
('TGF54FS', 'Trabajo de Grado', 8),

-- Logística
('CPT02L5', 'Costos en Operaciones Logísticas', 8), ('CPT04L5', 'Derecho del Transporte', 8), ('CBT06C5', 'Diseño y Seguridad de planta', 8),
('CPT09C5', 'Estudio del Trabajo', 8), ('CBF12L5', 'Física de los materiales', 8), ('CPT11L5', 'Formulación y Diseño de Proyectos Logísticos', 8),
('CPT13C5', 'Fundamentos de Logística y Cadena de Suministro', 8), ('CPT14L5', 'Geografía para el Transporte', 8),
('CPT15L5', 'Gestión de Compras y Sistemas de Inventarios', 8), ('CBT16C5', 'Gestión de Empresas', 8), ('CPT17C5', 'Gestión de la calidad', 8),
('CPT18L5', 'Gestión de las Tecnologías de la Información y la Comunicación', 8), ('CBT19C5', 'Gestión del Talento Humano', 8),
('CPT20L5', 'Gestión Portuaria y Vías Navegables', 8), ('CPT21L5', 'Gestión y Operaciones del transporte', 8), ('CCT22L5', 'Inglés Técnico Aplicado', 8),
('CCT23C5', 'Legislación Laboral', 8), ('CPT24L5', 'Logística de Distribución y Transporte', 8), ('CPT25L5', 'Logística de Producción', 8),
('CPT26L5', 'Logística en el Comercio Internacional', 8), ('CPT27L5', 'Logística Inversa', 8), ('CPT29L5', 'Modelado de Tráfico', 8),
('PT31L5', 'Pasantía', 8), ('CBQ12L5', 'Química de los materiales', 8), ('CPT36L5', 'Seguridad en el Transporte', 8),
('CPT37L5', 'Sistema de Transporte', 8), ('CPT39L5', 'Tecnología de Envases y Embalajes', 8), ('CBT41C5', 'Teoría Económica', 8),
('TGT42L5', 'Trabajo de Grado', 8), ('CPT44L5', 'Trade Marketing y Logística Integral', 8);

-- =========================================================
-- HORAS SEMANALES
-- =========================================================
-- Teóricas 3, Prácticas 2, HTD 5, HTI 10
INSERT OR IGNORE INTO HorasSemanales (id_asignatura, teoricas, practicas, htd, hti)
SELECT id_asignatura, 3, 2, 5, 10 FROM Asignatura WHERE codigo IN (
    'CBM08C5', 'CPB01B5', 'CPB07B5', 'CBM22C5', 'CBF19C5', 'CBQ17C5', 'CBQ23C5',
    'CBM05C5', 'CPM06C5', 'CBM09C5', 'CPE02E5', 'CPE03E5', 'CBM15C5', 'CPM16C5',
    'CPE04E5', 'CPM18C5', 'CPE06E5', 'CPE07E5', 'CPE08E5', 'CBM33C5', 'CPE11E5',
    'CPE12E5', 'CCE13E5', 'CBM36C5', 'CPE15C5', 'CPE16E5', 'CPE17E5', 'CPE18E5',
    'CPE20C5', 'CPE21E5', 'CPE22E5', 'CBM04CS', 'CBM15CS', 'CBM16CS', 'CCM17CS',
    'CBM22CS', 'CBM27CS', 'CBF02CS', 'CPF04FS', 'CPF05FS', 'CPF08CS', 'CPF09CS',
    'CPF13FS', 'CPF17FS', 'CPF23FS', 'CPF24FS', 'CPF26FS', 'CPF30FS', 'CCF31FS',
    'CPF34FS', 'CPF35FS', 'CBF37CS', 'CPF38FS', 'CPF39FS', 'CPF41FS', 'CPF42FS',
    'CPF45FS', 'CPF47FS', 'CBQ18CS', 'CPF52FS', 'CPF53FS', 'CPT02L5', 'CPT04L5',
    'CBT06C5', 'CPT09C5', 'CBF12L5', 'CPT11L5', 'CPT13C5', 'CPT14L5', 'CPT15L5',
    'CBT16C5', 'CPT17C5', 'CPT18L5', 'CBT19C5', 'CPT20L5', 'CPT21L5', 'CCT22L5',
    'CCT23C5', 'CPT24L5', 'CPT25L5', 'CPT26L5', 'CPT27L5', 'CPT29L5', 'CBQ12L5',
    'CPT36L5', 'CPT37L5', 'CPT39L5', 'CBT41C5', 'CPT44L5'
);

-- Teóricas 2, Prácticas 3, HTD 5, HTI 10
INSERT OR IGNORE INTO HorasSemanales (id_asignatura, teoricas, practicas, htd, hti)
SELECT id_asignatura, 2, 3, 5, 10 FROM Asignatura WHERE codigo IN (
    'CPB03B5', 'CPB04B5', 'CPB05B5', 'CBB08C5', 'CPB09B5', 'CPB13B5', 'CCD26C5',
    'CPB14B5', 'CPB15B5', 'COO0105', 'COO0205', 'COO0305', 'CBE09C5', 'CPB16B5',
    'CPB18B5', 'CPB19B5', 'CCD27C5', 'CPB21B5', 'CPB22B5', 'CCD28C5', 'CPB23B5',
    'CBG16C5', 'CCB24C5', 'CPB25B5', 'CPB26B5', 'CPB28B5', 'CPB30B5', 'CPB32B5',
    'CPB33B5', 'CPB34B5', 'CPB35B5', 'CPE01E5', 'COO01O5', 'COO02O5', 'COO03O5',
    'CPE10E5', 'CPB24C5', 'COO010S', 'COO020S', 'COO030S', 'CBE09CS'
);

-- Teóricas 0, Prácticas 5, HTD 5, HTI 10
INSERT OR IGNORE INTO HorasSemanales (id_asignatura, teoricas, practicas, htd, hti)
SELECT id_asignatura, 0, 5, 5, 10 FROM Asignatura WHERE codigo IN (
    'CPB29B5', 'TGB31B5', 'PE19E5', 'TGE23E5', 'PF49FS', 'TGF54FS', 'PT31L5', 'TGT42L5'
);