import Fastify from 'fastify';
import { initDb } from './db/database.js';
import { registerRoutes } from './routes/index.js';

const app = Fastify({ logger: true });
initDb();
await registerRoutes(app);
await app.listen({ port: 8080, host: '0.0.0.0' });
console.log('API running on http://localhost:8080');