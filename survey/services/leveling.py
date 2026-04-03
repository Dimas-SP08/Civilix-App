from django.http import JsonResponse
from django.db import transaction
from ..models import CalculatedResult

def process_leveling_data(project):
    # 1. Ambil data input
    raw_data = project.leveling_data.all().order_by('id')
    
    if not raw_data.exists():
        # Opsional: Jika input kosong, hapus semua hasil
        project.results.all().delete()
        return JsonResponse({'status': 'error', 'message': 'Belum ada data pengukuran!'}, status=400)

    # Kita tampung hasil hitungan matematika di List Dictionary dulu
    # Supaya kode rapi dan tidak bolak-balik akses DB
    final_data_list = []

    # ==========================================
    # BAGIAN A: LOGIKA MATEMATIKA (Hitung di Memory)
    # ==========================================
    
    # --- KONDISI 1: CLOSED LOOP (Tertutup) ---
    if project.survey_type == 'CLOSED':
        temp_results = []
        total_dist_loop = 0.0
        total_delta_h_loop = 0.0

        for i in range(len(raw_data)):
            row_curr = raw_data[i]
            row_prev = raw_data[i] if i == 0 else raw_data[i-1]

            # 1. Hitung Jarak (Pergi)
            dist = row_curr.distance
            if dist is None or dist == 0:
                dist_bs = 0.0; dist_fs= 0.0
                if row_prev.bs_top and row_prev.bs_bot: dist_bs = abs(row_prev.bs_top - row_prev.bs_bot) * 100
                if row_curr.fs_top and row_curr.fs_bot: dist_fs = abs(row_curr.fs_top - row_curr.fs_bot) * 100
                dist = dist_bs + dist_fs if i > 0 else 0.0
            
            # 2. Hitung Jarak (Pulang)
            dist_bwd = row_curr.distance_bwd or 0.0
            if dist_bwd == 0 and row_curr.bwd_bs_top and row_prev.bwd_fs_top:
                 d_bs_b = abs(row_curr.bwd_bs_top - row_curr.bwd_bs_bot) * 100
                 d_fs_b = abs(row_prev.bwd_fs_top - row_prev.bwd_fs_bot) * 100
                 dist_bwd = d_bs_b + d_fs_b

            # 3. Benang & Delta H
            bs = float(row_prev.bs_mid or 0); fs = float(row_curr.fs_mid or 0)
            if row_prev.bs_top and row_prev.bs_bot: bs = (row_prev.bs_top + row_prev.bs_bot) / 2
            if row_curr.fs_top and row_curr.fs_bot: fs = (row_curr.fs_top + row_curr.fs_bot) / 2
            
            # Untuk display Backsight di row ini
            bs2 = float(row_curr.bs_mid or 0)
            if row_curr.bs_top and row_curr.bs_bot: bs2 = (row_curr.bs_top + row_curr.bs_bot) / 2

            bwd_bs = float(row_curr.bwd_bs_mid or 0); bwd_fs = float(row_prev.bwd_fs_mid or 0)
            if row_curr.bwd_bs_top and row_curr.bwd_bs_bot: bwd_bs = (row_curr.bwd_bs_top + row_curr.bwd_bs_bot) / 2
            
            bwd_fs2 = float(row_curr.bwd_fs_mid or 0)
            if row_curr.bwd_fs_top and row_curr.bwd_fs_bot: bwd_fs2 = (row_curr.bwd_fs_top + row_curr.bwd_fs_bot) / 2

            if row_prev.bwd_fs_top and row_prev.bwd_fs_bot: bwd_fs = (row_prev.bwd_fs_top + row_prev.bwd_fs_bot) / 2

            height_diff = (bs - fs) if i > 0 else 0.0
            height_diff_bwd_raw = (bwd_bs - bwd_fs) if i > 0 else 0.0
            height_diff_bwd = -1 * height_diff_bwd_raw  # Kita balik tanda untuk logika closed loop


            # Logic Single/Double Run
            if dist_bwd > 0:
                height_diff_avg = (height_diff + height_diff_bwd)/2
                dist_avg = (dist + dist_bwd)/2
            else:
                height_diff_avg = height_diff
                dist_avg = dist 

            total_dist_loop += dist_avg
            total_delta_h_loop += height_diff_avg

            temp_results.append({
                'source_row': row_curr, # <--- INI PENTING (ID ASLI)
                'station': row_curr.station,
                'bs': bs2, 'fs': fs,
                'bwd_bs': bwd_bs, 'bwd_fs': bwd_fs2,
                'dist': dist, 'dist_bwd': dist_bwd, 'dist_avg': dist_avg,
                'hd': height_diff, 'hd_bwd': height_diff_bwd, 'hd_avg': height_diff_avg
            })

        # Koreksi
        kr_total = -1 * total_delta_h_loop 
        curr_elev = project.initial_elevation
        curr_dist = 0.0

        for i, item in enumerate(temp_results):
            correction = 0.0
            if i > 0 and total_dist_loop > 0:
                correction = (item['dist_avg'] / total_dist_loop) * kr_total
            
            eff_hd = item['hd_avg'] + correction
            curr_elev += eff_hd
            curr_dist += item['dist_avg']
            status = "RISE" if eff_hd > 0 else "FALL" if eff_hd < 0 else "FLAT"

            final_data_list.append({
                'source_row': item['source_row'], # Bawa ID Asli
                'station': item['station'],
                'backsight': item['bs'], 'foresight': item['fs'],
                'bwd_backsight': item['bwd_bs'], 'bwd_foresight': item['bwd_fs'],
                'distance': item['dist'], 'distance_bwd': item['dist_bwd'], 'distance_avg': item['dist_avg'],
                'height_difference': item['hd'], 'height_difference_bwd': item['hd_bwd'], 'height_difference_avg': item['hd_avg'],
                'correction': correction,
                'elevation': curr_elev,
                'cumulative_distance': curr_dist,
                'status': status
            })

    # --- KONDISI 2: OPEN LOOP (Terbuka) ---
    elif project.survey_type == 'OPEN':
        curr_elev = project.initial_elevation
        curr_dist = 0.0
        
        for i in range(len(raw_data)):
            row_curr = raw_data[i]
            row_prev = raw_data[i] if i == 0 else raw_data[i-1]
            
            # Hitung Jarak
            dist = row_curr.distance
            if dist is None or dist == 0:
                dist_bs = 0.0; dist_fs= 0.0
                if row_prev.bs_top and row_prev.bs_bot: dist_bs = abs(row_prev.bs_top - row_prev.bs_bot) * 100
                if row_curr.fs_top and row_curr.fs_bot: dist_fs = abs(row_curr.fs_top - row_curr.fs_bot) * 100
                dist = dist_bs + dist_fs if i > 0 else 0.0
            
            # Hitung Delta H
            bs = float(row_prev.bs_mid or 0); fs = float(row_curr.fs_mid or 0)
            if row_prev.bs_top and row_prev.bs_bot: bs = (row_prev.bs_top + row_prev.bs_bot) / 2
            if row_curr.fs_top and row_curr.fs_bot: fs = (row_curr.fs_top + row_curr.fs_bot) / 2
            
            bs2 = float(row_curr.bs_mid or 0)
            if row_curr.bs_top and row_curr.bs_bot: bs2 = (row_curr.bs_top + row_curr.bs_bot) / 2

            height_diff = (bs - fs) if i > 0 else 0.0
            curr_elev += height_diff
            curr_dist += dist
            status = "RISE" if height_diff > 0 else "FALL" if height_diff < 0 else "FLAT"

            final_data_list.append({
                'source_row': row_curr, # Bawa ID Asli
                'station': row_curr.station,
                'backsight': bs2, 'foresight': fs,
                'distance': dist,
                'height_difference': height_diff,
                'elevation': curr_elev,
                'cumulative_distance': curr_dist,
                'status': status,
                # Reset nilai closed
                'correction': 0, 'distance_bwd': None, 'distance_avg': None,
                'bwd_backsight': None, 'bwd_foresight': None
            })

    # ==========================================
    # BAGIAN B: SIMPAN KE DATABASE (Aman & Stabil)
    # ==========================================
    
    with transaction.atomic():
        # Disini magic-nya. Kita pakai update_or_create berdasarkan 'source_row'
        # source_row adalah ID unik dari input.
        
        for data in final_data_list:
            CalculatedResult.objects.update_or_create(
                project=project,
                source_row=data['source_row'], # <-- KUNCI JODOHNYA DISINI
                defaults={
                    'station': data['station'],
                    'backsight': data['backsight'],
                    'foresight': data['foresight'],
                    'distance': data['distance'],
                    'height_difference': data.get('height_difference', 0),
                    'elevation': data['elevation'],
                    'cumulative_distance': data['cumulative_distance'],
                    'status': data['status'],
                    # Field Closed (akan None kalau Open)
                    'bwd_backsight': data.get('bwd_backsight'),
                    'bwd_foresight': data.get('bwd_foresight'),
                    'distance_bwd': data.get('distance_bwd'),
                    'distance_avg': data.get('distance_avg'),
                    'height_difference_bwd': data.get('height_difference_bwd'),
                    'height_difference_avg': data.get('height_difference_avg'),
                    'correction': data.get('correction', 0),
                }
            )
            
    # Catatan: Tidak perlu kode penghapusan manual.
    # Karena kita pakai models.CASCADE di database, 
    # kalau user hapus Input ID 3, Django otomatis hapus Result ID 3 di background.

    return JsonResponse({'status': 'success', 'message': 'Perhitungan sukses & Data aman!'})