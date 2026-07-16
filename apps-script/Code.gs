/**
 * PEGA ESTE ARCHIVO COMPLETO en Apps Script (reemplaza todo).
 * Luego: Implementar → Administrar implementaciones → ✏️ → Nueva versión → Implementar
 * (misma URL — no crees una implementación nueva)
 */

function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var action = e ? e.parameter.action : null;

  if (action === "obtenerClientes") {
    var sheetClientes = ss.getSheetByName("Clientes");
    var rawClientes = sheetClientes.getDataRange().getValues();
    rawClientes.shift();

    var sheetAvances = ss.getSheetByName("Avances");
    var rawAvances = sheetAvances.getDataRange().getValues();
    rawAvances.shift();

    var clientes = rawClientes.map(function(row) {
      var obj = {
        id: row[0], nombre: row[1], sexo: row[2], edad: row[3], altura: row[4],
        peso: row[5], grasa: row[6], grasa_objetivo: row[7], fechaInicio: row[8],
        masa_muscular_kg: row[9], grasa_visceral: row[10], agua_corporal_perc: row[11],
        edad_metabolica: row[12], bmr_kcal: row[13], ohms: row[14],
        plan_asignado: row[15]
      };

      obj.avances = rawAvances.filter(function(aRow) {
        return String(aRow[0]).trim() === String(obj.id).trim();
      }).map(function(aRow) {
        return {
          id: aRow[0], fecha: aRow[1], peso: aRow[2], grasa: aRow[3],
          masa_muscular_kg: aRow[4], grasa_visceral: aRow[5], agua_corporal_perc: aRow[6],
          edad_metabolica: aRow[7], bmr_kcal: aRow[8], ohms: aRow[9]
        };
      });
      return obj;
    });

    return ContentService.createTextOutput(JSON.stringify(clientes)).setMimeType(ContentService.MimeType.JSON);
  }

  return ContentService.createTextOutput("Servidor Activo. Use ?action=obtenerClientes").setMimeType(ContentService.MimeType.TEXT);
}

function doPost(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  try {
    var data = JSON.parse(e.postData.contents);

    if (data.action === "guardarCliente") {
      var sheetClientes = ss.getSheetByName("Clientes");
      var c = data.cliente;
      var pd = c.predicta_data || {};
      sheetClientes.appendRow([
        c.id, c.nombre, c.sexo, c.edad, c.altura, c.peso, c.grasa,
        pd.grasa_objetivo || "", c.fechaInicio, pd.musculo || "",
        pd.visceral || "", pd.agua_perc || "", pd.edad_metabolica || "",
        pd.bmr || "", pd.ohms || "",
        c.plan_asignado
      ]);
      return ContentService.createTextOutput(JSON.stringify({ status: "Éxito" })).setMimeType(ContentService.MimeType.JSON);
    }

    if (data.action === "agregarAvance") {
      var sheetAvances = ss.getSheetByName("Avances");
      var a = data.avance;
      var pd = a.predicta_data || {};
      sheetAvances.appendRow([
        a.id, a.fecha, a.peso, a.grasa,
        pd.musculo || "", pd.visceral || "", pd.agua_perc || "",
        pd.edad_metabolica || "", pd.bmr || "", pd.ohms || ""
      ]);
      return ContentService.createTextOutput(JSON.stringify({ status: "Éxito" })).setMimeType(ContentService.MimeType.JSON);
    }

    if (data.action === "actualizarCliente") {
      var sheet = ss.getSheetByName("Clientes");
      var c = data.cliente;
      if (!c || c.id === undefined || c.id === null || c.id === "") {
        throw new Error("Falta cliente.id");
      }

      var values = sheet.getDataRange().getValues();
      var rowIndex = -1;
      var targetId = String(c.id).trim();

      for (var i = 1; i < values.length; i++) {
        if (String(values[i][0]).trim() === targetId) {
          rowIndex = i + 1;
          break;
        }
      }

      if (rowIndex < 0) {
        throw new Error("Paciente no encontrado: " + targetId);
      }

      // B=2 nombre, C=3 sexo, D=4 edad, E=5 altura, F=6 peso, G=7 grasa, I=9 fecha, P=16 plan
      sheet.getRange(rowIndex, 2).setValue(c.nombre);
      sheet.getRange(rowIndex, 3).setValue(c.sexo);
      sheet.getRange(rowIndex, 4).setValue(c.edad);
      sheet.getRange(rowIndex, 5).setValue(c.altura);
      sheet.getRange(rowIndex, 6).setValue(c.peso);
      sheet.getRange(rowIndex, 7).setValue(c.grasa);
      sheet.getRange(rowIndex, 9).setValue(c.fechaInicio);
      sheet.getRange(rowIndex, 16).setValue(c.plan_asignado);

      SpreadsheetApp.flush();

      return ContentService.createTextOutput(JSON.stringify({
        status: "Éxito",
        id: targetId,
        row: rowIndex,
        sexo: c.sexo,
        edad: c.edad
      })).setMimeType(ContentService.MimeType.JSON);
    }

    return ContentService.createTextOutput(JSON.stringify({
      status: "Error",
      message: "Acción desconocida: " + data.action
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "Error",
      message: error.message
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
