-- Prerrequisitos Biología
INSERT OR IGNORE INTO Prerequisito (id_asignatura, id_prerequisito)
SELECT a.id_asignatura, p.id_asignatura
FROM Asignatura a, Asignatura p
WHERE (a.codigo = 'CPB01B5' AND p.codigo = 'CPB34B5') OR -- Anatomía Funcional -> Zoología de Cordados
      (a.codigo = 'CPB03B5' AND p.codigo = 'CBF19C5') OR -- Biofísica -> Física General
      (a.codigo = 'CPB04B5' AND p.codigo = 'CPB15B5') OR -- Biogeografía -> Ecología General
      (a.codigo = 'CPB05B5' AND p.codigo = 'CBB08C5') OR -- Biología Celular -> Biología General
      (a.codigo = 'CPB07B5' AND p.codigo = 'CPB05B5') OR -- Biología del Desarrollo -> Biología Celular
      (a.codigo = 'CPB09B5' AND p.codigo = 'CPB19B5') OR -- Biología Molecular -> Genética General
      (a.codigo = 'CPB13B5' AND p.codigo = 'CBQ23C5') OR -- Bioquímica -> Química Orgánica
      (a.codigo = 'CPB14B5' AND p.codigo = 'CPB04B5') OR -- Ecología de Poblaciones -> Biogeografía
      (a.codigo = 'CPB15B5' AND p.codigo = 'CBG16C5') OR -- Ecología General -> Introducción a la Geología
      (a.codigo = 'CBE09C5' AND p.codigo = 'CBM08C5') OR -- Estadística Aplicada -> Álgebra y Geometría
      (a.codigo = 'CBF19C5' AND p.codigo = 'CBM22C5') OR -- Física General -> Cálculo Diferencial
      (a.codigo = 'CPB16B5' AND p.codigo = 'CPB28B5') OR -- Fisiología Vegetal -> Morfología Vegetal
      (a.codigo = 'CPB16B5' AND p.codigo = 'CPB03B5') OR -- Fisiología Vegetal -> Biofísica
      (a.codigo = 'CPB18B5' AND p.codigo = 'CPB19B5') OR -- Genética Evolutiva -> Genética General
      (a.codigo = 'CPB19B5' AND p.codigo = 'CBE09C5') OR -- Genética General -> Estadística Aplicada
      (a.codigo = 'CPB21B5' AND p.codigo = 'CPB15B5') OR -- Hidrobiología -> Ecología General
      (a.codigo = 'CPB22B5' AND p.codigo = 'CPB05B5') OR -- Histología Vegetal -> Biología Celular
      (a.codigo = 'CPB23B5' AND p.codigo = 'CPB09B5') OR -- Inmunología -> Biología Molecular
      (a.codigo = 'CCB24C5' AND p.codigo = 'CBE09C5') OR -- Metodología -> Estadística Aplicada
      (a.codigo = 'CPB25B5' AND p.codigo = 'CPB26B5') OR -- Micología -> Microbiología
      (a.codigo = 'CPB25B5' AND p.codigo = 'CPB30B5') OR -- Micología -> Sistemática Vegetal
      (a.codigo = 'CPB26B5' AND p.codigo = 'CPB13B5') OR -- Microbiología -> Bioquímica
      (a.codigo = 'CPB28B5' AND p.codigo = 'CPB22B5') OR -- Morfología Vegetal -> Histología Vegetal
      (a.codigo = 'CPB29B5' AND p.codigo = 'CPB26B5') OR -- Pasantía -> Microbiología
      (a.codigo = 'CPB29B5' AND p.codigo = 'CPB09B5');   -- Pasantía -> Biología Molecular

