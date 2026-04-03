from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from account import models
from .models import Project, LevelingData, CalculatedResult

class LevelingCalculationTest(TestCase):
    def setUp(self):
        # 1. ARRANGE: Siapkan User dan Client (Browser bayangan)
        User = get_user_model()
        self.user = User.objects.create_user(email='admin@civilix.com', password='password123', nama='sahawelah')
        self.client = Client()
        self.client.login(email='admin@civilix.com', password='password123') # Login otomatis

        # Siapkan Project dengan elevasi awal 100.0 (Sesuai model Project kamu)
        self.project = Project.objects.create(
            user=self.user,
            project_name="Test Kalkulasi Sipat Datar",
            survey_type="CLOSED",
            initial_elevation=100.0 
        )

        # Siapkan Data Mentah (LevelingData)
        # Misal: Stasiun 0+000 (Titik Awal)
        self.data_1 = LevelingData.objects.create(
            project=self.project,
            station="0+000",
            bs_mid=1.500, # Benang Tengah Belakang
            bs_top=1.700,
            bs_bot=1.300,
            fs_mid=0.000,
            fs_top=0.000,
            fs_bot=0.000,

            bwd_bs_mid=1.500, # Benang Tengah Belakang
            bwd_bs_top=1.700,
            bwd_bs_bot=1.300,
            bwd_fs_mid=0.000,
            bwd_fs_top=0.000,
            bwd_fs_bot=0.000,
            distance=0.0,
            distance_bwd=0.0
        )

        # Misal: Stasiun 0+050 (Titik Kedua)
        self.data_2 = LevelingData.objects.create(
            project=self.project,
            station="0+050",
            bs_top = 1.500,
            bs_mid=1.200, 
            bs_bot = 1.300,

            fs_top = 1.100,
            fs_mid=1.100, # Benang Tengah Muka (Bacaan dari setup alat sebelumnya)
            fs_bot = 0.900,

            bwd_bs_top = 1.500,
            bwd_bs_mid=1.200, 
            bwd_bs_bot = 1.300,

            bwd_fs_top = 1.100,
            bwd_fs_mid=1.100, # Benang Tengah Muka (Bacaan dari setup alat sebelumnya)
            bwd_fs_bot = 0.900,
            distance=50.0,
            distance_bwd=50.0
        )

    def test_perhitungan_elevasi_dan_beda_tinggi(self):
        """Mengecek apakah rumus Elevasi = Elevasi_Awal + (BS - FS) berjalan benar"""
        
        # 2. ACT: Panggil endpoint API untuk melakukan kalkulasi
        # Pastikan nama URL di survey/urls.py kamu sesuai, misal: 'survey:api_calculate_leveling'
        url = reverse('survey:api_calculate', args=[self.project.id]) 
        response = self.client.post(url)
        
        # Pastikan API merespons dengan sukses (Status Code 200)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        # 3. ASSERT: Tarik hasil perhitungannya dari database
        hasil_stasiun_1 = CalculatedResult.objects.get(project=self.project, station="0+000")
        hasil_stasiun_2 = CalculatedResult.objects.get(project=self.project, station="0+050")

        # Cek Titik 1: Elevasi harus sama dengan elevasi awal proyek (100.0)
        self.assertEqual(hasil_stasiun_1.elevation, 100.0)
        self.assertEqual(hasil_stasiun_1.height_difference, 0.0)

        # Cek Titik 2: 
        # mid = bs_t + bs_b / 2 = (1.700 + 1.300) / 2 = 1.500
        # mid = fs_t + fs_b / 2 = (1.100 + 0.900) / 2 = 1.000
        # Beda tinggi = BS(sebelumnya) - FS(sekarang) = 1.500 - 1.000 = 0.500
        # Toleransi angka desimal float sangat penting di Python!
        self.assertAlmostEqual(hasil_stasiun_2.height_difference, 0.500, places=3)
        
        self.assertEqual(hasil_stasiun_2.correction, 0)

        # Cek Elevasi Titik 2: Elevasi_Awal + Beda Tinggi = 100.0 + 0.500 = 100.500
        self.assertAlmostEqual(hasil_stasiun_2.elevation, 100.500, places=3)


        