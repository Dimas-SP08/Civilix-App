import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment
from ezdxf import bbox
import math
 
from survey.models import CalculatedResult
from survey.services.dxf_generator.dxf_utils import setup_layer_style

def draw_cross_section(project_id, kop, skala_x, skala_y, sta_start, sta_end, datum_value, datum_type, units, jarak_max, jarak_max_vertikal, jarak_default, jarak_default_vertikal, margin, jarak_kop, doc, paper_size, msp):
    query_results = CalculatedResult.objects.filter(
        project_id=project_id
    ).order_by('cumulative_distance')

    jarak_v_perblock = 30
    jarak_h_perblock = 30
    # 2. Format ulang (List Comprehension) menjadi list of dictionaries
    data_fromdb = []
    for item in query_results :
        data_fromdb.append(item.station)

    index_start = -1
    index_end = -1
    for i,d in enumerate(data_fromdb):
        if d == sta_start:
            index_start = i
        if d == sta_end:
            index_end = i
            break
    if index_start == -1 or index_end == -1:
        raise ValueError("STA start atau end tidak ditemukan di data leveling.")
    
    list_sta = []
    for i in range(index_start, index_end+1):
        list_sta.append(data_fromdb[i])

    
    data_survey = get_cross_section_data(project_id, list_sta)
    

    for i,d in enumerate(data_survey):
        for g in d:
            g['dist_skala'] = g['dist'] * skala_x
            g['elev_skala'] = g['elev'] * skala_y

    setup_layer_style(doc)
    
    batas_kop = bbox.extents(kop)
    center_kop = batas_kop.center
    kop.base_point = center_kop 

    koordinat = 0   
    daftar_gambar = []
    for i,data in enumerate(data_survey): 
        # gambar = doc.blocks.new(name=f'GAMBAR_{i+1}')
        data = data_survey_block(doc,data_survey[i],i)
        
        batas_data = bbox.extents(data)
        lebar_horizontal = batas_data.size.x  
        tinggi_vertikal = batas_data.size.y
        extmin_data = batas_data.extmin
        data.base_point = extmin_data
        dictionary = {
            'gambar': f'DATA_SURVEY_{i+1}',
            'batas_x' : lebar_horizontal,
            'batas_y' : tinggi_vertikal,
        }
        daftar_gambar.append(dictionary)
 

        # gambar.add_blockref(f'DATA_SURVEY_{i+1}', insert=(200-margin, 200))
        # gambar.add_blockref(kop_user, insert=(200, 200)) 
        

        # msp.add_blockref(f'GAMBAR_{i+1}', insert=(200+koordinat, 200))
        # koordinat += jarak_kop
    
    patok_h = daftar_gambar[0]['batas_x'] 
    kop_h = []
    data_sementara_h = []
    for i,d in enumerate(daftar_gambar):
        
        if patok_h < jarak_max :
            print(f'gambar = {d["gambar"]},{patok_h} < {jarak_max} ?')
            data_sementara_h.append(d)
            if i == len(daftar_gambar) - 1:
                kop_h.append(data_sementara_h)
            if i < len(daftar_gambar) - 1 :
                patok_h +=  daftar_gambar[i+1]['batas_x'] + jarak_h_perblock

        else:
            jarak_max += jarak_default
            kop_h.append(data_sementara_h)
            data_sementara_h = []
            data_sementara_h.append(d)
            patok_h = jarak_max - jarak_default
            if i == len(daftar_gambar) - 1:
                kop_h.append(data_sementara_h)
            if i < len(daftar_gambar) - 1 :
                patok_h +=  daftar_gambar[i+1]['batas_x'] 
                patok_h +=  daftar_gambar[i]['batas_x'] 
    
    

    y_terpanjang = []
    for i, d in enumerate(kop_h) :
        u_panjang_perblock = []
        for u_terpanjang in d :
            u_panjang_perblock.append(u_terpanjang['batas_y'])
        y_terpanjang.append(max(u_panjang_perblock))
    
    jumlah_kop = []
    jumlah_kop_sementara = []
    patok = y_terpanjang[0] 
    for i,data in enumerate(y_terpanjang):
        if patok < jarak_max_vertikal :
            jumlah_kop_sementara.append(data)
            if i == len(y_terpanjang) - 1:
                jumlah_kop.append(jumlah_kop_sementara)
        else:
            jarak_max_vertikal += jarak_default_vertikal
            jumlah_kop.append(jumlah_kop_sementara)
            jumlah_kop_sementara = []
            jumlah_kop_sementara.append(data)
            if i == len(y_terpanjang) - 1:
                jumlah_kop.append(jumlah_kop_sementara)
        if i < len(y_terpanjang) - 1 :
                patok +=  y_terpanjang[i+1] + jarak_v_perblock


    for i, data3 in enumerate(kop_h):
        horizontal = doc.blocks.new(name=f'horizontal_{i+1}')
        # Mulai dari X=0 atau margin kiri dikit
        step_x_perblock = 0
        
        for data4 in data3:
            horizontal.add_blockref(data4['gambar'], insert=(step_x_perblock, 0))
            step_x_perblock += data4['batas_x'] + jarak_h_perblock # Geser ke kanan buat gambar CS berikutnya
            
        batas_data = bbox.extents(horizontal)
        if batas_data.has_data: # Cek biar ga error kalo kosong
            horizontal.base_point = batas_data.extmin
            
           
            

    index_horizontal = 0 # Bikin counter terpisah buat manggil nama blok horizontal
    
    for idx_kop, data in enumerate(jumlah_kop): # Pake idx_kop biar ga bentrok
        # Mulai dari Y bawah, naik ke atas
        nama_keseluruhan = f'keseluruhan gambar{idx_kop+1}'
        keseluruhan = doc.blocks.new(name=nama_keseluruhan)
    
        keseluruhan_data = doc.blocks.new(name=f'keseluruhan data{idx_kop+1}')
        step_y_perblock = 0
         
        
        for idx_row, data2 in enumerate(data):
            # Panggil blok horizontal sesuai urutannya
            nama_blok_horiz = f'horizontal_{index_horizontal+1}'
            
            # Cek dulu apakah blok horizontal itu beneran ada di memori
            
            keseluruhan_data.add_blockref(nama_blok_horiz, insert=(margin, step_y_perblock))
            if index_horizontal < len(y_terpanjang)-1:
                step_y_perblock -= y_terpanjang[index_horizontal+1] +jarak_v_perblock 
            index_horizontal += 1 # Maju ke blok horizontal selanjutnya

        # Masukin Kop-nya (base_point kop kan di center, berarti insert di tengah kertas)

        batas= bbox.extents(keseluruhan_data)
        center_keseluruhan_data = batas.center
        keseluruhan_data.base_point = center_keseluruhan_data 

        keseluruhan.add_blockref(f'keseluruhan data{idx_kop+1}',insert=(200-20,200))
        keseluruhan.add_blockref(paper_size, insert=(200, 200)) 
    
        # Insert keseluruhan ke Model Space, jejerin ke Kanan
        msp.add_blockref(nama_keseluruhan, insert=(koordinat, 0))
        koordinat += jarak_kop

    return doc




