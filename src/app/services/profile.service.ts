import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import type { Observable } from 'rxjs';
import { Subject } from 'rxjs';

import { environment } from '../../environments/environment';

import { AuthService } from './auth.service';

export interface PerfilUsuario {
  id_usuario: number;
  nombre_usuario: string;
  correo: string;
  telefono: string | null;
  tiene_foto: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class ProfileService {
  private perfilActualizadoSubject = new Subject<PerfilUsuario>();
  readonly perfilActualizado$ = this.perfilActualizadoSubject.asObservable();

  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = environment.apiUrl;

  private get headers() {
    return { headers: this.authService.obtenerHeaders() };
  }

  obtenerPerfil(): Observable<PerfilUsuario> {
    return this.http.get<PerfilUsuario>(`${this.apiUrl}/usuarios/me`, this.headers);
  }

  notificarPerfilActualizado(perfil: PerfilUsuario): void {
    this.perfilActualizadoSubject.next(perfil);
  }

  actualizarPerfil(nombre_usuario: string): Observable<PerfilUsuario> {
    return this.http.put<PerfilUsuario>(`${this.apiUrl}/usuarios/me`, { nombre_usuario }, this.headers);
  }

  subirFoto(foto: File): Observable<PerfilUsuario> {
    const formData = new FormData();
    formData.append('foto', foto, foto.name);
    return this.http.put<PerfilUsuario>(`${this.apiUrl}/usuarios/me/foto`, formData, this.headers);
  }

  obtenerFoto(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/usuarios/me/foto`, {
      ...this.headers,
      responseType: 'blob',
    });
  }
}
