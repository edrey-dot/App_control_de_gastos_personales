import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import {
  IonHeader,
  IonToolbar,
  IonTitle,
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
  IonToast,
} from '@ionic/angular';
import { AuthService } from '../../services/auth.service';

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
  ],
})
export class LoginPage {
  private authService = inject(AuthService);
  private router = inject(Router);

  modo: 'login' | 'registro' = 'login';
  correo = '';
  contrasena = '';
  mensajeError = '';
  mensajeExito = '';

  cambiarModo(modo: any) {
    this.modo = modo;
    this.mensajeError = '';
    this.mensajeExito = '';
  }

  onSubmit() {
    this.mensajeError = '';
    this.mensajeExito = '';

    if (!this.correo || !this.contrasena) {
      this.mensajeError = 'Por favor completa todos los campos.';
      return;
    }

    if (this.modo === 'registro') {
      if (this.contrasena.length < 8) {
        this.mensajeError = 'La contraseña debe tener al menos 8 caracteres.';
        return;
      }

      this.authService.registrar(this.correo, this.contrasena).subscribe({
        next: () => {
          this.mensajeExito = 'Cuenta creada exitosamente. Iniciando sesión...';
          this.loginDirecto();
        },
        error: (err) => {
          this.mensajeError = err.error?.detail || 'Error al registrar usuario.';
        },
      });
    } else {
      this.loginDirecto();
    }
  }

  private loginDirecto() {
    this.authService.iniciarSesion(this.correo, this.contrasena).subscribe({
      next: () => {
        this.router.navigate(['/home']);
      },
      error: (err) => {
        this.mensajeError = err.error?.detail || 'Correo o contrasena incorrectos';
      },
    });
  }
}
