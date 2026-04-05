


// 1. Initialize Icons & Animations saat Load
document.addEventListener('DOMContentLoaded', function() {
    lucide.createIcons();
    
    // Trigger animasi angka awal
    setTimeout(() => triggerCountUp(), 500);

    // Hapus class reveal agar elemen muncul
    document.querySelectorAll('.reveal-load').forEach(el => {
        el.classList.remove('reveal-load');
    });
});

// 2. Number Counting Animation
function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        
        const value = (progress * (end - start) + start).toFixed(3); 
        const hasDecimals = end % 1 != 0;
        obj.innerHTML = hasDecimals ? parseFloat(value).toFixed(end.toString().split('.')[1]?.length || 2) : Math.floor(value);
        
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

function triggerCountUp(context = document) {
    context.querySelectorAll('.count-up').forEach(el => {
        const target = parseFloat(el.getAttribute('data-target'));
        animateValue(el, 0, target, 1500);
    });
}

// 3. Tab Switching Logic
function switchTab(tabId) {
    // Hide all contents
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.remove('active');
        const children = el.querySelectorAll('.animate-fade-in-up');
        children.forEach(child => {
            child.style.animation = 'none';
            child.offsetHeight; /* trigger reflow */
            child.style.animation = null; 
        });
    });
    
    // Deactivate all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Activate clicked button
    const clickedBtn = event.currentTarget;
    clickedBtn.classList.add('active');

    // Show target
    const target = document.getElementById(tabId);
    target.classList.add('active');
    
    // Trigger animation & resize chart
    if(tabId === 'tab-analysis' || tabId === 'tab-cutfill') {
        setTimeout(() => triggerCountUp(target), 100);
    }
    if(tabId === 'tab-analysis' && typeof Plotly !== 'undefined') {
        setTimeout(() => {
            try { Plotly.Plots.resize('elevationChart'); } catch(e){}
        }, 100);
    }
}

// 4. Modal Logic (Add Row)
function openAddRowModal() {
    const modal = document.getElementById('addRowModal');
    modal.classList.remove('hidden');
    document.getElementById('rowCountInput').focus();
}

function closeAddRowModal() {
    document.getElementById('addRowModal').classList.add('hidden');
}

function switchCsSubTab(tab) {
    const editTab = document.getElementById('subtab-cs-edit');
    const resultTab = document.getElementById('subtab-cs-result');
    const btnEdit = document.getElementById('btn-subtab-cs-edit');
    const btnResult = document.getElementById('btn-subtab-cs-result');

    if (tab === 'edit') {
        // Tampilkan Tab Edit
        editTab.classList.remove('hidden');
        editTab.classList.add('block');
        resultTab.classList.remove('block');
        resultTab.classList.add('hidden');
        
        // Ubah Warna Tombol Edit menjadi Aktif
        btnEdit.classList.add('border-primary', 'text-primary');
        btnEdit.classList.remove('border-transparent', 'text-tertiary');
        
        // Ubah Warna Tombol Result menjadi Pasif
        btnResult.classList.remove('border-primary', 'text-primary');
        btnResult.classList.add('border-transparent', 'text-tertiary');
    } else {
        // Tampilkan Tab Result
        resultTab.classList.remove('hidden');
        resultTab.classList.add('block');
        editTab.classList.remove('block');
        editTab.classList.add('hidden');
        
        // Ubah Warna Tombol Result menjadi Aktif
        btnResult.classList.add('border-primary', 'text-primary');
        btnResult.classList.remove('border-transparent', 'text-tertiary');
        
        // Ubah Warna Tombol Edit menjadi Pasif
        btnEdit.classList.remove('border-primary', 'text-primary');
        btnEdit.classList.add('border-transparent', 'text-tertiary');
    }
}

