import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

export interface Categoria {
  id_categoria: number;
  nombre: string;
}

export interface Gasto {
  id_gasto?: number;
  comercio: string;
  fecha: string;
  monto: number;
  id_categoria: number;
}

export interface ItemResumen {
  id_categoria: number;
  categoria: string;
  total: number;
  porcentaje: number;
}

export interface ResumenMensual {
  anio: number;
  mes: number;
  total_mes: number;
  items: ItemResumen[];
  mensaje?: string;
}

export interface TopeMensual {
  id_categoria: number;
  categoria: string;
  anio: number;
  mes: number;
  monto_tope: number;
  total_gastado: number;
  porcentaje: number;
  alerta_80: boolean;
  mensaje_alerta?: string;
}

@Injectable({
  providedIn: 'root',
})
export class ExpenseService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = environment.apiUrl;

  private get headers() {
    return { headers: this.authService.obtenerHeaders() };
  }

  obtenerCategorias(): Observable<Categoria[]> {
    return this.http.get<Categoria[]>(`${this.apiUrl}/categorias`, this.headers);
  }

  obtenerGastos(fecha?: string): Observable<Gasto[]> {
    const url = fecha ? `${this.apiUrl}/gastos?fecha=${fecha}` : `${this.apiUrl}/gastos`;
    return this.http.get<Gasto[]>(url, this.headers);
  }

  crearGasto(gasto: Gasto): Observable<Gasto> {
    return this.http.post<Gasto>(`${this.apiUrl}/gastos`, gasto, this.headers);
  }

  obtenerResumenMensual(anio: number, mes: number): Observable<ResumenMensual> {
    return this.http.get<ResumenMensual>(`${this.apiUrl}/resumenes?anio=${anio}&mes=${mes}`, this.headers);
  }

  obtenerTopes(anio: number, mes: number): Observable<TopeMensual[]> {
    return this.http.get<TopeMensual[]>(`${this.apiUrl}/topes?anio=${anio}&mes=${mes}`, this.headers);
  }

  definirTope(id_categoria: number, anio: number, mes: number, monto_tope: number): Observable<TopeMensual> {
    return this.http.put<TopeMensual>(
      `${this.apiUrl}/topes`,
      { id_categoria, anio, mes, monto_tope },
      this.headers
    );
  }
}