def get_cross_section_data(project_id, list_sta):
    """
    Mengambil data Potongan Melintang berdasarkan list STA yang diminta.
    Output berupa List of Lists (berurutan dari kiri ke kanan).
    """
    data_survey = []
    
    # 1. Query Stasiun Induk (Center Line)
    # Gunakan prefetch_related agar query ke CrossSection diambil sekaligus (Cepat!)
    stations = CalculatedResult.objects.filter(
        project_id=project_id,
        station__in=list_sta
    ).prefetch_related('c_section').order_by('cumulative_distance')

    # 2. Looping per Stasiun
    for sta in stations:
        titik_sta_ini = []
        
        # A. Masukkan Titik Tengah (As Jalan / Center Line) dari CalculatedResult
        
        # B. Masukkan Titik-Titik Sayap (Kiri/Kanan) dari model CrossSection
        for detail in sta.c_section.all():
            titik_sta_ini.append({
                'point': detail.label,
                'dist': float(detail.distance),
                'elev': float(detail.elevation) if detail.elevation is not None else 0.0
            })
            
        # 3. URUTKAN BERDASARKAN JARAK (dist)
        # Dari minus terbesar (Paling Kiri) ke plus terbesar (Paling Kanan)
        # Ini KUNCI UTAMA biar garis tanah (polyline) gak melintir pas digambar ezdxf
        titik_sta_ini_sorted = sorted(titik_sta_ini, key=lambda x: x['dist'])
        
        # 4. Simpan ke wadah utama
        data_survey.append(titik_sta_ini_sorted)
        
    return data_survey

