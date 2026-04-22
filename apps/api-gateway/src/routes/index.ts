import { FastifyInstance } from 'fastify';
import { z } from 'zod';
import * as sched from '../services/scheduling.js';

export async function registerRoutes(app: FastifyInstance) {
  app.get('/health', async () => ({ ok: true }));

  app.get('/slots/search', async (req) => {
    const q = z.object({ doctorId: z.string().optional(), clinicId: z.string().optional(), date: z.string().optional() }).parse(req.query);
    return sched.searchSlots(q);
  });

  app.post('/appointments/hold', async (req) => {
    const b = z.object({ slotId: z.string(), patientId: z.string(), ttlSeconds: z.number().default(90) }).parse(req.body);
    return sched.holdSlot(b.slotId, b.patientId, b.ttlSeconds);
  });

  app.post('/appointments/book', async (req) => {
    const b = z.object({ holdId: z.string(), patientId: z.string() }).parse(req.body);
    return sched.bookAppointment(b.holdId, b.patientId);
  });

  app.post('/appointments/cancel', async (req) => {
    const b = z.object({ appointmentId: z.string() }).parse(req.body);
    return sched.cancelAppointment(b.appointmentId);
  });

  app.post('/appointments/reschedule', async (req) => {
    const b = z.object({ appointmentId: z.string(), newHoldId: z.string(), patientId: z.string() }).parse(req.body);
    return sched.rescheduleAppointment(b.appointmentId, b.newHoldId, b.patientId);
  });

  app.get('/patients/:id/context', async (req) => {
    const { id } = z.object({ id: z.string() }).parse(req.params);
    return sched.getPatientContext(id);
  });

  app.post('/patients/:id/preferences', async (req) => {
    const { id } = z.object({ id: z.string() }).parse(req.params);
    const b = z.object({ key: z.string(), value: z.string() }).parse(req.body);
    return sched.savePreference(id, b.key, b.value);
  });

  app.get('/metrics/latency', async () => sched.getLatencyMetrics());

  app.post('/metrics/latency', async (req) => {
    const b = z.object({ stage: z.string(), durationMs: z.number() }).parse(req.body);
    sched.logLatency(b.stage, b.durationMs);
    return { ok: true };
  });

  app.post('/campaigns/outbound', async (req) => {
    const b = z.object({ patientId: z.string(), campaignType: z.enum(['reminder','followup','missed']) }).parse(req.body);
    return { queued: true, patientId: b.patientId, campaignType: b.campaignType };
  });
}