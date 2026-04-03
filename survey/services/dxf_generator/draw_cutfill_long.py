from ...models import CalculatedResult
from ezdxf import bbox
from ezdxf.enums import TextEntityAlignment
from .dxf_utils import setup_layer_style
import math


def draw_cutfill_long(project_id, kop, skala_x, skala_y, sta_start, sta_end, datum_value, datum_type, units, jarak_max, jarak_max_vertikal, jarak_default, jarak_default_vertikal, margin, jarak_kop, doc, paper_size, msp,):
    
    # 1. Query data dari database berdasarkan project_id
    # Sangat penting memakai .order_by() agar titik tergambar berurutan
    query_results = CalculatedResult.objects.filter(
        project_id=project_id
    ).order_by('cumulative_distance')

    # 2. Format ulang (List Comprehension) menjadi list of dictionaries
    data_fromdb = [
        {
            'point': item.station, 
            'dist': float(item.cumulative_distance), 
            'elev': float(item.elevation),
            'design_elev': float(item.design_elevation)
        }
        for item in query_results
    ]

    index_start = -1
    index_end = -1
    for i,d in enumerate(data_fromdb):
        if d['point'] == sta_start:
            index_start = i
        if d['point'] == sta_end:
            index_end = i
            break
    if index_start == -1 or index_end == -1:
        raise ValueError("STA start atau end tidak ditemukan di data leveling.")
    
    data_survey = []
    for i in range(index_start, index_end+1):
        data_survey.append(data_fromdb[i])
    

    for i,d in enumerate(data_survey):
        d['dist_skala'] = d['dist'] * skala_x
        d['elev_skala'] = d['elev'] * skala_y
        d['design_elev_skala'] = d['design_elev'] * skala_y
        
        
        if i > 0 :
            d['dist_nocum'] =  (d['dist']* skala_x) - (data_survey[i-1]['dist']* skala_x) 
        else :
            d['dist_nocum'] = 0

    


    patokan = data_survey[0]['dist_nocum']
    data_sekat = []
    data_sementara = []
    for i,d in enumerate(data_survey):
       
        
        if patokan < jarak_max:
            data_sementara.append(d)
            if i == len(data_survey) - 1:
                data_sekat.append(data_sementara)
            
        else:
            jarak_max += jarak_default
            data_sekat.append(data_sementara)
            data_sementara = []
            data_sementara.append(data_survey[i-1])
            data_sementara.append(d)
            if i == len(data_survey) - 1:
                data_sekat.append(data_sementara)
            if i > 0:
                patokan += data_survey[i-1]['dist_nocum']

        if i < len(data_survey) - 1 :
                patokan +=  data_survey[i+1]['dist_nocum']

    # print(patokan)

    
            
    data_all = data_survey_block(doc,data_survey,'all')
    batas_data_all = bbox.extents(data_all)
    exmint_data_all = batas_data_all.extmin
    data_all.base_point = exmint_data_all
    
    '''SETUP LAYER,BLOCK & BASE_POINT'''
    
    setup_layer_style(doc)
    
    batas_kop = bbox.extents(kop)
    center_kop = batas_kop.center
    kop.base_point = center_kop 

    koordinat = 0   
    for i,data in enumerate(data_sekat): 
        data = data_survey_block(doc,data_sekat[i],i)
        batas_data = bbox.extents(data)
        center_data = batas_data.center
        data.base_point = center_data
        gambar = doc.blocks.new(name=f'GAMBAR_{i+1}')
 

        gambar.add_blockref(f'DATA_SURVEY_{i+1}', insert=(200-margin, 200))
        gambar.add_blockref(paper_size, insert=(200, 200)) 
        

        msp.add_blockref(f'GAMBAR_{i+1}', insert=(200+koordinat, 200))
        koordinat += jarak_kop

    msp.add_blockref('DATA_SURVEY_all', insert=(200, 400+jarak_max_vertikal))




