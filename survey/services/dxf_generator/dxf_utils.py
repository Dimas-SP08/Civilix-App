import ezdxf
from ezdxf.enums import TextEntityAlignment


def setup_layer_style(doc):
    # Cek satu-satu biar 100% kebal error bentrok layer
    if 'KOP_KERTAS' not in doc.layers:
        doc.layers.new(name='KOP_KERTAS', dxfattribs={'color': 9})
        
    if 'TEXT' not in doc.layers:
        doc.layers.new(name='TEXT', dxfattribs={'color': 4})
        
    if 'GARIS_TABLE' not in doc.layers:
        doc.layers.new(name='GARIS_TABLE', dxfattribs={'color': 3})
        
    if 'GARIS_TANAH' not in doc.layers:
        doc.layers.new(name='GARIS_TANAH', dxfattribs={'color': 5})
        
    if 'GARIS_ELEV' not in doc.layers:
        doc.layers.new(name='GARIS_ELEV', dxfattribs={'color': 6})

    # Cek font style
    if 'ARIAL' not in doc.styles:
        doc.styles.new('ARIAL', dxfattribs={'font': 'arial.ttf'})


def kop_A4(doc,kop_user):

    block = doc.blocks.new(name=kop_user)
    
    # === 1. SETTING UKURAN & POSISI ===
    h_a4 = 297
    v_a4 = 210
    jarak = 5
    
    batas_kiri_kop = h_a4 - 35
    batas_kanan_kop = h_a4 - 5
    tengah_x = h_a4 - 20 
    tengah_kiri = h_a4 - 27.5
    tengah_kanan = h_a4 - 12.5

    # === 2. SETTING LAYER & STYLE (Biar gampang ngeditnya) ===
    layer_garis = {'layer': 'KOP_KERTAS'}
    
    # Fungsi kecil biar nulis teks nggak kepanjangan
    def gaya_teks(ukuran):
        return {'height': ukuran, 'style': 'ARIAL', 'layer': 'TEXT '}

    # === 3. GAMBAR GARIS TEPI & KERTAS ===
    kertas_a4 = [(0, 0), (h_a4, 0), (h_a4, v_a4), (0, v_a4)]
    garis_tepi = [
        (0 + jarak, 10), 
        (h_a4 - jarak, 10), 
        (h_a4 - jarak, v_a4 - jarak), 
        (0 + jarak, v_a4 - jarak)
    ]

    block.add_lwpolyline(kertas_a4, close=True, dxfattribs=layer_garis)
    block.add_lwpolyline(garis_tepi, close=True, dxfattribs=layer_garis)
    
    # Garis Vertikal Pembatas Kop (Kiri)
    block.add_line((batas_kiri_kop, 10), (batas_kiri_kop, v_a4 - 5), dxfattribs=layer_garis)
    
    # Garis Horizontal Pembagi Kotak (Looping)
    tinggi_kotak = 32.5
    y_garis =  tinggi_kotak # Mulai dari bawah ke atas
    y_garis2 = 5
    for i in range(5):
        block.add_line((batas_kiri_kop, y_garis), (batas_kanan_kop, y_garis), dxfattribs=layer_garis)
        block.add_line((batas_kiri_kop, y_garis+y_garis2), (batas_kanan_kop, y_garis+y_garis2), dxfattribs=layer_garis)
        y_garis += tinggi_kotak
        


    # === 4. ISI TEKS KOP ===
    # KOTAK 1: PEMILIK PROYEK
    block.add_text("PEMERINTAH KOTA", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 195), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BANDUNG DINAS", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 188), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BINA MARGA", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 181), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 2: KONSULTAN PERENCANA
    block.add_text("KONSULTAN PERENCANA:", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 165), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PT FUJICON ", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 158), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PRIANGAN PERDANA", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 153), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 3: NAMA PROYEK
    block.add_text("NAMA PROYEK:", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 133), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ENGINE CIVILIX", dxfattribs=gaya_teks(2.2)).set_placement((tengah_x, 124), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("AUTO-GENERATE LS", dxfattribs=gaya_teks(1.5)).set_placement((tengah_x, 118), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 4: JUDUL GAMBAR
    block.add_text("JUDUL GAMBAR:", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 100), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LONG SECTION", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 90), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 5: SKALA
    block.add_text("SKALA:", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 69), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA HORIZONTAL = 1:1000", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 60), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA VERTIKAL = 1:100", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 52), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ELEVASI DATUM = ...", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 44), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 6: PENGESAHAN & NOMOR GAMBAR
    # Garis pemisah vertikal buat tabel TTD sama No Gambar
    block.add_line((tengah_x, 10), (tengah_x,5+tinggi_kotak), dxfattribs=layer_garis)
    
    # Kolom Kiri: Drafter
    block.add_text("DIGAMBAR OLEH:", dxfattribs=gaya_teks(1.0)).set_placement((tengah_kiri, 35), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ISMAIL", dxfattribs=gaya_teks(1.8)).set_placement((tengah_kiri, 25), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("Drafter DPIB", dxfattribs=gaya_teks(1.0)).set_placement((tengah_kiri, 15), align=TextEntityAlignment.MIDDLE_CENTER)

    # Kolom Kanan: No Gambar
    block.add_text("NO. GAMBAR", dxfattribs=gaya_teks(1.0)).set_placement((tengah_kanan, 35), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LS-01", dxfattribs=gaya_teks(2.5)).set_placement((tengah_kanan, 25), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LEMBAR 1 / 1", dxfattribs=gaya_teks(1.0)).set_placement((tengah_kanan, 15), align=TextEntityAlignment.MIDDLE_CENTER)

    return block



def kop_A4(doc,kop_user):

    block = doc.blocks.new(name=kop_user)
    
    # === 1. SETTING UKURAN & POSISI ===
    h_a4 = 297
    v_a4 = 210
    jarak = 5
    
    batas_kiri_kop = h_a4 - 35
    batas_kanan_kop = h_a4 - 5
    tengah_x = h_a4 - 20 
    tengah_kiri = h_a4 - 27.5
    tengah_kanan = h_a4 - 12.5

    # === 2. SETTING LAYER & STYLE (Biar gampang ngeditnya) ===
    layer_garis = {'layer': 'KOP_KERTAS'}
    
    # Fungsi kecil biar nulis teks nggak kepanjangan
    def gaya_teks(ukuran):
        return {'height': ukuran, 'style': 'ARIAL', 'layer': 'TEKS_KOP'}

    # === 3. GAMBAR GARIS TEPI & KERTAS ===
    kertas_a4 = [(0, 0), (h_a4, 0), (h_a4, v_a4), (0, v_a4)]
    garis_tepi = [
        (0 + 10, jarak), 
        (h_a4 - jarak, jarak), 
        (h_a4 - jarak, v_a4 - jarak), 
        (0 + 10, v_a4 - jarak)
    ]

    block.add_lwpolyline(kertas_a4, close=True, dxfattribs=layer_garis)
    block.add_lwpolyline(garis_tepi, close=True, dxfattribs=layer_garis)
    
    # Garis Vertikal Pembatas Kop (Kiri)
    block.add_line((batas_kiri_kop, 10), (batas_kiri_kop, v_a4 - 5), dxfattribs=layer_garis)
    
    # Garis Horizontal Pembagi Kotak (Looping)
    tinggi_kotak = 32.5
    y_garis =  tinggi_kotak # Mulai dari bawah ke atas
    y_garis2 = 5
    for i in range(5):
        block.add_line((batas_kiri_kop, y_garis), (batas_kanan_kop, y_garis), dxfattribs=layer_garis)
        block.add_line((batas_kiri_kop, y_garis+y_garis2), (batas_kanan_kop, y_garis+y_garis2), dxfattribs=layer_garis)
        y_garis += tinggi_kotak
        


    # === 4. ISI TEKS KOP ===
    # KOTAK 1: PEMILIK PROYEK
    block.add_text("PEMERINTAH KOTA", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 195), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BANDUNG DINAS", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 188), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BINA MARGA", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 181), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 2: KONSULTAN PERENCANA
    block.add_text("KONSULTAN PERENCANA:", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 165), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PT FUJICON ", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 158), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PRIANGAN PERDANA", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 153), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 3: NAMA PROYEK
    block.add_text("NAMA PROYEK:", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 133), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ENGINE CIVILIX", dxfattribs=gaya_teks(2.2)).set_placement((tengah_x, 124), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("AUTO-GENERATE LS", dxfattribs=gaya_teks(1.5)).set_placement((tengah_x, 118), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 4: JUDUL GAMBAR
    block.add_text("JUDUL GAMBAR:", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 100), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LONG SECTION", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 90), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 5: SKALA
    block.add_text("SKALA:", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 69), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA HORIZONTAL = 1:1000", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 60), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA VERTIKAL = 1:100", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 52), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ELEVASI DATUM = ...", dxfattribs=gaya_teks(1.2)).set_placement((tengah_x, 44), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 6: PENGESAHAN & NOMOR GAMBAR
    # Garis pemisah vertikal buat tabel TTD sama No Gambar
    block.add_line((tengah_x, 10), (tengah_x,5+tinggi_kotak), dxfattribs=layer_garis)
    
    # Kolom Kiri: Drafter
    block.add_text("DIGAMBAR OLEH:", dxfattribs=gaya_teks(1.0)).set_placement((tengah_kiri, 35), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ISMAIL", dxfattribs=gaya_teks(1.8)).set_placement((tengah_kiri, 25), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("Drafter DPIB", dxfattribs=gaya_teks(1.0)).set_placement((tengah_kiri, 15), align=TextEntityAlignment.MIDDLE_CENTER)

    # Kolom Kanan: No Gambar
    block.add_text("NO. GAMBAR", dxfattribs=gaya_teks(1.0)).set_placement((tengah_kanan, 35), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LS-01", dxfattribs=gaya_teks(2.5)).set_placement((tengah_kanan, 25), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LEMBAR 1 / 1", dxfattribs=gaya_teks(1.0)).set_placement((tengah_kanan, 15), align=TextEntityAlignment.MIDDLE_CENTER)

    return block



def kop_A3(doc,kop_user):

    block = doc.blocks.new(name=kop_user)
    
    # === 1. SETTING UKURAN & POSISI ===
    h_a3 = 420
    v_a3 = 297
    jarak = 5
    
    # Lebar Kop dibesarin jadi 45 biar proporsional di A3
    batas_kiri_kop = h_a3 - 50
    batas_kanan_kop = h_a3 - 5
    tengah_x = h_a3 - 27.5 
    tengah_kiri = h_a3 - 38.75
    tengah_kanan = h_a3 - 16.25

    # === 2. SETTING LAYER & STYLE ===
    layer_garis = {'layer': 'KOP_KERTAS'}
    
    def gaya_teks(ukuran):
        return {'height': ukuran, 'style': 'ARIAL', 'layer': 'TEKS_KOP'}

    # === 3. GAMBAR GARIS TEPI & KERTAS ===
    kertas_a3 = [(0, 0), (h_a3, 0), (h_a3, v_a3), (0, v_a3)]
    garis_tepi = [
        (0 + 10, jarak), 
        (h_a3 - jarak, jarak), 
        (h_a3 - jarak, v_a3 - jarak), 
        (0 + 10, v_a3 - jarak)
    ]

    block.add_lwpolyline(kertas_a3, close=True, dxfattribs=layer_garis)
    block.add_lwpolyline(garis_tepi, close=True, dxfattribs=layer_garis)
    
    # Garis Vertikal Pembatas Kop (Kiri)
    block.add_line((batas_kiri_kop, 5), (batas_kiri_kop, v_a3 - 5), dxfattribs=layer_garis)
    
    # Garis Horizontal Pembagi Kotak (Di-scale jadi 46)
    tinggi_kotak = 46
    y_garis = tinggi_kotak 
    y_garis2 = 7 # Jarak double line ikut dilebarin dikit
    for i in range(5):
        block.add_line((batas_kiri_kop, y_garis), (batas_kanan_kop, y_garis), dxfattribs=layer_garis)
        block.add_line((batas_kiri_kop, y_garis+y_garis2), (batas_kanan_kop, y_garis+y_garis2), dxfattribs=layer_garis)
        y_garis += tinggi_kotak

    # === 4. ISI TEKS KOP (Tinggi & Ukuran Font Di-scale naik) ===
    # KOTAK 1: PEMILIK PROYEK

    block.add_text("PEMERINTAH KOTA", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 275), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BANDUNG DINAS", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 260), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BINA MARGA", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 245), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 2: KONSULTAN PERENCANA
    block.add_text("KONSULTAN PERENCANA:", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 233.5), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PT FUJICON ", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 215), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PRIANGAN PERDANA", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 200), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 3: NAMA PROYEK
    block.add_text("NAMA PROYEK:", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 187.5), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ENGINE CIVILIX", dxfattribs=gaya_teks(3.2)).set_placement((tengah_x, 170), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("AUTO-GENERATE LS", dxfattribs=gaya_teks(2.2)).set_placement((tengah_x, 155), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 4: JUDUL GAMBAR
    block.add_text("JUDUL GAMBAR:", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 141.5), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LONG SECTION", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 118), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 5: SKALA
    block.add_text("SKALA:", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 95.5), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA HORIZONTAL = 1:1000", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 82), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA VERTIKAL = 1:100", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 70), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ELEVASI DATUM = ...", dxfattribs=gaya_teks(1.8)).set_placement((tengah_x, 58), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 6: PENGESAHAN & NOMOR GAMBAR
    # Garis pemisah vertikal buat tabel TTD sama No Gambar
    block.add_line((tengah_x, 5), (tengah_x, 53), dxfattribs=layer_garis)
    
    # Kolom Kiri: Drafter
    block.add_text("DIGAMBAR OLEH:", dxfattribs=gaya_teks(1.5)).set_placement((tengah_kiri, 49.5), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ISMAIL", dxfattribs=gaya_teks(2.5)).set_placement((tengah_kiri, 35), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("Drafter DPIB", dxfattribs=gaya_teks(1.5)).set_placement((tengah_kiri, 21), align=TextEntityAlignment.MIDDLE_CENTER)

    # Kolom Kanan: No Gambar
    block.add_text("NO. GAMBAR", dxfattribs=gaya_teks(1.5)).set_placement((tengah_kanan, 49.5), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LS-01", dxfattribs=gaya_teks(3.5)).set_placement((tengah_kanan, 35), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LEMBAR 1 / 1", dxfattribs=gaya_teks(1.5)).set_placement((tengah_kanan, 21), align=TextEntityAlignment.MIDDLE_CENTER)

    return block

def kop_A2(doc,kop_user):
    block = doc.blocks.new(name=kop_user)
    
    # === 1. SETTING UKURAN & POSISI ===
    h_a2 = 594
    v_a2 = 420
    jarak = 5
    
    # Lebar Kop dibesarin jadi 70 biar gagah di A2
    batas_kiri_kop = h_a2 - 75
    batas_kanan_kop = h_a2 - 5
    tengah_x = h_a2 - 40 
    tengah_kiri = h_a2 - 57.5
    tengah_kanan = h_a2 - 22.5

    # === 2. SETTING LAYER & STYLE ===
    layer_garis = {'layer': 'KOP_KERTAS'}
    
    def gaya_teks(ukuran):
        return {'height': ukuran, 'style': 'ARIAL', 'layer': 'TEKS_KOP'}

    # === 3. GAMBAR GARIS TEPI & KERTAS ===
    kertas_a2 = [(0, 0), (h_a2, 0), (h_a2, v_a2), (0, v_a2)]
    garis_tepi = [
        (0 + 10, jarak), 
        (h_a2 - jarak, jarak), 
        (h_a2 - jarak, v_a2 - jarak), 
        (0 + 10, v_a2 - jarak)
    ]

    block.add_lwpolyline(kertas_a2, close=True, dxfattribs=layer_garis)
    block.add_lwpolyline(garis_tepi, close=True, dxfattribs=layer_garis)
    
    # Garis Vertikal Pembatas Kop (Kiri)
    block.add_line((batas_kiri_kop, 10), (batas_kiri_kop, v_a2 - 5), dxfattribs=layer_garis)
    
    # Garis Horizontal Pembagi Kotak (Di-scale jadi 65)
    tinggi_kotak = 65
    y_garis = tinggi_kotak 
    y_garis2 = 10 # Jarak double line (buat header) ikut dilebarin
    for i in range(5):
        block.add_line((batas_kiri_kop, y_garis), (batas_kanan_kop, y_garis), dxfattribs=layer_garis)
        block.add_line((batas_kiri_kop, y_garis+y_garis2), (batas_kanan_kop, y_garis+y_garis2), dxfattribs=layer_garis)
        y_garis += tinggi_kotak

    # === 4. ISI TEKS KOP (Tinggi & Ukuran Font Di-scale naik) ===
    # KOTAK 1: PEMILIK PROYEK
    block.add_text("PEMERINTAH KOTA", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 390), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BANDUNG DINAS", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 370), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BINA MARGA", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 350), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 2: KONSULTAN PERENCANA
    block.add_text("KONSULTAN PERENCANA:", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 330), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PT FUJICON ", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 310), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PRIANGAN PERDANA", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 290), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 3: NAMA PROYEK
    block.add_text("NAMA PROYEK:", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 265), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ENGINE CIVILIX", dxfattribs=gaya_teks(4.5)).set_placement((tengah_x, 240), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("AUTO-GENERATE LS", dxfattribs=gaya_teks(3.0)).set_placement((tengah_x, 220), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 4: JUDUL GAMBAR
    block.add_text("JUDUL GAMBAR:", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 200), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LONG SECTION", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 167.5), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 5: SKALA
    block.add_text("SKALA:", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 135), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA HORIZONTAL = 1:1000", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 115), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA VERTIKAL = 1:100", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 100), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ELEVASI DATUM = ...", dxfattribs=gaya_teks(2.5)).set_placement((tengah_x, 85), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 6: PENGESAHAN & NOMOR GAMBAR
    # Garis pemisah vertikal buat tabel TTD sama No Gambar
    block.add_line((tengah_x, 10), (tengah_x, 65), dxfattribs=layer_garis)
    
    # Kolom Kiri: Drafter
    block.add_text("DIGAMBAR OLEH:", dxfattribs=gaya_teks(2.0)).set_placement((tengah_kiri, 55), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ISMAIL", dxfattribs=gaya_teks(3.5)).set_placement((tengah_kiri, 35), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("Drafter DPIB", dxfattribs=gaya_teks(2.0)).set_placement((tengah_kiri, 18), align=TextEntityAlignment.MIDDLE_CENTER)

    # Kolom Kanan: No Gambar
    block.add_text("NO. GAMBAR", dxfattribs=gaya_teks(2.0)).set_placement((tengah_kanan, 55), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LS-01", dxfattribs=gaya_teks(5.0)).set_placement((tengah_kanan, 35), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LEMBAR 1 / 1", dxfattribs=gaya_teks(2.0)).set_placement((tengah_kanan, 18), align=TextEntityAlignment.MIDDLE_CENTER)

    return block


def kop_A1(doc,kop_user):
    block = doc.blocks.new(name=kop_user)
    
    # === 1. SETTING UKURAN & POSISI KERTAS A1 ===
    h_a1 = 841
    v_a1 = 594
    jarak = 5
    
    # Lebar Kop dibesarin jadi 100 biar imbang sama panjang A1
    batas_kiri_kop = h_a1 - 105
    batas_kanan_kop = h_a1 - 5
    tengah_x = h_a1 - 55 
    tengah_kiri = h_a1 - 80
    tengah_kanan = h_a1 - 30

    # === 2. SETTING LAYER & STYLE ===
    layer_garis = {'layer': 'KOP_KERTAS'}
    
    def gaya_teks(ukuran):
        return {'height': ukuran, 'style': 'ARIAL', 'layer': 'TEKS_KOP'}

    # === 3. GAMBAR GARIS TEPI & KERTAS ===
    kertas_a1 = [(0, 0), (h_a1, 0), (h_a1, v_a1), (0, v_a1)]
    garis_tepi = [
        (0 + 10, jarak), 
        (h_a1 - jarak, jarak), 
        (h_a1 - jarak, v_a1 - jarak), 
        (0 + 10, v_a1 - jarak)
    ]

    block.add_lwpolyline(kertas_a1, close=True, dxfattribs=layer_garis)
    block.add_lwpolyline(garis_tepi, close=True, dxfattribs=layer_garis)
    
    # Garis Vertikal Pembatas Kop (Kiri)
    block.add_line((batas_kiri_kop, 10), (batas_kiri_kop, v_a1 - 5), dxfattribs=layer_garis)
    
    # Garis Horizontal Pembagi Kotak (Di-scale jadi 90)
    tinggi_kotak = 90
    y_garis = tinggi_kotak + 10 # Start dari 100 (karena margin bawah 10)
    y_garis2 = 15 # Jarak double line (buat header) kita bikin lega 15 unit
    
    for i in range(5):
        block.add_line((batas_kiri_kop, y_garis), (batas_kanan_kop, y_garis), dxfattribs=layer_garis)
        block.add_line((batas_kiri_kop, y_garis+y_garis2), (batas_kanan_kop, y_garis+y_garis2), dxfattribs=layer_garis)
        y_garis += tinggi_kotak

    # === 4. ISI TEKS KOP (Font & Koordinat Y udah disesuaikan Proporsi A1) ===
    
    # KOTAK 1: PEMILIK PROYEK (Y: 460 - 550)
    # === 4. ISI TEKS KOP (Font & Koordinat Y udah disesuaikan Proporsi A1) ===
    
    # KOTAK 1: PEMILIK PROYEK (Y Safe Zone: 475 - 589)
    block.add_text("PEMERINTAH KOTA", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 560), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BANDUNG DINAS", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 532), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BINA MARGA", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 504), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 2: KONSULTAN PERENCANA (Y Safe Zone: 385 - 460)
    block.add_text("KONSULTAN PERENCANA:", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 445+22), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PT FUJICON ", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 420+22), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PRIANGAN PERDANA", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 395+22), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 3: NAMA PROYEK (Y Safe Zone: 295 - 370)
    block.add_text("NAMA PROYEK:", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 355+22), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ENGINE CIVILIX", dxfattribs=gaya_teks(6.0)).set_placement((tengah_x, 328+22), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("AUTO-GENERATE LS", dxfattribs=gaya_teks(4.5)).set_placement((tengah_x, 303+22), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 4: JUDUL GAMBAR (Y Safe Zone: 205 - 280)
    block.add_text("JUDUL GAMBAR:", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 265+22), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LONG SECTION", dxfattribs=gaya_teks(7.0)).set_placement((tengah_x, 235+22), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 5: SKALA (Y Safe Zone: 155 - 190)
    block.add_text("SKALA:", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 178+19), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA HORIZONTAL = 1:1000", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 158+15), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA VERTIKAL = 1:100", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 138+15), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ELEVASI DATUM = ...", dxfattribs=gaya_teks(3.5)).set_placement((tengah_x, 118+15), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 6: PENGESAHAN & NOMOR GAMBAR (Y Safe Zone: 10 - 100)
    # Garis pemisah vertikal buat tabel TTD sama No Gambar
    block.add_line((tengah_x, 10), (tengah_x, 100), dxfattribs=layer_garis)
    
    # Kolom Kiri: Drafter
    block.add_text("DIGAMBAR OLEH:", dxfattribs=gaya_teks(3.0)).set_placement((tengah_kiri, 80+27), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ISMAIL", dxfattribs=gaya_teks(5.0)).set_placement((tengah_kiri, 55+27), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("Drafter DPIB", dxfattribs=gaya_teks(3.0)).set_placement((tengah_kiri, 30+27), align=TextEntityAlignment.MIDDLE_CENTER)

    # Kolom Kanan: No Gambar
    block.add_text("NO. GAMBAR", dxfattribs=gaya_teks(3.0)).set_placement((tengah_kanan, 80+27), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LS-01", dxfattribs=gaya_teks(7.0)).set_placement((tengah_kanan, 55+27), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LEMBAR 1 / 1", dxfattribs=gaya_teks(3.0)).set_placement((tengah_kanan, 30+27), align=TextEntityAlignment.MIDDLE_CENTER)

    

    return block

def kop_A0(doc,kop_user):
    block = doc.blocks.new(name=kop_user)
    
    # === 1. SETTING UKURAN & POSISI KERTAS A0 ===
    h_a0 = 1189 
    v_a0 = 841
    jarak = 5
    
    # Lebar Kop dibesarin jadi 140 biar imbang sama raksasanya A0
    batas_kiri_kop = h_a0 - 145
    batas_kanan_kop = h_a0 - 5
    tengah_x = h_a0 - 75 
    tengah_kiri = h_a0 - 110
    tengah_kanan = h_a0 - 40

    # === 2. SETTING LAYER & STYLE ===
    layer_garis = {'layer': 'KOP_KERTAS'}
    
    def gaya_teks(ukuran):
        return {'height': ukuran, 'style': 'ARIAL', 'layer': 'TEKS_KOP'}

    # === 3. GAMBAR GARIS TEPI & KERTAS ===
    kertas_a0 = [(0, 0), (h_a0, 0), (h_a0, v_a0), (0, v_a0)]
    garis_tepi = [
        (0 + 10, jarak), 
        (h_a0 - jarak, jarak), 
        (h_a0 - jarak, v_a0 - jarak), 
        (0 + 10, v_a0 - jarak)
    ]

    block.add_lwpolyline(kertas_a0, close=True, dxfattribs=layer_garis)
    block.add_lwpolyline(garis_tepi, close=True, dxfattribs=layer_garis)
    
    # Garis Vertikal Pembatas Kop (Kiri)
    block.add_line((batas_kiri_kop, 10), (batas_kiri_kop, v_a0 - 5), dxfattribs=layer_garis)
    
    # Garis Horizontal Pembagi Kotak (Di-scale jadi 120)
    tinggi_kotak = 120
    y_garis = 130 # Start tinggi kotak TTD bawah
    y_garis2 = 20 # Jarak double line kita bikin lega 20 unit
    
    for i in range(5):
        block.add_line((batas_kiri_kop, y_garis), (batas_kanan_kop, y_garis), dxfattribs=layer_garis)
        block.add_line((batas_kiri_kop, y_garis+y_garis2), (batas_kanan_kop, y_garis+y_garis2), dxfattribs=layer_garis)
        y_garis += (tinggi_kotak + y_garis2) # 140 total per blok

    # === 4. ISI TEKS KOP (Font & Koordinat Y Proporsi Raksasa A0) ===
    
    # KOTAK 1: PEMILIK PROYEK (Y Safe Zone: 710 - 830)
    block.add_text("PEMERINTAH KOTA", dxfattribs=gaya_teks(7.0)).set_placement((tengah_x, 800), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BANDUNG DINAS", dxfattribs=gaya_teks(7.0)).set_placement((tengah_x, 770), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("BINA MARGA", dxfattribs=gaya_teks(7.0)).set_placement((tengah_x, 740), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 2: KONSULTAN PERENCANA (Y Safe Zone: 570 - 690)
    block.add_text("KONSULTAN PERENCANA:", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 665), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PT FUJICON ", dxfattribs=gaya_teks(7.0)).set_placement((tengah_x, 630), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("PRIANGAN PERDANA", dxfattribs=gaya_teks(7.0)).set_placement((tengah_x, 595), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 3: NAMA PROYEK (Y Safe Zone: 430 - 550)
    block.add_text("NAMA PROYEK:", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 525), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ENGINE CIVILIX", dxfattribs=gaya_teks(8.5)).set_placement((tengah_x, 485), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("AUTO-GENERATE LS", dxfattribs=gaya_teks(6.0)).set_placement((tengah_x, 450), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 4: JUDUL GAMBAR (Y Safe Zone: 290 - 410)
    block.add_text("JUDUL GAMBAR:", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 380), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LONG SECTION", dxfattribs=gaya_teks(10.0)).set_placement((tengah_x, 330), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 5: SKALA (Y Safe Zone: 150 - 270)
    block.add_text("SKALA:", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 245), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA HORIZONTAL = 1:1000", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 215), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("SKALA VERTIKAL = 1:100", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 185), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ELEVASI DATUM = ...", dxfattribs=gaya_teks(5.0)).set_placement((tengah_x, 155), align=TextEntityAlignment.MIDDLE_CENTER)

    # KOTAK 6: PENGESAHAN & NOMOR GAMBAR (Y Safe Zone: 10 - 130)
    # Garis pemisah vertikal buat tabel TTD sama No Gambar
    block.add_line((tengah_x, 10), (tengah_x, 130), dxfattribs=layer_garis)
    
    # Kolom Kiri: Drafter
    block.add_text("DIGAMBAR OLEH:", dxfattribs=gaya_teks(4.0)).set_placement((tengah_kiri, 105), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("ISMAIL", dxfattribs=gaya_teks(7.0)).set_placement((tengah_kiri, 70), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("Drafter DPIB", dxfattribs=gaya_teks(4.0)).set_placement((tengah_kiri, 35), align=TextEntityAlignment.MIDDLE_CENTER)

    # Kolom Kanan: No Gambar
    block.add_text("NO. GAMBAR", dxfattribs=gaya_teks(4.0)).set_placement((tengah_kanan, 105), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LS-01", dxfattribs=gaya_teks(10.0)).set_placement((tengah_kanan, 70), align=TextEntityAlignment.MIDDLE_CENTER)
    block.add_text("LEMBAR 1 / 1", dxfattribs=gaya_teks(4.0)).set_placement((tengah_kanan, 35), align=TextEntityAlignment.MIDDLE_CENTER)

    return block
