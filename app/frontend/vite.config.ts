import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load environment variables
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@common': path.resolve(__dirname, 'src/common'),
        '@features': path.resolve(__dirname, 'src/features'),
        '@assets': path.resolve(__dirname, 'src/assets'),
      },
    },
    server: {
      port: Number(env.VITE_PORT) || 3000,
      host: '0.0.0.0',
      https: false,
      strictPort: true,
      allowedHosts: ['prozeal.athenas.co.in', 'localhost'],
      proxy: env.VITE_API_PROXY_TARGET ? {
        '/api': {
          target: env.VITE_API_PROXY_TARGET,
          changeOrigin: true,
          secure: env.VITE_API_PROXY_SECURE === 'true',
        },
        '/authentication': {
          target: env.VITE_API_PROXY_TARGET,
          changeOrigin: true,
          secure: env.VITE_API_PROXY_SECURE === 'true',
        },
      } : undefined,
    },
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
      minify: mode === 'production',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            antd: ['antd'],
            router: ['react-router-dom'],
          },
        },
      },
    },
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },
  };
});
