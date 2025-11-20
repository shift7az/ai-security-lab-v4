# WebRTC Live Streaming Implementation Guide

## 🎯 Goal: Replace RTSP/HLS with Low-Latency WebRTC

**Timeline**: 3-4 weeks
**Benefit**: Sub-300ms latency (vs 3-5 seconds with RTSP/HLS)
**Complexity**: Medium-High

---

## 📐 Architecture

### Current State (RTSP/HLS)
```
Cameras → Frigate → RTSP Stream → HLS Transcoding → Dashboard
                                   (3-5 second delay)
```

### Target State (WebRTC)
```
Cameras → Frigate → WebRTC SFU → Dashboard/Mobile
                    (Mediasoup)   (<300ms delay)
```

---

## 🏗️ Technical Architecture

### Option 1: Mediasoup (Recommended)
**Pros**:
- Modern, performant SFU (Selective Forwarding Unit)
- Low latency (<300ms)
- Built on libuv (Node.js)
- Excellent scalability
- Active development

**Cons**:
- Requires Node.js service
- More complex setup

### Option 2: Janus Gateway
**Pros**:
- Mature, battle-tested
- C-based (very fast)
- Plugin architecture

**Cons**:
- Older codebase
- More complex configuration

### Decision: **Mediasoup** ✅

---

## 📦 Components

### 1. Mediasoup Server (New Service)
WebRTC Selective Forwarding Unit

**Location**: `services/streaming/mediasoup-server/`

**Responsibilities**:
- WebRTC signaling (SDP offer/answer)
- Media routing (forward streams to clients)
- TURN/STUN server integration
- Bandwidth adaptation
- Recording capabilities

### 2. Frigate Integration
Bridge between RTSP and WebRTC

**Responsibilities**:
- Convert RTSP to WebRTC
- Feed streams to Mediasoup
- Handle reconnections

### 3. Frontend Client
WebRTC player in dashboard

**Responsibilities**:
- WebRTC peer connection
- Stream rendering
- Controls (play/pause/mute)
- Error handling

---

## 🚀 Implementation Plan

### Week 1: Mediasoup Server Setup

#### Day 1-2: Initialize Mediasoup Service

**Create service structure**:
```bash
mkdir -p services/streaming/mediasoup-server
cd services/streaming/mediasoup-server

npm init -y
npm install mediasoup express socket.io cors
npm install --save-dev typescript @types/node @types/express ts-node
```

