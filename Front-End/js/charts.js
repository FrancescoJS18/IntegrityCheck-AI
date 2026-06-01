/* ==========================================================================
   IntegrityCheck AI - BI Visualizations (Chart.js Configuration)
   ========================================================================== */

const ChartManager = {
    charts: {},

    // Colores del tema del diseño
    colors: {
        cyan: '#00f2fe',
        blue: '#4facfe',
        purple: '#7f00ff',
        pink: '#ff007f',
        amber: '#ffb800',
        emerald: '#00e676',
        gridLines: 'rgba(255, 255, 255, 0.05)',
        text: '#8f9cae'
    },

    // 1. Gráfico de Tendencia Evolutiva (Líneas)
    crearGraficoTendencia(canvasId, datos) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const ctx = document.getElementById(canvasId).getContext('2d');
        
        // Crear gradiente de línea
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(0, 242, 254, 0.35)');
        gradient.addColorStop(1, 'rgba(0, 242, 254, 0.00)');

        const labels = datos.map(d => {
            const meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
            return meses[d.mes - 1] || `Mes ${d.mes}`;
        });
        const valores = datos.map(d => d.total_incidentes);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Incidentes Detectados',
                    data: valores,
                    borderColor: this.colors.cyan,
                    borderWidth: 3,
                    pointBackgroundColor: this.colors.cyan,
                    pointHoverRadius: 6,
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(11, 14, 31, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: 'rgba(0, 242, 254, 0.2)',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { color: this.colors.gridLines },
                        ticks: { color: this.colors.text }
                    },
                    y: {
                        grid: { color: this.colors.gridLines },
                        ticks: { 
                            color: this.colors.text,
                            stepSize: 5
                        },
                        beginAtZero: true
                    }
                }
            }
        });
    },

    // 2. Gráfico de Distribución por Tipo de Fraude (Dona)
    crearGraficoDistribucion(canvasId, datos) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const ctx = document.getElementById(canvasId).getContext('2d');
        const labels = datos.map(d => d.tipo_fraude);
        const valores = datos.map(d => d.total_casos);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: valores,
                    backgroundColor: [
                        this.colors.pink,
                        this.colors.purple,
                        this.colors.blue,
                        this.colors.amber,
                        this.colors.emerald,
                        '#8a2be2'
                    ],
                    borderWidth: 2,
                    borderColor: '#0f1326'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: this.colors.text,
                            padding: 15,
                            font: { size: 10 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(11, 14, 31, 0.9)',
                        borderColor: 'rgba(255, 255, 255, 0.08)',
                        borderWidth: 1
                    }
                },
                cutout: '70%'
            }
        });
    },

    // 3. Gráfico de Comparación de Facultades (Barras)
    crearGraficoFacultades(canvasId, datos) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const ctx = document.getElementById(canvasId).getContext('2d');
        const labels = datos.map(d => d.facultad.replace("Facultad de ", ""));
        const valores = datos.map(d => d.tasa_incidentes);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Tasa de Incidentes (%)',
                    data: valores,
                    backgroundColor: this.colors.blue,
                    hoverBackgroundColor: this.colors.cyan,
                    borderRadius: 8,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(11, 14, 31, 0.9)',
                        borderColor: 'rgba(255, 255, 255, 0.08)',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: this.colors.text }
                    },
                    y: {
                        grid: { color: this.colors.gridLines },
                        ticks: { color: this.colors.text },
                        beginAtZero: true
                    }
                }
            }
        });
    }
};
