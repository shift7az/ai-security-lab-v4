/**
 * AI Security Lab v5.0 - Mediasoup WebRTC Server
 *
 * Provides low-latency (<300ms) live video streaming using WebRTC.
 * Replaces traditional RTSP/HLS with modern SFU architecture.
 */

import express from 'express';
import { Server as SocketIOServer } from 'socket.io';
import { createServer } from 'http';
import * as mediasoup from 'mediasoup';
import type { Worker, Router, WebRtcTransport } from 'mediasoup/node/lib/types';

const app = express();
const httpServer = createServer(app);
const io = new SocketIOServer(httpServer, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
  },
});

// Configuration
const config = {
  worker: {
    rtcMinPort: 40000,
    rtcMaxPort: 49999,
    logLevel: 'warn' as const,
    logTags: ['info', 'ice', 'dtls', 'rtp', 'srtp', 'rtcp'] as const,
  },
  router: {
    mediaCodecs: [
      {
        kind: 'audio' as const,
        mimeType: 'audio/opus',
        clockRate: 48000,
        channels: 2,
      },
      {
        kind: 'video' as const,
        mimeType: 'video/VP8',
        clockRate: 90000,
        parameters: {
          'x-google-start-bitrate': 1000,
        },
      },
      {
        kind: 'video' as const,
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

/**
 * Mediasoup Service
 * Manages workers, routers, and transports
 */
class MediasoupService {
  private workers: Worker[] = [];
  private routers: Map<string, Router> = new Map();
  private transports: Map<string, WebRtcTransport> = new Map();

  async initialize(): Promise<void> {
    console.log('🚀 Initializing Mediasoup Service...');

    // Create workers (one per CPU core for load balancing)
    const numWorkers = require('os').cpus().length;
    console.log(`Creating ${numWorkers} Mediasoup workers...`);

    for (let i = 0; i < numWorkers; i++) {
      const worker = await mediasoup.createWorker({
        ...config.worker,
        rtcMinPort: 40000 + i * 1000,
        rtcMaxPort: 40000 + i * 1000 + 999,
      });

      worker.on('died', () => {
        console.error(`❌ Mediasoup worker ${i} died, exiting...`);
        process.exit(1);
      });

      this.workers.push(worker);
      console.log(`✅ Worker ${i + 1}/${numWorkers} created (PID: ${worker.pid})`);
    }

    console.log(`✅ Mediasoup initialized with ${numWorkers} workers`);
  }

  async getOrCreateRouter(roomId: string): Promise<Router> {
    let router = this.routers.get(roomId);

    if (!router) {
      // Round-robin worker selection
      const worker = this.workers[this.routers.size % this.workers.length];
      router = await worker.createRouter({
        mediaCodecs: config.router.mediaCodecs,
      });

      this.routers.set(roomId, router);
      console.log(`✅ Router created for room: ${roomId}`);
    }

    return router;
  }

  async createWebRtcTransport(router: Router, transportId: string): Promise<WebRtcTransport> {
    const transport = await router.createWebRtcTransport(config.webRtcTransport);
    this.transports.set(transportId, transport);

    transport.on('dtlsstatechange', (dtlsState) => {
      if (dtlsState === 'closed') {
        transport.close();
        this.transports.delete(transportId);
      }
    });

    return transport;
  }

  getTransport(transportId: string): WebRtcTransport | undefined {
    return this.transports.get(transportId);
  }

  getStats(): object {
    return {
      workers: this.workers.length,
      routers: this.routers.size,
      transports: this.transports.size,
    };
  }
}

// Initialize service
const mediasoupService = new MediasoupService();

// Express routes
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'mediasoup-server',
    stats: mediasoupService.getStats(),
    timestamp: new Date().toISOString(),
  });
});

app.get('/stats', (req, res) => {
  res.json({
    stats: mediasoupService.getStats(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
  });
});

// Socket.IO event handlers
io.on('connection', (socket) => {
  console.log(`🔌 Client connected: ${socket.id}`);

  // Get router RTP capabilities
  socket.on('getRouterRtpCapabilities', async (data: { roomId: string }, callback) => {
    try {
      const { roomId } = data;
      const router = await mediasoupService.getOrCreateRouter(roomId);

      callback({ rtpCapabilities: router.rtpCapabilities });
    } catch (error: any) {
      console.error('❌ Error getting router capabilities:', error);
      callback({ error: error.message });
    }
  });

  // Create WebRTC transport
  socket.on('createWebRtcTransport', async (data: { roomId: string; direction: string }, callback) => {
    try {
      const { roomId, direction } = data;
      const router = await mediasoupService.getOrCreateRouter(roomId);
      const transportId = `${socket.id}-${direction}`;

      const transport = await mediasoupService.createWebRtcTransport(router, transportId);

      callback({
        id: transport.id,
        iceParameters: transport.iceParameters,
        iceCandidates: transport.iceCandidates,
        dtlsParameters: transport.dtlsParameters,
      });
    } catch (error: any) {
      console.error('❌ Error creating transport:', error);
      callback({ error: error.message });
    }
  });

  // Connect transport
  socket.on('connectWebRtcTransport', async (data: { transportId: string; dtlsParameters: any }, callback) => {
    try {
      const { transportId, dtlsParameters } = data;
      const transport = mediasoupService.getTransport(transportId);

      if (!transport) {
        throw new Error('Transport not found');
      }

      await transport.connect({ dtlsParameters });
      callback({ connected: true });
    } catch (error: any) {
      console.error('❌ Error connecting transport:', error);
      callback({ error: error.message });
    }
  });

  socket.on('disconnect', () => {
    console.log(`🔌 Client disconnected: ${socket.id}`);
    // TODO: Clean up transports, producers, consumers for this client
  });
});

// Start server
const PORT = process.env.PORT || 3001;

(async () => {
  try {
    await mediasoupService.initialize();

    httpServer.listen(PORT, () => {
      console.log(`🚀 Mediasoup server running on port ${PORT}`);
      console.log(`   Health: http://localhost:${PORT}/health`);
      console.log(`   Stats: http://localhost:${PORT}/stats`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
})();

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n⏹️  Shutting down gracefully...');
  httpServer.close();
  process.exit(0);
});
