// --- project-api.js ---

function toggleProjectStatus() {
    console.log("Tombol Status Diklik"); // Cek di Console browser apakah muncul tulisan ini

    // Cek apakah Config sudah terbaca
    if (typeof PROJECT_CONFIG === 'undefined') {
        alert("Error: PROJECT_CONFIG belum dimuat. Pastikan urutan script di HTML benar.");
        return;
    }

    const btn = document.getElementById('statusBadge');
    // Efek loading visual
    btn.classList.add('opacity-50', 'cursor-not-allowed');
    
    // Kirim request ke server
    fetch(PROJECT_CONFIG.urls.toggleStatus, {
        method: 'POST',
        headers: {
            'X-CSRFToken': PROJECT_CONFIG.csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        // Cek jika ada error dari server (misal 403 Forbidden atau 500 Error)
        if (!response.ok) {
            throw new Error(`HTTP Error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Response Server:", data); // Debugging response
        if (data.status === 'success') {
            window.location.reload(); // Reload halaman jika sukses
        } else {
            alert("Gagal mengubah status: " + data.message);
            btn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    })
    .catch(error => {
        console.error('Error Detail:', error);
        alert("Terjadi kesalahan sistem: " + error.message);
        btn.classList.remove('opacity-50', 'cursor-not-allowed');
    });
}

// ... (Biarkan fungsi updateProjectDetails dan deleteProjectApi tetap seperti sebelumnya)
function updateProjectDetails() {
    const btn = document.getElementById('btnUpdateProject');
    const originalContent = btn.innerHTML;

    const data = {
        project_name: document.getElementById('setting_project_name').value,
        initial_elevation: document.getElementById('setting_initial_elevation').value,
        purpose: document.getElementById('setting_purpose').value
    };

    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Saving...';
    lucide.createIcons();

    fetch(PROJECT_CONFIG.urls.updateProject, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': PROJECT_CONFIG.csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Project updated successfully!');
            window.location.reload(); 
        } else {
            alert('Error: ' + data.message);
            btn.disabled = false;
            btn.innerHTML = originalContent;
            lucide.createIcons();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update settings.');
        btn.disabled = false;
        btn.innerHTML = originalContent;
        lucide.createIcons();
    });
}

function deleteProjectApi(projectId, buttonElement) {
    if (!confirm("Are you sure to delete this project? This cannot be undone.")) {
        return;
    }

    const url = PROJECT_CONFIG.urls.deleteProject.replace('0', projectId);
    const originalHtml = buttonElement.innerHTML;
    
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i>';
    lucide.createIcons();

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': PROJECT_CONFIG.csrfToken,
            'Content-Type': 'application/json'
        },
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(errorData.message || 'Failed to delete project.');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);
            window.location.href = PROJECT_CONFIG.urls.redirectIndex;
        } else {
            throw new Error(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Gagal menghapus data: " + error.message);
        buttonElement.disabled = false;
        buttonElement.innerHTML = originalHtml;
        lucide.createIcons();
    });
}



// Civilix-App/survey/static/survey/js/project-api.js

// ... existing functions ...

function createCrossSection(btnElement) {
    if (!confirm("Generate default Cross Section points (A, B, C, D) for all stations?")) return;

    // Save original button state
    const originalContent = btnElement.innerHTML;
    
    // UI Loading State
    btnElement.disabled = true;
    btnElement.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Processing...';
    lucide.createIcons(); // Refresh icons

    // Fetch API
    fetch(PROJECT_CONFIG.urls.createCSection, {
        method: 'POST',
        headers: {
            'X-CSRFToken': PROJECT_CONFIG.csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);
            // Refresh to see the changes (if you have a CS table/view)
            window.location.reload(); 
        } else if (data.status === 'info') {
             alert(data.message);
             // Restore button
             btnElement.disabled = false;
             btnElement.innerHTML = originalContent;
             lucide.createIcons();
        } else {
            alert("Error: " + data.message);
            btnElement.disabled = false;
            btnElement.innerHTML = originalContent;
            lucide.createIcons();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("System error occurred.");
        btnElement.disabled = false;
        btnElement.innerHTML = originalContent;
        lucide.createIcons();
    });
}



document.addEventListener('DOMContentLoaded', function() {
    // Ambil semua tombol dengan ID btn-generate-report (buat handle tombol generate & regenerate)
    const btnGenerates = document.querySelectorAll('#btn-generate-report');
    const noReportState = document.getElementById('no-report-state');
    const hasReportState = document.getElementById('has-report-state');
    const reportContent = document.getElementById('report-content');

    btnGenerates.forEach(btn => {
        btn.addEventListener('click', function() {
            const apiUrl = this.getAttribute('data-url');
            
            // 1. Simpan teks asli dan ubah jadi loading state
            const originalHtml = this.innerHTML;
            this.disabled = true;
            this.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 mr-2 animate-spin"></i> Processing AI...';
            if (typeof lucide !== 'undefined') lucide.createIcons();

            // 2. Tembak API ke Django
            fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // Pake fungsi getCookie bawaan lo
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // 3. Sembunyikan pesan "Belum ada laporan" jika ada
                    if (noReportState) noReportState.classList.add('hidden');
                    
                    // 4. Munculkan area laporan
                    if (hasReportState) hasReportState.classList.remove('hidden');
                    
                    // 5. Masukkan teks laporan dari AI ke dalam div HTML
                    if (reportContent) reportContent.textContent = data.report;
                    
                    // Kembalikan tombol ke semula (opsional, karena biasanya laporannya udah nutupin tombol generate)
                    this.disabled = false;
                    this.innerHTML = originalHtml;
                    if (typeof lucide !== 'undefined') lucide.createIcons();
                    
                    // Tampilkan notifikasi sukses kecil (opsional)
                    alert("Berhasil! Laporan AI telah dibuat.");
                } else {
                    alert('Gagal membuat laporan: ' + data.message);
                    this.disabled = false;
                    this.innerHTML = originalHtml;
                    if (typeof lucide !== 'undefined') lucide.createIcons();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Terjadi kesalahan jaringan atau server.');
                this.disabled = false;
                this.innerHTML = originalHtml;
                if (typeof lucide !== 'undefined') lucide.createIcons();
            });
        });
    });
});




document.addEventListener('DOMContentLoaded', function() {
    // Cari elemen-elemen Modal
    const reportModal = document.getElementById('report-modal');
    const btnOpenModal = document.getElementById('btn-open-report-modal');
    const btnCloseModal = document.getElementById('btn-close-report-modal');
    const btnCloseModalFooter = document.getElementById('btn-close-report-modal-footer');
    const modalOverlay = document.getElementById('report-modal-overlay');

    // Fungsi untuk membuka modal
    function openModal() {
        if (reportModal) {
            reportModal.classList.remove('hidden');
            // Mencegah *scroll* pada halaman utama saat modal terbuka
            document.body.classList.add('overflow-hidden');
            // Refresh icon lucide di dalam modal
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }
    }

    // Fungsi untuk menutup modal
    function closeModal() {
        if (reportModal) {
            reportModal.classList.add('hidden');
            // Mengembalikan *scroll* pada halaman utama
            document.body.classList.remove('overflow-hidden');
        }
    }

    // Event Listener untuk tombol-tombol
    if (btnOpenModal) {
        btnOpenModal.addEventListener('click', openModal);
    }

    if (btnCloseModal) {
        btnCloseModal.addEventListener('click', closeModal);
    }

    if (btnCloseModalFooter) {
        btnCloseModalFooter.addEventListener('click', closeModal);
    }

    // Menutup modal jika user mengklik area latar belakang (overlay)
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeModal);
    }

    // Menutup modal jika user menekan tombol 'Esc' di keyboard
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && reportModal && !reportModal.classList.contains('hidden')) {
            closeModal();
        }
    });
});