-- Prerrequisitos Matemática Estadística
INSERT OR IGNORE INTO Prerequisito (id_asignatura, id_prerequisito)
SELECT a.id_asignatura, p.id_asignatura
FROM Asignatura a, Asignatura p
WHERE (a.codigo = 'CPM06C5' AND p.codigo = 'CBM05C5') OR -- Álgebra Lineal II -> Álgebra Lineal I
      (a.codigo = 'CPE01E5' AND p.codigo = 'CPE06E5') OR -- Análisis de Datos -> Diseño de Encuestas
      (a.codigo = 'CPE02E5' AND p.codigo = 'CPE12E5') OR -- Análisis de Regresión -> Inferencia Estadística
      (a.codigo = 'CPE03E5' AND p.codigo = 'CPE08E5') OR -- Análisis de Series -> Econometría
      (a.codigo = 'CBM15C5' AND p.codigo = 'CBM22C5') OR -- Análisis Matemático I -> Cálculo Diferencial
      (a.codigo = 'CPM16C5' AND p.codigo = 'CBM15C5') OR -- Análisis Matemático II -> Análisis Matemático I
      (a.codigo = 'CPE04E5' AND p.codigo = 'CPE12E5') OR -- Análisis Multivariante -> Inferencia Estadística
      (a.codigo = 'CPM18C5' AND p.codigo = 'CPM06C5') OR -- Análisis Numérico -> Álgebra Lineal II
      (a.codigo = 'CPE06E5' AND p.codigo = 'CPE22E5') OR -- Diseño de Encuestas -> Técnica de Muestreo
      (a.codigo = 'CPE07E5' AND p.codigo = 'CPE17E5') OR -- Diseño de Experimentos -> Modelos Lineales
      (a.codigo = 'CPE08E5' AND p.codigo = 'CPE02E5') OR -- Econometría -> Análisis de Regresión
      (a.codigo = 'CBE09C5' AND p.codigo = 'CBM09C5') OR -- Estadística Aplicada -> Álgebra y Trigonometría
      (a.codigo = 'CPE10E5' AND p.codigo = 'CBE09C5') OR -- Estadísticas Demográficas -> Estadística Aplicada
      (a.codigo = 'CBF19C5' AND p.codigo = 'CBM22C5') OR -- Física General -> Cálculo Diferencial
      (a.codigo = 'CBM33C5' AND p.codigo = 'CBM09C5') OR -- Geometría Analítica -> Álgebra y Trigonometría
      (a.codigo = 'CPE11E5' AND p.codigo = 'CPE12E5') OR -- Inferencia Bayesiana -> Inferencia Estadística
      (a.codigo = 'CPE12E5' AND p.codigo = 'CPM06C5') OR -- Inferencia Estadística -> Álgebra Lineal II
      (a.codigo = 'CPE12E5' AND p.codigo = 'CPE20C5') OR -- Inferencia Estadística -> Probabilidad y Estadística
      (a.codigo = 'CCE13E5' AND p.codigo = 'CCE14E5') OR -- Ciencia de Datos -> Programación
      (a.codigo = 'CCE14E5' AND p.codigo = 'CPM18C5') OR -- Programación -> Análisis Numérico
      (a.codigo = 'CPE15C5' AND p.codigo = 'CBE09C5') OR -- Investigación Operativa -> Estadística Aplicada
      (a.codigo = 'CPB24C5' AND p.codigo = 'CBE09C5') OR -- Metodología -> Estadística Aplicada
      (a.codigo = 'CPE16E5' AND p.codigo = 'CPE11E5') OR -- Métodos No Paramétricos -> Inferencia Bayesiana
      (a.codigo = 'CPE17E5' AND p.codigo = 'CPE02E5') OR -- Modelos Lineales -> Análisis de Regresión
      (a.codigo = 'CPE18E5' AND p.codigo = 'CPE17E5') OR -- Modelos Lineales Generalizados -> Modelos Lineales
      (a.codigo = 'PE19E5' AND p.codigo = 'CPE02E5') OR  -- Pasantía -> Análisis de Regresión
      (a.codigo = 'PE19E5' AND p.codigo = 'CPE01E5') OR  -- Pasantía -> Análisis de Datos
      (a.codigo = 'CPE20C5' AND p.codigo = 'CBM36C5') OR -- Probabilidad y Estadística -> Matemática Discreta
      (a.codigo = 'CPE21E5' AND p.codigo = 'CPE20C5') OR -- Procesos Estocásticos -> Probabilidad y Estadística
      (a.codigo = 'CPE21E5' AND p.codigo = 'CPM16C5') OR -- Procesos Estocásticos -> Análisis Matemático II
      (a.codigo = 'CPE22E5' AND p.codigo = 'CPE20C5');   -- Técnica de Muestreo -> Probabilidad y Estadística

