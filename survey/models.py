from django.db import models
from django.conf import settings

# Model 1: "Folder" Project (Menyimpan parameter awal)
class Project(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="projects"
    )
    project_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    TRAVERSE_CHOICE = [
    ('OPEN', 'OPEN'),
    ('CLOSED', 'CLOSED'),
    ]

    survey_type = models.CharField(
        max_length=10, 
        choices=TRAVERSE_CHOICE, 
        default='OPEN'
    )

    # Data dari 'input_point.py' (Streamlit)
    initial_elevation = models.FloatField(
        default=100.0, 
        help_text="Elevasi (Z) awal dari titik pertama (dari init_amsl)"
    ) 
    purpose = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Tujuan survei (dari purpose)"
    )

    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ARCHIVED', 'Archived'),
    ]

    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='IN_PROGRESS' # Defaultnya proyek baru adalah In Progress
    )
    lane_width = models.FloatField(default=3.5, help_text="Lebar lajur utama (m)")
    lane_slope = models.FloatField(default=-2.0, help_text="Kemiringan lajur utama (%)")
    shoulder_width = models.FloatField(default=1.5, help_text="Lebar bahu jalan (m)")
    shoulder_slope = models.FloatField(default=-4.0, help_text="Kemiringan bahu jalan (%)")
    

    def __str__(self):
        return f"{self.project_name} (oleh {self.user.email})"


# Model 2: Data Mentah Sipat Datar (Lengkap dengan 3 Benang)
class LevelingData(models.Model):
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE,
        related_name="leveling_data" 
    )
    
    station = models.CharField(max_length=50, help_text="Example: 0+000, 0+100, dst.")
    
    # --- Data Backsight (BS) Lengkap ---
    bs_top = models.FloatField(null=True, blank=True, help_text="Benang Atas (BS)")
    bs_mid = models.FloatField(null=True,blank=True,help_text="Benang Tengah (BS) - WAJIB")
    bs_bot = models.FloatField(null=True, blank=True, help_text="Benang Bawah (BS)")
    
    # --- Data Foresight (FS) Lengkap ---
    fs_top = models.FloatField(null=True, blank=True, help_text="Benang Atas (FS)")
    fs_mid = models.FloatField(null=True,blank=True,help_text="Benang Tengah (FS) - WAJIB")
    fs_bot = models.FloatField(null=True, blank=True, help_text="Benang Bawah (FS)")
    
    bwd_bs_top = models.FloatField(null=True, blank=True)
    bwd_bs_mid = models.FloatField(null=True, blank=True) # Variable Baru
    bwd_bs_bot = models.FloatField(null=True, blank=True)
    
    bwd_fs_top = models.FloatField(null=True, blank=True)
    bwd_fs_mid = models.FloatField(null=True, blank=True) # Variable Baru
    bwd_fs_bot = models.FloatField(null=True, blank=True)

    # Jarak (bisa dihitung atau di-input manual)
    distance = models.FloatField(
        null=True, blank=True, 
        help_text="Jarak Datar (Optis atau Manual)"
    )

    distance_bwd = models.FloatField(
        null=True, blank=True, 
        help_text="Jarak Datar (Optis atau Manual)"
    )

    def __str__(self):
        return f"Data {self.station} (Proyek: {self.project.project_name})"
    
    # Fungsi ini menghitung Jarak Optis jika 'distance' kosong
    
    
    def save(self, *args, **kwargs):
        # 1. Cek Jarak Belakang (Backsight Distance)
        # Jika user mengosongkan distance_bwd, TAPI mereka ngisi Benang Atas & Bawah
        if not self.distance_bwd:
            if self.bwd_bs_top is not None and self.bwd_bs_bot is not None and self.bwd_fs_top is not None and self.bwd_fs_bot is not None:
                # Rumus Jarak Optis: (BA - BB) * 100
                distfs_bwd = abs(self.bwd_bs_top - self.bwd_bs_bot) * 100
                distbs_bwd = abs(self.bwd_fs_top - self.bwd_fs_bot) * 100
                self.distance_bwd = distbs_bwd + distfs_bwd

        # 2. Cek Jarak Muka (Foresight Distance)
        # Jika user mengosongkan distance, TAPI mereka ngisi Benang Atas & Bawah
        if not self.distance:
            if self.fs_top is not None and self.fs_bot is not None and self.bs_top is not None and self.bs_bot is not None:
                dist_fs = abs(self.fs_top - self.fs_bot) * 100
                dist_bs = abs(self.bs_top - self.bs_bot) * 100
                # Rata-rata Jarak Optis: (Dist_FS + Dist_BS) / 2
                self.distance = dist_bs + dist_fs


        # Panggil metode save asli bawaan Django buat nyimpen ke database
        super().save(*args, **kwargs)

    