def data_survey_block(doc,data_survey,angka):
    if type(angka) == int or type(angka) == float:
        angka += 1
    else:
        angka = angka
        
    all_elev = []
    all_elev_asli = []
    for i in data_survey:
        all_elev.append(i['elev_skala'])
        all_elev.append(i['design_elev_skala'])
        all_elev_asli.append(i['elev'])
    datum = math.floor(min(all_elev)) - 2
    dating = math.floor(max(all_elev)) - datum
    datum_asli = math.floor(min(all_elev_asli)) - 2
    
    
    
    data = doc.blocks.new(name=f'DATA_SURVEY_{angka}')

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
    th_titik =data.add_text(f"DL = {datum_asli}M", dxfattribs={'height': tt_biasa, 'style': 'ARIAL', 'layer': 'TEXT',}).set_placement((2, l_1/2+l_0), align=TextEntityAlignment.MIDDLE_LEFT) 
    th_titik =data.add_text("TITIK", dxfattribs={'height': tt_biasa, 'style': 'ARIAL', 'layer': 'TEXT',}).set_placement((2, -l_1/2), align=TextEntityAlignment.MIDDLE_LEFT) 


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
        y_design = d['design_elev_skala'] - datum
        patok = d['point']

        if i == len(data_survey) - 1:
            t_head = data.add_text("LONG SECTION (POTONGAN MEMANJANG)", dxfattribs={'height': 3.5, 'style': 'ARIAL', 'layer': 'TEXT'}).set_placement(( gp_x+x_new/2, gp_y-40), align=TextEntityAlignment.MIDDLE_CENTER)
            t_head.dxf.lineweight = 0.5

        t_patok =data.add_text(patok, dxfattribs={'height': tt_data, 'style': 'ARIAL', 'layer': 'TEXT',}).set_placement((x_new+gp_x, gp_y - l_1/2), align=TextEntityAlignment.MIDDLE_CENTER) # Taruh teks patok 5 meter di bawah titik tanah

        t_elev = data.add_text(f'{d["elev"]:.2f}', dxfattribs={'height': tt_data, 'style': 'ARIAL', 'layer': 'TEXT', 'rotation': 90,'color': 4}).set_placement((x_new+gp_x, gp_y-l_2-l_2/2), align=TextEntityAlignment.MIDDLE_CENTER) # Taruh teks patok 5 meter di bawah titik tanah

        t_dist = data.add_text(f'{d["dist"]:.2f}', dxfattribs={'height': tt_data, 'style': 'ARIAL', 'layer': 'TEXT', 'rotation': 90,'color': 4}).set_placement((x_new+gp_x, gp_y-l_3-l_2/2), align=TextEntityAlignment.MIDDLE_CENTER) # Taruh teks patok 5 meter di bawah titik tanah 

        g_kecil = data.add_line((x_new+gp_x,gp_y-l_1),(x_new+gp_x,gp_y-l_2), dxfattribs={'layer': 'GARIS_TABLE'}) # garis potong keci 5 dari tanah vertikal

        if i == len(data_survey)-1 or i == 0:
            g_elev =data.add_line((x_new+gp_x, gp_y), (x_new+gp_x, dating+gp_y), dxfattribs={'layer': 'GARIS_ELEV'}) # garis elev

        

        

        if i < len(data_survey) - 1:
            x_next = data_survey[i+1]['dist_skala'] 
            x_next_asli = data_survey[i+1]['dist'] 
            x_new2 = x_next - jarak_awal_kertas
            
            y_next = data_survey[i+1]['elev_skala']-datum 
            y_next_design = data_survey[i+1]['design_elev_skala']-datum 
            
            g_dist =data.add_line((x_new+gp_x,gp_y-l_0),(x_new2+gp_x, gp_y-l_0), dxfattribs={'layer': 'GARIS_TABLE'}) # garis distance
            g_dist =data.add_line((x_new+gp_x,gp_y-l_1),(x_new2+gp_x, gp_y-l_1), dxfattribs={'layer': 'GARIS_TABLE'}) # garis distance
            g_dist =data.add_line((x_new+gp_x,gp_y-l_2),(x_new2+gp_x, gp_y-l_2), dxfattribs={'layer': 'GARIS_TABLE'}) # garis distance
            g_dist =data.add_line((x_new+gp_x,gp_y-l_3),(x_new2+gp_x, gp_y-l_3), dxfattribs={'layer': 'GARIS_TABLE'}) # garis distance
            g_dist =data.add_line((x_new+gp_x,gp_y-l_4),(x_new2+gp_x, gp_y-l_4), dxfattribs={'layer': 'GARIS_TABLE'}) # garis distance
            
            t_dist = data.add_text(f'{x_next_asli-x_asli:.2f}', dxfattribs={'height': tt_data, 'style': 'ARIAL', 'layer': 'TEXT','color': 4}).set_placement((x_new+gp_x+(x_next-x)/2, gp_y - l_1-l_1/2), align=TextEntityAlignment.MIDDLE_CENTER) # Taruh teks jarak di bawah garis tanah

            titik_design = y_design+gp_y
            titik_design_next = y_next_design+gp_y
            
            titik = y+gp_y
            titik_next = y_next+gp_y

            garis_curr = titik_design - titik
            garis_next = titik_design_next - titik_next

            if garis_curr <= 0 and garis_next <= 0 :
                hatch_arsiran = data.add_hatch(dxfattribs={'color': 3,'layer': 'HATCH_CUT'})
                hatch_arsiran.set_pattern_fill('ANSI31', scale=1, angle=0) #cut
                titik_batas = [
                    (x_new+gp_x,y+gp_y),   # Titik 1
                    (x_new+gp_x,y_design+gp_y),   # Titik 2
                    (x_new2+gp_x, y_next_design+gp_y),  # Titik 3
                    (x_new2+gp_x, y_next+gp_y)   # Titik 4
                ]
                hatch_arsiran.paths.add_polyline_path(titik_batas, is_closed=True)

            elif garis_curr >= 0 and garis_next >= 0 :
                hatch_arsiran = data.add_hatch( dxfattribs={'color': 4,'layer': 'HATCH_FILL'})
                hatch_arsiran.set_pattern_fill('ANSI37', scale=1, angle=0) #fill
                titik_batas = [
                    (x_new+gp_x,y+gp_y),   # Titik 1
                    (x_new+gp_x,y_design+gp_y),   # Titik 2
                    (x_new2+gp_x, y_next_design+gp_y),  # Titik 3
                    (x_new2+gp_x, y_next+gp_y)   # Titik 4
                ]
                hatch_arsiran.paths.add_polyline_path(titik_batas, is_closed=True)

            else :
                # --- DI DALAM ELSE ---
                abs_gc = abs(garis_curr)
                abs_gn = abs(garis_next)
                total_abs = abs_gc + abs_gn

                if total_abs > 0:
                    # 1. Hitung Jarak Horizontal dari Patok Kiri ke Titik Potong
                    lebar_segmen = x_new2 - x_new
                    x1 = lebar_segmen * (abs_gc / total_abs)
                    
                    # 2. Hitung Kemiringan Garis Tanah Asli
                    m = (y_next - y) / lebar_segmen
                    
                    # 3. Hitung Titik Potong
                    center_point_x = x_new + gp_x + x1
                    center_point_y = titik + (m * x1)

                    # 4. BIKIN HATCH SEGITIGA KIRI
                    
                        
                    h1 = data.add_hatch(dxfattribs={'color':3 if garis_curr < 0 else 4,'layer': 'HATCH_FILL' if garis_curr < 0 else 'HATCH_CUT'}) # Merah kalo tanah di atas (Cut)
                    h1.set_pattern_fill('ANSI31'if garis_curr < 0 else 'ANSI37', scale=1 )
                    
                    titik_segitiga_kiri = [
                        (x_new + gp_x, titik_design), 
                        (x_new + gp_x, titik), 
                        (center_point_x, center_point_y)
                    ]
                    h1.paths.add_polyline_path(titik_segitiga_kiri, is_closed=True)

                    # 5. BIKIN HATCH SEGITIGA KANAN
                    h2 = data.add_hatch(dxfattribs={'color':3 if garis_next < 0 else 4,'layer': 'HATCH_FILL' if garis_next < 0 else 'HATCH_CUT'})
                    h2.set_pattern_fill('ANSI31' if garis_next < 0 else 'ANSI37',  scale=1)
                    
                    titik_segitiga_kanan = [
                        (center_point_x, center_point_y),
                        (x_new2 + gp_x, titik_next),
                        (x_new2 + gp_x, titik_design_next)
                    ]
                    h2.paths.add_polyline_path(titik_segitiga_kanan, is_closed=True)




            g_tanah = data.add_line((x_new+gp_x,y+gp_y), (x_new2+gp_x, y_next+gp_y), dxfattribs={'layer': 'GARIS_ELEV'}) # garis tanah

            g_tanah = data.add_line((x_new+gp_x,y_design+gp_y), (x_new2+gp_x, y_next_design+gp_y), dxfattribs={'layer': 'GARIS_ELEV_DESIGN'}) # garis tanah
            
            if i == len(data_survey) - 2:
                line_7 = data.add_line ((x_new2+gp_x+off_1,gp_y-l_0),(x_new2+gp_x+off_1, gp_y-l_4), dxfattribs={'layer': 'GARIS_TABLE'})
                line_7 = data.add_line ((x_new2+gp_x,gp_y-l_0),(x_new2+gp_x+off_1, gp_y-l_0), dxfattribs={'layer': 'GARIS_TABLE'})
                line_7 = data.add_line ((x_new2+gp_x,gp_y-l_1),(x_new2+gp_x+off_1, gp_y-l_1), dxfattribs={'layer': 'GARIS_TABLE'})
                line_7 = data.add_line ((x_new2+gp_x,gp_y-l_2),(x_new2+gp_x+off_1, gp_y-l_2), dxfattribs={'layer': 'GARIS_TABLE'})
                line_7 = data.add_line ((x_new2+gp_x,gp_y-l_3),(x_new2+gp_x+off_1, gp_y-l_3), dxfattribs={'layer': 'GARIS_TABLE'})
                line_7 = data.add_line ((x_new2+gp_x, gp_y-l_4),(x_new2+gp_x+off_1, gp_y-l_4), dxfattribs={'layer': 'GARIS_TABLE'})

    
    return data