-- Prerrequisitos Física
INSERT OR IGNORE INTO Prerequisito (id_asignatura, id_prerequisito)
SELECT a.id_asignatura, p.id_asignatura
FROM Asignatura a, Asignatura p
WHERE (a.codigo = 'CBM04CS' AND p.codigo = 'CBM08CS') OR -- Álgebra Lineal -> Álgebra y Geometría
      (a.codigo = 'CBM15CS' AND p.codigo = 'CBM22CS') OR -- Análisis Matemático I -> Cálculo Diferencial
      (a.codigo = 'CBM16CS' AND p.codigo = 'CBM15CS') OR -- Análisis Matemático II -> Análisis Matemático I
      (a.codigo = 'CCM17CS' AND p.codigo = 'CBM16CS') OR -- Análisis Matemático III -> Análisis Matemático II
      (a.codigo = 'CBM27CS' AND p.codigo = 'CBM16CS') OR -- Ecuaciones Diferenciales -> Análisis Matemático II
      (a.codigo = 'CBF02CS' AND p.codigo = 'CBF37CS') OR -- Electricidad y Magnetismo -> Mecánica
      (a.codigo = 'CPF04FS' AND p.codigo = 'CCM17CS') OR -- Elem. Física Teórica I -> Análisis Matemático III
      (a.codigo = 'CPF04FS' AND p.codigo = 'CBE09CS') OR -- Elem. Física Teórica I -> Estadística Aplicada
      (a.codigo = 'CPF05FS' AND p.codigo = 'CPF04FS') OR -- Elem. Física Teórica II -> Elem. Física Teórica I
      (a.codigo = 'CBE09CS' AND p.codigo = 'CBM08CS') OR -- Estadística Aplicada -> Álgebra y Geometría
      (a.codigo = 'CPF08CS' AND p.codigo = 'CBF02CS') OR -- Física Computacional I -> Electricidad y Magnetismo
      (a.codigo = 'CPF08CS' AND p.codigo = 'CBM04CS') OR -- Física Computacional I -> Álgebra Lineal
      (a.codigo = 'CPF09CS' AND p.codigo = 'CPF08CS') OR -- Física Computacional II -> Física Computacional I
      (a.codigo = 'CPF13FS' AND p.codigo = 'CPF17FS') OR -- Física del Estado Sólido -> Física Teórica
      (a.codigo = 'CPF17FS' AND p.codigo = 'CPF26FS') OR -- Física Teórica -> Física Térmica y Termodinámica
      (a.codigo = 'CPF23FS' AND p.codigo = 'CPF47FS') OR -- Física Moderna I -> Óptica Física
      (a.codigo = 'CPF23FS' AND p.codigo = 'CBQ18CS') OR -- Física Moderna I -> Química General I
      (a.codigo = 'CPF24FS' AND p.codigo = 'CPF23FS') OR -- Física Moderna II -> Física Moderna I
      (a.codigo = 'CPF26FS' AND p.codigo = 'CBM27CS') OR -- Física Térmica -> Ecuaciones Diferenciales
      (a.codigo = 'CPF30FS' AND p.codigo = 'CPF34FS') OR -- Lab Electricidad -> Lab Mecánica
      (a.codigo = 'CPF30FS' AND p.codigo = 'CBF02CS') OR -- Lab Electricidad -> Electricidad y Magnetismo
      (a.codigo = 'CCF31FS' AND p.codigo = 'CPF35FS') OR -- Lab Electrónica -> Lab Ondas
      (a.codigo = 'CPF34FS' AND p.codigo = 'CBF37CS') OR -- Lab Mecánica -> Mecánica
      (a.codigo = 'CPF35FS' AND p.codigo = 'CPF30FS') OR -- Lab Ondas -> Lab Electricidad
      (a.codigo = 'CPF35FS' AND p.codigo = 'CPF47FS') OR -- Lab Ondas -> Óptica Física
      (a.codigo = 'CPF38FS' AND p.codigo = 'CPF45FS') OR -- Mecánica Clásica I -> Ondas
      (a.codigo = 'CPF38FS' AND p.codigo = 'CBM27CS') OR -- Mecánica Clásica I -> Ecuaciones Diferenciales
      (a.codigo = 'CPF39FS' AND p.codigo = 'CPF38FS') OR -- Mecánica Clásica II -> Mecánica Clásica I
      (a.codigo = 'CPF41FS' AND p.codigo = 'CPF39FS') OR -- Mecánica Cuántica I -> Mecánica Clásica II
      (a.codigo = 'CPF41FS' AND p.codigo = 'CPF05FS') OR -- Mecánica Cuántica I -> Elem Fis Teórica II
      (a.codigo = 'CPF42FS' AND p.codigo = 'CPF41FS') OR -- Mecánica Cuántica II -> Mecánica Cuántica I
      (a.codigo = 'CPF45FS' AND p.codigo = 'CBM16CS') OR -- Ondas -> Análisis Matemático II
      (a.codigo = 'CPF45FS' AND p.codigo = 'CPF47FS') OR -- Ondas -> Óptica Física
      (a.codigo = 'CPF47FS' AND p.codigo = 'CBF37CS') OR -- Óptica Física -> Mecánica
      (a.codigo = 'PF49FS' AND p.codigo = 'CCF31FS') OR  -- Práctica Profesional -> Lab Electrónica
      (a.codigo = 'PF49FS' AND p.codigo = 'CPF09CS') OR  -- Práctica Profesional -> Física Computacional II
      (a.codigo = 'CPF52FS' AND p.codigo = 'CPF39FS') OR -- Teoría Electromagnética I -> Mecánica Clásica I
      (a.codigo = 'CPF52FS' AND p.codigo = 'CPF04FS') OR -- Teoría Electromagnética I -> Elem Fis Teórica I
      (a.codigo = 'CPF53FS' AND p.codigo = 'CPF52FS') OR -- Teoría Electromagnética II -> Teoría Electromagnética I
      (a.codigo = 'TGF54FS' AND p.codigo = 'PF49FS') OR  -- Trabajo de Grado -> Práctica Profesional
      (a.codigo = 'TGF54FS' AND p.codigo = 'CPF53FS');   -- Trabajo de Grado -> Teoría Electromagnética II

-- Prerrequisitos Logística
INSERT OR IGNORE INTO Prerequisito (id_asignatura, id_prerequisito)
SELECT a.id_asignatura, p.id_asignatura
FROM Asignatura a, Asignatura p
WHERE (a.codigo = 'CPT02L5' AND p.codigo = 'CPT13C5') OR -- Costos -> Fundamentos Logística
      (a.codigo = 'CPT04L5' AND p.codigo = 'CPT21L5');   -- Derecho Transporte -> Gestión y Operaciones