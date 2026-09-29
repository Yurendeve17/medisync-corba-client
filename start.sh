#!/bin/sh

set -e

export DISPLAY=:99

echo "======================================"
echo " Iniciando MediSync CORBA Client"
echo "======================================"

# Limpar locks antigos do X11
echo "Limpando locks antigos do X11..."

rm -f /tmp/.X99-lock
rm -rf /tmp/.X11-unix/X99

echo "A iniciar display virtual..."

Xvfb :99 -screen 0 1280x800x24 -ac +extension GLX +render -noreset &

XVFB_PID=$!

# Garantir que o Xvfb morreu se o script terminar
trap 'kill $XVFB_PID 2>/dev/null || true' EXIT

echo "Aguardando Xvfb..."

sleep 2

# Verificar se o X realmente iniciou
if ! xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "ERRO: Xvfb nÃ£o conseguiu iniciar no display :99"
    exit 1
fi

echo "Display :99 iniciado com sucesso."

xsetroot -solid "#0f172a"

echo "A iniciar window manager..."

fluxbox &

sleep 2

echo "A iniciar VNC..."

x11vnc \
    -display :99 \
    -forever \
    -shared \
    -nopw \
    -rfbport 5900 \
    -listen 0.0.0.0 &

echo "A iniciar noVNC..."

websockify \
    --web=/usr/share/novnc \
    6080 \
    localhost:5900 &

echo "======================================"
echo " MediSync iniciado"
echo " Display: :99"
echo " VNC: 5900"
echo " noVNC: 6080"
echo "======================================"

echo "A iniciar MediSync..."

exec python src/main.py
