import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AgGridModule } from 'ag-grid-angular';
import { CellClickedEvent, ColDef, GridReadyEvent } from 'ag-grid-community';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { DropdownModule } from 'primeng/dropdown';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { User } from '../../models/user.model';

const EMPTY_EXERCISE = { id: 0, titulo: '', descripcion: '', ejemplo_codigo: '', respuesta_correcta: '', xp_recompensa: 20, nivel_requerido: 1 };

@Component({
  selector: 'app-admin-panel',
  standalone: true,
  imports: [CommonModule, FormsModule, AgGridModule, ButtonModule, DialogModule, InputTextModule, DropdownModule],
  templateUrl: './admin-panel.component.html',
  styleUrls: ['./admin-panel.component.scss']
})
export class AdminPanelComponent implements OnInit {
  rowData: User[] = [];
  stats: any = null;
  exercises: any[] = [];
  message = '';
  errorMessage = '';

  // diálogos
  editUser: any = null;
  detail: any = null;
  editExercise: any = null;

  roles = [
    { label: 'Estudiante', value: 'estudiante' },
    { label: 'Docente', value: 'docente' },
    { label: 'Administrador', value: 'admin' }
  ];

  defaultColDef: ColDef = { flex: 1, minWidth: 110, sortable: true, filter: true, resizable: true };

  columnDefs: ColDef[] = [
    { field: 'id', headerName: 'ID', flex: 0, width: 80, minWidth: 70 },
    { field: 'nombre', headerName: 'Nombre', minWidth: 160 },
    { field: 'email', headerName: 'Correo', minWidth: 210 },
    { field: 'rol', headerName: 'Rol' },
    { field: 'nivel', headerName: 'Nivel' },
    { field: 'xp', headerName: 'XP' },
    { field: 'monedas', headerName: 'Monedas' },
    { field: 'racha', headerName: 'Racha 🔥' },
    {
      headerName: 'Acciones', sortable: false, filter: false, flex: 0, width: 170, minWidth: 170,
      cellRenderer: () =>
        `<button class="gbtn" data-action="detail" title="Ver avance" aria-label="Ver avance">👁️</button>
         <button class="gbtn" data-action="edit" title="Editar" aria-label="Editar">✏️</button>
         <button class="gbtn danger" data-action="delete" title="Eliminar" aria-label="Eliminar">🗑️</button>`
    }
  ];

  constructor(private api: ApiService, public auth: AuthService) {}

  get isAdmin(): boolean { return this.auth.currentUser?.rol === 'admin'; }

  ngOnInit(): void { this.loadAll(); }

  loadAll() {
    this.api.getUsers().subscribe({
      next: (users) => this.rowData = users,
      error: () => this.errorMessage = 'No se pudo cargar la lista de usuarios.'
    });
    this.api.getStats().subscribe({ next: (s) => this.stats = s, error: () => {} });
    this.api.getExercises().subscribe({ next: (e) => this.exercises = e, error: () => {} });
  }

  maxRetos(): number { return Math.max(1, ...(this.stats?.retos || []).map((r: any) => r.completados)); }

  private notify(text: string, isError = false) {
    this.message = isError ? '' : text;
    this.errorMessage = isError ? text : '';
    setTimeout(() => { this.message = ''; this.errorMessage = ''; }, 5000);
  }

  onGridReady(event: GridReadyEvent) {
    event.api.sizeColumnsToFit();
    window.addEventListener('resize', () => setTimeout(() => event.api.sizeColumnsToFit()));
  }

  onCellClicked(e: CellClickedEvent) {
    const btn = (e.event?.target as HTMLElement | null)?.closest('button');
    const action = btn?.dataset['action'];
    if (!action) { return; }
    const user = e.data as User;
    if (action === 'detail') { this.api.getUserDetail(user.id).subscribe(d => this.detail = d); }
    if (action === 'edit') { this.editUser = { ...user }; }
    if (action === 'delete') { this.deleteUser(user); }
  }

  closeEdit(open: boolean) { if (!open) { this.editUser = null; } }
  closeDetail(open: boolean) { if (!open) { this.detail = null; } }
  closeExercise(open: boolean) { if (!open) { this.editExercise = null; } }
  openExercise(ex: any) {
    this.editExercise = { id: ex.id, titulo: ex.titulo, descripcion: ex.descripcion, ejemplo_codigo: ex.ejemplo_codigo,
      respuesta_correcta: ex.respuesta_correcta, xp_recompensa: ex.xp_recompensa, nivel_requerido: ex.nivel_requerido };
  }

  // ---- usuarios ----
  saveUser() {
    const u = this.editUser;
    const body: any = { nombre: u.nombre, nivel: +u.nivel, xp: +u.xp, monedas: +u.monedas };
    if (this.isAdmin) { body.rol = u.rol; }
    this.api.updateUser(u.id, body).subscribe({
      next: () => { this.editUser = null; this.notify('Cambios guardados ✅'); this.loadAll(); },
      error: (e) => this.notify(e.error?.detail || 'No se pudo guardar', true)
    });
  }

  deleteUser(user: User) {
    if (!confirm(`¿Eliminar a ${user.nombre}? Se borrará también su progreso. Esta acción no se puede deshacer.`)) { return; }
    this.api.deleteUser(user.id).subscribe({
      next: () => { this.notify('Usuario eliminado 🗑️'); this.loadAll(); },
      error: (e) => this.notify(e.error?.detail || 'No se pudo eliminar', true)
    });
  }

  // ---- retos ----
  newExercise() { this.editExercise = { ...EMPTY_EXERCISE }; }

  saveExercise() {
    const { id, ...body } = this.editExercise;
    body.xp_recompensa = +body.xp_recompensa;
    body.nivel_requerido = +body.nivel_requerido;
    const req = id ? this.api.updateExercise(id, body) : this.api.createExercise(body);
    req.subscribe({
      next: () => { this.editExercise = null; this.notify('Reto guardado ✅'); this.loadAll(); },
      error: (e) => this.notify(typeof e.error?.detail === 'string' ? e.error.detail : 'Revisa los campos del reto', true)
    });
  }

  deleteExercise(ex: any) {
    if (!confirm(`¿Eliminar el reto "${ex.titulo}"? Se borrará el progreso asociado.`)) { return; }
    this.api.deleteExercise(ex.id).subscribe({
      next: () => { this.notify('Reto eliminado 🗑️'); this.loadAll(); },
      error: (e) => this.notify(e.error?.detail || 'No se pudo eliminar', true)
    });
  }

  // ---- reporte CSV real ----
  exportData() {
    const head = ['ID', 'Nombre', 'Correo', 'Rol', 'Nivel', 'XP', 'Monedas', 'Racha'];
    const esc = (v: any) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const rows = this.rowData.map(u => [u.id, u.nombre, u.email, u.rol, u.nivel, u.xp, u.monedas, u.racha].map(esc).join(','));
    const csv = '\ufeff' + [head.map(esc).join(','), ...rows].join('\n'); // BOM: Excel respeta las tildes
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    a.download = `reporte_pycods_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }
}
