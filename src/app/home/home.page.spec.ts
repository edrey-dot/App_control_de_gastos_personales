import type { ComponentFixture } from '@angular/core/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AlertController } from '@ionic/angular';
import { NEVER, of, Subject } from 'rxjs';

import { AuthService } from '../services/auth.service';
import type { Gasto } from '../services/expense.service';
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
