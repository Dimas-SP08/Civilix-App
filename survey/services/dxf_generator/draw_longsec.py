from ...models import CalculatedResult
from ezdxf import bbox
from ezdxf.enums import TextEntityAlignment
from .dxf_utils import setup_layer_style
import math


def draw_long_section(project_id, kop, skala_x, skala_y, sta_start, sta_end, datum_value, datum_type, units, jarak_max, jarak_max_vertikal, jarak_default, jarak_default_vertikal, margin, jarak_kop, doc, paper_size, msp):
    
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
            'elev': float(item.elevation)
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

    
    '''SETUP LAYER,BLOCK & BASE_POINT'''
    setup_layer_style(doc)
    
    batas_kop = bbox.extents(kop)
    center_kop = batas_kop.center
    kop.base_point = center_kop 

    koordinat = 0   
    for i,data in enumerate(data_sekat): 
        gambar = doc.blocks.new(name=f'GAMBAR_{i+1}')
        data = data_survey_block(doc,data_sekat[i],i,datum_value, datum_type,skala_y)
        batas_data = bbox.extents(data)
        center_data = batas_data.center
        data.base_point = center_data
 

        gambar.add_blockref(f'DATA_SURVEY_{i+1}', insert=(200-margin, 200))
        gambar.add_blockref(paper_size, insert=(200, 200)) 
        

        msp.add_blockref(f'GAMBAR_{i+1}', insert=(200+koordinat, 200))
        koordinat += jarak_kop
    
    return doc



def data_survey_block(doc,data_survey,angka,datum_value, datum_type, skala_y):
    


    all_elev = []
    all_elev_asli = []
    if datum_type == 'auto':
        for i in data_survey:
            all_elev.append(i['elev_skala'])
            all_elev_asli.append(i['elev'])

        datum = math.floor(min(all_elev)) - 2
        datum_asli = math.floor(min(all_elev_asli)) - 2
    else:
        datum = datum_value * skala_y
        datum_asli = datum_value
    
    
    
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
    th_titik =data.add_text(f"DL = {datum_asli:<.2f}M", dxfattribs={'height': tt_biasa, 'style': 'ARIAL', 'layer': 'TEXT',}).set_placement((2, l_1/2+l_0), align=TextEntityAlignment.MIDDLE_LEFT) 
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
        patok = d['point']

        if i == len(data_survey) - 1:
            t_head = data.add_text("LONG SECTION (POTONGAN MEMANJANG)", dxfattribs={'height': 3.5, 'style': 'ARIAL', 'layer': 'TEXT'}).set_placement(( gp_x+x_new/2, gp_y-40), align=TextEntityAlignment.MIDDLE_CENTER)
            t_head.dxf.lineweight = 0.5

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