**src/server.ts**:
```typescript
import express from 'express';
import { Server as SocketIOServer } from 'socket.io';
import { createServer } from 'http';
import * as mediasoup from 'mediasoup';
import { Worker, Router, WebRtcTransport, Producer, Consumer } from 'mediasoup/node/lib/types';

const app = express();
const httpServer = createServer(app);
const io = new SocketIOServer(httpServer, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
  },
});

// Mediasoup configuration
const mediasoupConfig = {
  worker: {
    rtcMinPort: 40000,
    rtcMaxPort: 49999,
    logLevel: 'warn',
    logTags: ['info', 'ice', 'dtls', 'rtp', 'srtp', 'rtcp'],
  },
  router: {
    mediaCodecs: [
      {
        kind: 'audio',
        mimeType: 'audio/opus',
        clockRate: 48000,
        channels: 2,
      },
      {
        kind: 'video',
        mimeType: 'video/VP8',
        clockRate: 90000,
        parameters: {
          'x-google-start-bitrate': 1000,
        },
      },
      {
        kind: 'video',
        mimeType: 'video/H264',
        clockRate: 90000,
        parameters: {
          'packetization-mode': 1,
          'profile-level-id': '42e01f',
          'level-asymmetry-allowed': 1,
        },
      },
    ],
  },
  webRtcTransport: {
    listenIps: [
      {
        ip: '0.0.0.0',
        announcedIp: process.env.ANNOUNCED_IP || '127.0.0.1',
      },
    ],
    enableUdp: true,
    enableTcp: true,
    preferUdp: true,
    initialAvailableOutgoingBitrate: 1000000,
    minimumAvailableOutgoingBitrate: 600000,
    maxSctpMessageSize: 262144,
  },
};

class MediasoupService {
  private workers: Worker[] = [];
  private routers: Map<string, Router> = new Map();
  private transports: Map<string, WebRtcTransport> = new Map();
  private producers: Map<string, Producer> = new Map();
  private consumers: Map<string, Consumer> = new Map();

  async initialize() {
    console.log('🚀 Initializing Mediasoup...');

    // Create workers (one per CPU core)
    const numWorkers = require('os').cpus().length;
    for (let i = 0; i < numWorkers; i++) {
      const worker = await mediasoup.createWorker({
        ...mediasoupConfig.worker,
        rtcMinPort: 40000 + i * 1000,
        rtcMaxPort: 40000 + i * 1000 + 999,
      });

      worker.on('died', () => {
        console.error('❌ Mediasoup worker died, exiting...');
        process.exit(1);
      });

      this.workers.push(worker);
      console.log(`✅ Worker ${i + 1} created (PID: ${worker.pid})`);
    }

    console.log(`✅ ${numWorkers} Mediasoup workers initialized`);
  }

  async createRouter(roomId: string): Promise<Router> {
    // Round-robin worker selection
    const worker = this.workers[this.routers.size % this.workers.length];
    const router = await worker.createRouter({
      mediaCodecs: mediasoupConfig.router.mediaCodecs,
    });

    this.routers.set(roomId, router);
    console.log(`✅ Router created for room: ${roomId}`);
    return router;
  }

  async createWebRtcTransport(
    router: Router,
    clientId: string
  ): Promise<WebRtcTransport> {
    const transport = await router.createWebRtcTransport(
      mediasoupConfig.webRtcTransport
    );

    this.transports.set(clientId, transport);

    return transport;
  }

  getRouter(roomId: string): Router | undefined {
    return this.routers.get(roomId);
  }

  getTransport(clientId: string): WebRtcTransport | undefined {
    return this.transports.get(clientId);
  }
}

const mediasoupService = new MediasoupService();

// Socket.IO event handlers
io.on('connection', (socket) => {
  console.log(`🔌 Client connected: ${socket.id}`);

  // Get router capabilities
  socket.on('getRouterRtpCapabilities', async (data, callback) => {
    const { roomId } = data;
    let router = mediasoupService.getRouter(roomId);

    if (!router) {
      router = await mediasoupService.createRouter(roomId);
    }

    callback({ rtpCapabilities: router.rtpCapabilities });
  });

  // Create WebRTC transport
  socket.on('createWebRtcTransport', async (data, callback) => {
    const { roomId, direction } = data; // direction: 'send' or 'recv'
    const router = mediasoupService.getRouter(roomId);

    if (!router) {
      callback({ error: 'Router not found' });
      return;
    }

    try {
      const transport = await mediasoupService.createWebRtcTransport(
        router,
        socket.id + '-' + direction
      );

      callback({
        id: transport.id,
        iceParameters: transport.iceParameters,
        iceCandidates: transport.iceCandidates,
        dtlsParameters: transport.dtlsParameters,
      });
    } catch (error) {
      console.error('❌ Error creating transport:', error);
      callback({ error: error.message });
    }
  });

  // Connect transport
  socket.on('connectWebRtcTransport', async (data, callback) => {
    const { transportId, dtlsParameters } = data;
    const transport = mediasoupService.getTransport(transportId);

    if (!transport) {
      callback({ error: 'Transport not found' });
      return;
    }

    try {
      await transport.connect({ dtlsParameters });
      callback({ connected: true });
    } catch (error) {
      callback({ error: error.message });
    }
  });

  // Produce media (camera streams)
  socket.on('produce', async (data, callback) => {
    const { transportId, kind, rtpParameters } = data;
    const transport = mediasoupService.getTransport(transportId);

    if (!transport) {
      callback({ error: 'Transport not found' });
      return;
    }

    try {
      const producer = await transport.produce({ kind, rtpParameters });
      callback({ id: producer.id });
    } catch (error) {
      callback({ error: error.message });
    }
  });

  // Consume media (viewer receives stream)
  socket.on('consume', async (data, callback) => {
    const { transportId, producerId, rtpCapabilities } = data;
    const transport = mediasoupService.getTransport(transportId);

    if (!transport) {
      callback({ error: 'Transport not found' });
      return;
    }

    const router = mediasoupService.getRouter(data.roomId);

    if (!router || !router.canConsume({ producerId, rtpCapabilities })) {
      callback({ error: 'Cannot consume' });
      return;
    }

    try {
      const consumer = await transport.consume({
        producerId,
        rtpCapabilities,
        paused: true,
      });

      callback({
        id: consumer.id,
        producerId,
        kind: consumer.kind,
        rtpParameters: consumer.rtpParameters,
      });
    } catch (error) {
      callback({ error: error.message });
    }
  });

  socket.on('disconnect', () => {
    console.log(`🔌 Client disconnected: ${socket.id}`);
    // Clean up transports, producers, consumers
  });
});

// Start server
(async () => {
  await mediasoupService.initialize();

  const PORT = process.env.PORT || 3001;
  httpServer.listen(PORT, () => {
    console.log(`🚀 Mediasoup server running on port ${PORT}`);
  });
})();
```

