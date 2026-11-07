import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

export interface LecturaRecibo {
  comercio?: string;
  fecha?: string;
  monto?: number;
  mensaje?: string;
}

@Injectable({
  providedIn: 'root',
})
export class ReceiptService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = environment.apiUrl;

  leerRecibo(archivoImagen: File | Blob): Observable<LecturaRecibo> {
    const formData = new FormData();
    formData.append('foto', archivoImagen, 'recibo.jpg');

    return this.http.post<LecturaRecibo>(`${this.apiUrl}/recibos/lecturas`, formData, {
      headers: this.authService.obtenerHeaders(),
    });
  }
}
