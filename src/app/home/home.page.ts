import { CommonModule } from '@angular/common';
import type { OnDestroy, OnInit } from '@angular/core';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import {
  AlertController,
  IonHeader,
  IonToolbar,
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
  IonAvatar,
} from '@ionic/angular';
import { addIcons } from 'ionicons';
import {
  cameraOutline,
  calendarOutline,
  addOutline,
  searchOutline,
  walletOutline,
  pieChartOutline,
  checkmarkCircleOutline,
  closeCircleOutline,
  warningOutline,
  cloudOfflineOutline,
  moonOutline,
  sunnyOutline,
  chevronBackOutline,
  chevronForwardOutline,
  refreshOutline,
  trashOutline,
  personCircleOutline,
} from 'ionicons/icons';
import { Subscription, TimeoutError, finalize, fromEvent, timeout } from 'rxjs';

import { AuthService } from '../services/auth.service';
import type { Categoria, Gasto, ItemResumen, ResumenMensual, TopeMensual } from '../services/expense.service';
import { ExpenseService } from '../services/expense.service';
import type { FotoPendiente } from '../services/offline-queue.service';
import { OfflineQueueService } from '../services/offline-queue.service';
import { ProfileService } from '../services/profile.service';
import type { PerfilUsuario } from '../services/profile.service';
import type { LecturaRecibo } from '../services/receipt.service';
import { ReceiptService } from '../services/receipt.service';
import { ThemeService } from '../services/theme.service';

type PeriodoGastos = 'dia' | 'semana' | 'mes' | 'rango';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonHeader,
    IonToolbar,
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
    IonAvatar,
  ],
})
export class HomePage implements OnInit, OnDestroy {
  private authService = inject(AuthService);
  private expenseService = inject(ExpenseService);
  private receiptService = inject(ReceiptService);
  private profileService = inject(ProfileService);
  private offlineService = inject(OfflineQueueService);
  private themeService = inject(ThemeService);
  private alertController = inject(AlertController);
  private changeDetector = inject(ChangeDetectorRef);
  private router = inject(Router);
  private readonly subscriptions = new Subscription();
  private readonly pendientesOmitidos = new Set<string>();

  segmentoActivo: 'gastos' | 'resumen' | 'topes' = 'gastos';
  modoOscuro = this.themeService.modoOscuro;

  categorias: Categoria[] = [];
  gastos: Gasto[] = [];
  fechaFiltro = this.fechaLocal(new Date());
  busquedaGastos = '';
  conectado = navigator.onLine;
  periodoFiltro: PeriodoGastos = 'dia';
  fechaInicioRango = this.fechaFiltro;
  fechaFinRango = this.fechaFiltro;

  mostrarVistaPrevia = false;
  esRegistroManual = false;
  cargandoLectura = false;
  previewComercio = '';
  previewFecha = '';
  previewMonto = 0;
  montoAnteriorValido = 0;
  previewIdCategoria = 0;
  private idFotoEnVistaPrevia: string | null = null;

  errorComercio = '';
  errorFecha = '';
  errorMonto = '';
  errorCategoria = '';
  errorTope = '';
  mensajeGeneral = '';
  guardandoGasto = false;
  guardandoTope = false;
  confirmacionEliminacionAbierta = false;
  eliminandoGastoId: number | null = null;

  topes: TopeMensual[] = [];
  resumen: ResumenMensual | null = null;
  anioResumen = new Date().getFullYear();
  mesResumen = new Date().getMonth() + 1;
  nuevoTopeCategoriaId = 0;
  nuevoTopeMonto = 0;

  fotosPendientes: FotoPendiente[] = [];
  avisoOffline = '';
  private procesandoCola = false;
  nombreUsuario = 'Mi perfil';
  fotoPerfilUrl: string | null = null;
  private fotoPerfilObjectUrl: string | null = null;

  constructor() {
    addIcons({
      cameraOutline,
      calendarOutline,
      addOutline,
      searchOutline,
      walletOutline,
      pieChartOutline,
      checkmarkCircleOutline,
      closeCircleOutline,
      warningOutline,
      cloudOfflineOutline,
      moonOutline,
      sunnyOutline,
      chevronBackOutline,
      chevronForwardOutline,
      refreshOutline,
      trashOutline,
      personCircleOutline,
    });
  }

