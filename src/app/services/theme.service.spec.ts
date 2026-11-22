import { ThemeService } from './theme.service';

describe('ThemeService', () => {
  beforeEach(() => {
    localStorage.removeItem('app_theme');
    document.documentElement.classList.remove('ion-palette-dark');
    delete document.documentElement.dataset['theme'];
  });

  afterEach(() => {
    localStorage.removeItem('app_theme');
    document.documentElement.classList.remove('ion-palette-dark');
    delete document.documentElement.dataset['theme'];
  });

  it('alterna el tema oscuro y guarda la preferencia', () => {
    const service = new ThemeService();
    expect(service.modoOscuro).toBe(true);
    expect(document.documentElement.classList.contains('ion-palette-dark')).toBe(true);

    service.alternar();

    expect(service.modoOscuro).toBe(false);
    expect(localStorage.getItem('app_theme')).toBe('light');
    expect(document.documentElement.classList.contains('ion-palette-dark')).toBe(false);
  });
});
