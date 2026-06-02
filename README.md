# IntegrityCheck AI — Plataforma BI de Detección de Fraude Académico

**IntegrityCheck AI** es una plataforma de Business Intelligence integral para la detección y monitoreo de fraudes académicos en universidades peruanas (por ejemplo, copias en exámenes virtuales, plagio de entregables/tesis e irregularidades en calificaciones de docentes). El sistema combina una base de datos analítica en SQL Server, procesos de ETL relacionales, un motor inteligente de Machine Learning (Python/scikit-learn) y un Front-End web dinámico y premium con estilo Glassmorphic.

---

## 🏗️ ARQUITECTURA BI DE 7 CAPAS

1. **Capa 1: Fuentes de Datos**: Conectores pyodbc y pandas para ingerir registros de notas SGA, logs LMS Moodle, similitudes Turnitin, IPs de exámenes virtuales y verificación RENIEC.
2. **Capa 2: Staging Area (Landing Zone)**: Tablas crudas de entrada con prefijo `stg_` en SQL Server para pre-auditar cargas por `id_carga` con validación de estado (`VALIDO`/`INVALIDO`).
3. **Capa 3: Proceso ETL**: Stored procedures en T-SQL (`sp_etl_extract`, `sp_etl_transform`, `sp_etl_load`) que limpian, normalizan e inyectan datos deduplicados (MERGE) en el DW.
4. **Capa 4: Data Warehouse (Modelo Snowflake)**: Tabla de hechos central `FactIncidenteFraude` rodeada por dimensiones como `DimEstudiante`, `DimDocente`, `DimCurso`, `DimFacultad`, `DimSede`, `DimTiempo`, `DimTipoPrueba` y `DimTipoFraude`.
5. **Capa 5: Motor de IA (Python ML)**:
   - **Riesgo de Fraude**: Random Forest Classifier que predice colusiones y copias virtuales.
   - **Plagio Textual**: Similitud Coseno + representación vectorial TF-IDF NLP (N-Gram 1-2).
   - **Anomalías de Notas**: Isolation Forest que localiza saltos sospechosos en actas (ej. notas infladas sin actividad).
6. **Capa 6: Capa Semántica (KPIs)**: Vistas analíticas calculadas (`vw_kpi_tasa_incidentes_facultad`, `vw_kpi_indice_integridad`, etc.) expuestas mediante clases de abstracción de datos en Python.
7. **Capa 7: Visualización BI (Front-End)**: Interfaz web de alta calidad estética (Glassmorphism), gráficos dinámicos con Chart.js y consumo REST fetch con validación JWT y control RLS (Row Level Security) para Decanos.

---

## 📁 ESTRUCTURA DEL PROYECTO