  ngOnInit(): void {
    if (!this.authService.estaAutenticado()) {
      void this.router.navigate(['/login']);
      return;
    }
    this.cargarPerfil();
    this.cargarCategorias();
    this.cargarGastos();
    this.cargarTopes();
    this.cargarResumen();
    this.subscriptions.add(
      this.profileService.perfilActualizado$.subscribe((perfil) => {
        this.aplicarPerfilEnEncabezado(perfil);
      }),
    );
    this.subscriptions.add(
      fromEvent(window, 'online').subscribe(() => {
        this.conectado = true;
        this.avisoOffline = '';
        this.changeDetector.markForCheck();
        void this.actualizarPendientes().then(() => this.procesarSiguientePendiente());
      }),
    );
    this.subscriptions.add(
      fromEvent(window, 'offline').subscribe(() => {
        this.conectado = false;
        this.avisoOffline = 'Sin conexión. Tus fotos se guardarán para después.';
        this.changeDetector.markForCheck();
      }),
    );
    void this.actualizarPendientes().then(() => this.procesarSiguientePendiente());
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
    if (this.fotoPerfilObjectUrl) URL.revokeObjectURL(this.fotoPerfilObjectUrl);
  }

  abrirPerfil(): void {
    void this.router.navigate(['/perfil']);
  }

  alternarTema(): void {
    this.themeService.alternar();
    this.modoOscuro = this.themeService.modoOscuro;
  }

  cambiarSegmento(event: CustomEvent<{ value?: string | number }>): void {
    const segmento = event.detail.value;
    if (typeof segmento !== 'string') return;
    if (segmento === 'gastos' || segmento === 'resumen' || segmento === 'topes') {
      this.segmentoActivo = segmento;
      if (segmento === 'resumen') this.cargarResumen();
      if (segmento === 'topes') this.cargarTopes();
    }
  }

  cargarCategorias(): void {
    this.expenseService.obtenerCategorias().subscribe({
      next: (categorias) => {
        this.categorias = categorias;
        this.changeDetector.markForCheck();
      },
      error: () => {
        this.cerrarSesionSiExpirado();
        this.changeDetector.markForCheck();
      },
    });
  }

  private cargarPerfil(): void {
    this.profileService.obtenerPerfil().subscribe({
      next: (perfil) => {
        this.aplicarPerfilEnEncabezado(perfil);
      },
      error: (error) => {
        if (error.status === 401) this.cerrarSesion();
        else {
          this.mensajeGeneral = error.error?.detail || 'No se pudo cargar el perfil.';
          this.changeDetector.markForCheck();
        }
      },
    });
  }

  private aplicarPerfilEnEncabezado(perfil: PerfilUsuario): void {
    this.nombreUsuario = perfil.nombre_usuario;
    if (!perfil.tiene_foto) {
      if (this.fotoPerfilObjectUrl) URL.revokeObjectURL(this.fotoPerfilObjectUrl);
      this.fotoPerfilObjectUrl = null;
      this.fotoPerfilUrl = null;
      this.changeDetector.markForCheck();
      return;
    }

    this.profileService.obtenerFoto().subscribe({
      next: (foto) => {
        if (this.fotoPerfilObjectUrl) URL.revokeObjectURL(this.fotoPerfilObjectUrl);
        this.fotoPerfilObjectUrl = URL.createObjectURL(foto);
        this.fotoPerfilUrl = this.fotoPerfilObjectUrl;
        this.changeDetector.markForCheck();
      },
      error: () => this.changeDetector.markForCheck(),
    });
    this.changeDetector.markForCheck();
  }

  cargarGastos(): void {
    const periodo = this.obtenerRangoPeriodo();
    if (!periodo) {
      this.mensajeGeneral = 'Revisa las fechas del período seleccionado.';
      return;
    }
    this.mensajeGeneral = '';
    this.expenseService.obtenerGastos(periodo.inicio, periodo.fin).subscribe({
      next: (gastos) => {
        this.gastos = gastos;
        this.changeDetector.markForCheck();
      },
      error: () => {
        this.cerrarSesionSiExpirado();
        this.changeDetector.markForCheck();
      },
    });
  }

  cargarTopes(): void {
    const ahora = new Date();
    this.expenseService.obtenerTopes(ahora.getFullYear(), ahora.getMonth() + 1).subscribe({
      next: (topes) => {
        this.topes = topes;
        this.changeDetector.markForCheck();
      },
      error: (error) => {
        this.mensajeGeneral = error.error?.detail || 'No se pudieron cargar los topes.';
        this.changeDetector.markForCheck();
      },
    });
  }

