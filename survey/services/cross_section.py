from ..models import CrossSection

def process_create_c_section(project):
    """
    Creates default CrossSection points (A, B, C, D) for every CalculatedResult 
    (Station) in the project if they don't already exist.
    """
    
    # 1. Get all stations (CalculatedResult) for this project
    # 'results' is the related_name defined in CalculatedResult model
    stations = project.results.all() 
    
    
    # 2. Define the standard templates (Label & Distance from Center)
    # Negative = Left, Positive = Right
    default_templates = [
        {'label': 'A', 'distance': -6.0}, 
        {'label': 'B', 'distance': -3.0}, 
        {'label':'point','distance':0.00},
        {'label': 'C', 'distance': 3.0},  
        {'label': 'D', 'distance': 6.0},  
    ]
    
    new_cross_sections = []
    
    # 3. Iterate through each station
    for sta in stations:
        # Check if this station already has cross sections to prevent duplicates
        # 'c_section' is the related_name defined in CrossSection model
        if sta.c_section.exists():
            continue
            
        # Prepare the objects for this station
        for tmpl in default_templates:
            if tmpl['label'] == 'point' :
                Label = f'{sta.station}'
                elev = float(sta.elevation)
            else:
                Label = tmpl['label']
                elev= None
            new_cross_sections.append(
                CrossSection(
                    station=sta,
          
                    label=Label,
                    distance=tmpl['distance'],
                    mid=0.0,                # Default dummy reading
                    top=0.0,
                    bot=0.0,
                    elevation=elev          # Will be calculated later based on readings
                )
            )
            
    # 4. Save everything to database in one go (Performance efficient)
    if new_cross_sections:
        CrossSection.objects.bulk_create(new_cross_sections)
        
    return len(new_cross_sections)

def process_calculate_CS(project):
    pass