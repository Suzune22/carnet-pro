/**
 * Backend du formulaire de parrainage (parrainage.html).
 *
 * À coller dans un projet Google Apps Script lié à une feuille Google Sheets,
 * puis à déployer en « Application Web » (exécuter en tant que : moi,
 * accès : tout le monde). Voir PARRAINAGE.md.
 *
 * Propriété de script facultative : ADMIN_KEY — code demandé aux organisateurs
 * pour consulter les inscrits et enregistrer les binômes. Sans ADMIN_KEY,
 * n'importe qui disposant de l'URL peut lire la liste des inscrits.
 */

var SHEET_STUDENTS = 'Etudiants';
var SHEET_PAIRS = 'Binomes';
var STUDENT_COLS = ['id', 'createdAt', 'role', 'firstName', 'lastName', 'email', 'phone', 'program', 'level', 'capacity', 'interests', 'mode', 'notes'];
var PAIR_COLS = ['id', 'parrainId', 'filleulId', 'score', 'createdAt'];

function doGet(e) {
  var key = (e && e.parameter && e.parameter.key) || '';
  if (!checkKey_(key)) return json_({ ok: false, error: 'Code organisateur invalide' });
  return json_({
    ok: true,
    students: readRows_(SHEET_STUDENTS, STUDENT_COLS).map(parseStudent_),
    pairs: readRows_(SHEET_PAIRS, PAIR_COLS).map(function (p) { p.score = Number(p.score) || 0; return p; })
  });
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var body = JSON.parse(e.postData.contents);
    switch (body.action) {
      case 'register':
        return json_(register_(body.data || {}));
      case 'setPairs':
        if (!checkKey_(body.key)) return json_({ ok: false, error: 'Code organisateur invalide' });
        writeRows_(SHEET_PAIRS, PAIR_COLS, body.pairs || []);
        return json_({ ok: true });
      case 'delete':
        if (!checkKey_(body.key)) return json_({ ok: false, error: 'Code organisateur invalide' });
        var id = String(body.id);
        writeRows_(SHEET_STUDENTS, STUDENT_COLS, readRows_(SHEET_STUDENTS, STUDENT_COLS).filter(function (s) { return s.id !== id; }));
        writeRows_(SHEET_PAIRS, PAIR_COLS, readRows_(SHEET_PAIRS, PAIR_COLS).filter(function (p) { return p.parrainId !== id && p.filleulId !== id; }));
        return json_({ ok: true });
      default:
        return json_({ ok: false, error: 'Action inconnue' });
    }
  } catch (err) {
    return json_({ ok: false, error: String(err.message || err) });
  } finally {
    lock.releaseLock();
  }
}

function register_(d) {
  var role = d.role === 'parrain' ? 'parrain' : 'filleul';
  var s = {
    id: Utilities.getUuid(),
    createdAt: new Date().toISOString(),
    role: role,
    firstName: clean_(d.firstName),
    lastName: clean_(d.lastName),
    email: clean_(d.email).toLowerCase(),
    phone: clean_(d.phone),
    program: clean_(d.program),
    level: role === 'filleul' ? 'L1' : clean_(d.level),
    capacity: role === 'parrain' ? Math.min(3, Math.max(1, Number(d.capacity) || 1)) : 0,
    interests: (Array.isArray(d.interests) ? d.interests : []).map(clean_).join('; '),
    mode: clean_(d.mode),
    notes: clean_(d.notes)
  };
  if (!s.firstName || !s.lastName || !s.email || !s.program) {
    return { ok: false, error: 'Champs obligatoires manquants' };
  }
  var dup = readRows_(SHEET_STUDENTS, STUDENT_COLS).some(function (x) {
    return x.email.toLowerCase() === s.email && x.role === s.role;
  });
  if (dup) return { ok: false, error: 'Cette adresse email est déjà inscrite avec ce rôle.' };

  sheet_(SHEET_STUDENTS, STUDENT_COLS).appendRow(STUDENT_COLS.map(function (c) { return String(s[c]); }));
  return { ok: true };
}

function parseStudent_(s) {
  s.capacity = Number(s.capacity) || 0;
  s.interests = s.interests ? s.interests.split(/\s*;\s*/) : [];
  return s;
}

function checkKey_(key) {
  var expected = PropertiesService.getScriptProperties().getProperty('ADMIN_KEY') || '';
  return !expected || key === expected;
}

function clean_(v) {
  return String(v == null ? '' : v).trim().slice(0, 500);
}

function sheet_(name, cols) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    // Tout en texte : évite que Sheets transforme les téléphones ou les dates.
    sh.getRange(1, 1, sh.getMaxRows(), cols.length).setNumberFormat('@');
    sh.getRange(1, 1, 1, cols.length).setValues([cols]).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

function readRows_(name, cols) {
  var sh = sheet_(name, cols);
  var last = sh.getLastRow();
  if (last < 2) return [];
  return sh.getRange(2, 1, last - 1, cols.length).getValues().map(function (row) {
    var o = {};
    cols.forEach(function (c, i) { o[c] = String(row[i]); });
    return o;
  });
}

function writeRows_(name, cols, rows) {
  var sh = sheet_(name, cols);
  var last = sh.getLastRow();
  if (last > 1) sh.getRange(2, 1, last - 1, cols.length).clearContent();
  if (!rows.length) return;
  var values = rows.map(function (r) {
    return cols.map(function (c) { return String(r[c] == null ? '' : r[c]); });
  });
  sh.getRange(2, 1, values.length, cols.length).setNumberFormat('@').setValues(values);
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
