import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import io

def make_graphic_file_io(table):
    '''Create survey visualization plots and return as BytesIO objects.
    
    Generates three types of plots:
    1. Elevation profile (line plot)
    2. Height difference (bar plot)
    3. Distance vs elevation (scatter plot)
    
    Args:
        table: Pandas DataFrame containing survey data
    
    Returns:
        dict: Dictionary containing three BytesIO objects with plot images
    '''
    
    buffers = {
        'elevation_profile': io.BytesIO(),
        'height_difference': io.BytesIO(),
        'elevation_scatter': io.BytesIO()
    }
    '''Make elevation profile plot'''
    fig1, ax = plt.subplots(dpi=100, tight_layout=True)
    ax.plot(table['point_label'], table['elevation'], lw=2, ls='-.')
    ax.grid(True)
    ax.set_xlabel('Point Number')
    ax.set_ylabel('Elevation (m)')
    ax.set_title('Elevation Profile')
    plt.xticks(rotation=45, ha='right')
    fig1.savefig(buffers['elevation_profile'], format='png')
    buffers['elevation_profile'].seek(0)
    plt.close(fig1)

    '''Make height difference bar plot'''
    fig2, ax2 = plt.subplots(dpi=100, tight_layout=True)
    ax2.bar(table['point_label'], table['height_difference'], color='orange')
    ax2.set_xlabel('Point Number')
    ax2.set_ylabel('Height Difference (m)')
    ax2.set_title('Height Difference Between Points')
    plt.xticks(rotation=45, ha='right')
    fig2.savefig(buffers['height_difference'], format='png')
    buffers['height_difference'].seek(0)
    plt.close(fig2)

    '''Make distance vs elevation with scatter plot'''
    fig3 = plt.figure(dpi=100)
    plt.scatter(table['distance'], table['elevation'])
    plt.title("Distances vs Elevation")
    plt.xlabel("Cumulative Distances (m)")
    plt.ylabel("Elevation AMSL (m)")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    plt.tight_layout()
    fig3.savefig(buffers['elevation_scatter'], format='png')
    buffers['elevation_scatter'].seek(0)
    plt.close(fig3)

    return buffers
    

def make_graphic_file_user(table,folder_path):
    '''Create and save survey visualization plots to files.
    
    Generates and saves three types of plots as PNG files:
    1. Elevation profile (line plot)
    2. Height difference (bar plot)
    3. Distance vs elevation (scatter plot)
    
    Args:
        table: Pandas DataFrame containing survey data
        folder_path: Directory path to save the plot images
    '''
    
    '''Make elevation profile plot'''
    fig1, ax = plt.subplots(dpi=100, tight_layout=True)
    ax.plot(table['POINT NUMBER'], table['ELEVATION (AMSL)'],lw=2, ls='-.')
    ax.grid(True)
    ax.set_xlabel('Point Number')
    ax.set_ylabel('Elevation (m)')
    ax.set_title('Elevation Profile')
    plt.xticks(rotation=45, ha='right')
    fig1.savefig(f"{folder_path}/elevation_profile.png" if folder_path else "elevation_profile.png")
    plt.close(fig1)

    '''Make height difference bar plot'''
    fig2, ax2 = plt.subplots(dpi=100, tight_layout=True)
    ax2.bar(table['POINT NUMBER'], table['HEIGHT DIFFERENCE'], color='orange')
    ax2.set_xlabel('Point Number')
    ax2.set_ylabel('Height Difference (m)')
    ax2.set_title('Height Difference Between Points')
    plt.xticks(rotation=45, ha='right')
    fig2.savefig(f"{folder_path}/height_difference_bar_plot.png" if folder_path else "height_difference_bar_plot.png")
    plt.close(fig2)
    
    '''Make distance vs elevation with scatter plot'''
    fig3=plt.figure(dpi=100)
    plt.scatter(table['DISTANCE (m)'], table['ELEVATION (AMSL)'])
    plt.title("Distances vs Elevation")
    plt.xlabel("Cumulative Distances (m)")
    plt.ylabel("Elevation AMSL (m)")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    plt.tight_layout()
    fig3.savefig(f"{folder_path}/elevation_scatter_plot.png" if folder_path else "elevation_scatter_plot.png")
    plt.close(fig3)

    
    