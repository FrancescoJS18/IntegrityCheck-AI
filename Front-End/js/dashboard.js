/* ==========================================================================
   IntegrityCheck AI - Dashboard Logic Controller
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Validar Sesión Activa
    if (!ApiClient.validarSesion()) return;

    // 2. Cargar Perfil de Usuario en el Sidebar
    const usuario = ApiClient.obtenerUsuarioLogueado();
    if (usuario) {
        document.getElementById("user-display-name").textContent = usuario.nombre;
        document.getElementById("user-display-role").textContent = usuario.rol;
        document.getElementById("user-avatar-text").textContent = usuario.nombre.substring(0, 2).toUpperCase();
        
        // Mostrar etiqueta de RLS si es Decano
        if (usuario.rol === "DECANO") {
            const rlsLabel = document.createElement("span");
            rlsLabel.className = "badge badge-revision";
            rlsLabel.style.marginLeft = "10px";
            rlsLabel.style.fontSize = "0.7rem";
            rlsLabel.textContent = usuario.facultad;
            document.querySelector(".header-title").appendChild(rlsLabel);
        }
    }

    // 3. Manejador de Cierre de Sesión
    document.getElementById("btn-logout").addEventListener("click", (e) => {
        e.preventDefault();
        ApiClient.cerrarSesion();
    });

    // 4. Cargar Métricas y Gráficos del Dashboard
    inicializarDashboard();
});

async function inicializarDashboard() {
    try {
        mostrarCargando(true);

        // A. Cargar KPIs
        const kpis = await ApiClient.getDashboardKPIs();
        if (kpis) {
            document.getElementById("val-total-casos").textContent = kpis.total_casos;
            document.getElementById("val-casos-pendientes").textContent = kpis.casos_pendientes;
            document.getElementById("val-indice-integridad").textContent = `${kpis.indice_integridad}%`;
            document.getElementById("val-similitud-promedio").textContent = `${kpis.similitud_promedio}%`;
        }

        // B. Cargar Evolución Mensual (Línea)
        const evolucion = await ApiClient.getEvolucionMensual();
        if (evolucion) {
            ChartManager.crearGraficoTendencia("chart-tendencia", evolucion);
        }

        // C. Cargar Distribución por Tipo (Dona)
        const distribucion = await ApiClient.getTiposFraude();
        if (distribucion) {
            ChartManager.crearGraficoDistribucion("chart-distribucion", distribucion);
        }

        // D. Cargar Ranking de Facultades (Barras)
        const ranking = await ApiClient.getFacultadesRanking();
        if (ranking) {
            ChartManager.crearGraficoFacultades("chart-facultades", ranking);
            cargarTablaRanking(ranking);
        }

        // E. Cargar Alertas Recientes (Tabla en Dashboard)
        const alertas = await ApiClient.getAlertas(70.0);
        if (alertas) {
            cargarTablaAlertasDashboard(alertas.slice(0, 5)); // Mostrar solo las 5 más críticas en el dashboard
        }

    } catch (error) {
        console.error("Error al cargar datos del dashboard:", error);
    } finally {
        mostrarCargando(false);
    }
}

function cargarTablaRanking(ranking) {
    const tbody = document.getElementById("table-body-ranking");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    
    ranking.forEach((item, index) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td><strong style="color: var(--accent-cyan)">#${index + 1}</strong></td>
            <td><strong>${item.facultad}</strong></td>
            <td class="text-right">${item.total_estudiantes}</td>
            <td class="text-right">${item.total_incidentes}</td>
            <td class="text-right"><span class="badge ${item.tasa_incidentes > 40 ? 'badge-grave' : 'badge-leve'}">${item.tasa_incidentes.toFixed(1)}%</span></td>
        `;
        tbody.appendChild(row);
    });
}

function cargarTablaAlertasDashboard(alertas) {
    const tbody = document.getElementById("table-body-alertas-dashboard");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    
    if (alertas.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted)">No hay alertas críticas pendientes.</td></tr>`;
        return;
    }

    alertas.forEach(alerta => {
        const row = document.createElement("tr");
        
        let badgeGravedad = "badge-leve";
        if (alerta.nivel_gravedad === "GRAVE") badgeGravedad = "badge-grave";
        else if (alerta.nivel_gravedad === "MODERADO") badgeGravedad = "badge-moderado";
        
        row.innerHTML = `
            <td><strong>${alerta.estudiante_codigo}</strong></td>
            <td>${alerta.estudiante_nombre}</td>
            <td>${alerta.curso_nombre}</td>
            <td><span class="badge ${badgeGravedad}">${alerta.nivel_gravedad}</span></td>
            <td>
                <div class="risk-indicator ${alerta.puntaje_riesgo >= 80 ? 'risk-high' : 'risk-medium'}">
                    <span class="risk-dot"></span>
                    <span>${alerta.puntaje_riesgo.toFixed(1)}%</span>
                </div>
            </td>
            <td><span class="badge badge-${alerta.estado_caso.toLowerCase().replace('_', '')}">${alerta.estado_caso}</span></td>
        `;
        tbody.appendChild(row);
    });
}

function mostrarCargando(cargando) {
    // Si hay un contenedor de loader se puede mostrar, si no simplemente logs
    if (cargando) {
        console.log("Cargando datos...");
    } else {
        console.log("Datos cargados.");
    }
}