  cargarResumen(): void {
    this.expenseService.obtenerResumenMensual(this.anioResumen, this.mesResumen).subscribe({
      next: (resumen) => {
        this.resumen = resumen;
        this.changeDetector.markForCheck();
      },
      error: (error) => {
        this.mensajeGeneral = error.error?.detail || 'No se pudo cargar el resumen mensual.';
        this.changeDetector.markForCheck();
      },
    });
  }

  moverMesResumen(delta: number): void {
    const fecha = new Date(this.anioResumen, this.mesResumen - 1 + delta, 1);
    this.anioResumen = fecha.getFullYear();
    this.mesResumen = fecha.getMonth() + 1;
    this.cargarResumen();
  }

  nombreMesResumen(): string {
    return new Date(this.anioResumen, this.mesResumen - 1, 1).toLocaleDateString('es-CO', {
      month: 'long',
      year: 'numeric',
    });
  }

  gradienteResumen(): string {
    const resumen = this.resumen;
    if (!resumen || resumen.items.length === 0 || resumen.total_mes <= 0) return 'none';
    let inicio = 0;
    const segmentos = resumen.items.map((item, index) => {
      const fin = index === resumen.items.length - 1 ? 100 : inicio + (item.total / resumen.total_mes) * 100;
      const segmento = `var(--chart-color-${index % 5}) ${inicio}% ${fin}%`;
      inicio = fin;
      return segmento;
    });
    return `conic-gradient(${segmentos.join(', ')})`;
  }

  seleccionarPeriodo(periodo: PeriodoGastos): void {
    this.periodoFiltro = periodo;
    this.cargarGastos();
  }

  gastosFiltrados(): Gasto[] {
    const termino = this.busquedaGastos.trim().toLocaleLowerCase('es-CO');
    if (!termino) return this.gastos;
    return this.gastos.filter((gasto) => {
      const categoria = this.obtenerNombreCategoria(gasto.id_categoria);
      return `${gasto.comercio} ${categoria}`.toLocaleLowerCase('es-CO').includes(termino);
    });
  }

  totalPeriodo(): number {
    return this.gastos.reduce((total, gasto) => total + gasto.monto, 0);
  }

  etiquetaPeriodo(): string {
    const etiquetas: Record<PeriodoGastos, string> = {
      dia: 'Día seleccionado',
      semana: 'Esta semana',
      mes: 'Este mes',
      rango: 'Rango personalizado',
    };
    return etiquetas[this.periodoFiltro];
  }

  totalPresupuesto(): number {
    return this.topes.reduce((total, tope) => total + tope.monto_tope, 0);
  }

  porcentajePresupuesto(): number {
    const presupuesto = this.totalPresupuesto();
    return presupuesto > 0 ? Math.round(((this.resumen?.total_mes ?? 0) / presupuesto) * 100) : 0;
  }

  progresoPresupuesto(): number {
    return Math.min(this.porcentajePresupuesto(), 100);
  }

  categoriaPrincipal(): ItemResumen | null {
    const items = this.resumen?.items ?? [];
    if (items.length === 0) return null;
    return items.reduce((principal, item) => (item.total > principal.total ? item : principal));
  }

  async actualizarPendientes(): Promise<void> {
    try {
      const pendientes = await this.offlineService.obtenerPendientes();
      this.fotosPendientes = pendientes;
      this.changeDetector.markForCheck();
    } catch (error) {
      this.mensajeGeneral = error instanceof Error ? error.message : 'No se pudo abrir la cola de fotos pendientes.';
      this.changeDetector.markForCheck();
    }
  }

  onArchivoSeleccionado(event: Event): void {
    const input = event.target as HTMLInputElement;
    const archivo = input.files?.[0];
    input.value = '';
    if (!archivo) return;

    if (!this.offlineService.hayInternet()) {
      void this.guardarFotoPendiente(archivo);
      return;
    }
    this.leerArchivo(archivo);
  }

  registrarGastoManual(): void {
    this.esRegistroManual = true;
    this.cargandoLectura = false;
    this.mostrarVistaPrevia = true;
    this.idFotoEnVistaPrevia = null;
    this.previewComercio = '';
    this.previewFecha = this.fechaLocal(new Date());
    this.previewMonto = 0;
    this.montoAnteriorValido = 0;
    this.previewIdCategoria = 0;
    this.mensajeGeneral = '';
    this.limpiarErrores();
  }

