# Pycods móvil (Expo Go)

App móvil de Pycods (React Native + Expo). Usa **el mismo backend FastAPI** (puerto 8001) que la versión web.

## 1. Requisitos
- Node.js 20 o superior en tu PC.
- La app **Expo Go** en el celular.
- PC y celular en **la misma red Wi-Fi**.
- El backend encendido: `docker compose up -d` (desde la carpeta raíz del proyecto).

## 2. Instalar y arrancar (dentro de la carpeta `mobile`)
```bash
npm install
npm run setup     # instala las librerías con las versiones correctas para Expo
npm start
```
Se muestra un código QR:
- **Android:** abre Expo Go y toca "Scan QR code".
- **iPhone:** escanéalo con la cámara y ábrelo en Expo Go.

La app detecta sola la IP de tu PC y se conecta al puerto 8001.

## 3. Si Expo Go dice "versión de SDK incompatible"
Expo Go solo abre proyectos de su misma versión de SDK. El mensaje te dice cuál necesita (por ejemplo 57). Ajusta el proyecto:
```bash
npx expo install expo@^57.0.0 --fix
npm start -- --clear
```
(cambia 57 por el número que te indique).

## 4. Si no inicia sesión o dice que no se conecta
1. Prueba en el navegador del celular: `http://IP_DE_TU_PC:8001/health`. Debe mostrar `{"status":"ok"}`.
   Tu IP la ves en Windows con `ipconfig` (IPv4, por ejemplo 192.168.1.20).
2. Si no abre: firewall de Windows (permite Node.js y Docker en redes privadas) o una red Wi-Fi que aísla dispositivos (redes de invitados, universidades).
3. Si la IP no se detecta sola (o usas `npm run tunnel`), crea un archivo `.env` en `mobile/`:
   ```
   EXPO_PUBLIC_API_URL=http://192.168.1.20:8001
   ```
   y reinicia con `npm start -- --clear`.

## 5. Recordatorios y foto de perfil
- **Foto:** en la pestaña ⭐ Yo hay botones de Cámara y Galería (Expo Go pide permiso la primera vez).
- **Recordatorio diario (6:00 pm):** es una notificación local. En Expo Go para Android puede aparecer un aviso sobre
  notificaciones push remotas; no afecta, porque la app solo usa recordatorios locales.

## 6. Qué trae
Registro, inicio de sesión y recuperar contraseña · foto de perfil · racha con recordatorio · escribir código que se ejecuta de verdad · panel para docentes (pestaña 📊) · rutina visual "Primero / Luego" · chequeo de emociones · retos con
opción múltiple y "ordena el código" (toca los bloques) · voz guía · juego de parejas ·
Mi Monstruo con tienda de monedas · respiración guiada · stickers de logros · **Modo calma**.
