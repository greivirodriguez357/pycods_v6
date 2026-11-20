import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { SelectButtonModule } from 'primeng/selectbutton';
import { ButtonModule } from 'primeng/button';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { AVATARS, isPhoto, photoUrl, avatarIcon } from '../../shared/avatars';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, SelectButtonModule, ButtonModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent {
  profileForm: FormGroup;
  avatars = AVATARS;

  learningOptions = [
    { label: '🔊 Escuchando con voz', value: 'audio' },
    { label: '🤫 Leyendo en silencio', value: 'visual' }
  ];

  selectedAvatar: string = 'avatar1';

  saving = false;
  photoBusy = false;
  photoMsg = '';
  avatarTouched = false;
  readonly isPhoto = isPhoto;
  readonly photoUrl = photoUrl;
  readonly avatarIcon = avatarIcon;

  constructor(private fb: FormBuilder, private router: Router, private api: ApiService, public auth: AuthService) {
    this.profileForm = this.fb.group({
      preferencia: ['audio']
    });
    // Muestra el avatar que ya tiene guardado el usuario
    const saved = this.auth.currentUser?.avatar;
    if (saved && AVATARS.some(a => a.id === saved)) { this.selectedAvatar = saved; }
  }

  selectAvatar(id: string) {
    this.selectedAvatar = id;
    this.avatarTouched = true;
  }

  /** Foto desde la galería o la cámara: se recorta cuadrada y se reduce a 256 px antes de subirla. */
  onPhoto(ev: Event) {
    const file = (ev.target as HTMLInputElement).files?.[0];
    if (!file) { return; }
    this.photoMsg = '';
    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        const size = 256, side = Math.min(img.width, img.height);
        const canvas = document.createElement('canvas');
        canvas.width = canvas.height = size;
        canvas.getContext('2d')!.drawImage(img, (img.width - side) / 2, (img.height - side) / 2, side, side, 0, 0, size, size);
        this.photoBusy = true;
        this.api.uploadPhoto(canvas.toDataURL('image/jpeg', 0.85)).subscribe({
          next: () => { this.auth.loadUser().subscribe(); this.photoBusy = false; this.avatarTouched = false; this.photoMsg = '¡Foto guardada! 📸'; },
          error: (e) => { this.photoBusy = false; this.photoMsg = e.error?.detail || 'No se pudo subir la foto'; }
        });
      };
      img.src = reader.result as string;
    };
    reader.readAsDataURL(file);
  }

  saveProfile() {
    if (!this.avatarTouched) { this.router.navigate(['/dashboard']); return; }
    this.saving = true;
    this.api.updateMe({ avatar: this.selectedAvatar }).subscribe({
      next: () => this.auth.loadUser().subscribe({
        next: () => this.router.navigate(['/dashboard']),
        error: () => this.router.navigate(['/dashboard'])
      }),
      error: () => { this.saving = false; }
    });
  }
}
