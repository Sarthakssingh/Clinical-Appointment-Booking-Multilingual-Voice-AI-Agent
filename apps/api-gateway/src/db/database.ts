import Database from 'better-sqlite3';

export const db = new Database('clinic.db');

export function initDb() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS patients (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      phone TEXT NOT NULL,
      preferred_language TEXT DEFAULT 'en',
      preferred_doctor_id TEXT,
      preferred_clinic_id TEXT,
      preferred_time_of_day TEXT
    );
    CREATE TABLE IF NOT EXISTS doctors (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      specialty TEXT NOT NULL,
      active INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS clinics (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS slots (
      id TEXT PRIMARY KEY,
      doctor_id TEXT NOT NULL,
      clinic_id TEXT NOT NULL,
      start_at TEXT NOT NULL,
      end_at TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'open'
    );
    CREATE TABLE IF NOT EXISTS slot_holds (
      id TEXT PRIMARY KEY,
      slot_id TEXT NOT NULL,
      patient_id TEXT NOT NULL,
      expires_at TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'active'
    );
    CREATE TABLE IF NOT EXISTS appointments (
      id TEXT PRIMARY KEY,
      patient_id TEXT NOT NULL,
      doctor_id TEXT NOT NULL,
      clinic_id TEXT NOT NULL,
      start_at TEXT NOT NULL,
      end_at TEXT NOT NULL,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS latency_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      stage TEXT NOT NULL,
      duration_ms INTEGER NOT NULL,
      created_at TEXT NOT NULL
    );
  `);
  seedIfEmpty();
}

function seedIfEmpty() {
  const count = (db.prepare('SELECT COUNT(*) as c FROM doctors').get() as any).c;
  if (count > 0) return;

  db.prepare('INSERT INTO doctors VALUES (?,?,?,1)').run('d1','Dr Mehta','cardiology');
  db.prepare('INSERT INTO doctors VALUES (?,?,?,1)').run('d2','Dr Rao','dermatology');
  db.prepare('INSERT INTO clinics VALUES (?,?)').run('c1','City Clinic');
  db.prepare('INSERT INTO clinics VALUES (?,?)').run('c2','Metro Clinic');
  db.prepare('INSERT INTO patients (id,name,phone,preferred_language) VALUES (?,?,?,?)').run('p1','Test Patient','+919999999999','en');

  for (let i = 1; i <= 10; i++) {
    const start = new Date(Date.now() + i * 3600000);
    const end = new Date(start.getTime() + 1800000);
    db.prepare('INSERT INTO slots VALUES (?,?,?,?,?,?)').run(
      `s${i}`, i%2===0?'d2':'d1', i%2===0?'c2':'c1',
      start.toISOString(), end.toISOString(), 'open'
    );
  }
}