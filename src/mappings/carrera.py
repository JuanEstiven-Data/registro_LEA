"""
Diccionario de normalización de Carreras de la Universidad
Las llaves (keys) deben estar en minúsculas y sin tildes, ya que el texto
se normaliza antes de pasar por este mapeo.
"""
CARRERA_MAPPING = {
    # --- CIENCIAS ECONÓMICAS ---
    'administracion de empresas': 'Administración de Empresas',
    'adminstracion de empresas': 'Administración de Empresas', # Typo común
    'administración de empresas': 'Administración de Empresas',
    
    'negocios internacionales': 'Negocios Internacionales',
    'negocios internationales': 'Negocios Internacionales', # Typo en inglés
    'negocios internacionales y economia': 'Negocios Internacionales',
    
    'mercadeo': 'Mercadeo',
    'mercado': 'Mercadeo', # Typo
    'mercadeo y negocios internacionales': 'Mercadeo', # Se elige la primera carrera
    'economia y mercadeo': 'Economía', # Se elige la primera carrera
    
    'finanzas': 'Finanzas',
    
    'economia': 'Economía',
    'economía': 'Economía',
    
    # --- POSGRADOS ---
    'mba': 'Maestría en Administración de Empresas',
    'maestria en administracion de empresas': 'Maestría en Administración de Empresas',
    'maestria en restauracion ecologica': 'Maestría en Restauración Ecológica',
    'maestria politica social': 'Maestría en Política Social',
    'maestria gestion': 'Maestría en Gestión',
    'maestría gestión': 'Maestría en Gestión',
    'doctorado en economia': 'Doctorado en Economía',
    
    # --- INGENIERÍAS ---
    'ingenieria industrial': 'Ingeniería Industrial',
    'ingeniera industrial': 'Ingeniería Industrial', # Typo de género
    
    'ingenieria de sistemas': 'Ingeniería de Sistemas',
    'ingenieria en sistemas': 'Ingeniería de Sistemas', # Variación 'en'
    
    'ingenieria biomedica': 'Ingeniería Biomédica',
    'ingenieria civil': 'Ingeniería Civil',
    
    'ingenieria electronica': 'Ingeniería Electrónica',
    'ingieneria electronica': 'Ingeniería Electrónica', # Typo
    
    'ingenieria': 'Ingeniería', # Categoría genérica
    
    # --- SALUD ---
    'enfermeria': 'Enfermería',
    'medicina': 'Medicina',
    'nutricion': 'Nutrición',
    'nutricion y dietetica': 'Nutrición',
    
    # --- CIENCIAS SOCIALES / HUMANIDADES ---
    'derecho': 'Derecho',
    'ciencia politica': 'Ciencia Política',
    'comunicacion': 'Comunicación',
    'diseno de comunicacion': 'Diseño de Comunicación',
    'diseño de comunicación': 'Diseño de Comunicación',
    'turismo': 'Turismo',
    'arquitectura': 'Arquitectura',
    'biologia': 'Biología',
    
    # --- OTROS / CONVENIOS ---
    'cali visible': 'Cali Visible',
    'javeriano collage': 'Javeriano Collage',
    
    # --- EXCLUSIONES ADICIONALES ---
    'departamento de economia y finanzas': 'NO APLICA'
}