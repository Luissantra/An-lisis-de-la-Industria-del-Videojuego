import folium
import pandas as pd
from folium.plugins import MarkerCluster

def create_interactive_map(df, center=[20, 0], zoom=2):
    """
    Crea un mapa interactivo utilizando Folium para visualizar 
    la ubicación de los estudios de videojuegos de forma intereactiva.
    """
    # Cargar el mapa base del mundo
    m = folium.Map(location=center, zoom_start=zoom, tiles='CartoDB dark_matter')

    # Estilos personalizados para las regiones
    region_styles = {
        'North America': {'pin': 'purple', 'hex': '#800080'},
        'South America': {'pin': 'green', 'hex': '#28a745'},
        'Europe': {'pin': 'blue', 'hex': '#007bff'},
        'Asia': {'pin': 'red', 'hex': '#dc3545'},
        'Africa': {'pin': 'orange', 'hex': '#fd7e14'},
        'Oceania': {'pin': 'cadetblue', 'hex': '#5f9ea0'},
        'Other': {'pin': 'gray', 'hex': '#6c757d'}
    }
    # Capturamos las regiones únicas para crear un clúster de marcadores por región
    unique_regions = df['Region'].unique()
    for region in unique_regions:
        style = region_styles.get(region, region_styles['Other'])
        hex_color = style['hex']
        pin_color = style['pin']

        # Creamos capa de regiones
        region_layer = folium.FeatureGroup(name=region)

        # Modificamos los colores de las regiones de forma dinámica
        custom_js = f"""
        function(cluster) {{
            var childCount = cluster.getChildCount();
            var size = Math.min(30 + (childCount * 2), 80); 
            
            var html = '<div style="' +
                'background-color: {hex_color}40; ' +  // 40 adds transparency to the hex code
                'border: 2px solid {hex_color}; ' +
                'border-radius: 50%; ' +
                'color: {hex_color}; ' +
                'font-weight: bold; ' +
                'font-size: 14px; ' +
                'display: flex; ' +
                'align-items: center; ' +
                'justify-content: center; ' +
                'width: ' + size + 'px; ' +
                'height: ' + size + 'px;' +
                'box-shadow: 0 0 10px {hex_color};' + 
                '">' + childCount + '</div>';
                
            return new L.DivIcon({{ html: html, className: 'custom-cluster', iconSize: new L.Point(size, size) }});
        }}
        """

        # Inicializamos el cluster
        region_cluster = MarkerCluster(icon_create_function=custom_js).add_to(region_layer)
        # Filtramos el DataFrame por región
        region_df = df[df['Region'] == region]

        # Añadimos las estudios de la región al cluster
        for idx, row in region_df.iterrows():
            if pd.notna(row['Lat']) and pd.notna(row['Lon']):
                
                # Option 1 Implementation: Rich Data Popup. 
                # Using .get() means it safely shows 'N/A' if you haven't added these columns yet!
                founded = row.get('Founded', 'N/A')
                employees = row.get('Employees', 'N/A')
                
                popup_html = f"""
                <div style="font-family: Arial; min-width: 200px;">
                    <h4 style="margin-bottom: 5px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 3px;">
                        {row['Studio Name']}
                    </h4>
                    <p style="margin: 3px 0; color: #555;"><b>🌍 Region:</b> {region}</p>
                    <p style="margin: 3px 0; color: #555;"><b>📍 Location:</b> {row['City']}, {row['Country']}</p>
                </div>
                """
                
                folium.Marker(
                    location=[row['Lat'], row['Lon']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=row['Studio Name'],
                    icon=folium.Icon(color=pin_color, icon='gamepad', prefix='fa')
                ).add_to(region_cluster)

        # Capa completa regional
        region_layer.add_to(m)
  # Añadimos control de capas para poder activar/desactivar regiones
    folium.LayerControl(collapsed=False).add_to(m)

    return m



