import json
from survey.models import LevelingData,CrossSection,AIReport,CalculatedResult
from survey.forms import ProjectForm
from django.db import transaction
import pandas as pd
from django.http import HttpResponse, JsonResponse
import io
from survey.utils.helper import to_float_or_none
from django.db.models.functions import Cast
from django.db.models import FloatField

def process_upload_CS_excel(project_id, excel_file):
    # 1. BACA EXCEL PAKAI PANDAS
    df = pd.read_excel(excel_file)
    
    # Validasi ringan: Pastikan kolom wajib ada biar gak error di tengah jalan
    required_columns = ['STA', 'Titik', 'Jarak_dari_As', 'BT']
    for col in required_columns:
        if col not in df.columns:
            return JsonResponse({'status': 'error', 'message': f'Kolom wajib "{col}" tidak ada di Excel!'}, status=400)

    # Buang baris yang kosong/nggak jelas
    df = df.dropna(subset=['STA', 'Titik', 'Jarak_dari_As', 'BT'])

    # 2. AMBIL DAFTAR STA DARI EXCEL
    # Kita ubah jadi string dan hapus spasi berlebih
    uploaded_stas = df['STA'].astype(str).str.strip().unique()
    
    # 3. CARI STA TERSEBUT DI DATABASE (LONG SECTION)
    # Jurus ini biar kenceng: Kita tarik semua objek STA sekaligus!
    stas_in_db = CalculatedResult.objects.filter(project_id=project_id, station__in=uploaded_stas)
    
    # Kita jadikan Dictionary -> {'0+000': <Objek CalculatedResult>, '0+050': <Objek>}
    sta_dict = {sta.station: sta for sta in stas_in_db}

    # 4. HAPUS DATA LAMA (ANTI DUPLIKAT)
    # Kalau user re-upload Excel, data CS yang lama di STA tersebut kita sapu bersih dulu
    CrossSection.objects.filter(station__in=stas_in_db).delete()

    # Wadah buat nyimpen data yang siap di-insert
    cs_to_create = []
    sta_not_found = set() # Buat nyimpen STA yang salah ketik / nggak ada

    # 5. LOOPING BACA BARIS EXCEL
    for index, row in df.iterrows():
        nama_sta = str(row['STA']).strip()
        
        # Kalau STA yang di Excel gak ada di Long Section Database, skip baris ini
        if nama_sta not in sta_dict:
            sta_not_found.add(nama_sta)
            continue
        
        sta_induk = sta_dict[nama_sta]

        # Amanin data angka (Pakai if else buat handle nilai kosong / NaN dari pandas)
        ba = to_float_or_none(row['BA']) if 'BA' in df.columns and pd.notna(row['BA']) else None
        bb = to_float_or_none(row['BB']) if 'BB' in df.columns and pd.notna(row['BB']) else None
        elevasi = to_float_or_none(row['Elevasi']) if 'Elevasi' in df.columns and pd.notna(row['Elevasi']) else None
        
        ket = str(row['Keterangan']) if 'Keterangan' in df.columns and pd.notna(row['Keterangan']) else ""
        if ket.lower() == 'nan': ket = "" # Jaga-jaga sifat aneh pandas

        # BIKIN OBJEK BARU TAPI JANGAN DI-SAVE DULU (Biar cepat)
        cs_to_create.append(CrossSection(
            station=sta_induk,
            label=str(row['Titik']).strip(),
            distance=to_float_or_none(row['Jarak_dari_As']),
            top=ba,
            mid=to_float_or_none(row['BT']),
            bot=bb,
            elevation=elevasi,
            description=ket
        ))

    # 6. INSERT KE DATABASE SEKALIGUS (BULK CREATE)
    # Jurus ini bikin masukin 5000 titik cuma butuh waktu 0.1 detik!
    if cs_to_create:
        CrossSection.objects.bulk_create(cs_to_create)

    return cs_to_create,sta_not_found

