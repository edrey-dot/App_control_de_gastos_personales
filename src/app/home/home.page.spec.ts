import type { ComponentFixture } from '@angular/core/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AlertController } from '@ionic/angular';
import { NEVER, of, Subject } from 'rxjs';

import { AuthService } from '../services/auth.service';
import type { Categoria, Gasto, TopeMensual } from '../services/expense.service';
import { ExpenseService } from '../services/expense.service';
import { OfflineQueueService } from '../services/offline-queue.service';
import { ProfileService } from '../services/profile.service';
import { ReceiptService } from '../services/receipt.service';

import { HomePage } from './home.page';

describe('HomePage', () => {
  let component: HomePage;
  let fixture: ComponentFixture<HomePage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomePage],
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: { estaAutenticado: () => true },
        },
        {
          provide: ExpenseService,
          useValue: {
            obtenerCategorias: () => of([]),
            obtenerGastos: () => of([]),
            crearGasto: () => of({}),
            eliminarGasto: () => of(undefined),
            obtenerTopes: () => of([]),
            obtenerResumenMensual: () => of({ anio: 2026, mes: 1, total_mes: 0, items: [] }),
          },
        },
        {
          provide: AlertController,
          useValue: {
            create: () =>
              Promise.resolve({
                present: () => Promise.resolve(),
                onDidDismiss: () => Promise.resolve({ role: 'cancel' }),
              }),
          },
        },
        {
          provide: OfflineQueueService,
          useValue: {
            obtenerPendientes: async () => [],
            hayInternet: () => true,
          },
        },
        {
          provide: ReceiptService,
          useValue: { leerRecibo: () => of({}) },
        },
        {
          provide: ProfileService,
          useValue: {
            perfilActualizado$: NEVER,
            obtenerPerfil: () =>
              of({
                id_usuario: 1,
                nombre_usuario: 'Usuario de prueba',
                correo: 'prueba@correo.com',
                telefono: null,
                tiene_foto: false,
              }),
            obtenerFoto: () => of(new Blob()),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HomePage);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('marca en rojo y explica una fecha futura en la vista previa', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date(2026, 9, 24, 12));
    component.mostrarVistaPrevia = true;
    component.previewFecha = '2026-12-30';

    try {
      // Dado: hoy es 24/10/2026 y la vista previa tiene fecha 30/12/2026.
      // Cuando: se valida la fecha del gasto.
      component.validarFechaEnTiempoReal();
      fixture.detectChanges();

      // Entonces: la fecha queda marcada en rojo y muestra el mensaje de HU-02.
      expect(component.errorFecha).toBe('La fecha no puede ser posterior a hoy');
      expect(fixture.nativeElement.textContent).toContain('La fecha no puede ser posterior a hoy');
      expect(fixture.nativeElement.querySelector('.preview-item.input-error')).not.toBeNull();
    } finally {
      vi.useRealTimers();
    }
  });

  it('actualiza el monto corregido sin volver a leer el recibo', () => {
    const leerRecibo = vi.spyOn(TestBed.inject(ReceiptService), 'leerRecibo');
    component.previewMonto = 58000;
    component.montoAnteriorValido = 58000;

    // Dado: el monto leído de $58.000 en la vista previa.
    // Cuando: se corrige a $85.000.
    component.onMontoChange(new CustomEvent('ionChange', { detail: { value: 85000 } }));

    // Entonces: conserva el monto corregido y no vuelve a procesar la foto.
    expect(component.previewMonto).toBe(85000);
    expect(component.montoAnteriorValido).toBe(85000);
    expect(component.errorMonto).toBe('');
    expect(leerRecibo).not.toHaveBeenCalled();
  });

  it.each([
    ['abc', 'abc'],
    ['cero', 0],
  ])('rechaza %s y conserva el monto anterior', (_caso, montoIngresado) => {
    component.previewMonto = 58000;
    component.montoAnteriorValido = 58000;

    // Dado: el monto anterior válido de $58.000.
    // Cuando: se ingresa un valor no numérico o cero.
    component.onMontoChange(new CustomEvent('ionChange', { detail: { value: montoIngresado } }));

    // Entonces: muestra el mensaje de HU-03 y restaura el valor previo.
    expect(component.errorMonto).toBe('El monto debe ser un número mayor a 0');
    expect(component.previewMonto).toBe(58000);
    expect(component.montoAnteriorValido).toBe(58000);
  });

  it('muestra la alerta definida para el 81 % del tope', () => {
    const categoria: Categoria = { id_categoria: 1, nombre: 'Comida' };
    const tope: TopeMensual = {
      id_categoria: 1,
      categoria: 'Comida',
      anio: 2026,
      mes: 10,
      monto_tope: 400000,
      total_gastado: 325000,
      porcentaje: 81.25,
      alerta_80: true,
      mensaje_alerta: 'Llevas el 81 % de tu tope en Comida',
    };
    component.segmentoActivo = 'topes';
    component.categorias = [categoria];
    component.topes = [tope];

    // Dado: «Comida» tiene un tope de $400.000 y acumula $325.000.
    // Cuando: se muestra el estado de topes.
    fixture.detectChanges();

    // Entonces: se muestra el mensaje de alerta de HU-08.
    expect(fixture.nativeElement.textContent).toContain('Llevas el 81 % de tu tope en Comida');
    expect(fixture.nativeElement.querySelector('.alert-box')).not.toBeNull();
  });

  it('no muestra alerta cuando el gasto es exactamente el 80 % del tope', () => {
    const categoria: Categoria = { id_categoria: 1, nombre: 'Comida' };
    const tope: TopeMensual = {
      id_categoria: 1,
      categoria: 'Comida',
      anio: 2026,
      mes: 10,
      monto_tope: 400000,
      total_gastado: 320000,
      porcentaje: 80,
      alerta_80: false,
    };
    component.segmentoActivo = 'topes';
    component.categorias = [categoria];
    component.topes = [tope];

    // Dado: «Comida» acumula exactamente el 80 % de su tope.
    // Cuando: se muestra el estado de topes.
    fixture.detectChanges();

    // Entonces: no se presenta la alerta de HU-08.
    expect(fixture.nativeElement.querySelector('.alert-box')).toBeNull();
  });

  it('indica que Ocio no tiene tope y no muestra alerta', () => {
    const categoria: Categoria = { id_categoria: 3, nombre: 'Ocio' };
    component.segmentoActivo = 'topes';
    component.categorias = [categoria];
    component.topes = [];

    // Dado: «Ocio» no tiene un tope definido.
    // Cuando: se muestra el estado de topes.
    fixture.detectChanges();

    // Entonces: aparece «Sin tope definido» y no hay alerta.
    expect(fixture.nativeElement.textContent).toContain('Sin tope definido');
    expect(fixture.nativeElement.textContent).toContain('Ocio');
    expect(fixture.nativeElement.querySelector('.alert-box')).toBeNull();
  });

  it('notifica a Angular cuando termina la búsqueda de gastos', () => {
    const respuesta = new Subject<Gasto[]>();
    const obtenerGastos = vi.spyOn(TestBed.inject(ExpenseService), 'obtenerGastos').mockReturnValue(respuesta);
    const changeDetector = component['changeDetector'];
    const marcarVista = vi.spyOn(changeDetector, 'markForCheck');

    component.cargarGastos();
    respuesta.next([
      {
        id_gasto: 1,
        comercio: 'Tienda de prueba',
        fecha: '2026-11-19',
        monto: 12000,
        id_categoria: 1,
      },
    ]);

    expect(obtenerGastos).toHaveBeenCalledTimes(1);
    expect(component.gastos[0]?.comercio).toBe('Tienda de prueba');
    expect(marcarVista).toHaveBeenCalled();
  });

  it('notifica a Angular cuando termina la lectura del recibo', () => {
    const respuesta = new Subject<{ comercio: string; fecha: string; monto: number }>();
    const leerRecibo = vi.spyOn(TestBed.inject(ReceiptService), 'leerRecibo').mockReturnValue(respuesta);
    const changeDetector = component['changeDetector'];
    const marcarVista = vi.spyOn(changeDetector, 'markForCheck');

    component.onArchivoSeleccionado({
      target: {
        files: [new File(['imagen'], 'recibo.jpg', { type: 'image/jpeg' })],
      },
    } as unknown as Event);
    respuesta.next({ comercio: 'Cajero de prueba', fecha: '2026-11-19', monto: 180000 });

    expect(leerRecibo).toHaveBeenCalledTimes(1);
    expect(component.cargandoLectura).toBe(false);
    expect(component.previewComercio).toBe('Cajero de prueba');
    expect(marcarVista).toHaveBeenCalled();
  });

  it('ignora nuevos envíos del gasto mientras hay uno en curso', () => {
    const servicio = TestBed.inject(ExpenseService);
    const respuesta = new Subject<Gasto>();
    const crearGasto = vi.spyOn(servicio, 'crearGasto').mockReturnValue(respuesta);
    component.previewComercio = 'Tienda';
    component.previewFecha = '2026-11-19';
    component.previewMonto = 12000;
    component.previewIdCategoria = 1;

    component.guardarGasto();
    component.guardarGasto();

    expect(crearGasto).toHaveBeenCalledTimes(1);
    expect(component.guardandoGasto).toBe(true);

    respuesta.next({
      id_gasto: 1,
      comercio: 'Tienda',
      fecha: '2026-11-19',
      monto: 12000,
      id_categoria: 1,
    });
    respuesta.complete();

    expect(component.guardandoGasto).toBe(false);
  });

  it('libera el formulario si el servidor no responde', async () => {
    const crearGasto = vi.spyOn(TestBed.inject(ExpenseService), 'crearGasto').mockReturnValue(NEVER);
    component.previewComercio = 'Tienda';
    component.previewFecha = '2026-11-19';
    component.previewMonto = 12000;
    component.previewIdCategoria = 1;
    vi.useFakeTimers();

    try {
      component.guardarGasto();
      expect(component.guardandoGasto).toBe(true);

      await vi.advanceTimersByTimeAsync(15_000);

      expect(crearGasto).toHaveBeenCalledTimes(1);
      expect(component.guardandoGasto).toBe(false);
      expect(component.mensajeGeneral).toContain('Revisa el historial');
    } finally {
      vi.useRealTimers();
    }
  });

  it('detiene el indicador y muestra error si el escaneo excede el tiempo máximo', async () => {
    const leerRecibo = vi.spyOn(TestBed.inject(ReceiptService), 'leerRecibo').mockReturnValue(NEVER);
    vi.useFakeTimers();

    try {
      component.onArchivoSeleccionado({
        target: {
          files: [new File(['imagen'], 'recibo.jpg', { type: 'image/jpeg' })],
        },
      } as unknown as Event);
      expect(component.cargandoLectura).toBe(true);

      await vi.advanceTimersByTimeAsync(35_000);

      expect(leerRecibo).toHaveBeenCalledTimes(1);
      expect(component.cargandoLectura).toBe(false);
      expect(component.mensajeGeneral).toContain('tardó demasiado');
    } finally {
      vi.useRealTimers();
    }
  });
});
