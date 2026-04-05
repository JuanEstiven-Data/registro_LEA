"""
Diccionario de homologación para la columna 'actividades'.
Las llaves (keys) deben estar en minúsculas y sin tildes, ya que el texto
se normaliza antes de pasar por este mapeo.
"""

ACTIVIDADES_MAPPING = {
    # --- USO LIBRE Y MONITORÍAS ---
    'uso del espacio': 'Uso del Espacio',
    'monitoria': 'Monitoría',
    
    # --- CAPACITACIONES TABLEAU ---
    'capacitacion de tableau': 'Capacitación Tableau',
    'capacitacion tableau': 'Capacitación Tableau',
    'tableau': 'Capacitación Tableau',
    'curso tableau - sesion 1': 'Capacitación Tableau',
    'curso tableau - sesion 2': 'Capacitación Tableau',
    'monitoria tableau': 'Capacitación Tableau', # O podrías dejarlo en Monitoría, tú decides el enfoque
    
    # --- CAPACITACIONES R ---
    'capacitacion de r': 'Capacitación R',
    'curso eda r': 'Capacitación R',
    'curso eda - r': 'Capacitación R',
    'curso eda r - sesion 1': 'Capacitación R',
    'curso eda r - sesion 2': 'Capacitación R',
    'capacitacion r - semillero economia cubana': 'Capacitación R',
    
    # --- CAPACITACIONES POWER BI ---
    'capacitacion de power bi': 'Capacitación Power BI',
    'capacitacion power bi': 'Capacitación Power BI',
    'curso power bi': 'Capacitación Power BI',
    'curso basico - power bi': 'Capacitación Power BI',
    'curso lea power bi - ventas': 'Capacitación Power BI',
    
    # --- OTRAS CAPACITACIONES/CURSOS ---
    'capacitacion stata': 'Capacitación STATA',
    'capacitacion excel': 'Capacitación Excel',
    'curso python': 'Capacitación Python',
    'curso introduccion datos espaciales - sesion 1': 'Capacitación Datos Espaciales',
    'curso introduccion datos espaciales - sesion 2': 'Capacitación Datos Espaciales',
    'curso econometria espacial - sesion 1': 'Capacitación Econometría Espacial',
    'curso econometria espacial - sesion 2': 'Capacitación Econometría Espacial',
    
    # --- SIMULADORES ---
    'simulador stackelberg': 'Simulador Stackelberg',
    'simulador competencia perfecta': 'Simulador Competencia Perfecta',
    'simulador de competencia perfecta': 'Simulador Competencia Perfecta',
    'simulador tragedia de los comunes': 'Simulador Tragedia de los Comunes',
    'simulador: economia circular': 'Simulador Economía Circular',
    'simulador de economia circular': 'Simulador Economía Circular',
    'simulador economia circular': 'Simulador Economía Circular',
    'economia circular': 'Simulador Economía Circular',
    'simulador: harvard oligopolio': 'Simulador Harvard Oligopolio',
    
    # SIMULADOR ECONLAND (Incluye corrección de error 'ecoland')
    'capacitacion econland': 'Simulador Econland',
    'curso econland': 'Simulador Econland',
    'econland': 'Simulador Econland',
    'ecoland': 'Simulador Econland',
    
    # --- PROYECTOS Y TALLERES ESPECIALES ---
    'proyecto pobreza: yadira diaz': 'Proyecto Pobreza',
    'taller: gentrificacion': 'Taller Gentrificación',
    'busqueda de datos macroeconomicos': 'Búsqueda de Datos Macroeconómicos'
}