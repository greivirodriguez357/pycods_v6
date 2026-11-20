import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { User } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  // Ruta relativa: el navegador llama a http://localhost:4042/api/...
  // En Docker, Nginx lo reenvía a backend:8001; con `ng serve`, proxy.conf.json
  // lo reenvía a localhost:8001. Así no hay peticiones cross-origin (sin CORS).
  private readonly baseUrl = '/api';

  constructor(private http: HttpClient) {}

  // Auth
  register(userData: any): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/auth/register`, userData);
  }

  login(credentials: { email: string; password: string }): Observable<{ access_token: string; token_type: string }> {
    return this.http.post<{ access_token: string; token_type: string }>(`${this.baseUrl}/auth/login`, credentials);
  }

  getMe(): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/auth/me`);
  }

  // Users
  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/users/`);
  }

  updateMe(data: { avatar?: string }): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/users/me`, data);
  }

  // Exercises
  getExercises(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/exercises/`);
  }

  getCompletedExercises(userId: number): Observable<number[]> {
    return this.http.get<number[]>(`${this.baseUrl}/exercises/progress/${userId}`);
  }

  submitProgress(userId: number, progressData: { ejercicio_id: number; completado: boolean }): Observable<any> {
    return this.http.post(`${this.baseUrl}/exercises/progress/${userId}`, progressData);
  }

  // Recuperar contraseña
  forgotPassword(email: string): Observable<{ message: string; codigo_dev?: string }> {
    return this.http.post<{ message: string; codigo_dev?: string }>(`${this.baseUrl}/auth/forgot-password`, { email });
  }
  resetPassword(data: { email: string; code: string; new_password: string }): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.baseUrl}/auth/reset-password`, data);
  }

  // Lecciones interactivas y código seguro
  getLessons(): Observable<any[]> { return this.http.get<any[]>(`${this.baseUrl}/lessons/`); }
  runCode(code: string): Observable<{ salida: string; error: string | null }> {
    return this.http.post<{ salida: string; error: string | null }>(`${this.baseUrl}/code/run`, { code });
  }
  uploadPhoto(imageBase64: string): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/users/me/avatar-photo`, { image_base64: imageBase64 });
  }
  getAchievements(): Observable<any[]> { return this.http.get<any[]>(`${this.baseUrl}/gamification/achievements`); }

  // Panel docente / admin
  getStats(): Observable<any> { return this.http.get(`${this.baseUrl}/users/stats`); }
  getUserDetail(id: number): Observable<any> { return this.http.get(`${this.baseUrl}/users/${id}/detail`); }
  updateUser(id: number, data: any): Observable<User> { return this.http.patch<User>(`${this.baseUrl}/users/${id}`, data); }
  deleteUser(id: number): Observable<any> { return this.http.delete(`${this.baseUrl}/users/${id}`); }
  createExercise(data: any): Observable<any> { return this.http.post(`${this.baseUrl}/exercises/`, data); }
  updateExercise(id: number, data: any): Observable<any> { return this.http.put(`${this.baseUrl}/exercises/${id}`, data); }
  deleteExercise(id: number): Observable<any> { return this.http.delete(`${this.baseUrl}/exercises/${id}`); }

  // Monstruo y juegos
  getMonster(): Observable<any> { return this.http.get(`${this.baseUrl}/gamification/monster`); }
  buyMonsterItem(itemId: string): Observable<any> { return this.http.post(`${this.baseUrl}/gamification/monster/buy`, { item_id: itemId }); }
  saveMonster(parts: Record<string, string>): Observable<any> { return this.http.put(`${this.baseUrl}/gamification/monster`, parts); }
  completeMemory(movimientos: number): Observable<any> { return this.http.post(`${this.baseUrl}/gamification/memory`, { movimientos }); }

  // Gamification
  getGamificationStatus(userId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/gamification/status/${userId}`);
  }
}
