// --- table-manager.js ---

// A. LOGIC ADD ROW
function submitAddRows() {
    const count = document.getElementById('rowCountInput').value;
    if (count < 1) return alert("Minimal 1 baris!");

    fetch(PROJECT_CONFIG.urls.addRows, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': PROJECT_CONFIG.csrfToken
        },
        body: JSON.stringify({ 'count': count })
    })
    .then(response => {
        if (response.ok) window.location.reload(); 
        else alert("Gagal menambahkan baris. Coba lagi.");
    })
    .catch(error => console.error('Error:', error));
}

// B. LOGIC BULK DELETE
function toggleSelectAll(source) {
    const checkboxes = document.querySelectorAll('.row-checkbox');
    checkboxes.forEach(cb => cb.checked = source.checked);
    updateDeleteButton();
}

function updateDeleteButton() {
    const checkedCount = document.querySelectorAll('.row-checkbox:checked').length;
    const btn = document.getElementById('btnBulkDelete');
    
    if (checkedCount > 0) {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="trash-2" class="w-4 h-4 inline mr-1"></i> Delete (${checkedCount})`;
        lucide.createIcons();
    } else {
        btn.disabled = true;
    }
}

function bulkDelete() {
    const checkedBoxes = document.querySelectorAll('.row-checkbox:checked');
    const ids = Array.from(checkedBoxes).map(cb => cb.value);

    if (ids.length === 0) return;
    if (!confirm(`Yakin hapus ${ids.length} data terpilih?`)) return;

    fetch(PROJECT_CONFIG.urls.bulkDelete, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': PROJECT_CONFIG.csrfToken
        },
        body: JSON.stringify({ ids: ids })
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            alert('Success: ' + data.message);
            window.location.reload();
        } else {
            alert("Gagal: " + data.message);
        }
    });
}

// C. LOGIC BULK EDIT
let isEditMode = false;

function toggleGlobalEditMode() {
    const rows = document.querySelectorAll('.raw-data-row');
    const btnEdit = document.getElementById('btnGlobalEdit');
    const btnSave = document.getElementById('btnSaveAll');
    
    isEditMode = !isEditMode; // Toggle status

    if (isEditMode) {
        // -- MASUK MODE EDIT --
        btnEdit.innerHTML = '<i data-lucide="x" class="w-4 h-4 inline mr-1"></i> Cancel';
        btnSave.classList.remove('hidden');
        
        rows.forEach(row => {
            // 1. Ubah Station jadi Input
            const stationCell = row.querySelector('.cell-station');
            stationCell.innerHTML = `<input type="text" class="w-20 px-2 py-1 border rounded text-xs" value="${stationCell.dataset.val}">`;

            // 2. Ubah Angka-angka jadi Input (TAMBAHKAN FIELD 'bwd_' DI SINI)
            const fields = [
                // Data Forward
                'bs_top', 'bs_mid', 'bs_bot', 'fs_top', 'fs_mid', 'fs_bot', 
                // Data Backward (INI YANG KURANG SEBELUMNYA)
                'bwd_bs_top', 'bwd_bs_mid', 'bwd_bs_bot', 'bwd_fs_top', 'bwd_fs_mid', 'bwd_fs_bot',
                // Jarak
                'distance','distance_bwd'
            ];

            fields.forEach(field => {
                const cell = row.querySelector(`.cell-${field}`);
                // Cek apakah cell ada (untuk menghindari error di tabel OPEN yang tidak punya kolom bwd)
                if (cell) {
                    const val = cell.dataset.val; 
                    cell.innerHTML = `<input type="number" step="0.001" class="w-16 px-1 py-1 border rounded text-xs" value="${val}">`;
                }
            });
        });

    } else {
        // -- KELUAR MODE EDIT --
        window.location.reload();
    }
    lucide.createIcons();
}

function saveAllRows() {
    const rows = document.querySelectorAll('.raw-data-row');
    let payload = [];

    rows.forEach(row => {
        const rowId = row.dataset.rowId;
        let rowData = { id: rowId };
        
        const getVal = (field) => {
            const input = row.querySelector(`.cell-${field} input`);
            return input ? input.value : '';
        };

        rowData.station = getVal('station');
        rowData.bs_top = getVal('bs_top');
        rowData.bs_mid = getVal('bs_mid');
        rowData.bs_bot = getVal('bs_bot');
        rowData.fs_top = getVal('fs_top');
        rowData.fs_mid = getVal('fs_mid');
        rowData.fs_bot = getVal('fs_bot');
        
        rowData.bwd_bs_top = getVal('bwd_bs_top');
        rowData.bwd_bs_mid = getVal('bwd_bs_mid');
        rowData.bwd_bs_bot = getVal('bwd_bs_bot');
        rowData.bwd_fs_top = getVal('bwd_fs_top');
        rowData.bwd_fs_mid = getVal('bwd_fs_mid');
        rowData.bwd_fs_bot = getVal('bwd_fs_bot');
        
        rowData.distance = getVal('distance');
        rowData.distance_bwd = getVal('distance_bwd');

        payload.push(rowData);
    });

    const btnSave = document.getElementById('btnSaveAll');
    const originalText = btnSave.innerHTML;
    btnSave.disabled = true;
    btnSave.innerHTML = '<i data-lucide="loader-2" class="animate-spin w-4 h-4 inline mr-1"></i> Saving...';
    lucide.createIcons();

    fetch(PROJECT_CONFIG.urls.bulkUpdate, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': PROJECT_CONFIG.csrfToken
        },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            alert(data.message);
            window.location.reload();
        } else {
            alert("Gagal menyimpan: " + data.message);
            btnSave.disabled = false;
            btnSave.innerHTML = originalText;
            lucide.createIcons();
        }
    })
    .catch(err => {
        console.error(err);
        alert("Terjadi kesalahan sistem.");
        btnSave.disabled = false;
        btnSave.innerHTML = originalText;
        lucide.createIcons();
    });
}

// D. EXCEL UPLOAD
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('excelFileInput');
    // Mencari tombol yang memiliki onclick trigger ke file input
    const uploadBtn = document.querySelector('button[onclick="document.getElementById(\'excelFileInput\').click()"]');

    if (fileInput && uploadBtn) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                if (!confirm(`Anda akan mengunggah file ${this.files[0].name}. Lanjutkan?`)) {
                    this.value = ''; 
                    return;
                }
                
                const formData = new FormData(document.getElementById('excelUploadForm'));
                const originalHtml = uploadBtn.innerHTML;
                
                uploadBtn.disabled = true;
                uploadBtn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 mr-1 animate-spin"></i> Uploading...';
                lucide.createIcons();

                fetch(document.getElementById('excelUploadForm').action, {
                    method: 'POST',
                    body: formData 
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(errorData => { throw new Error(errorData.message || 'Error'); });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        alert(data.message);
                        window.location.reload(); 
                    } else {
                        throw new Error(data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert("Gagal Upload: " + error.message);
                    uploadBtn.disabled = false;
                    uploadBtn.innerHTML = originalHtml;
                    fileInput.value = ''; 
                    lucide.createIcons();
                });
            }
        });
    }
});



// --- Tambahkan di bagian bawah table-manager.js ---

// E. LOGIC EDIT CROSS SECTION (CS)



// 1. Fungsi Buka-Tutup Accordion
function toggleAccordion(id) {
    const content = document.getElementById(id);
    const icon = document.getElementById('icon-' + id);
    
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        icon.style.transform = 'rotate(180deg)';
    } else {
        content.classList.add('hidden');
        icon.style.transform = 'rotate(0deg)';
    }
}

// 2. Fungsi Tambah Titik via AJAX
function addPoint(stationId) {
    const label = document.getElementById(`input-label-${stationId}`).value;
    const dist = document.getElementById(`input-dist-${stationId}`).value;
    const top = document.getElementById(`input-top-${stationId}`).value;
    const mid = document.getElementById(`input-mid-${stationId}`).value;
    const bot = document.getElementById(`input-bot-${stationId}`).value;

    if (!dist || !mid) {
        alert("Jarak dan Benang Tengah (BT) wajib diisi!");
        return;
    }

    fetch(`/survey/api/cross-section/add/${stationId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': PROJECT_CONFIG.csrfToken
        },
        body: JSON.stringify({ 
            label: label, 
            distance: dist, 
            top: top,     
            mid: mid, 
            bot: bot      
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Hapus tulisan "Belum ada titik" kalau ada
            const emptyRow = document.getElementById(`empty-row-${stationId}`);
            if (emptyRow) emptyRow.remove();

            // Format angka
            const newDist = parseFloat(dist);
            const fmtTop = top ? parseFloat(top).toFixed(3) : "-";
            const fmtMid = parseFloat(mid).toFixed(3);
            const fmtBot = bot ? parseFloat(bot).toFixed(3) : "-";

            // HTML Baris Baru (Pastikan class cs-data-row dan data-val ada biar bisa disortir lagi)
            const newRow = `
                <tr id="row-point-${data.id}" class="border-b border-border/50 hover:bg-slate-50 cs-data-row">
                    <td class="px-4 py-3 font-semibold text-tertiary border-r border-border">${label}</td>
                    <td class="px-4 py-3 text-emerald-700 font-mono font-semibold bg-emerald-50/5 border-r border-border cell-cs-distance" data-val="${newDist}">${newDist.toFixed(2)}</td>
                    <td class="px-4 py-3 text-xs text-tertiary border-r border-dashed border-gray-200 font-mono">${fmtTop}</td>
                    <td class="px-4 py-3 font-bold text-blue-700 bg-blue-50/10 border-r border-dashed border-gray-200 font-mono">${fmtMid}</td>
                    <td class="px-4 py-3 text-xs text-tertiary border-r border-border font-mono">${fmtBot}</td>
                    <td class="px-4 py-2">
                        <button onclick="deletePoint(${data.id})" class="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 transition-colors">
                            <i data-lucide="trash-2" class="w-4 h-4"></i>
                        </button>
                    </td>
                </tr>
            `;

            const tbody = document.querySelector(`#table-sta-${stationId} tbody`);
            
            // LOGIKA AUTO-SORTING UI (Dari Terkecil ke Terbesar)
            const existingRows = Array.from(tbody.querySelectorAll('tr.cs-data-row'));
            let isInserted = false;

            for (let i = 0; i < existingRows.length; i++) {
                const row = existingRows[i];
                
                // KITA UBAH CARA BACA JARAKNYA: Ambil dari tag <input> nya!
                const distInput = row.querySelector('.cs-input-dist');
                
                if (distInput) {
                    const rowDist = parseFloat(distInput.value); // Ambil nilainya langsung
                    
                    // Kalau nemu baris yang jaraknya lebih besar dari input baru lu, selipin di atasnya!
                    if (newDist < rowDist) {
                        row.insertAdjacentHTML('beforebegin', newRow);
                        isInserted = true;
                        break; // Stop looping karena udah dapet posisinya
                    }
                }
            }

            // Kalau nggak ada yang lebih besar (berarti dia yang paling besar/ujung kanan), taruh paling bawah
            if (!isInserted) {
                tbody.insertAdjacentHTML('beforeend', newRow);
            }

            lucide.createIcons(); 

            // Bersihin input form
            document.getElementById(`input-label-${stationId}`).value = '';
            document.getElementById(`input-dist-${stationId}`).value = '';
            document.getElementById(`input-top-${stationId}`).value = '';
            document.getElementById(`input-mid-${stationId}`).value = '';
            document.getElementById(`input-bot-${stationId}`).value = '';
            
            // Bikin input fokus lagi ke Label biar cepet ngetik data selanjutnya
            document.getElementById(`input-label-${stationId}`).focus();
            
        } else {
            alert("Gagal menyimpan: " + data.message);
        }
    });
}

