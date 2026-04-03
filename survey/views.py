from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Project
import pandas as pd
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Project,CrossSection,CalculatedResult
from .services import *


@login_required
@require_POST
def api_toggle_status(request, project_id):
    """API untuk mengubah status proyek antara IN_PROGRESS dan COMPLETED"""
    
    
    try:
        # Logika Toggle: Jika sedang In Progress, ubah jadi Completed, dan sebaliknya
        project_status,new_status_label = process_togle_status(get_object_or_404(Project, pk=project_id, user=request.user))
        
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Status proyek berhasil diubah menjadi {new_status_label}',
            'current_status': project_status
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def api_update_project(request, project_id):
    """API untuk mengupdate informasi umum proyek (Settings)"""
    try:
        process_update_project(request,get_object_or_404(Project, pk=project_id, user=request.user))
        return JsonResponse({'status': 'success', 'message': 'Proyek berhasil diperbarui.'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    

# --- survey/views.py ---
@login_required
@require_POST
def api_calculate_cut_fill(request,project_id):
    try: 
        total_cut,total_fill = save_design_data(request,get_object_or_404(Project, pk=project_id, user=request.user))
        return JsonResponse({
            'status': 'success',
            'message': 'Perhitungan Volume Selesai!',
            'total_cut': f"{total_cut:,.2f}",
            'total_fill': f"{total_fill:,.2f}"
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)




@login_required
@require_POST
def api_update_thread(request, project_id):
    try:
        project = get_object_or_404(Project, pk=project_id, user=request.user)

        # 2. Proses update data mentah (Save Edit)
        """Update banyak baris sekaligus"""
        rows_to_update = process_update_thread(request, project)
    
        # 3. [TAMBAHAN] Panggil fungsi hitung ulang (Recalculate) di sini
        process_leveling_data(project)
    
        

        return JsonResponse({'status': 'success', 'message': f'{len(rows_to_update)} baris berhasil disimpan dan dihitung ulang otomatis!'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def api_delete_thread(request, project_id):
    """Hapus banyak baris berdasarkan ID yang dipilih"""
    try:
        

        # Hapus data yang ID-nya ada di list DAN milik user yang login (security)
        deleted_count, stat = process_delete_thread(request,project_id)
            
        if stat:
            return JsonResponse({'status': 'success', 'message': f'{deleted_count} baris berhasil dihapus.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Tidak ada data yang dipilih'}, status=400)
            
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def api_get_chart_data(request, project_id):
    # Pastikan proyek dimiliki oleh user yang sedang login
    chart_data = process_elevation_chart(get_object_or_404(Project, pk=project_id, user=request.user))
   
    
    
    if chart_data is None:
        return JsonResponse({'status': 'error', 'message': 'Tidak ada hasil perhitungan yang ditemukan.'}, status=404)
        

    return JsonResponse({'status': 'success', 'data': chart_data}, status=200)

@login_required
def export_project_data_excel(request, project_id): # <-- FUNGSI BARU UNTUK EXPORT
    response = process_export_file(get_object_or_404(Project, pk=project_id, user=request.user))
    
    
    return response

# ... (lanjutan fungsi views lainnya) ...



@login_required
def api_upload_raw_data(request,project_id):
    try:
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        
        if 'excel_file' not in request.FILES:
            return JsonResponse({'status': 'error', 'message': 'File tidak ditemukan.'}, status=400)
        
        excel_file = request.FILES['excel_file']

        # Batasi jenis file
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            return JsonResponse({'status': 'error', 'message': 'Hanya file Excel (.xlsx, .xls) yang diizinkan.'}, status=400)

    
        # 1. Baca file Excel menggunakan utility yang sudah ada
        df = pd.read_excel(excel_file)
        
        if project.survey_type == 'OPEN':
            # 2. Cek ketersediaan kolom wajib
            if 'bs_mid' not in df.columns or 'fs_mid' not in df.columns or 'station' not in df.columns:
                return JsonResponse({'status': 'error', 'message': 'File Excel harus mengandung kolom wajib: station, bs_mid, dan fs_mid.'}, status=400)
        else:
            if 'bs_mid' not in df.columns or 'fs_mid' not in df.columns or 'station' not in df.columns or 'bwd_bs_mid' not in df.columns or 'bwd_fs_mid' not in df.columns:
                return JsonResponse({'status': 'error', 'message': 'File Excel harus mengandung kolom wajib: station, bs_mid, fs_mid, bwd_fs_mid, bwd_bs_mid'}, status=400)


        new_data_objects,stat = process_upload_file(project,df)
        
        if stat is False:
            return JsonResponse({'status': 'error', 'message': f'Nilai BS Mid atau FS Mid di baris {index + 2} bukan angka valid.'}, status=400)
        elif new_data_objects is None:
            return None
        else:
            message = f'{len(new_data_objects)} baris data berhasil diunggah dan disimpan.'
            return JsonResponse({'status': 'success', 'message': message, 'row_count': len(new_data_objects)}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Gagal memproses file: {str(e)}'}, status=500)

@login_required
def api_delete_project(request,project_id):
    try:
        
        process_delete_project(get_object_or_404(Project, pk=project_id, user=request.user))
        return JsonResponse({'status': 'success', 'message': 'Project was deleted.'}, status=200)
    except Project.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Project tidak ditemukan atau Anda tidak memiliki izin.'}, status=404)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)





@login_required # Memastikan hanya user terautentikasi yang bisa membuat proyek
@require_POST
def api_create_project(request):
    """
    Menerima request AJAX dari modal untuk membuat Project baru
    """
    try:
        context,stat = process_create_project(request)
        if stat:
            return JsonResponse({
                'status': 'success', 
                'message': 'Proyek baru berhasil dibuat!',
                'project_id': context.id,
                # Gunakan redirect().url untuk mendapatkan URL string
                'redirect_url': redirect('survey:details', pk=context.id).url 
            }, status=201) # 201 Created
        else:
            # Kirim kembali error form dalam format JSON
            return JsonResponse({
                'status': 'error', 
                'message': 'Data tidak valid',
                'errors': context.errors.as_json()
            }, status=400) # 400 Bad Request
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
# Create your views here.
@login_required 
def index(request): 
    # Ambil semua proyek user
    context = calculate_data_projects(request,Project.objects.filter(user=request.user).order_by('-created_at'))

    
    return render(request, 'survey/dashboard.html', context)

def details(request, pk): 
    context = get_project_detail(request,get_object_or_404(Project, pk=pk))
    return render(request, 'survey/detail_projects.html', context)

# --- LOGIC BARU: API ADD ROWS ---
@require_POST
def api_add_rows(request, project_id):
    try:
        count = process_add_row(request,get_object_or_404(Project, pk=project_id))
        
        return JsonResponse({'status': 'success', 'message': f'{count} baris ditambahkan'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    

@require_POST
def api_calculate_leveling(request, project_id):
    try:

        context = process_leveling_data(get_object_or_404(Project, pk=project_id))
    
    

        return JsonResponse({
            'status': 'success', 
            'message': 'Perhitungan selesai!',
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500) 
    
@login_required
@require_POST
def create_c_section(request, project_id):
    try:
        # Get project and ensure it belongs to the user
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        
        # Call the logic
        count_created = process_create_c_section(project)
        
        if count_created > 0:
            return JsonResponse({
                'status': 'success', 
                'message': f'Berhasil membuat {count_created} titik Cross Section (A,B,C,D).'
            })
        else:
            return JsonResponse({
                'status': 'info', 
                'message': 'Titik Cross Section sudah ada untuk semua stasiun.'
            })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def api_update_c_section_data(request, project_id):
    try:
        data = json.loads(request.body)
        updated_count = 0

        for row in data:
            # Ambil object CrossSection berdasarkan ID
            obj = get_object_or_404(CrossSection, pk=row['id'])
            
            # Update field (gunakan validasi sederhana)
            # Konversi string kosong jadi None (NULL) untuk data angka opsional
            obj.label = row.get('label', obj.label)
            
            # Helper untuk konversi float
            def to_float(val):
                if val == '' or val is None: return None
                return float(val)

            obj.distance = to_float(row.get('distance'))
            obj.top = to_float(row.get('top'))
            obj.mid = to_float(row.get('mid'))
            obj.bot = to_float(row.get('bot'))
            
            obj.save()
            updated_count += 1
            
        return JsonResponse({
            'status': 'success', 
            'message': f'{updated_count} titik Cross Section berhasil diperbarui.'
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    


from .models import CalculatedResult, CrossSection

def calculate_CS(request, project_id):
    try:
        # 1. Ambil data Station beserta anak-anaknya (CrossSection)
        # prefetch_related -> Biar query nggak nembak berkali-kali (Optimasi)
        stations = CalculatedResult.objects.filter(project_id=project_id).prefetch_related('c_section')

        # List penampung untuk bulk_update
        cs_update_list = []

        # 2. Loop per Station (Bukan per titik global)
        for station in stations:
            # Ambil titik CS di station ini, urutkan (misal berdasarkan id atau distance)
            cs_points = list(station.c_section.all().order_by('id'))
            
            # Variable bantu untuk logic "Previous" di dalam station ini
            # Kita reset setiap ganti station
            prev_point = None 
            
            # Ambil elevasi induk dari station (CalculatedResult)
            current_elevation_ref = station.elevation 

            for i, point in enumerate(cs_points):
                # --- A. Hitung MID (Benang Tengah) ---
                # Pastikan float, jaga-jaga kalau None
                top = point.top if point.top is not None else 0.0
                bot = point.bot if point.bot is not None else 0.0
                
                # Jika Top & Bot ada, hitung Mid ulang. Jika tidak, pakai Mid inputan.
                if point.top and point.bot:
                    point.mid = (top + bot) / 2
                
                # Pastikan mid tidak None buat hitungan matematika
                curr_mid = point.mid if point.mid is not None else 0.0

                # --- B. Hitung Beda Tinggi (Height Difference) ---
                if i == 0:
                    # Titik pertama di station ini (biasanya Center Line / Patok Utama)
                    point.height_difference = 0.0
                    
                    # Elevasi titik pertama = Elevasi Station (Asumsi Center Line)
                    point.elevation = current_elevation_ref
                else:
                    # Titik kedua dst... bandingkan dengan titik sebelumnya
                    prev_mid = prev_point.mid if prev_point and prev_point.mid else 0.0
                    
                    # Rumus Beda Tinggi (Benang): Belakang - Muka (atau Prev - Curr)
                    # Sesuaikan dengan kaidah ukur tanahmu. 
                    # Disini saya pakai: Mid Sebelumnya - Mid Sekarang
                    diff = prev_mid - curr_mid
                    point.height_difference = diff
                    
                    # Hitung Elevasi Titik ini
                    # Elevasi Sekarang = Elevasi Sebelumnya + Beda Tinggi
                    point.elevation = prev_point.elevation + diff

                # Update 'prev_point' untuk iterasi berikutnya
                prev_point = point
                
                # Masukkan object yang sudah diedit ke keranjang update
                cs_update_list.append(point)

        # 3. SIMPAN KE DATABASE (BULK UPDATE)
        if cs_update_list:
            with transaction.atomic():
                CrossSection.objects.bulk_update(
                    cs_update_list, 
                    ['mid', 'height_difference', 'elevation'] # Kolom yang mau di-update
                )

        

            
            
        
        return JsonResponse({'status': 'success', 'message': 'Perhitungan sukses & Data aman!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

import re
from .services.ai_prompt import prompt_for_detect_anomalies,GeminiClient,prompts_make_report
def analyze_anomaly_api(request):


    if request.method == 'POST':
        try:
            # 1. Ambil data yang dikirim dari JavaScript
            # 1. Ambil data yang dikirim dari JavaScript
            data = json.loads(request.body)
            tabel_data = data.get('tabel_data', '')
            survey_type = data.get('survey_type', 'OPEN') # <-- Tambahan baru

            
            # 2. Siapkan prompt 
            prompt = prompt_for_detect_anomalies(tabel_data, survey_type)
            
            # 3. Panggil Gemini
            ai = GeminiClient(api_code="AIzaSyAHsV9LsaY2EMtmqnj0yhY4MyNUrBUbQaM") 
            response = ai.genrate_content(prompt, "gemini-2.5-flash", 0.3, 100000)
            clean_response = re.sub(r"```(?:json)?\s*", "", response)
            clean_response = re.sub(r"```", "", clean_response)
            clean_response = re.sub(r",\s*]", "]", clean_response)
            clean_response = clean_response.strip()
            # 4. Ubah teks JSON dari AI menjadi Python dictionary
            ai_json = json.loads(clean_response)
            
            return JsonResponse({'status': 'success', 'data': ai_json})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'invalid method'}, status=405)



@require_POST
def api_generate_ai_report(request, project_id):
    try:
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        # 1. Ambil data hasil kalkulasi (CalculatedResult)
        results = CalculatedResult.objects.filter(project=project).values(
            'station', 'elevation', 'distance_avg' # Sesuaikan dengan field model lo
        )
        data_list = list(results)
        data_str = json.dumps(data_list)
        
        # 2. Siapkan prompt
        purpose = project.purpose or "General Survey"
        prompt = prompts_make_report(data_str, purpose)
        
        # 3. Panggil Gemini
        ai = GeminiClient(api_code="AIzaSyAHsV9LsaY2EMtmqnj0yhY4MyNUrBUbQaM") # Gunakan env var untuk API key yg aman!
        report_text_ai = ai.genrate_content(prompt, "gemini-2.5-flash", 0.7, 100000)
        
        # 4. Save hasil AI ke Database
        ai_result, created = AIReport.objects.update_or_create(
            project=project,
            defaults={'report_text': report_text_ai} # Timpa field report_text dengan hasil baru
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Report berhasil dibuat',
            'report': report_text_ai
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    


# Civilix-App/survey/views.py
from .utils.export import export_to_word

def download_ai_report_word(request, project_id):

    project = get_object_or_404(Project, pk=project_id, user=request.user)
    
    # Cek apakah project punya relasi ke AIReport (pakai hasattr untuk OneToOneField)
    if not hasattr(project, 'ai_report'):
        return HttpResponse("Report belum di-generate.", status=404)
        
    # Ambil teksnya DARI MODEL AIReport
    teks_laporan = project.ai_report.report_text
    
    # Bikin file word di memory
    word_buffer = export_to_word(teks_laporan)
    
    # ... (lanjutkan return HttpResponse seperti biasa) ...
    
    # Kirim sebagai response
    response = HttpResponse(
        word_buffer.getvalue(), 
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    # Nama file download
    file_name = f"AI_Report_{project.project_name.replace(' ', '_')}.docx"
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    
    return response




@require_POST
def api_add_cross_section(request, station_id):
    try:
        data = json.loads(request.body)
        station = get_object_or_404(CalculatedResult, id=station_id)
        
        # Bikin data baru di database
        new_point = CrossSection.objects.create(
            station=station,
            label=data.get('label', ''),
            distance=float(data.get('distance', 0.0)),
            mid=float(data.get('mid', 0.0)),
            top=float(data.get('top', 0.0)),
            bot=float(data.get('bot', 0.0)),
            # Nanti top, bot, sama hitungan elevasi bisa lu tambahin logika kalkulasinya di sini
        )
        
        return JsonResponse({
            'status': 'success', 
            'id': new_point.id,
            'message': 'Titik berhasil ditambahkan!'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# API untuk Hapus Titik
@require_POST
def api_delete_cross_section(request, point_id):
    try:
        point = get_object_or_404(CrossSection, id=point_id)
        point.delete()
        return JsonResponse({'status': 'success', 'message': 'Titik dihapus!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def api_get_station_list(request, project_id):
    try:
        # Tambahkan .order_by('cumulative_distance') biar urut dari STA awal ke akhir
        stations = CalculatedResult.objects.filter(
            project_id=project_id
        ).order_by('cumulative_distance').values('id', 'station')
        
        station_list = list(stations)
        
        return JsonResponse({'status': 'success', 'stations': station_list})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
 

def api_export_dxf_advanced(request, project_id):
    if request.method == 'POST':
        # 1. AMBIL DATA TEKS/ANGKA (Pake request.POST.get)
        # Nama di dalam kurung harus sama dengan atribut name="..." di HTML
        grafik_type = request.POST.get('grafik')
        skala_x = float(request.POST.get('skala_x'))
        skala_y = float(request.POST.get('skala_y'))
        sta_start = (request.POST.get('sta_start'))
        sta_end = request.POST.get('sta_end')
        kop_type = request.POST.get('kop_type')
        custom_kop_file = request.FILES.get('custom_kop')
        units = request.POST.get('units')
        datum_raw = request.POST.get('datum_value')
        datum_value = float(datum_raw) if datum_raw else 0.0
        datum_type = request.POST.get('datum_type')
        paper_size = request.POST.get('paper_size')
        
        context = {'grafik_type':grafik_type,
                   'skala_x':skala_x,
                   'skala_y':skala_y,
                   'sta_start':sta_start,
                   'sta_end':sta_end,
                   'kop_type':kop_type,
                   'custom_kop_file': custom_kop_file,
                   'units': units,
                   'datum_value': datum_value,
                   'datum_type': datum_type,
                   'paper_size': paper_size
        }
        # 2. AMBIL FILE UPLOAD (Pake request.FILES.get)
        # 'custom_kop' ini dari <input type="file" name="custom_kop">
        

        # 3. LOGIC CEK FILE
        if kop_type == 'custom' and not custom_kop_file:
            return JsonResponse({"error": "File kop tidak ditemukan!"}, status=400)

        # ----------------------------------------------------
        # 4. PROSES BIKIN FILE DXF (Misal pakai library ezdxf)
        # ----------------------------------------------------
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        try:
            # Fungsi ini bakal mereturn string berisi kode mentah DXF
            dxf_string_content = process_export_dxf_advanced(project, context)
        except Exception as e:
            print(f"Error DXF: {e}")
            return JsonResponse({"error": "Gagal memproses DXF."}, status=500)
        
        # 5. KEMBALIKAN SEBAGAI FILE KE BROWSER
        # Anggap 'dxf_string_content' itu adalah hasil file DXF yang udah lu generate 
        
       

        # Django otomatis mengubah string jadi format yang bisa didownload browser
        response = HttpResponse(dxf_string_content, content_type='application/dxf')
        return response

    # Kalau ada yang iseng akses URL ini langsung lewat browser (method GET)
    return JsonResponse({"error": "Method not allowed"}, status=405)





@require_POST
def api_upload_cs_excel(request, project_id):
    excel_file = request.FILES.get('excel_file')
    
    if not excel_file:
        return JsonResponse({'status': 'error', 'message': 'File Excel tidak ditemukan.'}, status=400)

    try:
        

        cs_to_create,sta_not_found = process_upload_CS_excel(project_id, excel_file)

        # 7. BIKIN PESAN KESIMPULAN
        msg = f"Berhasil menyimpan {len(cs_to_create)} titik Cross Section dan sudah terhitung."
        if sta_not_found:
            msg += f" (Warning: STA {', '.join(sta_not_found)} dilewati karena belum dihitung di profil memanjang)."

        return JsonResponse({'status': 'success', 'message': msg})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Gagal memproses file: {str(e)}'}, status=500)