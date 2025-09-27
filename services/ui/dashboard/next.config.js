/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost'],
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/intelligence/:path*',
        destination: 'http://ai-orchestrator:8000/api/:path*',
      },
      {
        source: '/api/threats/:path*',
        destination: 'http://threat-detector:8001/api/:path*',
      },
      {
        source: '/api/frigate/:path*',
        destination: 'http://frigate:5000/api/:path*',
      },
    ];
  },
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };
    return config;
  },
};

module.exports = nextConfig;
