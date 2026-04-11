/**
 * Fungsi untuk export tabel HTML ke Excel
 * @param {string} tableId - ID dari tabel HTML (contoh: 'resultsTable')
 * @param {string} filename - Nama file yang diinginkan (tanpa .xlsx)
 */
function exportHTMLTableToExcel(tableId, filename) {
    // 1. Ambil elemen tabel
    var table = document.getElementById(tableId);
    
    if (!table) {
        alert("Tabel tidak ditemukan!");
        return;
    }

    // 2. Ubah tabel HTML menjadi Worksheet Excel
    // {raw:true} agar angka tetap dianggap angka
    var wb = XLSX.utils.table_to_book(table, {sheet: "Sheet 1", raw: true});

    // 3. Download file
    // Pastikan nama file punya ekstensi .xlsx
    var fullFilename = filename ? (filename + ".xlsx") : "Export_Data.xlsx";
    XLSX.writeFile(wb, fullFilename);
}