  private leerArchivo(archivo: Blob, idPendiente: string | null = null): void {
    this.cargandoLectura = true;
    this.mostrarVistaPrevia = true;
    this.esRegistroManual = false;
    this.idFotoEnVistaPrevia = idPendiente;
    this.previewComercio = '';
    this.previewFecha = this.fechaLocal(new Date());
    this.previewMonto = 0;
    this.montoAnteriorValido = 0;
    this.previewIdCategoria = 0;
    this.mensajeGeneral = '';
    this.limpiarErrores();
    this.changeDetector.markForCheck();

    this.receiptService
      .leerRecibo(archivo)
      .pipe(timeout({ first: 35_000 }))
      .subscribe({
        next: (lectura) => this.aplicarLectura(lectura),
        error: (error) => {
          this.cargandoLectura = false;
          const mensajeError =
            error instanceof TimeoutError
              ? 'El escaneo tardó demasiado. Intenta de nuevo.'
              : error.error?.detail || 'No se pudo leer el recibo. Intenta de nuevo.';
          if (idPendiente) {
            this.mostrarVistaPrevia = false;
            this.idFotoEnVistaPrevia = null;
            void this.marcarPendienteConError(idPendiente, mensajeError);
          } else if (!this.offlineService.hayInternet()) {
            void this.guardarFotoPendiente(archivo);
            this.mostrarVistaPrevia = false;
          } else {
            this.mensajeGeneral = mensajeError;
          }
          this.changeDetector.markForCheck();
        },
      });
  }

  private aplicarLectura(lectura: LecturaRecibo): void {
    this.cargandoLectura = false;
    this.previewComercio = lectura.comercio ?? '';
    this.previewFecha = lectura.fecha ?? this.fechaLocal(new Date());
    this.previewMonto = lectura.monto ?? 0;
    this.montoAnteriorValido = this.previewMonto;
    this.previewIdCategoria = 0;
    this.mensajeGeneral = lectura.mensaje ?? '';
    this.validarFechaEnTiempoReal();
    this.changeDetector.markForCheck();
  }

  private async guardarFotoPendiente(foto: Blob): Promise<void> {
    try {
      await this.offlineService.guardarPendiente(foto);
      this.avisoOffline = 'Foto guardada. Se reintentara mas tarde.';
      this.changeDetector.markForCheck();
      await this.actualizarPendientes();
    } catch (error) {
      this.mensajeGeneral = error instanceof Error ? error.message : 'No se pudo guardar la foto pendiente.';
      this.changeDetector.markForCheck();
    }
  }

  async procesarPendiente(id: string): Promise<void> {
    this.pendientesOmitidos.delete(id);
    const pendiente = this.fotosPendientes.find((foto) => foto.id === id);
    if (!pendiente || this.procesandoCola || this.mostrarVistaPrevia || !this.offlineService.hayInternet()) {
      return;
    }
    await this.leerPendiente(pendiente);
  }

  private async procesarSiguientePendiente(): Promise<void> {
    if (this.procesandoCola || this.mostrarVistaPrevia || !this.offlineService.hayInternet()) {
      return;
    }
    const pendiente = this.fotosPendientes.find(
      (foto) => !this.pendientesOmitidos.has(foto.id) && foto.estado !== 'Procesando',
    );
    if (pendiente) await this.leerPendiente(pendiente);
  }

  private async leerPendiente(pendiente: FotoPendiente): Promise<void> {
    this.procesandoCola = true;
    try {
      await this.offlineService.actualizarEstado(pendiente.id, 'Procesando');
      await this.actualizarPendientes();
      this.procesandoCola = false;
      this.leerArchivo(pendiente.foto, pendiente.id);
    } catch (error) {
      this.procesandoCola = false;
      await this.marcarPendienteConError(
        pendiente.id,
        error instanceof Error ? error.message : 'No se pudo procesar la foto.',
      );
    }
  }

  private async marcarPendienteConError(id: string, mensaje: string): Promise<void> {
    this.procesandoCola = false;
    this.avisoOffline = mensaje || 'Se reintentara mas tarde';
    this.changeDetector.markForCheck();
    try {
      await this.offlineService.actualizarEstado(id, 'Error');
      await this.actualizarPendientes();
    } catch (error) {
      this.mensajeGeneral = error instanceof Error ? error.message : 'No se pudo actualizar la cola.';
      this.changeDetector.markForCheck();
    }
  }

  validarFechaEnTiempoReal(): void {
    this.errorFecha = '';
    if (this.previewFecha && this.previewFecha > this.fechaLocal(new Date())) {
      this.errorFecha = 'La fecha no puede ser posterior a hoy';
    }
  }