# Model 3: Hasil Perhitungan (Output Olahan)
class CalculatedResult(models.Model):
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE,
        related_name="results" 
    )
    
    station = models.CharField(max_length=50, help_text="Exxample 0+100 ext...")
    source_row = models.OneToOneField(
        LevelingData,       # Nama model Input (Raw Data) kamu
        on_delete=models.CASCADE, # Kalo Input dihapus, Hasil ikut mati
        related_name='calculated_result',
        null=True, blank=True # Biar aman saat migrasi awal
    )
    backsight = models.FloatField(null=True, blank=True)
    foresight = models.FloatField(null=True, blank=True)
    
    bwd_backsight = models.FloatField(null=True, blank=True)
    bwd_foresight = models.FloatField(null=True, blank=True)
    
    distance = models.FloatField(null=True, blank=True)
    distance_bwd = models.FloatField(null=True, blank=True)
    distance_avg = models.FloatField(null=True, blank=True)

    design_elevation = models.FloatField(null=True, blank=True, help_text="Elevasi Rencana")
    
    # Menyimpan hasil hitungan volume di titik ini
    cut_volume = models.FloatField(default=0.0, help_text="Volume Galian (m3)")
    fill_volume = models.FloatField(default=0.0, help_text="Volume Timbunan (m3)")
    
    # Hasil hitungan dari logika 'Survey_Point'
    height_difference = models.FloatField(null=True, blank=True)
    height_difference_bwd = models.FloatField(null=True, blank=True)
    height_difference_avg = models.FloatField(null=True, blank=True)
    elevation = models.FloatField(help_text="Elevasi (AMSL) hasil hitungan")
    
    correction = models.FloatField(null=True, blank=True)
    cumulative_distance = models.FloatField()
    status = models.CharField(max_length=10, help_text="RISE, FALL, atau FLAT")

    def __str__(self):
        return f"Hasil {self.station} (Proyek: {self.project.project_name})"


class CrossSection(models.Model):
    """
    Menyimpan titik-titik detail (A, B, C, D) untuk setiap stasiun.
    Satu CalculatedResult (Stasiun) bisa punya banyak CrossSection (Titik).
    """
    # Menghubungkan titik ini ke Stasiun induknya (misal: 0+100)
    station = models.ForeignKey(
        CalculatedResult, 
        on_delete=models.CASCADE,
        related_name="c_section" 
    )

    
    
    # Label titik (Contoh: "A", "B", "C", "D" atau "Tepi Kiri")
    label = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Label titik, misal: A, B, C, D"
    )
 
    # Jarak dari As (Center Line). 
    # Konvensi: Kiri = Negatif (-), Kanan = Positif (+)
    distance = models.FloatField(help_text="Jarak dari As (m). Kiri (-), Kanan (+)")

    # Data Bacaan Benang
    top = models.FloatField(null=True, blank=True, help_text="Benang Atas")
    mid = models.FloatField(help_text="Benang Tengah (Wajib)")
    bot = models.FloatField(null=True, blank=True, help_text="Benang Bawah")

    height_difference = models.FloatField(null=True, blank=True, help_text="height difference")
    # Hasil Perhitungan Elevasi (Disimpan otomatis)
    elevation = models.FloatField(blank=True, null=True, help_text="Elevasi Titik")
    
    # Keterangan tambahan (opsional)
    description = models.CharField(max_length=100, blank=True, null=True)

   
    

    def __str__(self): 
        return f"{self.station.station} - {self.label} ({self.distance}m)"
# Model 4: Laporan AI (Output Olahan)
class AIReport(models.Model):
    project = models.OneToOneField(
        Project, 
        on_delete=models.CASCADE,
        related_name="ai_report" 
    )
    report_text = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Laporan AI untuk {self.project.project_name}"