def process_update_thread(request, project):
    data = json.loads(request.body) # List of dictionaries
    rows_to_update = []
    
    # Ambil semua ID yang mau diupdate untuk query database
    ids = [item['id'] for item in data]
    existing_rows = LevelingData.objects.filter(id__in=ids, project=project)
    row_map = {row.id: row for row in existing_rows}

    for item in data:
        row = row_map.get(int(item['id']))
        if row:
            # Update field jika ada di data kiriman
            row.station = item.get('station', row.station)
            
            # Helper function untuk convert string kosong jadi None
            def parse_float(val):
                if val == '' or val is None: return None
                return float(val)

            row.bs_top = parse_float(item.get('bs_top'))
            row.bs_mid = parse_float(item.get('bs_mid')) # <-- UBAH INI
            row.bs_bot = parse_float(item.get('bs_bot'))
            
            row.fs_top = parse_float(item.get('fs_top'))
            row.fs_mid = parse_float(item.get('fs_mid')) # <-- UBAH INI
            row.fs_bot = parse_float(item.get('fs_bot'))

            row.bwd_bs_top = parse_float(item.get('bwd_bs_top'))
            row.bwd_bs_mid = parse_float(item.get('bwd_bs_mid')) # <-- UBAH INI (Jika CLOSED)
            row.bwd_bs_bot = parse_float(item.get('bwd_bs_bot'))
            
            row.bwd_fs_top = parse_float(item.get('bwd_fs_top'))
            row.bwd_fs_mid = parse_float(item.get('bwd_fs_mid')) # <-- UBAH INI (Jika CLOSED)
            row.bwd_fs_bot = parse_float(item.get('bwd_fs_bot'))
            
            row.distance = parse_float(item.get('distance'))
            row.distance_bwd = parse_float(item.get('distance_bwd'))
            
            rows_to_update.append(row)

    # Gunakan bulk_update untuk performa tinggi (1 query ke DB)
    fields_to_update = ['station', 'bs_top', 'bs_mid', 'bs_bot', 'fs_top', 'fs_mid', 'fs_bot','bwd_bs_top', 'bwd_bs_mid', 'bwd_bs_bot', 'bwd_fs_top', 'bwd_fs_mid', 'bwd_fs_bot', 'distance','distance_bwd']
    LevelingData.objects.bulk_update(rows_to_update, fields_to_update)

    return rows_to_update

def process_delete_thread(request, project_id):
    data = json.loads(request.body)
    ids = data.get('ids', [])
    
    if not ids:
        
        return deleted_count,False

    # Hapus data yang ID-nya ada di list DAN milik user yang login (security)
    deleted_count, _ = LevelingData.objects.filter(
        id__in=ids, 
        project__id=project_id, 
        project__user=request.user
    ).delete()

    return deleted_count,True
    
def process_update_project(request,project):
    data = json.loads(request.body)
        
    project.project_name = data.get('project_name', project.project_name)
    
    # Validasi Initial Elevation
    init_elev = data.get('initial_elevation')
    if init_elev is not None and init_elev != "":
        project.initial_elevation = float(init_elev)
        
    project.purpose = data.get('purpose', project.purpose)
    
    project.save()


