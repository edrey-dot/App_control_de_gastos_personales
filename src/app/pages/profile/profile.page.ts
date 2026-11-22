import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import type { OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import {
  IonAvatar,
  IonButton,
  IonButtons,
  IonCard,
  IonCardContent,
  IonContent,
  IonHeader,
  IonIcon,
  IonInput,
  IonItem,
  IonLabel,
  IonSpinner,
  IonText,
  IonTitle,
  IonToolbar,
} from '@ionic/angular';
import { addIcons } from 'ionicons';
import { arrowBackOutline, cameraOutline, logOutOutline, personCircleOutline } from 'ionicons/icons';

import { AuthService } from '../../services/auth.service';
import { ProfileService } from '../../services/profile.service';
import type { PerfilUsuario } from '../../services/profile.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.page.html',
  styleUrls: ['./profile.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonAvatar,
    IonButton,
    IonButtons,
    IonCard,
    IonCardContent,
    IonContent,
    IonHeader,
    IonIcon,
    IonInput,
    IonItem,
    IonLabel,
    IonSpinner,
    IonText,
    IonTitle,
    IonToolbar,
  ],
})
export class ProfilePage implements OnInit, OnDestroy {
  private authService = inject(AuthService);
  private profileService = inject(ProfileService);
  private router = inject(Router);
  private changeDetector = inject(ChangeDetectorRef);
  private fotoObjectUrl: string | null = null;

  perfil: PerfilUsuario | null = null;
  nombreUsuario = '';
  fotoUrl: string | null = null;
  cargando = true;
  guardando = false;
  subiendoFoto = false;
  mensajeError = '';
  mensajeExito = '';

  constructor() {
    addIcons({ arrowBackOutline, cameraOutline, logOutOutline, personCircleOutline });
  }

  ngOnInit(): void {
    if (!this.authService.estaAutenticado()) {
      void this.router.navigate(['/login']);
      return;
    }

    this.profileService.obtenerPerfil().subscribe({
      next: (perfil) => {
        this.perfil = perfil;
        this.nombreUsuario = perfil.nombre_usuario;
        this.cargando = false;
        this.changeDetector.markForCheck();
        if (perfil.tiene_foto) this.cargarFoto();
      },
      error: (error) => {
        this.cargando = false;
        this.mensajeError = error.error?.detail || 'No se pudo cargar el perfil.';
        this.changeDetector.markForCheck();
      },
    });
  }

  ngOnDestroy(): void {
    if (this.fotoObjectUrl) URL.revokeObjectURL(this.fotoObjectUrl);
  }

  guardarNombre(): void {
    if (this.guardando) return;
    const nombre = this.nombreUsuario.trim();
    if (nombre.length < 2 || nombre.length > 50) {
      this.mensajeError = 'El nombre debe tener entre 2 y 50 caracteres.';
      this.mensajeExito = '';
      return;
    }

    this.guardando = true;
    this.mensajeError = '';
    this.mensajeExito = '';
    this.profileService.actualizarPerfil(nombre).subscribe({
      next: (perfil) => {
        this.perfil = perfil;
        this.nombreUsuario = perfil.nombre_usuario;
        this.mensajeExito = 'Perfil actualizado.';
        this.guardando = false;
        this.profileService.notificarPerfilActualizado(perfil);
        this.changeDetector.markForCheck();
      },
      error: (error) => {
        this.mensajeError = error.error?.detail || 'No se pudo actualizar el nombre.';
        this.guardando = false;
        this.changeDetector.markForCheck();
      },
    });
  }

  seleccionarFoto(event: Event): void {
    const input = event.currentTarget as HTMLInputElement;
    const foto = input.files?.[0];
    input.value = '';
    if (!foto) return;

    if (foto.size > 2 * 1024 * 1024) {
      this.mensajeError = 'La foto no puede superar 2 MB.';
      this.mensajeExito = '';
      return;
    }
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(foto.type)) {
      this.mensajeError = 'Elige una foto JPG, PNG o WebP.';
      this.mensajeExito = '';
      return;
    }

    this.subiendoFoto = true;
    this.mensajeError = '';
    this.mensajeExito = '';
    this.profileService.subirFoto(foto).subscribe({
      next: (perfil) => {
        this.perfil = perfil;
        this.mensajeExito = 'Foto de perfil actualizada.';
        this.subiendoFoto = false;
        this.profileService.notificarPerfilActualizado(perfil);
        this.changeDetector.markForCheck();
        this.cargarFoto();
      },
      error: (error) => {
        this.mensajeError = error.error?.detail || 'No se pudo guardar la foto.';
        this.subiendoFoto = false;
        this.changeDetector.markForCheck();
      },
    });
  }

  volverInicio(): void {
    void this.router.navigate(['/home']);
  }

  cerrarSesion(): void {
    this.authService.cerrarSesion();
    void this.router.navigate(['/login']);
  }

  private cargarFoto(): void {
    this.profileService.obtenerFoto().subscribe({
      next: (foto) => {
        if (this.fotoObjectUrl) URL.revokeObjectURL(this.fotoObjectUrl);
        this.fotoObjectUrl = URL.createObjectURL(foto);
        this.fotoUrl = this.fotoObjectUrl;
        this.changeDetector.markForCheck();
      },
      error: (error) => {
        this.mensajeError = error.error?.detail || 'No se pudo cargar la foto de perfil.';
        this.changeDetector.markForCheck();
      },
    });
  }
}
