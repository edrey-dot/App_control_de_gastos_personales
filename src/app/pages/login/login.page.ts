import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonIcon,
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonItem,
  IonLabel,
  IonInput,
  IonButton,
  IonText,
  IonSegment,
  IonSegmentButton,
  IonSpinner,
} from '@ionic/angular';
import { addIcons } from 'ionicons';
import { moonOutline, sunnyOutline } from 'ionicons/icons';

import { AuthService } from '../../services/auth.service';
import { ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.page.html',
  styleUrls: ['./login.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonButtons,
    IonIcon,
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonItem,
    IonLabel,
    IonInput,
    IonButton,
    IonText,
    IonSegment,
    IonSegmentButton,
    IonSpinner,
  ],
})
export class LoginPage {
  private authService = inject(AuthService);
  private themeService = inject(ThemeService);
  private changeDetector = inject(ChangeDetectorRef);
  private router = inject(Router);

  modo: 'login' | 'registro' = 'login';
  modoOscuro = this.themeService.modoOscuro;
  identificador = '';
  correo = '';
  telefono = '';
  nombreUsuario = '';
  contrasena = '';
  enviando = false;
  mensajeError = '';
  mensajeExito = '';

  constructor() {
    addIcons({ moonOutline, sunnyOutline });
  }

  alternarTema(): void {
    this.themeService.alternar();
    this.modoOscuro = this.themeService.modoOscuro;
  }

  cambiarModo(modo: string | number | null | undefined): void {
    if (modo !== 'login' && modo !== 'registro') return;
    this.modo = modo;
    this.mensajeError = '';
    this.mensajeExito = '';
  }

  onSubmit(): void {
    if (this.enviando) return;
    this.mensajeError = '';
    this.mensajeExito = '';

    const identificador = this.modo === 'registro' ? this.correo : this.identificador;
    if (
      !identificador.trim() ||
      !this.contrasena ||
      (this.modo === 'registro' && (!this.nombreUsuario.trim() || !this.telefono.trim()))
    ) {
      this.mensajeError = 'Por favor completa todos los campos.';
      return;
    }

    if (this.modo === 'registro') {
      if (this.contrasena.length < 8) {
        this.mensajeError = 'La contraseña debe tener al menos 8 caracteres.';
        return;
      }

      this.enviando = true;
      this.authService
        .registrar({
          nombre_usuario: this.nombreUsuario.trim(),
          telefono: this.telefono.trim(),
          correo: this.correo.trim(),
          contrasena: this.contrasena,
        })
        .subscribe({
          next: () => {
            this.mensajeExito = 'Cuenta creada exitosamente. Iniciando sesión...';
            this.changeDetector.markForCheck();
            this.loginDirecto(this.correo);
          },
          error: (err) => {
            this.enviando = false;
            this.mensajeError = err.error?.detail || 'Error al registrar usuario.';
            this.changeDetector.markForCheck();
          },
        });
    } else {
      this.loginDirecto(identificador);
    }
  }

  private loginDirecto(identificador: string): void {
    this.enviando = true;
    this.authService.iniciarSesion(identificador, this.contrasena).subscribe({
      next: () => {
        this.enviando = false;
        this.changeDetector.markForCheck();
        void this.router.navigate(['/home']);
      },
      error: (err) => {
        this.enviando = false;
        this.mensajeError = err.error?.detail || 'Correo/celular o contraseña incorrectos.';
        this.changeDetector.markForCheck();
      },
    });
  }
}
