import pandas as pd

def to_float_or_none(value):
    """
    Utility untuk membersihkan string dari koma/titik 
    dan mengubahnya menjadi float yang valid.
    """
    if value is None or pd.isna(value):
        return None
    
    # Jika sudah float/int, langsung return
    if isinstance(value, (int, float)):
        return float(value)
    
    # Jika string, kita bersihkan
    if isinstance(value, str):
        # 1. Hilangkan spasi
        val = value.strip()
        if not val:
            return None
        
        # LOGIKA KRUSIAL: 
        # Jika ada format '1,234.56' (ribuan koma, desimal titik) 
        # atau '1.234,56' (ribuan titik, desimal koma)
        
        # Deteksi format Eropa/Indo (koma sebagai desimal: 1.234,56)
        if ',' in val and '.' in val:
            # Kasus: 1.234,567 -> hapus titik, ubah koma jadi titik
            val = val.replace('.', '').replace(',', '.')
        elif ',' in val:
            # Kasus: 1,235 -> ubah jadi 1.235
            val = val.replace(',', '.')
        try:
            return float(val)
        except ValueError:
            return None
    return None