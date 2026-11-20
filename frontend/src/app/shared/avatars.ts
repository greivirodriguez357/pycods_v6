export interface Avatar { id: string; name: string; icon: string; }

export const AVATARS: Avatar[] = [
  { id: 'avatar1', name: 'Monstruo Azul', icon: '🤖' },
  { id: 'avatar2', name: 'Guerrero', icon: '⚔️' },
  { id: 'avatar3', name: 'Princesa', icon: '👑' },
  { id: 'avatar4', name: 'Dragón Sabio', icon: '🐉' }
];

export function avatarIcon(id: string | null | undefined): string {
  return AVATARS.find(a => a.id === id)?.icon ?? '🤖';
}

/** Foto de perfil subida por el usuario: el backend guarda "foto:archivo.jpg". */
export function isPhoto(id: string | null | undefined): boolean {
  return !!id && id.startsWith('foto:');
}
export function photoUrl(id: string | null | undefined): string {
  return isPhoto(id) ? '/api/uploads/' + id!.slice(5) : '';
}
