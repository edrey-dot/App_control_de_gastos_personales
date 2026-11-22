import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { environment } from '../../environments/environment';

import { AuthService } from './auth.service';
import { ExpenseService } from './expense.service';

describe('ExpenseService', () => {
  let service: ExpenseService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: { obtenerHeaders: () => ({}) } },
      ],
    });
    service = TestBed.inject(ExpenseService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    try {
      http.verify();
    } finally {
      TestBed.resetTestingModule();
    }
  });

  it('consulta los gastos entre las fechas solicitadas', () => {
    service.obtenerGastos('2026-10-01', '2026-10-31').subscribe();

    const request = http.expectOne(
      (req) =>
        req.url === `${environment.apiUrl}/gastos` &&
        req.params.get('fecha_inicio') === '2026-10-01' &&
        req.params.get('fecha_fin') === '2026-10-31',
    );
    expect(request.request.method).toBe('GET');
    request.flush([]);
  });

  it('conserva el filtro diario existente', () => {
    service.obtenerGastos('2026-10-15').subscribe();

    const request = http.expectOne(
      (req) => req.url === `${environment.apiUrl}/gastos` && req.params.get('fecha') === '2026-10-15',
    );
    request.flush([]);
  });

  it('elimina un gasto por su identificador', () => {
    service.eliminarGasto(42).subscribe();

    const request = http.expectOne(`${environment.apiUrl}/gastos/42`);
    expect(request.request.method).toBe('DELETE');
    request.flush(null);
  });
});
