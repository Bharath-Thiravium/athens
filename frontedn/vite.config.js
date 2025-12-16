import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@common': path.resolve(__dirname, 'src/common'),
            '@features': path.resolve(__dirname, 'src/features'),
        },
    },
    server: {
        proxy: {
            '/authentication': {
                target: 'http://35.154.206.54:82',
                changeOrigin: true,
                secure: false,
            },
        },
    },
});