**package.json**:
```json
{
  "name": "mediasoup-server",
  "version": "1.0.0",
  "scripts": {
    "dev": "ts-node src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js"
  },
  "dependencies": {
    "mediasoup": "^3.13.0",
    "express": "^4.18.0",
    "socket.io": "^4.6.0",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0",
    "@types/express": "^4.17.0",
    "ts-node": "^10.9.0"
  }
}
```

**tsconfig.json**:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

**Dockerfile**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3001
EXPOSE 40000-49999/udp

CMD ["npm", "start"]
```

---

### Week 2: RTSP to WebRTC Bridge

#### FFmpeg RTSP to RTP Bridge

**services/streaming/rtsp-bridge/bridge.py**:
```python
"""
RTSP to RTP bridge for feeding Mediasoup
Converts RTSP camera streams to RTP for WebRTC consumption
"""

import asyncio
import subprocess
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RTSPBridge:
    """Bridge between RTSP cameras and WebRTC (Mediasoup)."""

    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}

    async def start_camera_stream(
        self,
        camera_id: str,
        rtsp_url: str,
        rtp_host: str = "localhost",
        rtp_port: int = 5004
    ):
        """
        Start streaming from RTSP to RTP.

        Args:
            camera_id: Unique camera identifier
            rtsp_url: RTSP stream URL
            rtp_host: RTP destination host
            rtp_port: RTP destination port
        """

        if camera_id in self.processes:
            logger.warning(f"Stream already running for camera: {camera_id}")
            return

        # FFmpeg command to convert RTSP to RTP
        cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-b:v", "1M",
            "-maxrate", "1M",
            "-bufsize", "2M",
            "-pix_fmt", "yuv420p",
            "-g", "30",
            "-keyint_min", "30",
            "-c:a", "libopus",
            "-b:a", "128k",
            "-f", "rtp",
            f"rtp://{rtp_host}:{rtp_port}",
        ]

        logger.info(f"Starting RTSP bridge for camera: {camera_id}")
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            self.processes[camera_id] = process
            logger.info(f"✅ Stream started for camera: {camera_id}")

            # Monitor process in background
            asyncio.create_task(self._monitor_process(camera_id, process))

        except Exception as e:
            logger.error(f"❌ Failed to start stream for {camera_id}: {e}")
            raise

    async def _monitor_process(self, camera_id: str, process: subprocess.Popen):
        """Monitor FFmpeg process and restart if it crashes."""

        while True:
            await asyncio.sleep(5)

            if process.poll() is not None:
                logger.error(f"❌ Stream crashed for camera: {camera_id}")
                # TODO: Implement auto-restart logic
                del self.processes[camera_id]
                break

    async def stop_camera_stream(self, camera_id: str):
        """Stop streaming for a camera."""

        process = self.processes.get(camera_id)
        if not process:
            logger.warning(f"No stream found for camera: {camera_id}")
            return

        logger.info(f"Stopping stream for camera: {camera_id}")
        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning(f"Force killing stream for camera: {camera_id}")
            process.kill()

        del self.processes[camera_id]
        logger.info(f"✅ Stream stopped for camera: {camera_id}")

    async def stop_all_streams(self):
        """Stop all active streams."""

        camera_ids = list(self.processes.keys())
        for camera_id in camera_ids:
            await self.stop_camera_stream(camera_id)
