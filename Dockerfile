FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libegl1 \
    libglib2.0-0 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libfontconfig1 \
    libdbus-1-3 \
    tzdata \
    xvfb \
    x11vnc \
    novnc \
    fluxbox \
    x11-xserver-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --timeout 300 --retries 10 -r requirements.txt

COPY . .

RUN sed -i 's/\r$//' start.sh && \
    sed -i '1s/^\xEF\xBB\xBF//' start.sh && \
    chmod +x start.sh

CMD ["./start.sh"]
