import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonButton,
  IonIcon,
  IonSegment,
  IonSegmentButton,
  IonLabel,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonList,
  IonItem,
  IonInput,
  IonSelect,
  IonSelectOption,
  IonText,
  IonBadge,
  IonProgressBar,
  IonSpinner,
} from '@ionic/angular';
import { addIcons } from 'ionicons';
import {
  cameraOutline,
  logOutOutline,
  calendarOutline,
  walletOutline,
  pieChartOutline,
  checkmarkCircleOutline,
  closeCircleOutline,
  warningOutline,
  cloudOfflineOutline,
} from 'ionicons/icons';

import { AuthService } from '../services/auth.service';
import { ExpenseService, Categoria, Gasto, ResumenMensual, TopeMensual } from '../services/expense.service';
import { ReceiptService } from '../services/receipt.service';
import { OfflineQueueService, FotoPendiente } from '../services/offline-queue.service';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonButtons,
    IonButton,
    IonIcon,
    IonSegment,
    IonSegmentButton,
    IonLabel,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonList,
    IonItem,
    IonInput,
    IonSelect,
    IonSelectOption,
    IonText,
    IonBadge,
    IonProgressBar,
    IonSpinner,
  ],
})
export class HomePage implements OnInit {
  private authService = inject(AuthService);
  private expenseService = inject(ExpenseService);
  private receiptService = inject(ReceiptService);
  private offlineService = inject(OfflineQueueService);
  private router = inject(Router);

  segmentoActivo: 'gastos' | 'resumen' | 'topes' = 'gastos';

  // Datos de usuario y estado
  categorias: Categoria[] = [];
  gastos: Gasto[] = [];
  fechaFiltro: string = new Date().toISOString().split('T')[0];

  // Vista Previa Editable (HU-01, HU-02, HU-03, HU-04, HU-09)
  mostrarVistaPrevia = false;
  cargandoLectura = false;
  previewComercio = '';
  previewFecha = '';
  previewMonto: number = 0;
  montoAnteriorValido: number = 0;
  previewIdCategoria: number = 0;

  // Errores de validación en pantalla
  errorFecha = '';
  errorMonto = '';
  errorCategoria = '';
  mensajeGeneral = '';

  // Topes y resumen
  topes: TopeMensual[] = [];
  resumen: ResumenMensual | null = null;
  nuevoTopeCategoriaId: number = 0;
  nuevoTopeMonto: number = 0;

  // Offline
  fotosPendientes: FotoPendiente[] = [];
  avisoOffline = '';

  constructor() {
    addIcons({
      cameraOutline,
      logOutOutline,
      calendarOutline,
      walletOutline,
      pieChartOutline,
      checkmarkCircleOutline,
      closeCircleOutline,
      warningOutline,
      cloudOfflineOutline,
    });
  }

  ngOnInit() {
    if (!this.authService.estaAutenticado()) {
      this.router.navigate(['/login']);
      return;
    }
    this.cargarCategorias();
    this.cargarGastos();
    this.cargarTopes();
    this.cargarResumen();
    this.actualizarPendientes();
  }

  cambiarSegmento(event: any) {
    this.segmentoActivo = event.detail.value;
    if (this.segmentoActivo === 'resumen') this.cargarResumen();
    if (this.segmentoActivo === 'topes') this.cargarTopes();
  }

  cargarCategorias() {
    this.expenseService.obtenerCategorias().subscribe({
      next: (cats) => (this.categorias = cats),
      error: () => this.cerrarSesionSiExpirado(),
    });
  }

  cargarGastos() {
    this.expenseService.obtenerGastos(this.fechaFiltro).subscribe({
      next: (g) => (this.gastos = g),
      error: () => this.cerrarSesionSiExpirado(),
    });
  }

  cargarTopes() {
    const ahora = new Date();
    this.expenseService.obtenerTopes(ahora.getFullYear(), ahora.getMonth() + 1).subscribe({
      next: (t) => (this.topes = t),
    });
  }

  cargarResumen() {
    const ahora = new Date();
    this.expenseService.obtenerResumenMensual(ahora.getFullYear(), ahora.getMonth() + 1).subscribe({
      next: (r) => (this.resumen = r),
    });
  }

  actualizarPendientes() {
    this.fotosPendientes = this.offlineService.obtenerPendientes();
  }

  // =========================================================================
  // Captura y lectura de recibo (HU-01, HU-05)
  // =========================================================================

