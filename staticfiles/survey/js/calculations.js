// --- calculations.js ---

// 1. SAVE & CALCULATE VOLUME
function saveAndCalculateVolume() {

    // 1. Ambil Nilai dari Input Template Jalan (Global)
    const laneWidth = parseFloat(document.getElementById('input_lane_width').value) || 0;
    const laneSlope = parseFloat(document.getElementById('input_lane_slope').value) || 0;
    const shoulderWidth = parseFloat(document.getElementById('input_shoulder_width').value) || 0;
    const shoulderSlope = parseFloat(document.getElementById('input_shoulder_slope').value) || 0;

    // 2. Ambil Semua Baris Data dari Tabel Design Elevation
    const rows = document.querySelectorAll('.design-row');
    const designData = [];
    let hasInput = false;

    rows.forEach(row => {
        const rowId = row.getAttribute('data-id');
        const designInput = row.querySelector('.input-design').value;
        
        // Simpan id baris dan elevasinya ke dalam array
        designData.push({
            id: rowId,
            design_elevation: designInput ? parseFloat(designInput) : null,
        });

        if (designInput) hasInput = true;
    });

    // Validasi: Cegah hitung jika kosong melompong
    if (!hasInput) {
        alert("Mohon isi 'Design Elev' setidaknya pada satu stasiun.");
        return;
    }

    // 3. Susun Data (Payload) untuk dikirim ke Backend
    // Kita pisahkan antara 'template' jalan dan list 'elevations'
    const payload = {
        template: {
            lane_width: laneWidth,
            lane_slope: laneSlope,
            shoulder_width: shoulderWidth,
            shoulder_slope: shoulderSlope
        },
        elevations: designData
    };

    // 4. Ubah Tampilan Tombol Jadi Loading
    const btn = document.getElementById('btnSaveVol');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin mr-2"></i> Calculating...';
    lucide.createIcons();

    // 5. Kirim Request ke Django API
    fetch(PROJECT_CONFIG.urls.saveDesign, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': PROJECT_CONFIG.csrfToken
        },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            alert(`Perhitungan Selesai!\n\nTotal Cut: ${data.total_cut} m³\nTotal Fill: ${data.total_fill} m³`);
            window.location.reload(); // Refresh halaman agar tabel terupdate
        } else {
            alert("Error: " + data.message);
            btn.disabled = false;
            btn.innerHTML = originalText;
            lucide.createIcons();
        }
    })
    .catch(err => {
        console.error(err);
        alert("Gagal menghubungi server. Pastikan URL API benar.");
        btn.disabled = false;
        btn.innerHTML = originalText;
        lucide.createIcons();
    });
}

// 2. AUTO SLOPE GENERATOR
function generateSlope() {
    const startElev = parseFloat(document.getElementById('gen_start_elev').value);
    const endElev = parseFloat(document.getElementById('gen_end_elev').value);
    const inputs = document.querySelectorAll('.input-design');
    
    if (isNaN(startElev) || isNaN(endElev)) {
        alert("Isi Elevasi Awal dan Akhir dulu!");
        return;
    }

    const totalPoints = inputs.length;
    if (totalPoints < 2) return;

    const step = (endElev - startElev) / (totalPoints - 1);

    inputs.forEach((input, index) => {
        const val = startElev + (step * index);
        input.value = val.toFixed(3);
    });

    alert("Tabel otomatis terisi! Klik 'Save & Calculate' untuk memproses volume.");
}

// 3. MAIN PROCESS ANIMATION (Recalculate Leveling)
function runProcessAnimation() {
    const icon = document.getElementById('refresh-icon');
    
    icon.classList.add('animate-spin');
    
    fetch(PROJECT_CONFIG.urls.calculate, {
        method: 'POST',
        headers: {
            'X-CSRFToken': PROJECT_CONFIG.csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        setTimeout(() => {
            icon.classList.remove('animate-spin');
            
            if (data.status === 'success') {
                window.location.reload(); 
            } else {
                alert("Gagal: " + data.message);
            }
        }, 800); 
    })
    .catch(error => {
        console.error('Error:', error);
        icon.classList.remove('animate-spin');
        alert("Terjadi kesalahan sistem.");
    });
}



function saveAndRecalculateCS() {
    // 1. Kumpulin semua data dari inputan di layar (HANYA di bagian Cross Section Edit)
    const rows = document.querySelectorAll('#accordion-container .cs-data-row');
    const payload = [];

    rows.forEach(row => {
        const id = row.getAttribute('data-row-id');
        // Ambil value dari class input siluman kita
        const label = row.querySelector('.cs-input-label')?.value || '';
        const distance = row.querySelector('.cs-input-dist')?.value || '';
        const top = row.querySelector('.cs-input-top')?.value || '';
        const mid = row.querySelector('.cs-input-mid')?.value || '';
        const bot = row.querySelector('.cs-input-bot')?.value || '';
        
        // Kita masukin ke payload untuk dikirim massal
        payload.push({
            id: id,
            label: label,
            distance: distance,
            top: top,
            mid: mid,
            bot: bot
        });
    });

    // 2. Ubah tombol jadi status Loading
    const btn = document.getElementById('btnSaveRecalculateCS');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Processing...';
    lucide.createIcons();

    // 3. Tembak API Save (Bulk Update CS)
    // Pastikan PROJECT_CONFIG.urls.bulkUpdateCS udah bener ngarah ke views penyimpanannya
    fetch(PROJECT_CONFIG.urls.bulkUpdateCS, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PROJECT_CONFIG.csrfToken },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            // 4. Kalau Save sukses, langsung hajar API Calculate CS!
            return fetch(PROJECT_CONFIG.urls.calculate_CS, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': PROJECT_CONFIG.csrfToken }
            });
        } else {
            throw new Error("Gagal menyimpan data: " + data.message);
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            // 5. Beres semua, refresh halaman dan pindah ke tab Result!
            window.location.reload(); 
        } else {
            throw new Error("Data tersimpan, tapi gagal kalkulasi: " + data.message);
        }
    })
    .catch(err => {
        alert(err.message);
        btn.disabled = false;
        btn.innerHTML = originalText;
        lucide.createIcons();
    });
}