function switchSubTab(tab) {
    const editTab = document.getElementById('subtab-edit');
    const resultTab = document.getElementById('subtab-result');
    const btnEdit = document.getElementById('btn-subtab-edit');
    const btnResult = document.getElementById('btn-subtab-result');

    if (tab === 'edit') {
        // Tampilkan Tab Edit
        editTab.classList.remove('hidden');
        editTab.classList.add('block');
        resultTab.classList.remove('block');
        resultTab.classList.add('hidden');
        
        // Ubah Warna Tombol Edit menjadi Aktif
        btnEdit.classList.add('border-primary', 'text-primary');
        btnEdit.classList.remove('border-transparent', 'text-tertiary');
        
        // Ubah Warna Tombol Result menjadi Pasif
        btnResult.classList.remove('border-primary', 'text-primary');
        btnResult.classList.add('border-transparent', 'text-tertiary');
    } else {
        // Tampilkan Tab Result
        resultTab.classList.remove('hidden');
        resultTab.classList.add('block');
        editTab.classList.remove('block');
        editTab.classList.add('hidden');
        
        // Ubah Warna Tombol Result menjadi Aktif
        btnResult.classList.add('border-primary', 'text-primary');
        btnResult.classList.remove('border-transparent', 'text-tertiary');
        
        // Ubah Warna Tombol Edit menjadi Pasif
        btnEdit.classList.remove('border-primary', 'text-primary');
        btnEdit.classList.add('border-transparent', 'text-tertiary');
    }
}




