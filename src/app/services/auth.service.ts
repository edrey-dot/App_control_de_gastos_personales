import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UsuarioResponse {
  id_usuario: number;
  correo: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;
  private readonly TOKEN_KEY = 'auth_token';

  registrar(correo: string, contrasena: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/usuarios`, { correo, contrasena });
  }

  iniciarSesion(correo: string, contrasena: string): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.apiUrl}/sesiones`, { correo, contrasena }).pipe(
      tap((res) => {
        if (res && res.access_token) {
          localStorage.setItem(this.TOKEN_KEY, res.access_token);
        }
      })
    );
  }

  cerrarSesion(): void {
    localStorage.removeItem(this.TOKEN_KEY);
  }

  obtenerToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  estaAutenticado(): boolean {
    return !!this.obtenerToken();
  }

  obtenerHeaders(): { [header: string]: string } {
    const token = this.obtenerToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
}
