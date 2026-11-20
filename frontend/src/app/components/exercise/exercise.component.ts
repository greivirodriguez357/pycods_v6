import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { MascotComponent } from '../../shared/mascot.component';

const shuffle = (a: number[]): number[] => {
  const r = [...a];
  for (let i = r.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [r[i], r[j]] = [r[j], r[i]]; }
  return r;
};

@Component({
  selector: 'app-exercise',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, ButtonModule, MascotComponent],
  templateUrl: './exercise.component.html',
  styleUrls: ['./exercise.component.scss']
})
export class ExerciseComponent implements OnInit {
  exerciseId = 1;
  lesson: any = null;
  error = '';
  i = 0;
  result: any = null;
  saving = false;

  // estado del paso actual
  optionOrder: number[] = [];
  wrong: number[] = [];
  ok = false;
  shuffled: number[] = [];
  chosen: number[] = [];
  msg = '';
  code = '';
  codeOut = '';
  codeErr = '';
  running = false;

  constructor(private route: ActivatedRoute, private api: ApiService, private auth: AuthService) {
    this.exerciseId = Number(this.route.snapshot.paramMap.get('id')) || 1;
  }

  ngOnInit(): void {
    this.api.getLessons().subscribe({
      next: (ls) => {
        this.lesson = ls.find(l => l.exercise_id === this.exerciseId) || null;
        if (this.lesson) { this.enterStep(); } else { this.error = 'Esta lección todavía no está lista.'; }
      },
      error: () => this.error = 'No se pudo cargar la lección.'
    });
  }

  get step(): any { return this.lesson?.pasos[this.i]; }
  get isLast(): boolean { return this.i === this.lesson.pasos.length - 1; }

  private enterStep() {
    const s = this.step;
    this.ok = false; this.wrong = []; this.chosen = []; this.msg = ''; this.codeOut = ''; this.codeErr = '';
    if (s.tipo === 'opcion') { this.optionOrder = shuffle(s.opciones.map((_: any, k: number) => k)); }
    if (s.tipo === 'ordenar') {
      const n = s.bloques.length;
      let a: number[];
      do { a = shuffle([...Array(n).keys()]); } while (n > 1 && a.every((v, k) => v === k));
      this.shuffled = a;
    }
    if (s.tipo === 'codigo') { this.code = s.inicial; }
  }

  get bank(): number[] { return this.shuffled.filter(id => !this.chosen.includes(id)); }

  // ---- opción múltiple ----
  pick(idx: number) {
    if (this.ok || this.wrong.includes(idx)) { return; }
    if (idx === this.step.correcta) { this.ok = true; } else { this.wrong = [...this.wrong, idx]; }
  }

  // ---- ordenar el código ----
  add(id: number) { if (!this.ok) { this.chosen = [...this.chosen, id]; this.msg = ''; } }
  remove(id: number) { if (!this.ok) { this.chosen = this.chosen.filter(x => x !== id); } }
  checkOrder() {
    if (this.chosen.every((v, k) => v === k)) { this.ok = true; }
    else { this.msg = '¡Casi! Toca un bloque de arriba para quitarlo y prueba otro orden 💪'; }
  }

  // ---- escribir código (se ejecuta en el servidor con un intérprete seguro) ----
  runCode() {
    if (this.running) { return; }
    this.running = true; this.codeOut = ''; this.codeErr = '';
    this.api.runCode(this.code).subscribe({
      next: (r) => {
        this.running = false;
        this.codeOut = r.salida;
        this.codeErr = r.error || '';
        if (!r.error) {
          if (r.salida.trim() === (this.step.esperada || '').trim()) { this.ok = true; }
          else { this.codeErr = `Tu código funciona, pero debía mostrar: ${this.step.esperada}`; }
        }
      },
      error: () => { this.running = false; this.codeErr = 'No se pudo ejecutar. Revisa tu conexión.'; }
    });
  }

  insertTab(ev: Event) {
    ev.preventDefault();
    const ta = ev.target as HTMLTextAreaElement;
    const pos = ta.selectionStart;
    this.code = this.code.slice(0, pos) + '    ' + this.code.slice(ta.selectionEnd);
    setTimeout(() => ta.setSelectionRange(pos + 4, pos + 4));
  }

  speak(text: string) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'es-ES'; u.rate = 0.9;
      window.speechSynthesis.speak(u);
    }
  }
  stepText(): string { const s = this.step; return s.tipo === 'aprender' ? s.texto : s.tipo === 'opcion' ? s.pregunta : s.instruccion; }

  next() {
    if (!this.isLast) { this.i++; this.enterStep(); return; }
    const user = this.auth.currentUser;
    if (!user) { return; }
    this.saving = true;
    this.api.submitProgress(user.id, { ejercicio_id: this.exerciseId, completado: true }).subscribe({
      next: (r) => { this.result = r; this.saving = false; this.auth.loadUser().subscribe(); },
      error: () => { this.saving = false; this.error = 'No se pudo guardar tu progreso.'; }
    });
  }
}
