/**
 * PATCH — Paste into your existing Google Apps Script (doPost).
 *
 * 1. Open the Apps Script bound to your Weight Control spreadsheet.
 * 2. Inside doPost(e), where you handle actions (guardarCliente / agregarAvance),
 *    add a case for: action === "actualizarCliente"
 * 3. Deploy → Manage deployments → New version (same Web App URL).
 *
 * Expected POST body (JSON):
 *   { "action": "actualizarCliente", "cliente": { id, nombre, sexo, edad, altura, peso, grasa, fechaInicio, plan_asignado } }
 *
 * Adjust SHEET_NAME / column indexes to match your "Clientes" sheet headers.
 */

function handleActualizarCliente(cliente) {
  if (!cliente || cliente.id === undefined || cliente.id === null || cliente.id === '') {
    throw new Error('actualizarCliente: missing cliente.id');
  }

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Clientes') || ss.getSheets()[0];
  var data = sheet.getDataRange().getValues();
  if (data.length < 2) throw new Error('Clientes sheet is empty');

  var headers = data[0].map(function (h) { return String(h).trim().toLowerCase(); });
  var idCol = headers.indexOf('id');
  if (idCol < 0) idCol = 0;

  var targetId = String(cliente.id).trim();
  var rowIndex = -1; // 1-based sheet row
  for (var r = 1; r < data.length; r++) {
    if (String(data[r][idCol]).trim() === targetId) {
      rowIndex = r + 1;
      break;
    }
  }
  if (rowIndex < 0) throw new Error('Patient ID not found: ' + targetId);

  function setByHeader(names, value) {
    for (var i = 0; i < names.length; i++) {
      var col = headers.indexOf(names[i]);
      if (col >= 0 && value !== undefined && value !== null && value !== '') {
        sheet.getRange(rowIndex, col + 1).setValue(value);
        return;
      }
    }
  }

  setByHeader(['nombre', 'name', 'paciente'], cliente.nombre);
  setByHeader(['sexo', 'gender', 'genero'], cliente.sexo);
  setByHeader(['edad', 'age'], cliente.edad);
  setByHeader(['altura', 'height', 'estatura'], cliente.altura);
  setByHeader(['peso', 'peso_inicial', 'weight', 'start_weight'], cliente.peso);
  setByHeader(['grasa', 'grasa_inicial', 'fat', 'body_fat'], cliente.grasa);
  setByHeader(['fechainicio', 'fecha_inicio', 'start', 'start_date'], cliente.fechaInicio);
  setByHeader(['plan_asignado', 'plan', 'nutrition_plan'], cliente.plan_asignado);

  return { ok: true, id: targetId, row: rowIndex };
}

/**
 * Example wiring inside doPost(e):
 *
 *   var body = JSON.parse(e.postData.contents);
 *   if (body.action === 'actualizarCliente') {
 *     var result = handleActualizarCliente(body.cliente);
 *     return ContentService.createTextOutput(JSON.stringify(result))
 *       .setMimeType(ContentService.MimeType.JSON);
 *   }
 */