document.addEventListener("DOMContentLoaded", function() {
    // ... (Kode untuk chart dan lain-lain biarkan saja) ...

    // AMBIL ELEMEN TOMBOL & CONTAINER ALERT AI
    const btnAnalyze = document.getElementById('btn-analyze');
    const alertContainer = document.getElementById('ai-alert-container');
    const loadingBox = document.getElementById('ai-loading');
    const summaryBox = document.getElementById('anomaly-summary');
    
    // 1. CEK LOCAL STORAGE SAAT HALAMAN DIBUKA
    

    // 2. SAAT TOMBOL DIKLIK
    // 2. SAAT TOMBOL DIKLIK
    if (btnAnalyze) {
        btnAnalyze.addEventListener('click', function() {
            alertContainer.classList.remove('hidden');
            summaryBox.classList.add('hidden');
            loadingBox.classList.remove('hidden');
            loadingBox.classList.add('flex'); 
            btnAnalyze.disabled = true;

            let tableData = [];
            let isClosedSurvey = false;

            // --- 3. AMBIL DATA TABEL ASLI (SEMUA KOLOM) ---
            document.querySelectorAll('#rawTableBody .raw-data-row').forEach(row => {
                let rowData = {};
                rowData.station = row.querySelector('.cell-station')?.dataset.val || "";
                
                // Forward
                rowData.bs_top = row.querySelector('.cell-bs_top')?.dataset.val || "";
                rowData.bs_mid = row.querySelector('.cell-bs_mid')?.dataset.val || "";
                rowData.bs_bot = row.querySelector('.cell-bs_bot')?.dataset.val || "";
                
                rowData.fs_top = row.querySelector('.cell-fs_top')?.dataset.val || "";
                rowData.fs_mid = row.querySelector('.cell-fs_mid')?.dataset.val || "";
                rowData.fs_bot = row.querySelector('.cell-fs_bot')?.dataset.val || "";

                rowData.distance = row.querySelector('.cell-distance')?.dataset.val || "";

                // Backward (Jika metode CLOSED)
                let bwd_bs_mid_el = row.querySelector('.cell-bwd_bs_mid');
                if (bwd_bs_mid_el) {
                    isClosedSurvey = true;
                    rowData.bwd_bs_top = row.querySelector('.cell-bwd_bs_top')?.dataset.val || "";
                    rowData.bwd_bs_mid = bwd_bs_mid_el.dataset.val || "";
                    rowData.bwd_bs_bot = row.querySelector('.cell-bwd_bs_bot')?.dataset.val || "";

                    rowData.bwd_fs_top = row.querySelector('.cell-bwd_fs_top')?.dataset.val || "";
                    rowData.bwd_fs_mid = row.querySelector('.cell-bwd_fs_mid')?.dataset.val || "";
                    rowData.bwd_fs_bot = row.querySelector('.cell-bwd_fs_bot')?.dataset.val || "";
                }
                
                tableData.push(rowData);
            });

            const dataToAnalyze = JSON.stringify(tableData); 
            const surveyType = isClosedSurvey ? 'CLOSED' : 'OPEN';

            // Kirim ke Backend
            fetch('/survey/api/analyze-anomaly/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 
                    tabel_data: dataToAnalyze,
                    survey_type: surveyType // Kirim status OPEN/CLOSED ke backend
                })
            })
            // ... (lanjutan fetch success / catch error tetap sama)
            .then(response => response.json())
            .then(data => {
                // Matikan loading
                loadingBox.classList.add('hidden');
                loadingBox.classList.remove('flex');
                btnAnalyze.disabled = false;

                if(data.status === 'success') {
                    // Simpan hasil ke browser
                    // Warnai tabel
                    applyAnomalyColors(data.data);
                } else {
                    alertContainer.classList.add('hidden');
                    alert("Gagal menganalisis: " + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                loadingBox.classList.add('hidden');
                loadingBox.classList.remove('flex');
                btnAnalyze.disabled = false;
                alert("Terjadi kesalahan jaringan atau respons server.");
            });
        });
    }

    // 4. FUNGSI UNTUK MEWARNAI TABEL & MENAMPILKAN SUMMARY
    // 4. FUNGSI UNTUK MEWARNAI TABEL & MENAMPILKAN SUMMARY
    // 4. FUNGSI UNTUK MEWARNAI TABEL & MENAMPILKAN SUMMARY
    function applyAnomalyColors(aiData) {
        const alertContainer = document.getElementById('ai-alert-container');
        const summaryBox = document.getElementById('anomaly-summary');
        
        alertContainer.classList.remove('hidden');
        summaryBox.classList.remove('hidden');
        
        summaryBox.innerHTML = '<h4 class="font-bold text-red-600 mb-2 border-b border-red-200 pb-1">⚠️ Laporan Analisis AI:</h4><ul class="list-disc pl-5 text-red-700 space-y-1"></ul>';
        const ul = summaryBox.querySelector('ul');
        
        let hasAnomaly = false;
        const rows = document.querySelectorAll('#rawTableBody .raw-data-row');

        if (Array.isArray(aiData)) {
            aiData.forEach((item, index) => {
                const row = rows[index];
                if (!row) return;
                
                const stCell = row.querySelector('.cell-station');
                const stationName = stCell ? stCell.dataset.val : `Baris ${index + 1}`;
                
                let isRowAnomalous = false;
                let errorMessages = [];

                // Helper function untuk mengecek & mewarnai cell spesifik
                const checkHighlight = (aiKeyPart, threadKey, cellClass) => {
                    const exactKey = Object.keys(item).find(key => key.includes(aiKeyPart));
                    if (exactKey && item[exactKey] && (item[exactKey][threadKey] === "True" || item[exactKey][threadKey] === true)) {
                        isRowAnomalous = true;
                        errorMessages.push(item[exactKey][`desc_${threadKey}`] || item[exactKey]['desc'] || "Anomali terdeteksi");
                        const cell = row.querySelector(cellClass);
                        if (cell) cell.classList.add('border-2', 'border-red-500', 'text-red-700', 'bg-red-100');
                    }
                };

                // Cek Forward
                checkHighlight('backsight', 'top', '.cell-bs_top');
                checkHighlight('backsight', 'mid', '.cell-bs_mid');
                checkHighlight('backsight', 'bottom', '.cell-bs_bot');
                
                checkHighlight('foresight', 'top', '.cell-fs_top');
                checkHighlight('foresight', 'mid', '.cell-fs_mid');
                checkHighlight('foresight', 'bottom', '.cell-fs_bot');

                // Cek Distance
                checkHighlight('distance', 'dist', '.cell-distance');

                // Cek Backward
                checkHighlight('bwd_backsight', 'top', '.cell-bwd_bs_top');
                checkHighlight('bwd_backsight', 'mid', '.cell-bwd_bs_mid');
                checkHighlight('bwd_backsight', 'bottom', '.cell-bwd_bs_bot');
                
                checkHighlight('bwd_foresight', 'top', '.cell-bwd_fs_top');
                checkHighlight('bwd_foresight', 'mid', '.cell-bwd_fs_mid');
                checkHighlight('bwd_foresight', 'bottom', '.cell-bwd_fs_bot');

                if (isRowAnomalous) {
                    hasAnomaly = true;
                    // Hilangkan duplikat pesan error
                    const uniqueErrors = [...new Set(errorMessages)];
                    ul.innerHTML += `<li><b>${stationName}:</b> ${uniqueErrors.join(' & ')}</li>`;
                    row.classList.add('bg-red-50'); 
                }
            });
        }
        
        if (!hasAnomaly) {
            summaryBox.innerHTML = '<h4 class="font-bold text-emerald-600 mb-2 border-b border-emerald-200 pb-1">✅ Laporan Analisis AI:</h4><p class="text-emerald-600 font-bold">Data terlihat normal dan konsisten! Tidak ada anomali.</p>';
        }
    }
});

