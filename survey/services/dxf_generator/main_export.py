import io
from ezdxf.addons import Importer
import ezdxf
from .dxf_utils import kop_A0, kop_A1, kop_A2, kop_A3, kop_A4
from .draw_longsec import draw_long_section
from .draw_crosssec import draw_cross_section
from .draw_cutfill_long import draw_cutfill_long
import os 
import tempfile 


def process_export_dxf_advanced (project_id,context):
    """
    Fungsi ini baca data project, baca kop di memory (jika ada), 
    menggambar grafik, lalu mereturn data DXF dalam bentuk string.
    """
    # A. MENYIAPKAN DOKUMEN DXz`F (CANVAS)

    version = context.get('dxf_version', 'R2018')
    kop_type = context.get('kop_type')
    skala_x = context.get('skala_x')
    grafik_type = context.get('grafik_type')
    skala_y = context.get('skala_y')
    sta_start = context.get('sta_start')
    sta_end = context.get('sta_end')
    custom_kop_file = context.get('custom_kop_file')
    datum_value = context.get('datum_value')
    datum_type = context.get('datum_type')
    units = context.get('units')
    paper_size = context.get('paper_size')

    doc = ezdxf.new(version)
    if units == 'm':
        doc.units = ezdxf.units.M
        skala_y = 1000/skala_y
        skala_x = 1000/skala_x
    elif units == 'cm':
        doc.units = ezdxf.units.CM
        skala_y = 10/skala_y
        skala_x = 10/skala_x
    else:
        doc.units = ezdxf.units.MM
        skala_y = 1/skala_y
        skala_x = 1/skala_x
    msp = doc.modelspace()

    if kop_type == 'custom' and custom_kop_file:
        tmp_file_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp_file:
                for chunk in custom_kop_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name # Simpan lokasi filenya

            # BACA PAKAI readfile() -> JAUH LEBIH STABIL!
            doc_sumber = ezdxf.readfile(tmp_file_path)
            
            importer = Importer(doc_sumber, doc)
            importer.import_table('styles', replace=True)
            importer.import_blocks(['KOP']) 
            importer.finalize()
            
            kop = doc.blocks.get('KOP')
            
            
            if paper_size in ['A4', 'A3', 'A2', 'A1', 'A0']:
                doc.blocks.rename_block('KOP', paper_size)

        except Exception as e:
            print(f"Error DXF Import Custom Kop: {e}")
        finally:
            # BERSIH-BERSIH: Wajib hapus file temp setelah selesai dibaca
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
                
    elif kop_type == 'default':
        if paper_size == 'A4':
            kop = kop_A4(doc,paper_size)
        elif paper_size == 'A3':
            kop = kop_A3(doc,paper_size)
        elif paper_size == 'A2':
            kop = kop_A2(doc,paper_size)
        elif paper_size == 'A1':
            kop = kop_A1(doc,paper_size)
        elif paper_size == 'A0':
            kop = kop_A0(doc,paper_size)
        else:
            kop = kop_A3(doc,paper_size) 

    if paper_size == 'A4':
        # A4 Landscape: 297 x 210 mm
        jarak_max = 200            # Lebar area gambar
        jarak_max_vertikal = 210 - 20  # 190
        jarak_default = 200
        jarak_default_vertikal = 210 - 20
        margin = 14
        jarak_kop = 400

    elif paper_size == 'A3':
        # A3 Landscape: 420 x 297 mm
        jarak_max = 300 
        jarak_max_vertikal = 297 - 20  # 277
        jarak_default = 300
        jarak_default_vertikal = 297 - 20
        margin = 13 * 2
        jarak_kop = 400 * 2

    elif paper_size == 'A2':
        # A2 Landscape: 594 x 420 mm
        jarak_max = 450
        jarak_max_vertikal = 420 - 20  # 400
        jarak_default = 450
        jarak_default_vertikal = 420 - 20
        margin = 13 * 3
        jarak_kop = 400 * 3

    elif paper_size == 'A1':
        # A1 Landscape: 841 x 594 mm
        jarak_max = 650
        jarak_max_vertikal = 594 - 20  # 574
        jarak_default = 650
        jarak_default_vertikal = 594 - 20
        margin = 14 * 4
        jarak_kop = 400 * 4

    elif paper_size == 'A0':
        # A0 Landscape: 1189 x 841 mm
        jarak_max = 950
        jarak_max_vertikal = 841 - 20  # 821
        jarak_default = 950
        jarak_default_vertikal = 841 - 20
        margin = 14 * 5
        jarak_kop = 400 * 5

    else:
        # Default ke A3 jika input tidak dikenal
        jarak_max = 300 
        jarak_max_vertikal = 297 - 20
        jarak_default = 300
        jarak_default_vertikal = 297 - 20
        margin = 13 * 3
        jarak_kop = 400 * 3

    if grafik_type == 'long_section':
        draw_long_section(project_id, kop, skala_x, skala_y, sta_start, sta_end, datum_value, datum_type, units, jarak_max, jarak_max_vertikal, jarak_default, jarak_default_vertikal, margin, jarak_kop, doc, paper_size, msp)

    elif grafik_type == 'cross_section':
        draw_cross_section(project_id, kop, skala_x, skala_y, sta_start, sta_end, datum_value, datum_type, units, jarak_max, jarak_max_vertikal, jarak_default, jarak_default_vertikal, margin, jarak_kop, doc, paper_size, msp)
    
    elif grafik_type == 'cutfill_long':
        draw_cutfill_long(project_id, kop, skala_x, skala_y, sta_start, sta_end, datum_value, datum_type, units, jarak_max, jarak_max_vertikal, jarak_default, jarak_default_vertikal, margin, jarak_kop, doc, paper_size, msp, )


   # 4. KELUARKAN SEBAGAI STRING (Teks DXF)
    out_buffer = io.StringIO()
    doc.write(out_buffer)
    hasil_dxf_teks = out_buffer.getvalue()
    out_buffer.close() 
    
    return hasil_dxf_teks

