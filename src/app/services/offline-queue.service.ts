import { Injectable } from '@angular/core';

export interface FotoPendiente {
  id: string;
  dataUrl: string;
  fechaCaptura: string;
  estado: 'Pendiente' | 'Procesando' | 'Error';
}

@Injectable({
  providedIn: 'root',
})
export class OfflineQueueService {
  private readonly QUEUE_KEY = 'fotos_pendientes_recibos';

  obtenerPendientes(): FotoPendiente[] {
    const data = localStorage.getItem(this.QUEUE_KEY);
    return data ? JSON.parse(data) : [];
  }

  guardarPendiente(dataUrl: string): FotoPendiente {
    const pendientes = this.obtenerPendientes();
    const nueva: FotoPendiente = {
      id: Date.now().toString(),
      dataUrl,
      fechaCaptura: new Date().toISOString(),
      estado: 'Pendiente',
    };
    pendientes.push(nueva);
    localStorage.setItem(this.QUEUE_KEY, JSON.stringify(pendientes));
    return nueva;
  }

  eliminarPendiente(id: string): void {
    let pendientes = this.obtenerPendientes();
    pendientes = pendientes.filter((p) => p.id !== id);
    localStorage.setItem(this.QUEUE_KEY, JSON.stringify(pendientes));
  }

  hayInternet(): boolean {
    return navigator.onLine;
  }
}