// Fungsi bawaan untuk ngambil CSRF token Django di JS
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// ❌ HAPUS TANDA KURUNG KURAWAL "}" EKSTRA YANG ADA DI BARIS PALING BAWAH SEBELUMNYA!



document.addEventListener("DOMContentLoaded", function() {
    loadStaOptions();
    
    // ==========================================
    // LOGIC EXPORT AUTOCAD (DXF) DENGAN KOPS & SKALA
    // ==========================================
    const btnGenerateDxf = document.getElementById('btn-generate-dxf');
    const textGenerateDxf = document.getElementById('text-generate-dxf');
    const formExportDxf = document.getElementById('form-export-dxf');
    
    // Elements for Dynamic Toggle
    const datumTypeSelect = document.getElementById('dxf-datum-type');
    const datumValueInput = document.getElementById('dxf-datum-value');
    
    const kopTypeSelect = document.getElementById('dxf-kop-type');
    const kopUploadContainer = document.getElementById('dxf-kop-upload-container');

    const staStartSelect = document.getElementById('dxf-sta-start');
    const staEndSelect = document.getElementById('dxf-sta-end');

    // 1. Toggle Manual Datum Input
    if(datumTypeSelect) {
        datumTypeSelect.addEventListener('change', function() {
            if (this.value === 'manual') {
                datumValueInput.classList.remove('hidden');
                datumTypeSelect.classList.remove('w-full');
                datumTypeSelect.classList.add('w-1/2');
            } else {
                datumValueInput.classList.add('hidden');
                datumTypeSelect.classList.add('w-full');
                datumTypeSelect.classList.remove('w-1/2');
                datumValueInput.value = ''; // Reset value
            }
        });
    }

    // 2. Toggle Upload Custom Kop
    if(kopTypeSelect) {
        kopTypeSelect.addEventListener('change', function() {
            if (this.value === 'custom') {
                kopUploadContainer.classList.remove('hidden');
            } else {
                kopUploadContainer.classList.add('hidden');
                document.getElementById('dxf-custom-kop').value = ''; // Clear file
            }
        });
    }

    // 3. FUNGSI UNTUK MENGAMBIL DATA STA DARI DATABASE
    // Memanggil API endpoint backend (misal: /survey/api/get-sta-list/)
    function loadStaOptions() {
        // Ganti URL ini dengan URL API lu yang mereturn list STA dari database
        fetch(PROJECT_CONFIG.urls.getStationList, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            // Sekarang kita cek data.stations, bukan data.data
            if (data.status === 'success' && data.stations.length > 0) {
                staStartSelect.innerHTML = '';
                staEndSelect.innerHTML = '';
                
                // Looping array object dari Django
                data.stations.forEach((item, index) => {
                    // Ambil string station-nya (misal: "0+000")
                    let staValue = item.station; 
                    
                    // Masukkan ke dalam Option(text, value)
                    let optionStart = new Option(staValue, staValue);
                    let optionEnd = new Option(staValue, staValue);
                    
                    staStartSelect.add(optionStart);
                    staEndSelect.add(optionEnd);
                });

                // Set default Akhir STA ke item terakhir
                staEndSelect.selectedIndex = data.stations.length - 1;
            } else {
                staStartSelect.innerHTML = '<option value="">Data STA Kosong</option>';
                staEndSelect.innerHTML = '<option value="">Data STA Kosong</option>';
            }
        
        })
        .catch(error => {
            console.error('Error fetching STA:', error);
            staStartSelect.innerHTML = '<option value="">Gagal muat STA</option>';
            staEndSelect.innerHTML = '<option value="">Gagal muat STA</option>';
            
            /* --- FALLBACK: JIKA BELUM ADA API, AMBIL DARI TABEL HTML DOM SAAT INI --- */
            /* Ini trik kalau lu belum sempet bikin API endpoint di Django-nya */
            const staCells = document.querySelectorAll('#designTableBody .design-row td:first-child');
            if(staCells.length > 0) {
                staStartSelect.innerHTML = '';
                staEndSelect.innerHTML = '';
                staCells.forEach(cell => {
                    let staVal = cell.innerText.trim();
                    if(staVal) {
                        staStartSelect.add(new Option(staVal, staVal));
                        staEndSelect.add(new Option(staVal, staVal));
                    }
                });
                staEndSelect.selectedIndex = staEndSelect.options.length - 1;
            }
        });
    }

    // Panggil fungsi load STA saat tab diclick atau saat page diload
    // Misal di trigger di dalam fungsi switchTab() lu juga bisa


    // 4. ACTION GENERATE & DOWNLOAD
    if (btnGenerateDxf) {
        btnGenerateDxf.addEventListener('click', function() {
            // Validasi manual datum
            if (datumTypeSelect.value === 'manual' && datumValueInput.value === '') {
                alert('Silakan masukkan nilai Datum Elevasi!');
                datumValueInput.focus();
                return;
            }

            // Validasi Custom Kop
            if (kopTypeSelect.value === 'custom' && document.getElementById('dxf-custom-kop').files.length === 0) {
                alert('Silakan upload file Custom Kop Anda (.dxf)!');
                return;
            }

            // State Loading pada tombol
            const originalText = textGenerateDxf.innerText;
            const originalIcon = btnGenerateDxf.innerHTML;
            
            btnGenerateDxf.disabled = true;
            btnGenerateDxf.classList.add('opacity-75', 'cursor-wait');
            textGenerateDxf.innerText = 'MEMPROSES...';

            // Menggunakan FormData karena kita mungkin ngirim File (Custom Kop)
            const formData = new FormData(formExportDxf);
            
            // Tambahan data lain jika perlu (contoh survey_id)
            // formData.append('survey_id', '123');
 
            // Fetch ke Backend
            fetch(PROJECT_CONFIG.urls.exportDxfAdvanced, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken') 
                    // Jangan set Content-Type ke application/json, 
                    // biarkan browser otomatis set multipart/form-data biar file kebaca.
                },
                body: formData
            })
            .then(response => {
                if (!response.ok) throw new Error('Gagal dari server');
                return response.blob(); 
            })
            .then(blob => {
                // Auto Download
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                
                const grafikType = formData.get('grafik').toUpperCase();
                const dateStr = new Date().toISOString().slice(0, 10);
                a.download = `CIVILIX_${grafikType}_${dateStr}.dxf`; 
                
                document.body.appendChild(a);
                a.click();
                
                // Cleanup
                window.URL.revokeObjectURL(url);
                a.remove();
                resetDxfButton();
            })
            .catch(error => {
                console.error('Error generating:', error);
                alert('Terjadi kesalahan memproses file CAD. Pastikan data dari STA awal ke akhir valid.');
                resetDxfButton();
            });

            function resetDxfButton() {
                btnGenerateDxf.disabled = false;
                btnGenerateDxf.classList.remove('opacity-75', 'cursor-wait');
                textGenerateDxf.innerText = originalText;
            }
        });
    }
});