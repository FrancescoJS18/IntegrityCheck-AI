/* ==========================================================================
   IntegrityCheck AI - API Fetch Wrapper (Capa de Integración)
   ========================================================================== */

const API_BASE_URL = "http://localhost:5000";

const ApiClient = {
    // Obtener los datos del usuario logueado en formato objeto
    obtenerUsuarioLogueado() {
        const userStr = localStorage.getItem("user");
        if (!userStr) return null;
        try {
            return JSON.parse(userStr);
        } catch (e) {
            return null;
        }
    },

    // Obtener token JWT
    obtenerToken() {
        return localStorage.getItem("token");
    },

    // Guardar sesión
    guardarSesion(token, usuario) {
        localStorage.setItem("token", token);
        localStorage.setItem("user", JSON.stringify(usuario));
    },

    // Cerrar sesión y redireccionar
    cerrarSesion() {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.href = "login.html";
    },

    // Validar si existe sesión activa, si no redirigir a login
    validarSesion() {
        const token = this.obtenerToken();
        const user = this.obtenerUsuarioLogueado();
        
        // Evitar bucles infinitos en login.html
        const enLogin = window.location.pathname.includes("login.html");
        
        if (!token || !user) {
            if (!enLogin) {
                window.location.href = "login.html";
            }
            return false;
        }
        
        if (enLogin) {
            window.location.href = "dashboard.html";
        }
        return true;
    },

    // Realizar peticiones fetch genéricas con cabeceras Bearer JWT
    async request(endpoint, method = "GET", body = null) {
        const url = `${API_BASE_URL}${endpoint}`;
        const token = this.obtenerToken();
        
        const headers = {
            "Content-Type": "application/json"
        };
        
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        const config = {
            method: method,
            headers: headers
        };

        if (body) {
            config.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(url, config);
            
            // Si el token es inválido o expiró (401), cerrar sesión
            if (response.status === 401) {
                console.warn("Sesión expirada o token inválido.");
                this.cerrarSesion();
                return null;
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.mensaje || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`Error en API Request [${method}] ${endpoint}:`, error);
            throw error;
        }
    },

    // --- Métodos de la API ---

    async login(usuario, password) {
        const res = await this.request("/auth/login", "POST", { usuario, password });
        if (res && res.token) {
            this.guardarSesion(res.token, res.usuario);
            return res.usuario;
        }
        return null;
    },

    async getDashboardKPIs() {
        return await this.request("/api/kpis/dashboard");
    },

    async getFacultadesRanking() {
        return await this.request("/api/kpis/facultades");
    },

    async getAlertas(umbral = 70.0) {
        return await this.request(`/api/alertas?umbral=${umbral}`);
    },

    async getAlertaDetalle(id) {
        return await this.request(`/api/alertas/${id}`);
    },

    async actualizarAlertaEstado(id, nuevoEstado) {
        return await this.request(`/api/alertas/${id}`, "PUT", { estado_caso: nuevoEstado });
    },

    async predecirRiesgo(datosEstudiante) {
        return await this.request("/api/predecir/riesgo", "POST", datosEstudiante);
    },

    async predecirPlagio(texto) {
        return await this.request("/api/predecir/plagio", "POST", { texto });
    },

    async getReporteMensual() {
        return await this.request("/api/reportes/mensual");
    },

    async getEvolucionMensual() {
        return await this.request("/api/evolucion/mensual");
    },

    async getTiposFraude() {
        return await this.request("/api/tipos-fraude");
    }
};
