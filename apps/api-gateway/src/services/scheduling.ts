import { randomUUID } from 'node:crypto';
import { db } from '../db/database.js';

export function searchSlots(filters: { doctorId?: string; clinicId?: string; date?: string }) {
  return db.prepare(`
    SELECT id as slotId, doctor_id as doctorId, clinic_id as clinicId,
           start_at as startAt, end_at as endAt
    FROM slots
    WHERE status = 'open'
      AND (? IS NULL OR doctor_id = ?)
      AND (? IS NULL OR clinic_id = ?)
      AND (? IS NULL OR substr(start_at,1,10) = ?)
    ORDER BY start_at ASC LIMIT 5
  `).all(
    filters.doctorId??null, filters.doctorId??null,
    filters.clinicId??null, filters.clinicId??null,
    filters.date??null,    filters.date??null
  );
}

export function holdSlot(slotId: string, patientId: string, ttlSeconds = 90) {
  const slot = db.prepare('SELECT * FROM slots WHERE id=?').get(slotId) as any;
  if (!slot)               throw new Error('Slot not found');
  if (slot.status!=='open') throw new Error('Slot not available');
  if (new Date(slot.start_at) < new Date()) throw new Error('Cannot book past slot');

  const holdId = randomUUID();
  const expiresAt = new Date(Date.now() + ttlSeconds*1000).toISOString();
  db.transaction(() => {
    db.prepare('UPDATE slots SET status=? WHERE id=?').run('held', slotId);
    db.prepare('INSERT INTO slot_holds VALUES (?,?,?,?,?)').run(holdId, slotId, patientId, expiresAt, 'active');
  })();
  return { holdId, slotId, expiresAt };
}

export function bookAppointment(holdId: string, patientId: string) {
  const hold = db.prepare('SELECT * FROM slot_holds WHERE id=? AND patient_id=? AND status=?').get(holdId, patientId, 'active') as any;
  if (!hold) throw new Error('Hold not found or expired');
  if (new Date(hold.expires_at) < new Date()) throw new Error('Hold expired');

  const slot = db.prepare('SELECT * FROM slots WHERE id=?').get(hold.slot_id) as any;
  const appointmentId = randomUUID();
  db.transaction(() => {
    db.prepare(`INSERT INTO appointments VALUES (?,?,?,?,?,?,?,?)`).run(
      appointmentId, patientId, slot.doctor_id, slot.clinic_id,
      slot.start_at, slot.end_at, 'booked', new Date().toISOString()
    );
    db.prepare('UPDATE slot_holds SET status=? WHERE id=?').run('consumed', holdId);
    db.prepare('UPDATE slots SET status=? WHERE id=?').run('booked', slot.id);
  })();
  return { appointmentId, startAt: slot.start_at, endAt: slot.end_at };
}

export function cancelAppointment(appointmentId: string) {
  const a = db.prepare('SELECT * FROM appointments WHERE id=?').get(appointmentId) as any;
  if (!a) throw new Error('Appointment not found');
  db.transaction(() => {
    db.prepare('UPDATE appointments SET status=? WHERE id=?').run('cancelled', appointmentId);
    db.prepare('INSERT INTO slots VALUES (?,?,?,?,?,?)').run(
      randomUUID(), a.doctor_id, a.clinic_id, a.start_at, a.end_at, 'open'
    );
  })();
  return { ok: true };
}

export function rescheduleAppointment(appointmentId: string, newHoldId: string, patientId: string) {
  cancelAppointment(appointmentId);
  return bookAppointment(newHoldId, patientId);
}

export function getPatientContext(patientId: string) {
  const p = db.prepare('SELECT * FROM patients WHERE id=?').get(patientId) as any;
  if (!p) throw new Error('Patient not found');
  return {
    patientId: p.id,
    preferredLanguage: p.preferred_language,
    preferredDoctorId: p.preferred_doctor_id,
    preferredClinicId: p.preferred_clinic_id,
    preferredTimeOfDay: p.preferred_time_of_day
  };
}

export function savePreference(patientId: string, key: string, value: string) {
  const allowed = ['preferred_language','preferred_doctor_id','preferred_clinic_id','preferred_time_of_day'];
  if (!allowed.includes(key)) throw new Error('Invalid preference key');
  db.prepare(`UPDATE patients SET ${key}=? WHERE id=?`).run(value, patientId);
  return { ok: true };
}

export function logLatency(stage: string, durationMs: number) {
  db.prepare('INSERT INTO latency_logs (stage,duration_ms,created_at) VALUES (?,?,?)').run(stage, durationMs, new Date().toISOString());
}

export function getLatencyMetrics() {
  return db.prepare('SELECT stage, AVG(duration_ms) as avgMs, COUNT(*) as count FROM latency_logs GROUP BY stage').all();
}