def get_project_detail(request, project):
    # 1. Ambil Object Results
    results = list(project.results.all().order_by('id'))
    c_section = list(
    CrossSection.objects.select_related('station')
    .filter(station__project=project)
    .order_by('station__id', 'distance')  # <-- Cukup begini aja, Mail!
)
    
    total_cut = sum(res.cut_volume for res in results)
    total_fill = sum(res.fill_volume for res in results)
    elev = []
    h_diff_total = 0.0
    corr_total = 0.0
    cumulative_dist= 0.0
    if project.survey_type == 'CLOSED':
        for result in results:
            h_diff_total +=  result.height_difference_avg
            corr_total += result.correction
            
    for result in results:
       
        cumulative_dist = result.cumulative_distance
        elev.append(result.elevation)
    max_elev = max(elev) if elev else 0.0
    min_elev = min(elev) if elev else 0.0

    ai_result = AIReport.objects.filter(project=project).first()  # Ambil laporan AI jika ada
    text_ai = ai_result.report_text if ai_result else None  # Ambil teks laporan atau None jika tidak ada


    # 2. Ambil data spesifik dari LevelingData (Raw Data)
    # .values() mengambil kolom-kolom tertentu saja sebagai dictionary
    raw_data_values = project.leveling_data.all().order_by('id').values(
        'bs_top', 'bs_bot', 'fs_top', 'fs_bot','bwd_bs_top', 'bwd_bs_bot', 'bwd_fs_top', 'bwd_fs_bot'
    )

    # 3. Inject (tempelkan) data ke object results
    if len(results) == len(raw_data_values):
        for res, raw in zip(results, raw_data_values):
            # Ambil dari dictionary 'raw' dan pasang ke object 'res'
            res.bs_top = raw['bs_top']
            res.bs_bot = raw['bs_bot']
            res.fs_top = raw['fs_top']
            res.fs_bot = raw['fs_bot']
            res.bwd_bs_top = raw['bwd_bs_top']
            res.bwd_bs_bot = raw['bwd_bs_bot']
            res.bwd_fs_top = raw['bwd_fs_top']
            res.bwd_fs_bot = raw['bwd_fs_bot']
            
            
            # Sekarang object 'res' punya 4 atribut tambahan ini di memori

    
    # ... dst ...

    context = {
        'results': results,
        'cumulative_dist':cumulative_dist,
        'project': project,
        'h_avg_total':h_diff_total,
        'c_section':c_section,
        'corr_total':corr_total,
        'max_elev':max_elev,
        'min_elev':min_elev,
        'total_cut': total_cut,
        'total_fill': total_fill,
        'net_balance': total_cut - total_fill,
        'text_ai': text_ai,  # Tambahkan hasil AI ke context
        # ... context lainnya
    }
    return context


def process_create_project(request):
    data = json.loads(request.body)
    form = ProjectForm(data)
    if form.is_valid():
        # 1. Simpan project, tapi jangan langsung commit ke DB
        new_project = form.save(commit=False)
        
        # 2. Assign user yang sedang login
        new_project.user = request.user
        
        # 3. Simpan ke database
        new_project.save()
        
        # 4. Beri respons sukses & URL untuk redirect
        return new_project,True
    else:
        # Kirim kembali error form dalam format JSON
        return form,False

def process_delete_project( project):
    project.delete()
    pass

