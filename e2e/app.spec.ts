import { expect, test } from '@playwright/test';
import type { Page } from '@playwright/test';

const profileCorsHeaders = {
  'access-control-allow-origin': 'http://localhost:4200',
  'access-control-allow-credentials': 'true',
  'access-control-allow-methods': 'GET,PUT,OPTIONS',
  'access-control-allow-headers': 'authorization,content-type',
};

async function mockProfile(page: Page): Promise<void> {
  await page.route('**/usuarios/me', async (route) => {
    if (route.request().method() === 'OPTIONS') {
      await route.fulfill({ status: 204, headers: profileCorsHeaders });
      return;
    }

    await route.fulfill({
      json: {
        id_usuario: 1,
        nombre_usuario: 'Ana de prueba',
        correo: 'ana@correo.com',
        telefono: '3001112233',
        tiene_foto: false,
      },
      headers: profileCorsHeaders,
    });
  });
}

test('visits the app root url', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('heading', { name: 'Bienvenido' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Iniciar Sesión' })).toBeVisible();
});

test('cambia entre temas y conserva la selección', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await page.getByRole('button', { name: 'Cambiar a modo claro' }).click();
  await expect(page.locator('html')).not.toHaveClass(/ion-palette-dark/);
  await expect(page.getByRole('button', { name: 'Cambiar a modo oscuro' })).toBeVisible();

  await page.reload({ waitUntil: 'domcontentloaded' });

  await expect(page.locator('html')).not.toHaveClass(/ion-palette-dark/);
  await expect(page.getByRole('button', { name: 'Cambiar a modo oscuro' })).toBeVisible();
});

test('abre el formulario para registrar un gasto manual', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('auth_token', 'token-de-prueba'));
  await mockProfile(page);
  await page.goto('/home', { waitUntil: 'domcontentloaded' });
  await page.getByRole('button', { name: 'Registrar gasto' }).click();

  await expect(page.getByRole('heading', { name: 'Registrar gasto' })).toBeVisible();
  await expect(page.getByRole('textbox', { name: 'Comercio' })).toBeVisible();
});

test('mantiene visible el formulario de gasto en una pantalla móvil', async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 640 });
  await page.addInitScript(() => localStorage.setItem('auth_token', 'token-de-prueba'));
  await mockProfile(page);
  await page.goto('/home', { waitUntil: 'domcontentloaded' });
  await page.getByRole('button', { name: 'Registrar gasto' }).click();

  const tarjeta = page.locator('.preview-card');
  await expect(page.getByRole('heading', { name: 'Registrar gasto' })).toBeVisible();
  const caja = await tarjeta.boundingBox();
  if (!caja) throw new Error('No se pudo medir el formulario de gasto.');
  const encabezado = await page.locator('ion-header').boundingBox();
  if (!encabezado) throw new Error('No se pudo medir el encabezado.');
  expect(caja.y).toBeGreaterThanOrEqual(0);
  expect(caja.y + caja.height).toBeLessThanOrEqual(640);
  expect(caja.y).toBeLessThan(encabezado.y + encabezado.height);
});

test('abre el perfil desde el encabezado', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('auth_token', 'token-de-prueba'));
  await mockProfile(page);
  await page.goto('/home', { waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('button', { name: 'Cerrar sesión' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Abrir mi perfil' }).click();

  await expect(page).toHaveURL(/\/perfil$/);
  await expect(page.getByText('Mi perfil')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Ana de prueba' })).toBeVisible();
  await expect(page.getByText('Correo electrónico', { exact: true })).toHaveCount(0);
  await expect(page.getByText('Celular', { exact: true })).toHaveCount(0);
  await page.getByRole('button', { name: 'Cerrar sesión' }).click();
  await expect(page).toHaveURL(/\/login$/);
});

test('elimina un gasto con confirmación', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('auth_token', 'token-de-prueba'));
  await mockProfile(page);
  const corsHeaders = {
    'access-control-allow-origin': 'http://localhost:4200',
    'access-control-allow-credentials': 'true',
    'access-control-allow-methods': 'GET,DELETE,OPTIONS',
    'access-control-allow-headers': 'authorization,content-type',
  };
  let eliminado = false;
  await page.route('**/gastos**', async (route) => {
    const metodo = route.request().method();
    if (metodo === 'OPTIONS') {
      await route.fulfill({ status: 204, headers: corsHeaders });
      return;
    }
    if (metodo === 'DELETE') {
      eliminado = true;
      await route.fulfill({ status: 204, headers: corsHeaders });
      return;
    }

    await route.fulfill({
      json: eliminado
        ? []
        : [{ id_gasto: 42, comercio: 'Mercado prueba', fecha: '2026-11-19', monto: 18000, id_categoria: 1 }],
      headers: corsHeaders,
    });
  });
  await page.route('**/categorias', async (route) => {
    if (route.request().method() === 'OPTIONS') {
      await route.fulfill({ status: 204, headers: corsHeaders });
      return;
    }
    await route.fulfill({ json: [{ id_categoria: 1, nombre: 'Comida' }], headers: corsHeaders });
  });
  await page.route('**/topes**', async (route) => {
    if (route.request().method() === 'OPTIONS') {
      await route.fulfill({ status: 204, headers: corsHeaders });
      return;
    }
    await route.fulfill({ json: [], headers: corsHeaders });
  });
  await page.route('**/resumenes**', async (route) => {
    if (route.request().method() === 'OPTIONS') {
      await route.fulfill({ status: 204, headers: corsHeaders });
      return;
    }
    await route.fulfill({
      json: {
        anio: 2026,
        mes: 11,
        total_mes: 18000,
        items: [{ id_categoria: 1, categoria: 'Comida', total: 18000, porcentaje: 100 }],
      },
      headers: corsHeaders,
    });
  });

  await page.goto('/home', { waitUntil: 'domcontentloaded' });
  await expect(page.getByText('Mercado prueba')).toBeVisible();
  await page.getByRole('button', { name: 'Eliminar gasto de Mercado prueba' }).click();
  await expect(page.getByRole('alertdialog')).toBeVisible();
  await page.getByRole('button', { name: 'Eliminar', exact: true }).click();

  await expect.poll(() => eliminado).toBe(true);
  await expect(page.getByText('No hay gastos para este período.')).toBeVisible();
});

test('guarda una foto en la cola persistente cuando no hay conexión', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('auth_token', 'token-de-prueba');
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: false });
  });
  await mockProfile(page);
  await page.goto('/home', { waitUntil: 'domcontentloaded' });
  expect(await page.evaluate(() => navigator.onLine)).toBe(false);
  const fileChooserPromise = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Escanear recibo' }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: 'recibo.png',
    mimeType: 'image/png',
    buffer: Buffer.from('imagen de prueba'),
  });

  const pendientes = await page.evaluate(
    () =>
      new Promise<number>((resolve, reject) => {
        const request = indexedDB.open('control-gastos');
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
          const transaction = request.result.transaction('recibos-pendientes', 'readonly');
          const count = transaction.objectStore('recibos-pendientes').count();
          count.onsuccess = () => resolve(count.result);
          count.onerror = () => reject(count.error);
        };
      }),
  );
  expect(pendientes).toBe(1);
  await expect(page.getByText('Foto guardada. Se reintentara mas tarde.')).toBeVisible();
  await expect(page.getByText('Recibos pendientes')).toBeVisible();
});