```

---

### Week 3: Frontend WebRTC Client

#### React Component for Live Stream

**dashboard/src/components/WebRTCPlayer.tsx**:
```typescript
import React, { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { Device } from 'mediasoup-client';

interface WebRTCPlayerProps {
  cameraId: string;
  roomId: string;
  mediasoupUrl: string;
}

export const WebRTCPlayer: React.FC<WebRTCPlayerProps> = ({
  cameraId,
  roomId,
  mediasoupUrl,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [device, setDevice] = useState<Device | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initWebRTC = async () => {
      try {
        // Connect to Mediasoup server
        const newSocket = io(mediasoupUrl, {
          transports: ['websocket'],
        });

        setSocket(newSocket);

        // Wait for connection
        await new Promise((resolve) => {
          newSocket.on('connect', resolve);
        });

        console.log('✅ Connected to Mediasoup server');

        // Get router capabilities
        const { rtpCapabilities } = await new Promise((resolve, reject) => {
          newSocket.emit('getRouterRtpCapabilities', { roomId }, (response) => {
            if (response.error) {
              reject(response.error);
            } else {
              resolve(response);
            }
          });
        });

        // Create device
        const newDevice = new Device();
        await newDevice.load({ routerRtpCapabilities: rtpCapabilities });
        setDevice(newDevice);

        console.log('✅ Device loaded');

        // Create receive transport
        const transportInfo = await new Promise((resolve, reject) => {
          newSocket.emit(
            'createWebRtcTransport',
            { roomId, direction: 'recv' },
            (response) => {
              if (response.error) {
                reject(response.error);
              } else {
                resolve(response);
              }
            }
          );
        });

        const recvTransport = newDevice.createRecvTransport(transportInfo);

        // Connect transport
        recvTransport.on('connect', async ({ dtlsParameters }, callback, errback) => {
          try {
            await new Promise((resolve, reject) => {
              newSocket.emit(
                'connectWebRtcTransport',
                {
                  transportId: recvTransport.id,
                  dtlsParameters,
                },
                (response) => {
                  if (response.error) {
                    reject(response.error);
                  } else {
                    resolve(response);
                  }
                }
              );
            });

            callback();
          } catch (error) {
            errback(error);
          }
        });

        console.log('✅ Receive transport created');

        // Consume stream
        // TODO: Get producer ID from server
        const producerId = 'camera-' + cameraId;

        const consumerInfo = await new Promise((resolve, reject) => {
          newSocket.emit(
            'consume',
            {
              roomId,
              transportId: recvTransport.id,
              producerId,
              rtpCapabilities: newDevice.rtpCapabilities,
            },
            (response) => {
              if (response.error) {
                reject(response.error);
              } else {
                resolve(response);
              }
            }
          );
        });

        const consumer = await recvTransport.consume(consumerInfo);

        // Attach stream to video element
        if (videoRef.current) {
          const stream = new MediaStream();
          stream.addTrack(consumer.track);
          videoRef.current.srcObject = stream;
          videoRef.current.play();
          setIsPlaying(true);
        }

        console.log('✅ Stream playing');
      } catch (err) {
        console.error('❌ WebRTC error:', err);
        setError(err.message);
      }
    };

    initWebRTC();

    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, [cameraId, roomId, mediasoupUrl]);

  return (
    <div className="webrtc-player">
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        style={{
          width: '100%',
          height: 'auto',
          backgroundColor: '#000',
        }}
      />

      <div className="controls">
        <button onClick={() => videoRef.current?.play()}>
          {isPlaying ? '⏸ Pause' : '▶ Play'}
        </button>
        <button onClick={() => videoRef.current?.requestFullscreen()}>
          ⛶ Fullscreen
        </button>
      </div>
    </div>
  );
};
```

**Install dependencies**:
```bash
cd dashboard
npm install socket.io-client mediasoup-client
```

---

### Week 4: Integration & Testing

#### Docker Compose Integration

**docker/compose/docker-compose.yml** (add):
```yaml
  mediasoup-server:
    <<: *common
    build: ./services/streaming/mediasoup-server
    container_name: mediasoup-server
    environment:
      ANNOUNCED_IP: ${PUBLIC_IP:-127.0.0.1}
      NODE_ENV: production
    ports:
      - "3001:3001"
      - "40000-40100:40000-40100/udp"  # RTP ports
    networks:
      - security-network

  rtsp-bridge:
    <<: *common
    build: ./services/streaming/rtsp-bridge
    container_name: rtsp-bridge
    environment:
      MEDIASOUP_HOST: mediasoup-server
      MEDIASOUP_PORT: 3001
    depends_on:
      - mediasoup-server
    networks:
      - security-network
```

#### Testing Script

**test-webrtc.sh**:
```bash
#!/bin/bash

echo "🧪 Testing WebRTC Streaming..."

# 1. Check Mediasoup server
echo "1. Checking Mediasoup server..."
curl -f http://localhost:3001/health || echo "❌ Mediasoup server not responding"

# 2. Test Socket.IO connection
echo "2. Testing Socket.IO connection..."
# TODO: Add Socket.IO test

# 3. Test RTSP bridge
echo "3. Testing RTSP bridge..."
docker logs rtsp-bridge | tail -n 20

# 4. Check RTP ports
echo "4. Checking RTP ports (40000-40100)..."
netstat -an | grep -E ":(4000[0-9]|401[0-9][0-9])" | head -n 5

echo "✅ WebRTC test complete"
```

---

## 📊 Performance Benchmarks

### Target Metrics
- **Latency**: <300ms (glass-to-glass)
- **Bitrate**: 1-2 Mbps per stream
- **CPU Usage**: <20% per stream
- **Concurrent Viewers**: 50+ per camera
- **FPS**: 25-30 FPS

### Testing Plan
```bash
# Load test with multiple viewers
npm install -g artillery

# artillery.yml
config:
  target: 'http://localhost:3001'
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Ramp up"
    - duration: 300
      arrivalRate: 50
      name: "Sustained load"

scenarios:
  - name: "WebRTC viewer"
    engine: socketio
    flow:
      - emit:
          channel: "getRouterRtpCapabilities"
          data:
            roomId: "camera-entrance-01"
      - think: 1
      - emit:
          channel: "createWebRtcTransport"
          data:
            roomId: "camera-entrance-01"
            direction: "recv"

# Run test
artillery run artillery.yml
```

---

## 🔒 Security Considerations

### 1. TURN Server (NAT Traversal)
```yaml
# docker-compose.yml
  coturn:
    image: coturn/coturn:latest
    container_name: coturn
    network_mode: host
    environment:
      TURNSERVER_ENABLED: 1
      TURN_USERNAME: ${TURN_USERNAME}
      TURN_PASSWORD: ${TURN_PASSWORD}
      REALM: ${DOMAIN}
    command:
      - "-n"
      - "--log-file=stdout"
      - "--external-ip=${PUBLIC_IP}"
      - "--listening-port=3478"
      - "--min-port=49152"
      - "--max-port=65535"
      - "--realm=${DOMAIN}"
      - "--user=${TURN_USERNAME}:${TURN_PASSWORD}"
```

### 2. Encryption
- WebRTC uses DTLS-SRTP (encrypted by default)
- Signaling over WSS (WebSocket Secure)
- TURN over TLS

### 3. Authentication
- Validate JWT tokens before allowing stream access
- Per-camera access control
- Rate limiting on connections

---

## 🎯 Success Criteria

- [ ] Latency <300ms measured
- [ ] Supports 50+ concurrent viewers per camera
- [ ] Works on mobile browsers (iOS Safari, Android Chrome)
- [ ] Graceful fallback to HLS if WebRTC fails
- [ ] CPU usage <20% per stream
- [ ] Zero packet loss under normal conditions
- [ ] Automatic reconnection on network issues

---

## 📚 Next Steps

1. **Week 1**: Set up Mediasoup server ✅
2. **Week 2**: Implement RTSP bridge ✅
3. **Week 3**: Build frontend player ✅
4. **Week 4**: Integration testing & optimization ✅

---

**Start now with Week 1 setup! 🚀**