def process_upload_file(project,df):
    
        # 1. Baca file Excel menggunakan utility yang sudah ada
        

        new_data_objects = []
        
        # 3. Iterasi baris DataFrame dan persiapkan objek LevelingData
        for index, row in df.iterrows():
            # 1. Ambil Data Utama (Forward) dengan aman
            # Pakai row.get() supaya kalau kolom gak ada, dia gak error (return None)
            station = str(row['station'])
            
            bs_top = to_float_or_none(row.get('bs_top'))
            bs_mid = to_float_or_none(row.get('bs_mid'))
            bs_bot = to_float_or_none(row.get('bs_bot'))
            
            fs_top = to_float_or_none(row.get('fs_top'))
            fs_mid = to_float_or_none(row.get('fs_mid'))
            fs_bot = to_float_or_none(row.get('fs_bot'))
            # 2. Ambil Data Backward (Hanya jika CLOSED)
            # Kita set default None dulu
            bwd_bs_top = None
            bwd_bs_mid = None
            bwd_bs_bot = None
            bwd_fs_top = None
            bwd_fs_mid = None
            bwd_fs_bot = None

            if project.survey_type == 'CLOSED':
                # Ambil data backward, gunakan .get() agar aman jika kolom tidak ada di Excel
                bwd_bs_top = to_float_or_none(row.get('bwd_bs_top'))
                bwd_bs_mid = to_float_or_none(row.get('bwd_bs_mid'))
                bwd_bs_bot = to_float_or_none(row.get('bwd_bs_bot'))
                
                bwd_fs_top = to_float_or_none(row.get('bwd_fs_top'))
                bwd_fs_mid = to_float_or_none(row.get('bwd_fs_mid'))
                bwd_fs_bot = to_float_or_none(row.get('bwd_fs_bot'))

            # 3. Validasi Logic (Opsional tapi disarankan)
            # Kalau mau memastikan minimal ada data BS atau FS (agar tidak baris kosong total)
            # if bs_mid is None and fs_mid is None:
            #     continue  # Skip baris kosong

            # 4. SATU KALI Append Saja (Gabungkan semua data)
            new_data_objects.append(LevelingData(
                project=project,
                station=station,
                
                # Forward Data
                bs_top=bs_top,
                bs_mid=bs_mid,
                bs_bot=bs_bot,
                fs_top=fs_top,
                fs_mid=fs_mid,
                fs_bot=fs_bot,
                
                # Backward Data (Akan terisi jika CLOSED, atau None jika OPEN)
                bwd_bs_top=bwd_bs_top,
                bwd_bs_mid=bwd_bs_mid,
                bwd_bs_bot=bwd_bs_bot,
                bwd_fs_top=bwd_fs_top,
                bwd_fs_mid=bwd_fs_mid,
                bwd_fs_bot=bwd_fs_bot,
                
                # Jarak (Jika ada di excel)
                distance=to_float_or_none(row.get('distance')),
                distance_bwd=to_float_or_none(row.get('distance_bwd'))
            ))

        # 4. Simpan secara massal untuk performa cepat
        with transaction.atomic():
            LevelingData.objects.bulk_create(new_data_objects)
        
        

        return new_data_objects,True

def process_togle_status(project):
    if project.status == 'COMPLETED':
        project.status = 'IN_PROGRESS'
        new_status_label = "In Progress"
    else:
        project.status = 'COMPLETED'
        new_status_label = "Completed"
        
    project.save()

    return project.status,new_status_label

def process_export_file(project):
    # 1. Ambil data mentah (LevelingData)
    raw_data = project.leveling_data.all().order_by('id').values()
    df_raw = pd.DataFrame(list(raw_data))
    
    # 2. Ambil data hasil perhitungan (CalculatedResult)
    results = project.results.all().order_by('id').values()
    df_results = pd.DataFrame(list(results))
    
    # 3. Hapus kolom ID dan FK yang tidak perlu
    df_raw = df_raw.drop(columns=['id', 'project_id'], errors='ignore')
    df_results = df_results.drop(columns=['id', 'project_id', 'backsight', 'foresight'], errors='ignore')

    # 4. Buat buffer in-memory untuk menyimpan file Excel
    output = io.BytesIO()
    
    # 5. Tulis DataFrame ke dalam file Excel dengan sheet yang berbeda
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_raw.to_excel(writer, sheet_name='Raw Data (Input)', index=False)
        df_results.to_excel(writer, sheet_name='Calculation Results', index=False)
    
    # Posisikan pointer kembali ke awal buffer
    output.seek(0)
    
    # 6. Buat Respons HTTP dengan header yang tepat
    filename = f"Project_{project.project_name.replace(' ', '_')}_Data.xlsx"
    response = HttpResponse(
        output, 
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    # Header ini yang membuat browser otomatis mendownload file
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def process_add_row(request,project):

    
    
    
    data = json.loads(request.body)
    count = int(data.get('count', 1))
    
    new_rows = []
    for _ in range(count):
        new_rows.append(LevelingData(
            project=project,
            station='0+000',
            bs_mid=0.000,
            fs_mid=0.000,
        ))
    
    LevelingData.objects.bulk_create(new_rows)

    return count