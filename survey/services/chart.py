def process_elevation_chart(project):
    # Ambil data hasil perhitungan yang sudah diurutkan
    # TAMBAHKAN 'design_elevation' di sini
    results = project.results.all().order_by('id').values(
        'station', 'cumulative_distance', 'elevation', 'design_elevation'
    )
    
    if not results.exists():
        return None
        
    data = list(results) 
    
    # Pisahkan data untuk format yang mudah dikonsumsi di JS
    chart_data = {
        'stations': [r['station'] for r in data],
        'distances': [r['cumulative_distance'] for r in data],
        'elevations': [r['elevation'] for r in data],
        # TAMBAHKAN list design_elevations. 
        # Jika kosong (None), kita isi None agar grafik putus atau tidak tergambar.
        'design_elevations': [r['design_elevation'] for r in data], 
    }
    return chart_data