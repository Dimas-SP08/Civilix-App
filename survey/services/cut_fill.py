import json
from django.http import JsonResponse
from ..models import CalculatedResult

def save_design_data(request, project):
        
    # Parse data JSON dari JavaScript
    data = json.loads(request.body)
    
    # 1. Update Tabel Project (Template Jalan)
    template_data = data.get('template', {})
    
    project.lane_width = template_data.get('lane_width', 3.5)
    project.lane_slope = template_data.get('lane_slope', -2.0)
    project.shoulder_width = template_data.get('shoulder_width', 1.5)
    project.shoulder_slope = template_data.get('shoulder_slope', -4.0)
    project.save() # Simpan parameter ke database

    # 2. Update Tabel CalculatedResult (Elevasi As)
    elevations_data = data.get('elevations', [])
    
    for item in elevations_data:
        # Cari baris berdasarkan ID
        res = CalculatedResult.objects.get(id=item['id'])
        
        if item['design_elevation'] is not None:
            res.design_elevation = item['design_elevation']
        else:
            res.design_elevation = None
        res.save() # Simpan elevasi ke database
    total_cut, total_fill = calculate_project_volume(project)
    return total_cut, total_fill
    # 3. Lakukan Perhitungan Cut & Fill 

def calculate_project_volume(project):
    """
    Fungsi untuk menghitung total Galian & Timbunan menggunakan 
    metode Average End Area dengan Typical Cross Section.
    """
    # 1. Ambil Parameter Template Jalan dari Project
    w_lane = project.lane_width
    s_lane = project.lane_slope / 100        # Ubah persen jadi desimal (contoh: -2% jadi -0.02)
    w_shoulder = project.shoulder_width
    s_shoulder = project.shoulder_slope / 100

    # Total lebar jalan (kiri + kanan)
    half_width = w_lane + w_shoulder
    total_width = half_width * 2

    if total_width == 0:
        return 0, 0 # Hindari error dibagi nol kalau user belum input lebar

    # 2. Hitung Rata-rata Penurunan Elevasi karena Kemiringan (Slope/Camber)
    # Ini pake rumus luas trapesium untuk nyari "rata-rata" tinggi desain di luar as jalan.
    y_lane = w_lane * s_lane
    y_shoulder = y_lane + (w_shoulder * s_shoulder)

    area_lane = 0.5 * (0 + y_lane) * w_lane
    area_shoulder = 0.5 * (y_lane + y_shoulder) * w_shoulder
    total_offset_area = area_lane + area_shoulder


    # avg_slope_drop adalah seberapa turun garis desain secara rata-rata dibanding titik AS (Center)
    avg_slope_drop = total_offset_area / half_width

    results = CalculatedResult.objects.filter(project=project).order_by('id')
    
    total_cut = 0
    total_fill = 0
    
    # KITA SIAPIN VARIABEL "MEMORY" DI LUAR LOOP
    prev_persegi = 0 

    for i, res in enumerate(results):
        
        # 1. KUMPULIN ELEVASI TANAH ASLI
        titik_sayap = res.c_section.all()
        elev_as = []
        
        if res.elevation is not None:
            elev_as.append(res.elevation)

        for titik in titik_sayap:
            if titik.elevation is not None:
                elev_as.append(titik.elevation)
                
        elev_as_avg = sum(elev_as) / len(elev_as) if elev_as else 0
        
        # [PENTING 1] Kasih nilai default untuk persegi kalau user belum isi elevasi desain
        persegi = 0 
        
        # 2. HITUNG LUAS AREA (PERSEGI) STASIUN INI
        if res.design_elevation is not None:
            design_elev = res.design_elevation + avg_slope_drop
            height_diff = design_elev - elev_as_avg 
            persegi = height_diff * total_width
            
        # 3. HITUNG VOLUME (Mulai dari Stasiun Kedua / i > 0)
        if i > 0:
            distance = res.distance_avg if res.distance_avg else 0
            if distance == None or distance == 0:
                distance = res.distance if res.distance else 0

            A1 = prev_persegi 
            A2 = persegi       

            vol_cut = 0.0
            vol_fill = 0.0

            # KONDISI 1: Keduanya sejenis
            if (A1 >= 0 and A2 >= 0) or (A1 <= 0 and A2 <= 0):
                avg_area = (A1 + A2) / 2
                volume = avg_area * distance
                
                if volume > 0:
                    vol_fill = abs(volume)
                elif volume < 0:
                    vol_cut = abs(volume)

            # KONDISI 2: Terjadi persilangan
            else:
                abs_A1 = abs(A1)
                abs_A2 = abs(A2)
                
                # [PENTING 2] Pengaman ZeroDivisionError kalau kebetulan luasan dua-duanya persis 0
                total_abs_area = abs_A1 + abs_A2
                if total_abs_area > 0:
                    d1 = distance * (abs_A1 / total_abs_area)
                    d2 = distance * (abs_A2 / total_abs_area)
                    
                    vol1 = (abs_A1 / 2) * d1
                    vol2 = (abs_A2 / 2) * d2
                    
                    if A1 > 0: 
                        vol_fill = vol1
                        vol_cut = vol2
                    else:      
                        vol_cut = vol1
                        vol_fill = vol2

            # 4. SIMPAN KE MODEL
            res.cut_volume = vol_cut
            res.fill_volume = vol_fill
            
            # [PENTING 3] JANGAN LUPA DI-SAVE! Kalau nggak, datanya nggak masuk database
            res.save() 
            
            # [PENTING 4] JUMLAHIN TOTAL CUT & FILL BIAR FUNGSI INI BISA RETURN NILAINYA
            total_cut += vol_cut
            total_fill += vol_fill

        # 5. KUNCI MAGIC-NYA! 
        # [PENTING 5] INDENTASI HARUS DI SINI! (Sejajar dengan if i > 0)
        # Biar saat stasiun pertama (i=0) diproses, dia tetep nyimpen luasan 'persegi'-nya
        # untuk dipakai di stasiun kedua (i=1).
        prev_persegi = persegi
    
    return total_cut, total_fill