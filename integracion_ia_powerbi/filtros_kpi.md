# 🎛 Filtros KPI — IntegrityCheck AI Dashboard

Documentación de los filtros (slicers) disponibles en el dashboard de Power BI.

---

## Filtros disponibles

### 1. 🏫 Facultad
Filtra todos los visuales por facultad académica.

| Valor | Descripción |
|---|---|
| Ingeniería | Facultad de Ingeniería y Tecnología |
| Medicina | Facultad de Ciencias de la Salud |
| Derecho | Facultad de Derecho y Ciencias Políticas |
| Administración | Facultad de Administración y Negocios |

**Vista SQL afectada:** `v_kpi_tasa_fraude`, `v_kpi_notas`, `v_dashboard_principal`

---

### 2. ⚠ Nivel de Riesgo
Filtra por el nivel de riesgo calculado por el pipeline IA.

| Valor | Rango score_riesgo | Color dashboard |
|---|---|---|
| BAJO | 0 – 39 | Verde |
| MEDIO | 40 – 69 | Amarillo |
| ALTO | 70 – 100 | Rojo |

**Vista SQL afectada:** `v_kpi_nivel_riesgo`, `v_dashboard_principal`

---

### 3. 📅 Semestre
Filtra por período académico.

| Valor | Descripción |
|---|---|
| 2024-I | Primer semestre 2024 |
| 2024-II | Segundo semestre 2024 |
| 2025-I | Primer semestre 2025 |

---

### 4. 🔍 Tipo de Fraude
Filtra por categoría de fraude detectada por los modelos IA.

| Valor | Modelo que lo detecta |
|---|---|
| Plagio directo | TF-IDF + Turnitin |
| Copia entre pares | Random Forest |
| Contrato de trampa | Isolation Forest + RF |
| Sin incidente | — |

---

### 5. 👨‍🏫 Docente
Filtra por docente responsable del curso.

Slicer de lista desplegable conectado a `dw.DimDocente`.

---

## Interacción entre filtros

Todos los filtros actúan de forma **cruzada** (cross-filter). Al seleccionar Ingeniería + ALTO riesgo, todos los visuales del dashboard se actualizan simultáneamente mostrando solo estudiantes de Ingeniería con riesgo alto.

## Restablecer filtros

Botón **"Limpiar filtros"** en la esquina superior derecha del dashboard resetea todos los slicers a su estado inicial.
