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