```
SIS/
├── Front-End/
│   ├── index.html                # Enrutador e inicio
│   ├── login.html                # Pantalla de login premium con roles
│   ├── dashboard.html            # Panel central de métricas y gráficos
│   ├── alertas.html              # Bandeja de alertas y filtros dinámicos
│   ├── reportes.html             # Métricas de IA y playgrounds interactivos
│   ├── css/
│   │   ├── styles.css            # Estilos globales y tokens
│   │   └── dashboard.css         # Estilos específicos del BI y tablas
│   └── js/
│       ├── api.js                # Cliente HTTP fetch y manejo de JWT
│       ├── charts.js             # Configurador de Chart.js
│       └── dashboard.js          # Orquestador del dashboard
│
├── Back-End/
│   ├── app.py                    # Servidor Flask principal y APScheduler
│   ├── requirements.txt          # Dependencias del Backend
│   ├── config.py                 # Carga de configuraciones de entorno
│   ├── ClaseBD/
│   │   ├── __init__.py
│   │   ├── conexion.py           # Conector robusto pyodbc a SQL Server
│   │   ├── estudiante.py         # CRUD DimEstudiante
│   │   ├── incidente.py          # CRUD FactIncidente y disparador ETL
│   │   ├── docente.py            # CRUD DimDocente
│   │   └── kpi.py                # Acceso a Vistas de KPIs
│   └── ClaseMLS/
│       ├── __init__.py
│       ├── preprocesador.py      # Limpieza y formateo pre-ML
│       ├── predictor.py          # Interfaz de estimación (PKL)
│       └── evaluador.py          # Monitor de métricas de IA
│
├── ML/
│   ├── requirements_ml.txt       # Dependencias de Machine Learning
│   ├── config_ml.py              # Parámetros y paths del motor
│   ├── train_modelo_riesgo.py    # Entrenador de Random Forest
│   ├── train_modelo_plagio.py    # Entrenador de NLP TF-IDF
│   ├── train_modelo_anomalia.py  # Entrenador de Isolation Forest
│   ├── predict.py                # Inferencia batch de prueba
│   ├── evaluar_modelos.py        # Generador de reportes de performance
│   └── modelos/
│       └── .gitkeep              # Directorio compilado .pkl
│
├── BD/
│   ├── script_crear_bd.sql       # Creación e inicialización del Collation
│   ├── script_tablas_staging.sql # Esquema temporal staging
│   ├── script_dw.sql             # Estructura de Hechos y Dimensiones
│   ├── script_kpis_views.sql     # Definición de KPIs en vistas SQL
│   ├── script_sp_etl.sql         # Procedimientos almacenados ETL (Merge)
│   ├── script_indices.sql        # Índices de performance
│   └── script_datos_prueba.sql   # Generador de +200 registros peruanos
│
├── README.md                     # Documentación general
├── .gitignore                    # Filtros Git
└── docker-compose.yml            # Levantar infraestructura integrada
```

---

## 🛠️ INSTRUCCIONES DE INSTALACIÓN Y USO

### Paso 1: Configurar la Base de Datos (SQL Server)

Ejecute en orden los scripts ubicados en la carpeta `BD/` en su instancia de SQL Server 2022:

1. `script_crear_bd.sql`
2. `script_tablas_staging.sql`
3. `script_dw.sql`
4. `script_kpis_views.sql`
5. `script_sp_etl.sql`
6. `script_indices.sql`
7. `script_datos_prueba.sql`

### Paso 2: Configurar variables de entorno (.env)

Si desea personalizar el conector SQL Server, cree un archivo `.env` en la raíz de `Back-End/` con la siguiente información:

```env
DB_SERVER=localhost
DB_DATABASE=IntegrityCheckAI
DB_PORT=1433
DB_TRUSTED_CONNECTION=True
```

_Nota: Si la base de datos no está disponible, el backend activará automáticamente un **modo simulado (Mock Mode)**, el cual cargará datos realistas ficticios directamente en memoria para que pueda evaluar la interfaz web al instante sin configuraciones previas._

### Paso 3: Instalar Dependencias y Entrenar Modelos ML

Abra su terminal y ejecute los instaladores y scripts de entrenamiento de IA:

```bash
# Instalar requerimientos del backend y ML
pip install -r Back-End/requirements.txt -r ML/requirements_ml.txt

# Entrenar los 3 modelos predictivos
python ML/train_modelo_riesgo.py
python ML/train_modelo_plagio.py
python ML/train_modelo_anomalia.py

# (Opcional) Evaluar métricas de rendimiento compiladas
python ML/evaluar_modelos.py
```

### Paso 4: Iniciar el Backend API Flask

Para encender el servidor REST en `http://localhost:5000`:

```bash
python Back-End/app.py
```

_Esto iniciará además el programador interno (APScheduler), el cual orquesta el ETL diario a las 2:00 AM y la actualización de predicciones batch a las 6:00 AM._

### Paso 5: Abrir la interfaz Front-End

Abra el archivo `Front-End/login.html` directamente en su navegador web favorito.

---

## 🔐 CREDENCIALES DE PRUEBA (JWT LOGIN ROLES)

Para evaluar las diferentes vistas y restricciones de seguridad, use los accesos rápidos de la pantalla de Login:

- **Rector** (Ver todo el campus peruano):
  - Usuario: `rector@integrity.edu.pe` | Password: `rector123`
