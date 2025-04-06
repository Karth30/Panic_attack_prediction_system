function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var raw = e.parameter.raw;
  var gsrvoltage = e.parameter.gsrvoltage;
  var temp = e.parameter.temp;
  var timestamp = new Date();

  sheet.appendRow([timestamp, raw, gsrvoltage, temp]);

  return ContentService.createTextOutput("Success");
}