  onArchivoSeleccionado(event: any) {
    const archivo = event.target.files?.[0];
    if (!archivo) return;

    if (!navigator.onLine) {
      // HU-05: Sin internet guarda como Pendiente
      const reader = new FileReader();
      reader.onload = () => {
        this.offlineService.guardarPendiente(reader.result as string);
        this.actualizarPendientes();
        this.avisoOffline = 'Se reintentara mas tarde';
      };
      reader.readAsDataURL(archivo);
      return;
    }

    this.cargandoLectura = true;
    this.mostrarVistaPrevia = true;
    this.mensajeGeneral = '';
    this.limpiarErrores();

    this.receiptService.leerRecibo(archivo).subscribe({
      next: (lectura) => {
        this.cargandoLectura = false;
        this.previewComercio = lectura.comercio || 'Comercio no detectado';
        this.previewFecha = lectura.fecha || new Date().toISOString().split('T')[0];
        this.previewMonto = lectura.monto || 0;
        this.montoAnteriorValido = this.previewMonto;
        this.previewIdCategoria = 0;

        if (lectura.mensaje) {
          this.mensajeGeneral = lectura.mensaje;
        }
        this.validarFechaEnTiempoReal();
      },
      error: () => {
        this.cargandoLectura = false;
        this.mensajeGeneral = 'No se pudo leer el monto';
        this.previewMonto = 0;
        this.previewFecha = new Date().toISOString().split('T')[0];
      },
    });
  }

  // =========================================================================
  // Validaciones de la Vista Previa (HU-02, HU-03, HU-04)
  // =========================================================================

  validarFechaEnTiempoReal() {
    this.errorFecha = '';
    if (!this.previewFecha) return;

    const hoyStr = new Date().toISOString().split('T')[0];
    if (this.previewFecha > hoyStr) {
      // HU-02 Escenario 2: Mensaje exacto y marca en rojo
      this.errorFecha = 'La fecha no puede ser posterior a hoy';
    }
  }

  onMontoChange(event: any) {
    const valor = parseFloat(event.target.value);
    // HU-03 Escenario 2: si escribe <= 0 o no numérico, muestra error y conserva anterior
    if (isNaN(valor) || valor <= 0) {
      this.errorMonto = 'El monto debe ser un numero mayor a 0';
      // Restaurar el valor anterior tras un breve momento
      setTimeout(() => {
        this.previewMonto = this.montoAnteriorValido;
      }, 100);
    } else {
      this.errorMonto = '';
      this.montoAnteriorValido = valor;
      this.previewMonto = valor;
    }
  }

  guardarGasto() {
    this.limpiarErrores();
    this.validarFechaEnTiempoReal();

    if (this.errorFecha) return;

    if (!this.previewMonto || this.previewMonto <= 0) {
      this.errorMonto = 'El monto debe ser un numero mayor a 0';
      return;
    }

    if (!this.previewIdCategoria || this.previewIdCategoria <= 0) {
      // HU-04 Escenario 2
      this.errorCategoria = 'Elige una categoria';
      return;
    }

    const payload: Gasto = {
      comercio: this.previewComercio || 'Gasto registrado',
      fecha: this.previewFecha,
      monto: this.previewMonto,
      id_categoria: this.previewIdCategoria,
    };

    this.expenseService.crearGasto(payload).subscribe({
      next: () => {
        this.mostrarVistaPrevia = false;
        this.cargarGastos();
        this.cargarTopes();
        this.cargarResumen();
      },
      error: (err) => {
        this.mensajeGeneral = err.error?.detail || 'Error al guardar el gasto';
      },
    });
  }

  cancelarVistaPrevia() {
    // HU-09 Escenario 2: Cancelar no guarda nada
    this.mostrarVistaPrevia = false;
    this.limpiarErrores();
  }

  private limpiarErrores() {
    this.errorFecha = '';
    this.errorMonto = '';
    this.errorCategoria = '';
  }

  // =========================================================================
  // Topes (HU-07, HU-08)
  // =========================================================================

  guardarNuevoTope() {
    if (!this.nuevoTopeCategoriaId || this.nuevoTopeMonto <= 0) {
      return;
    }
    const ahora = new Date();
    this.expenseService
      .definirTope(this.nuevoTopeCategoriaId, ahora.getFullYear(), ahora.getMonth() + 1, this.nuevoTopeMonto)
      .subscribe({
        next: () => {
          this.nuevoTopeMonto = 0;
          this.cargarTopes();
        },
      });
  }

  // =========================================================================
  // Utilidades
  // =========================================================================

  formatearCOP(monto: number): string {
    return '$' + Math.round(monto).toLocaleString('es-CO');
  }

  obtenerNombreCategoria(id_categoria: number): string {
    const c = this.categorias.find((item) => item.id_categoria === id_categoria);
    return c ? c.nombre : 'Sin categoría';
  }

  cerrarSesion() {
    this.authService.cerrarSesion();
    this.router.navigate(['/login']);
  }

  private cerrarSesionSiExpirado() {
    if (!this.authService.estaAutenticado()) {
      this.cerrarSesion();
    }
  }
}