  onMontoChange(event: CustomEvent<{ value?: string | number | null }>): void {
    const valor = Number(event.detail.value);
    if (!Number.isFinite(valor) || valor <= 0) {
      this.errorMonto = 'El monto debe ser un numero mayor a 0';
      this.previewMonto = this.montoAnteriorValido;
      return;
    }
    this.errorMonto = '';
    this.montoAnteriorValido = valor;
    this.previewMonto = valor;
  }

  guardarGasto(): void {
    if (this.guardandoGasto) return;

    this.limpiarErrores();
    this.validarFechaEnTiempoReal();
    if (this.errorFecha) return;

    if (!this.previewComercio.trim()) {
      this.errorComercio = 'El comercio es obligatorio';
    }
    if (!Number.isFinite(this.previewMonto) || this.previewMonto <= 0) {
      this.errorMonto = 'El monto debe ser un numero mayor a 0';
    }
    if (!this.previewIdCategoria || this.previewIdCategoria <= 0) {
      this.errorCategoria = 'Elige una categoria';
    }
    if (this.errorComercio || this.errorMonto || this.errorCategoria) return;

    const payload: Gasto = {
      comercio: this.previewComercio.trim(),
      fecha: this.previewFecha,
      monto: this.previewMonto,
      id_categoria: this.previewIdCategoria,
    };

    this.guardandoGasto = true;
    this.expenseService
      .crearGasto(payload)
      .pipe(
        timeout({ first: 15_000 }),
        finalize(() => {
          this.guardandoGasto = false;
          this.changeDetector.markForCheck();
        }),
      )
      .subscribe({
        next: () => {
          const idFoto = this.idFotoEnVistaPrevia;
          this.mostrarVistaPrevia = false;
          this.esRegistroManual = false;
          this.idFotoEnVistaPrevia = null;
          this.cargarGastos();
          this.cargarTopes();
          this.cargarResumen();
          if (idFoto) {
            void this.eliminarPendienteYContinuar(idFoto);
          }
        },
        error: (error) => {
          this.mensajeGeneral =
            error instanceof TimeoutError
              ? 'El servidor no respondió a tiempo. Revisa el historial antes de intentar guardar otra vez.'
              : (error.error?.detail ?? 'Error al guardar el gasto.');
          if (this.idFotoEnVistaPrevia) {
            void this.marcarPendienteConError(this.idFotoEnVistaPrevia, this.mensajeGeneral);
          }
        },
      });
  }

  async confirmarEliminarGasto(gasto: Gasto): Promise<void> {
    const idGasto = gasto.id_gasto;
    if (!idGasto || this.confirmacionEliminacionAbierta || this.eliminandoGastoId !== null) return;

    this.confirmacionEliminacionAbierta = true;
    try {
      const alerta = await this.alertController.create({
        header: 'Eliminar gasto',
        message: '¿Seguro que deseas eliminar este gasto? Esta acción no se puede deshacer.',
        buttons: [
          { text: 'Cancelar', role: 'cancel' },
          { text: 'Eliminar', role: 'confirm', cssClass: 'alert-button-danger' },
        ],
      });
      await alerta.present();
      const { role } = await alerta.onDidDismiss();
      this.confirmacionEliminacionAbierta = false;
      this.changeDetector.markForCheck();
      if (role !== 'confirm') return;
    } catch (error) {
      this.confirmacionEliminacionAbierta = false;
      this.mensajeGeneral = error instanceof Error ? error.message : 'No se pudo confirmar la eliminación del gasto.';
      this.changeDetector.markForCheck();
      return;
    }

    this.eliminandoGastoId = idGasto;
    this.changeDetector.markForCheck();
    this.expenseService.eliminarGasto(idGasto).subscribe({
      next: () => {
        this.eliminandoGastoId = null;
        this.mensajeGeneral = '';
        this.gastos = this.gastos.filter((gastoActual) => gastoActual.id_gasto !== idGasto);
        this.cargarResumen();
        this.cargarTopes();
        this.changeDetector.markForCheck();
      },
      error: (error) => {
        this.eliminandoGastoId = null;
        this.mensajeGeneral = error.error?.detail || 'No se pudo eliminar el gasto.';
        this.changeDetector.markForCheck();
      },
    });
  }

  cancelarVistaPrevia(): void {
    const idFoto = this.idFotoEnVistaPrevia;
    this.mostrarVistaPrevia = false;
    this.esRegistroManual = false;
    this.idFotoEnVistaPrevia = null;
    this.limpiarErrores();
    if (idFoto) {
      this.pendientesOmitidos.add(idFoto);
      void this.offlineService.actualizarEstado(idFoto, 'Pendiente').then(() => {
        void this.actualizarPendientes().then(() => this.procesarSiguientePendiente());
      });
    }
  }

