/**
 * Sistema de captura de firmas digitales con HTML5 Canvas
 */

class SignatureCapture {
    constructor(canvasId, hiddenInputId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Canvas no encontrado:', canvasId);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.hiddenInput = document.getElementById(hiddenInputId);
        this.isDrawing = false;
        this.lastX = 0;
        this.lastY = 0;
        
        this.setupCanvas();
        this.bindEvents();
    }
    
    setupCanvas() {
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
        
        this.ctx.strokeStyle = '#000000';
        this.ctx.lineWidth = 2;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    bindEvents() {
        this.canvas.addEventListener('mousedown', this.startDrawing.bind(this));
        this.canvas.addEventListener('mousemove', this.draw.bind(this));
        this.canvas.addEventListener('mouseup', this.stopDrawing.bind(this));
        this.canvas.addEventListener('mouseout', this.stopDrawing.bind(this));
        
        this.canvas.addEventListener('touchstart', this.handleTouch.bind(this));
        this.canvas.addEventListener('touchmove', this.handleTouch.bind(this));
        this.canvas.addEventListener('touchend', this.stopDrawing.bind(this));
    }
    
    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }
    
    getTouchPos(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: e.touches[0].clientX - rect.left,
            y: e.touches[0].clientY - rect.top
        };
    }
    
    startDrawing(e) {
        this.isDrawing = true;
        const pos = this.getMousePos(e);
        this.lastX = pos.x;
        this.lastY = pos.y;
    }
    
    draw(e) {
        if (!this.isDrawing) return;
        
        const pos = this.getMousePos(e);
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.lastX, this.lastY);
        this.ctx.lineTo(pos.x, pos.y);
        this.ctx.stroke();
        
        this.lastX = pos.x;
        this.lastY = pos.y;
        
        this.updateHiddenInput();
    }
    
    handleTouch(e) {
        e.preventDefault();
        
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 'mousemove', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        this.canvas.dispatchEvent(mouseEvent);
    }
    
    stopDrawing() {
        if (this.isDrawing) {
            this.isDrawing = false;
            this.updateHiddenInput();
        }
    }
    
    updateHiddenInput() {
        // Convertir canvas a base64 con calidad optimizada
        const dataURL = this.canvas.toDataURL('image/jpeg', 0.8);
        this.hiddenInput.value = dataURL;
    }
    
    clear() {
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.hiddenInput.value = '';
    }
    
    isEmpty() {
        // Verificar si el canvas está vacío (solo fondo blanco)
        const blank = document.createElement('canvas');
        blank.width = this.canvas.width;
        blank.height = this.canvas.height;
        const blankCtx = blank.getContext('2d');
        blankCtx.fillStyle = '#ffffff';
        blankCtx.fillRect(0, 0, blank.width, blank.height);
        
        return this.canvas.toDataURL() === blank.toDataURL();
    }
}

// Sistema de validación mejorado para formularios
class RoundFormValidator {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.signatures = {};
        this.sinNovedadMode = false;
        
        this.initializeSignatures();
        this.bindEvents();
    }
    
    initializeSignatures() {
        // Inicializar captura de firmas
        if (document.getElementById('canvas-firma-servicio')) {
            this.signatures.servicio = new SignatureCapture('canvas-firma-servicio', 'id_firma_servicio');
        }
        if (document.getElementById('canvas-firma-ronda')) {
            this.signatures.ronda = new SignatureCapture('canvas-firma-ronda', 'id_firma_ronda');
        }
    }
    
    bindEvents() {
        // Botón "Sin novedad"
        const sinNovedadBtn = document.getElementById('btn-sin-novedad');
        if (sinNovedadBtn) {
            sinNovedadBtn.addEventListener('click', this.toggleSinNovedad.bind(this));
        }
        
        // Botones limpiar firma
        const clearButtons = document.querySelectorAll('.btn-clear-signature');
        clearButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const canvasId = e.target.getAttribute('data-canvas');
                if (canvasId && this.signatures[canvasId]) {
                    this.signatures[canvasId].clear();
                }
            });
        });
        
        // Validación al enviar
        this.form.addEventListener('submit', this.validateForm.bind(this));
    }
    
    toggleSinNovedad() {
        this.sinNovedadMode = !this.sinNovedadMode;
        
        const fieldsToToggle = [
            'id_hallazgo',
            'id_placa_equipo', 
            'id_orden_trabajo',
            'id_eventos_seguridad',
            'id_fuera_de_servicio'
        ];
        
        const btn = document.getElementById('btn-sin-novedad');
        const hiddenSinNovedad = document.getElementById('id_sin_novedad');
        
        fieldsToToggle.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                if (this.sinNovedadMode) {
                    field.disabled = true;
                    field.style.backgroundColor = '#f8f9fa';
                    field.value = '';
                } else {
                    field.disabled = false;
                    field.style.backgroundColor = '';
                }
            }
        });
        
        if (this.sinNovedadMode) {
            btn.textContent = 'Habilitar campos';
            btn.className = 'btn btn-warning';
            hiddenSinNovedad.value = 'true';
        } else {
            btn.textContent = 'Sin novedad';
            btn.className = 'btn btn-secondary';
            hiddenSinNovedad.value = 'false';
        }
    }
    
    validateForm(e) {
        const errors = [];
        
        // Validar nombres obligatorios
        const nombreServicio = document.getElementById('id_nombre_encargado_servicio');
        const nombreRonda = document.getElementById('id_nombre_encargado_ronda');
        
        if (!nombreServicio.value.trim()) {
            errors.push('El nombre del encargado del servicio es obligatorio');
        }
        
        if (!nombreRonda.value.trim()) {
            errors.push('El nombre del encargado de la ronda es obligatorio');
        }
        
        // Validar firmas obligatorias
        if (this.signatures.servicio && this.signatures.servicio.isEmpty()) {
            errors.push('La firma del encargado del servicio es obligatoria');
        }
        
        if (this.signatures.ronda && this.signatures.ronda.isEmpty()) {
            errors.push('La firma del encargado de la ronda es obligatoria');
        }
        
        // Si no es "sin novedad", validar campos obligatorios
        if (!this.sinNovedadMode) {
            const hallazgo = document.getElementById('id_hallazgo');
            const placa = document.getElementById('id_placa_equipo');
            
            if (!hallazgo.value.trim()) {
                errors.push('El hallazgo es obligatorio');
            }
            
            if (!placa.value.trim()) {
                errors.push('La placa del equipo es obligatoria');
            }
        }
        
        // Mostrar errores si los hay
        if (errors.length > 0) {
            e.preventDefault();
            this.showErrors(errors);
        }
    }
    
    showErrors(errors) {
        // Remover alertas previas
        const prevAlerts = document.querySelectorAll('.alert-validation');
        prevAlerts.forEach(alert => alert.remove());
        
        // Crear nueva alerta
        const alertHtml = `
            <div class="alert alert-danger alert-validation" role="alert">
                <h6><i class="fas fa-exclamation-triangle"></i> Errores en el formulario:</h6>
                <ul class="mb-0">
                    ${errors.map(error => `<li>${error}</li>`).join('')}
                </ul>
            </div>
        `;
        
        // Insertar al inicio del formulario
        this.form.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Scroll al inicio
        this.form.scrollIntoView({ behavior: 'smooth' });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar si estamos en una página con formulario de ronda
    if (document.getElementById('form-ronda')) {
        window.roundFormValidator = new RoundFormValidator('form-ronda');
    }
});