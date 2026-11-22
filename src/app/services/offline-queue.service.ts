import { Injectable } from '@angular/core';

export interface FotoPendiente {
  id: string;
  foto: Blob;
  fechaCaptura: string;
  estado: 'Pendiente' | 'Procesando' | 'Error';
}

interface FotoPendienteAnterior {
  id?: string;
  dataUrl: string;
  fechaCaptura?: string;
  estado?: FotoPendiente['estado'];
}

@Injectable({
  providedIn: 'root',
})
export class OfflineQueueService {
  private readonly databaseName = 'control-gastos';
  private readonly storeName = 'recibos-pendientes';
  private readonly oldQueueKey = 'fotos_pendientes_recibos';
  private database: Promise<IDBDatabase> | null = null;

  async obtenerPendientes(): Promise<FotoPendiente[]> {
    const database = await this.abrirBaseDatos();
    const transaction = database.transaction(this.storeName, 'readonly');
    const request = transaction.objectStore(this.storeName).getAll();
    const fotos = await this.esperarSolicitud<FotoPendiente[]>(request);
    for (const foto of fotos) {
      if (foto.estado === 'Procesando') {
        await this.actualizarEstado(foto.id, 'Pendiente');
        foto.estado = 'Pendiente';
      }
    }
    return fotos.sort((a, b) => a.fechaCaptura.localeCompare(b.fechaCaptura));
  }

  async guardarPendiente(foto: Blob): Promise<FotoPendiente> {
    const pendiente: FotoPendiente = {
      id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`,
      foto,
      fechaCaptura: new Date().toISOString(),
      estado: 'Pendiente',
    };
    const database = await this.abrirBaseDatos();
    const transaction = database.transaction(this.storeName, 'readwrite');
    transaction.objectStore(this.storeName).put(pendiente);
    await this.esperarTransaccion(transaction);
    return pendiente;
  }

  async actualizarEstado(id: string, estado: FotoPendiente['estado']): Promise<void> {
    const database = await this.abrirBaseDatos();
    const transaction = database.transaction(this.storeName, 'readwrite');
    const store = transaction.objectStore(this.storeName);
    const request = store.get(id);
    const pendiente = await this.esperarSolicitud<FotoPendiente | undefined>(request);
    if (pendiente) {
      store.put({ ...pendiente, estado });
    }
    await this.esperarTransaccion(transaction);
  }

  async eliminarPendiente(id: string): Promise<void> {
    const database = await this.abrirBaseDatos();
    const transaction = database.transaction(this.storeName, 'readwrite');
    transaction.objectStore(this.storeName).delete(id);
    await this.esperarTransaccion(transaction);
  }

  hayInternet(): boolean {
    return navigator.onLine;
  }

  private abrirBaseDatos(): Promise<IDBDatabase> {
    if (!globalThis.indexedDB) {
      return Promise.reject(new Error('El almacenamiento local de recibos no está disponible.'));
    }
    if (this.database) return this.database;

    this.database = new Promise((resolve, reject) => {
      const request = indexedDB.open(this.databaseName, 1);
      request.onupgradeneeded = () => {
        request.result.createObjectStore(this.storeName, { keyPath: 'id' });
      };
      request.onerror = () => reject(request.error ?? new Error('No se pudo abrir la cola de recibos.'));
      request.onsuccess = () => {
        const database = request.result;
        this.migrarColaAnterior(database).then(
          () => resolve(database),
          (error: unknown) => reject(error),
        );
      };
    });
    return this.database;
  }

  private async migrarColaAnterior(database: IDBDatabase): Promise<void> {
    const guardados = localStorage.getItem(this.oldQueueKey);
    if (!guardados) return;

    const anteriores = JSON.parse(guardados) as FotoPendienteAnterior[];
    const transaction = database.transaction(this.storeName, 'readwrite');
    const store = transaction.objectStore(this.storeName);
    const ids = new Set<string>();
    for (const anterior of anteriores) {
      const id =
        anterior.id && !ids.has(anterior.id)
          ? anterior.id
          : (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`);
      ids.add(id);
      store.put({
        id,
        foto: this.convertirDataUrlABlob(anterior.dataUrl),
        fechaCaptura: anterior.fechaCaptura ?? new Date().toISOString(),
        estado: 'Pendiente',
      } satisfies FotoPendiente);
    }
    await this.esperarTransaccion(transaction);
    localStorage.removeItem(this.oldQueueKey);
  }

  private convertirDataUrlABlob(dataUrl: string): Blob {
    const [metadata, contenido] = dataUrl.split(',');
    if (!metadata || !contenido) {
      throw new Error('Hay una foto pendiente con formato inválido.');
    }
    const tipo = metadata.match(/^data:([^;]+);base64$/)?.[1] ?? 'image/jpeg';
    const binario = atob(contenido);
    const bytes = Uint8Array.from(binario, (caracter) => caracter.charCodeAt(0));
    return new Blob([bytes], { type: tipo });
  }

  private esperarSolicitud<T>(request: IDBRequest): Promise<T> {
    return new Promise((resolve, reject) => {
      request.onsuccess = () => resolve(request.result as T);
      request.onerror = () => reject(request.error ?? new Error('Falló una operación de la cola local.'));
    });
  }

  private esperarTransaccion(transaction: IDBTransaction): Promise<void> {
    return new Promise((resolve, reject) => {
      transaction.oncomplete = () => resolve();
      transaction.onabort = transaction.onerror = () =>
        reject(transaction.error ?? new Error('No se pudo guardar la cola de recibos.'));
    });
  }
}