def data_survey_block(doc,data_survey,angka):
    
    all_elev = []
    all_elev_asli = []
    for i in data_survey:
        all_elev.append(i['elev_skala'])
        all_elev_asli.append(i['elev'])
    
    datum = math.floor(min(all_elev)) - 2
    datum_asli = math.floor(min(all_elev_asli)) -2
    
    
    data = doc.blocks.new(name=f'DATA_SURVEY_{angka+1}')

    tt_data = 2
    tt_biasa = 2.5
    gp_y = 0
    gp_x = 32
    
    l_0 = 0
    l_1 = 5
    l_2 = 10
    l_3 = 20  
    l_4 = 30

    off_1 = 3
 
    th_jarak = data.add_text("JARAK (M)", dxfattribs={'height': tt_biasa, 'style': 'ARIAL', 'layer': 'TEXT',}).set_placement((2, -l_1/2-l_1), align=TextEntityAlignment.MIDDLE_LEFT) 
    th_elev = data.add_text("ELEVASI (M)", dxfattribs={'height': tt_biasa, 'style': 'ARIAL', 'layer': 'TEXT',}).set_placement((2, -l_2/2-l_2), align=TextEntityAlignment.MIDDLE_LEFT) 
    th_kumulative_j = data.add_text("JARAK K (M)", dxfattribs={'height': tt_biasa, 'style': 'ARIAL', 'layer': 'TEXT',}).set_placement((2, -l_2/2-l_3), align=TextEntityAlignment.MIDDLE_LEFT) 
    th_titik =data.add_text("TITIK", dxfattribs={'height': tt_biasa, 'style': 'ARIAL', 'layer': 'TEXT',}).set_placement((2, -l_1/2), align=TextEntityAlignment.MIDDLE_LEFT) 
    th_titik =data.add_text(f"DL = {datum_asli}M", dxfattribs={'height': tt_biasa, 'style': 'ARIAL', 'layer': 'TEXT',}).set_placement((2, l_1/2+l_0), align=TextEntityAlignment.MIDDLE_LEFT) 


    line_1 = data.add_line ((0, 0-l_0), (gp_x, 0-l_0), dxfattribs={'layer': 'GARIS_TABLE'})
    line_2 = data.add_line ((0, 0-l_1), (gp_x, 0-l_1), dxfattribs={'layer': 'GARIS_TABLE'})
    line_3 = data.add_line ((0, 0-l_2), (gp_x, 0-l_2), dxfattribs={'layer': 'GARIS_TABLE'})
    line_4 = data.add_line ((0, 0-l_3), (gp_x, 0-l_3), dxfattribs={'layer': 'GARIS_TABLE'})
    line_5 = data.add_line ((0, 0-l_4), (gp_x, 0-l_4), dxfattribs={'layer': 'GARIS_TABLE'})
    line_6 = data.add_line ((0, 0), (0, 0-l_4), dxfattribs={'layer': 'GARIS_TABLE'})
    line_7 = data.add_line ((gp_x-off_1, 0), (gp_x-off_1, 0-l_4), dxfattribs={'layer': 'GARIS_TABLE'})

    
    


    jarak_awal_kertas = data_survey[0]['dist_skala']
    for i,d in enumerate(data_survey):
        x = d['dist_skala'] 
        x_asli = d['dist'] 
        x_new = d['dist_skala'] - jarak_awal_kertas
        y =d['elev_skala']-datum # Skala vertikal biar lekukan tanahnya kelihatan jelas
        patok = d['point']
        if d['dist'] == 0 :
            point = d["point"]
        
        if i == len(data_survey) - 1:
            t_head = data.add_text(f'{point}', dxfattribs={'height': 3.5, 'style': 'ARIAL', 'layer': 'TEXT'}).set_placement(( (gp_x+x_new)/2, gp_y-40), align=TextEntityAlignment.MIDDLE_CENTER)
            t_head.dxf.lineweight = 0.5
        # if i == len(data_survey) - 1:
        #     t_head = data.add_text("LONG SECTION (POTONGAN MEMANJANG)", dxfattribs={'height': 3.5, 'style': 'ARIAL', 'layer': 'TEXT'}).set_placement(( gp_x+x_new/2, gp_y-40), align=TextEntityAlignment.MIDDLE_CENTER)
        #     t_head.dxf.lineweight = 0.5

        t_patok =data.add_text(patok, dxfattribs={'height': tt_data, 'style': 'ARIAL', 'layer': 'TEXT',}).set_placement((x_new+gp_x, gp_y - l_1/2), align=TextEntityAlignment.MIDDLE_CENTER) # Taruh teks patok 5 meter di bawah titik tanah

        t_elev = data.add_text(f'{d["elev"]:.2f}', dxfattribs={'height': tt_data, 'style': 'ARIAL', 'layer': 'TEXT', 'rotation': 90,'color': 4}).set_placement((x_new+gp_x, gp_y-l_2-l_2/2), align=TextEntityAlignment.MIDDLE_CENTER) # Taruh teks patok 5 meter di bawah titik tanah

        t_dist = data.add_text(f'{d["dist"]:.2f}', dxfattribs={'height': tt_data, 'style': 'ARIAL', 'layer': 'TEXT', 'rotation': 90,'color': 4}).set_placement((x_new+gp_x, gp_y-l_3-l_2/2), align=TextEntityAlignment.MIDDLE_CENTER) # Taruh teks patok 5 meter di bawah titik tanah 

        g_kecil = data.add_line((x_new+gp_x,gp_y-l_1),(x_new+gp_x,gp_y-l_2), dxfattribs={'layer': 'GARIS_TABLE'}) # garis potong keci 5 dari tanah vertikal


        g_elev =data.add_line((x_new+gp_x, gp_y), (x_new+gp_x, y+gp_y), dxfattribs={'layer': 'GARIS_ELEV'}) # garis elev

        if i < len(data_survey) - 1:
            x_next = data_survey[i+1]['dist_skala'] 
            x_next_asli = data_survey[i+1]['dist'] 
            x_new2 = x_next - jarak_awal_kertas
            
            y_next = data_survey[i+1]['elev_skala']-datum 
            
            g_dist =data.add_line((x_new+gp_x,gp_y-l_0),(x_new2+gp_x, gp_y-l_0), dxfattribs={'layer': 'GARIS_TABLE'}) # garis distance
            g_dist =data.add_line((x_new+gp_x,gp_y-l_1),(x_new2+gp_x, gp_y-l_1), dxfattribs={'layer': 'GARIS_TABLE'}) # garis distance
            g_dist =data.add_line((x_new+gp_x,gp_y-l_2),(x_new2+gp_x, gp_y-l_2), dxfattribs={'layer': 'GARIS_TABLE'}) # garis distance
            g_dist =data.add_line((x_new+gp_x,gp_y-l_3),(x_new2+gp_x, gp_y-l_3), dxfattribs={'layer': 'GARIS_TABLE'}) # garis distance
            g_dist =data.add_line((x_new+gp_x,gp_y-l_4),(x_new2+gp_x, gp_y-l_4), dxfattribs={'layer': 'GARIS_TABLE'}) # garis distance
            
            t_dist = data.add_text(f'{x_next_asli-x_asli:.2f}', dxfattribs={'height': tt_data, 'style': 'ARIAL', 'layer': 'TEXT','color': 4}).set_placement((x_new+gp_x+(x_next-x)/2, gp_y - l_1-l_1/2), align=TextEntityAlignment.MIDDLE_CENTER) # Taruh teks jarak di bawah garis tanah

            g_tanah = data.add_line((x_new+gp_x,y+gp_y), (x_new2+gp_x, y_next+gp_y), dxfattribs={'layer': 'GARIS_ELEV'}) # garis tanah
            if i == len(data_survey) - 2:
                line_7 = data.add_line ((x_new2+gp_x+off_1,gp_y-l_0),(x_new2+gp_x+off_1, gp_y-l_4), dxfattribs={'layer': 'GARIS_TABLE'})
                line_7 = data.add_line ((x_new2+gp_x,gp_y-l_0),(x_new2+gp_x+off_1, gp_y-l_0), dxfattribs={'layer': 'GARIS_TABLE'})
                line_7 = data.add_line ((x_new2+gp_x,gp_y-l_1),(x_new2+gp_x+off_1, gp_y-l_1), dxfattribs={'layer': 'GARIS_TABLE'})
                line_7 = data.add_line ((x_new2+gp_x,gp_y-l_2),(x_new2+gp_x+off_1, gp_y-l_2), dxfattribs={'layer': 'GARIS_TABLE'})
                line_7 = data.add_line ((x_new2+gp_x,gp_y-l_3),(x_new2+gp_x+off_1, gp_y-l_3), dxfattribs={'layer': 'GARIS_TABLE'})
                line_7 = data.add_line ((x_new2+gp_x, gp_y-l_4),(x_new2+gp_x+off_1, gp_y-l_4), dxfattribs={'layer': 'GARIS_TABLE'})

    
    return data
