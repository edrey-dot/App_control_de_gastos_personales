import { Injectable } from '@angular/core';

export type ThemeMode = 'dark' | 'light';

@Injectable({
  providedIn: 'root',
})
export class ThemeService {
  private readonly storageKey = 'app_theme';
  private currentMode: ThemeMode;

  constructor() {
    this.currentMode = localStorage.getItem(this.storageKey) === 'light' ? 'light' : 'dark';
    this.aplicarTema();
  }

  get modoOscuro(): boolean {
    return this.currentMode === 'dark';
  }

  alternar(): void {
    this.currentMode = this.modoOscuro ? 'light' : 'dark';
    localStorage.setItem(this.storageKey, this.currentMode);
    this.aplicarTema();
  }

  private aplicarTema(): void {
    document.documentElement.classList.toggle('ion-palette-dark', this.modoOscuro);
    document.documentElement.dataset['theme'] = this.currentMode;
  }
}