  private async eliminarPendienteYContinuar(id: string): Promise<void> {
    try {
      await this.offlineService.eliminarPendiente(id);
      this.pendientesOmitidos.delete(id);
      await this.actualizarPendientes();
      await this.procesarSiguientePendiente();
    } catch (error) {
      this.avisoOffline =
        error instanceof Error ? error.message : 'El gasto se guardó, pero la foto sigue pendiente de eliminar.';
      this.changeDetector.markForCheck();
    }
  }

  private limpiarErrores(): void {
    this.errorComercio = '';
    this.errorFecha = '';
    this.errorMonto = '';
    this.errorCategoria = '';
  }

  guardarNuevoTope(): void {
    if (this.guardandoTope) return;

    this.errorTope = '';
    if (!this.nuevoTopeCategoriaId) {
      this.errorTope = 'Elige una categoria';
      return;
    }
    if (!Number.isFinite(this.nuevoTopeMonto) || this.nuevoTopeMonto <= 0) {
      this.errorTope = 'El tope debe ser mayor a $0';
      return;
    }
    this.guardandoTope = true;
    const ahora = new Date();
    this.expenseService
      .definirTope(this.nuevoTopeCategoriaId, ahora.getFullYear(), ahora.getMonth() + 1, this.nuevoTopeMonto)
      .subscribe({
        next: () => {
          this.guardandoTope = false;
          this.nuevoTopeMonto = 0;
          this.changeDetector.markForCheck();
          this.cargarTopes();
        },
        error: (error) => {
          this.guardandoTope = false;
          this.errorTope = error.error?.detail || 'No se pudo guardar el tope.';
          this.changeDetector.markForCheck();
        },
      });
  }

  formatearCOP(monto: number): string {
    return '$' + Math.round(monto).toLocaleString('es-CO');
  }

  obtenerNombreCategoria(idCategoria: number): string {
    return this.categorias.find((categoria) => categoria.id_categoria === idCategoria)?.nombre ?? 'Sin categoría';
  }

  formatearFecha(fecha: string): string {
    const [anio, mes, dia] = fecha.split('-');
    return `${dia}/${mes}/${anio}`;
  }

  obtenerTope(idCategoria: number): TopeMensual | undefined {
    return this.topes.find((tope) => tope.id_categoria === idCategoria);
  }

  cerrarSesion(): void {
    this.authService.cerrarSesion();
    void this.router.navigate(['/login']);
  }

  private cerrarSesionSiExpirado(): void {
    if (!this.authService.estaAutenticado()) this.cerrarSesion();
  }

  private obtenerRangoPeriodo(): { inicio: string; fin: string } | null {
    if (this.periodoFiltro === 'rango') {
      if (!this.fechaInicioRango || !this.fechaFinRango) return null;
      if (this.fechaInicioRango > this.fechaFinRango) return null;
      return { inicio: this.fechaInicioRango, fin: this.fechaFinRango };
    }

    const seleccionada = new Date(`${this.fechaFiltro}T00:00:00`);
    if (Number.isNaN(seleccionada.getTime())) return null;
    if (this.periodoFiltro === 'dia') {
      return { inicio: this.fechaFiltro, fin: this.fechaFiltro };
    }

    if (this.periodoFiltro === 'semana') {
      const diaSemana = (seleccionada.getDay() + 6) % 7;
      const inicio = new Date(seleccionada);
      inicio.setDate(seleccionada.getDate() - diaSemana);
      const fin = new Date(inicio);
      fin.setDate(inicio.getDate() + 6);
      return { inicio: this.fechaLocal(inicio), fin: this.fechaLocal(fin) };
    }

    const inicioMes = new Date(seleccionada.getFullYear(), seleccionada.getMonth(), 1);
    const finMes = new Date(seleccionada.getFullYear(), seleccionada.getMonth() + 1, 0);
    return { inicio: this.fechaLocal(inicioMes), fin: this.fechaLocal(finMes) };
  }

  private fechaLocal(fecha: Date): string {
    const anio = fecha.getFullYear();
    const mes = `${fecha.getMonth() + 1}`.padStart(2, '0');
    const dia = `${fecha.getDate()}`.padStart(2, '0');
    return `${anio}-${mes}-${dia}`;
  }
}