// 3. Fungsi Hapus Titik via AJAX
function deletePoint(pointId) {
    if (!confirm("Hapus titik ini?")) return;

    fetch(`/survey/api/cross-section/delete/${pointId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': PROJECT_CONFIG.csrfToken }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById(`row-point-${pointId}`).remove();
        } else {
            alert("Gagal menghapus: " + data.message);
        }
    });
}






function handleCSExcelUpload(event) {
    const fileInput = event.target;
    const file = fileInput.files[0];
    
    // Kalau user batal milih file, hentikan fungsi
    if (!file) return;

    // 1. Validasi Ekstensi File
    const validExtensions = ['xlsx', 'xls'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    if (!validExtensions.includes(fileExtension)) {
        Swal.fire('Format Salah!', 'Harap upload file Excel dengan format .xlsx atau .xls', 'error');
        fileInput.value = ''; // Reset input
        return;
    }

    // 2. Bungkus file ke dalam FormData
    const formData = new FormData();
    formData.append('excel_file', file);
    
    // 3. Tampilkan Loading biar kelihatan pro (Pake SweetAlert)
    Swal.fire({
        title: 'Membaca Excel...',
        text: 'Sedang memproses dan menyimpan data Cross Section',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    // 4. Kirim ke Backend Django (PASTIKAN ADA GARIS MIRING DI AKHIR URL)
    // Nanti di Django lu tinggal bikin path('api/upload-cs-excel/<int:project_id>/', ...)
    fetch(PROJECT_CONFIG.urls.uploadExcel_CS, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': PROJECT_CONFIG.csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            Swal.fire('Berhasil!', data.message || 'Data berhasil diunggah', 'success')
            .then(() => {
                // Reload halaman biar tabel accordion-nya nampilin data yang baru di-upload
                window.location.reload(); 
            });
        } else {
            throw new Error(data.message || 'Gagal memproses file Excel.');
        }
    })
    .catch(error => {
        console.error('Upload Error:', error);
        Swal.fire('Oops!', error.message, 'error');
    })
    .finally(() => {
        // Reset file input biar bisa dipake upload file yang sama lagi kalau butuh
        fileInput.value = ''; 
    });
}