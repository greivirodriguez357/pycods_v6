import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { ButtonModule } from 'primeng/button';
import { MessageModule } from 'primeng/message';
import { ApiService } from '../../services/api.service';
import { MascotComponent } from '../../shared/mascot.component';

@Component({
  selector: 'app-forgot',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, InputTextModule, PasswordModule, ButtonModule, MessageModule, MascotComponent],
  templateUrl: './forgot.component.html',
  styleUrls: ['./forgot.component.scss']
})
export class ForgotComponent {
  step: 1 | 2 | 3 = 1;
  email = '';
  code = '';
  password = '';
  loading = false;
  info = '';
  devCode = '';
  error = '';

  sendCode() {
    if (!this.email.includes('@') || this.loading) { return; }
    this.loading = true; this.error = '';
    this.api.forgotPassword(this.email.trim().toLowerCase()).subscribe({
      next: (r) => { this.info = r.message; this.devCode = r.codigo_dev || ''; this.step = 2; this.loading = false; },
      error: (e) => { this.error = e.status === 0 ? 'No se pudo conectar con el servidor.' : 'Revisa que el correo esté bien escrito.'; this.loading = false; }
    });
  }

  changePassword() {
    if (this.code.length < 6 || this.password.length < 6 || this.loading) { return; }
    this.loading = true; this.error = '';
    this.api.resetPassword({ email: this.email.trim().toLowerCase(), code: this.code.trim(), new_password: this.password }).subscribe({
      next: () => { this.step = 3; this.loading = false; },
      error: (e) => { this.error = typeof e.error?.detail === 'string' ? e.error.detail : 'Revisa el código y la contraseña.'; this.loading = false; }
    });
  }

  constructor(private api: ApiService) {}
}