- **Decano de Ingeniería** (Restringido por RLS a su facultad):
  - Usuario: `decano_ing@integrity.edu.pe` | Password: `decano123`
- **Decano de Derecho** (Restringido por RLS a su facultad):
  - Usuario: `decano@integrity.edu.pe` | Password: `decano123`
- **Auditor** (Solo visualización general):
  - Usuario: `auditor@integrity.edu.pe` | Password: `auditor123`

# 🔍 IntegrityCheck AI

> **Sistema de detección de fraude académico** basado en un pipeline de Business Intelligence de 7 capas con modelos de Inteligencia Artificial integrados.

---

## 🏗 Arquitectura — Pipeline 7 Capas BI

```
┌─────────────────────────────────────────────────────────┐
│  C1: Fuentes    →  SGA, LMS, Turnitin, Excel, Exámenes  │
│  C2: Staging    →  Validación, cuarentena, reglas VR    │
│  C3: ETL        →  Extract → Transform → Load (SQL)     │
│  C4: DW         →  Esquema Copo de Nieve (Snowflake)    │
│  C5: IA         →  Random Forest + TF-IDF + Iso Forest  │
│  C6: KPIs       →  6 métricas semánticas trazables      │
│  C7: Dashboard  →  Power BI + gráficos interactivos     │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del proyecto

```
IntegrityCheck AI/
├── Front-End/
│   └── demo_7capas.html          ← Demo interactivo del pipeline
├── integracion_ia_powerbi/       ← Integración IA + Power BI ⭐
│   ├── README.md
│   ├── conexion_powerbi.py       ← Pipeline Python completo
│   ├── kpi_queries.sql           ← Vistas SQL para Power BI
│   ├── powerbi_config.json       ← Configuración de conexión
│   └── filtros_kpi.md            ← Documentación de filtros
├── data/
│   └── estudiantes_lote1_500.xlsx
├── IntegrityCheck_Dashboard.pbix ← Dashboard Power BI
└── README.md                     ← Este archivo
```

---

## 🚀 Cómo usar

### Demo interactivo

1. Abre `Front-End/demo_7capas.html` en Chrome o Edge
2. Carga el archivo `data/estudiantes_lote1_500.xlsx`
3. Haz clic en **▶ PROCESAR POR LAS 7 CAPAS BI**
4. Navega capa por capa con el botón **Siguiente →**
5. En Capa 7, haz clic en **⚡ ABRIR EN POWER BI**

### Pipeline completo (Python)

```bash
cd integracion_ia_powerbi
pip install pandas scikit-learn sqlalchemy pyodbc openpyxl
python conexion_powerbi.py --input ../data/estudiantes_lote1_500.xlsx
```

---

## 🤖 Modelos de IA

| Modelo                      | Tarea                                 | Métricas                    |
| --------------------------- | ------------------------------------- | --------------------------- |
| Random Forest (100 árboles) | Clasificación supervisada de fraude   | Accuracy: 94.2% · F1: 92.4% |
| TF-IDF + Cosine Similarity  | Detección de plagio semántico         | Similitud umbral: 40%       |
| Isolation Forest            | Detección de anomalías no supervisada | Contaminación: 5%           |

---

## 📊 KPIs del Dashboard

1. **Tasa de Fraude** — `COUNT(fraude) / COUNT(*) × 100`
2. **Similitud Turnitin** — `AVG(similitud_turnitin)`
3. **Estudiantes Alto Riesgo** — `COUNT WHERE score_riesgo ≥ 70`
4. **Nota Promedio** — `AVG(nota_final)`
5. **Efectividad IA** — F1-Score del modelo Random Forest
6. **Tiempo de Procesamiento** — Latencia media del pipeline

---

## 🛠 Tecnologías

- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Backend / IA**: Python 3.11, scikit-learn, pandas, numpy
- **Base de Datos**: SQL Server (DW con esquema Snowflake)
- **Visualización**: Power BI Desktop (.pbix)
- **Pipeline**: ETL personalizado con staging area y validación

---

## 👥 Proyecto académico

Desarrollado como proyecto de curso de Business Intelligence.
Universidad · Facultad de Ingeniería · 2025
