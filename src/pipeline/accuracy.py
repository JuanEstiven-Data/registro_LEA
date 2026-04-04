import pandas as pd
df = pd.read_csv('data/processed/registro_consolidado.csv')
# PRUEBA 1: PRIVACIDAD (PII CHECK)
columnas_prohibidas = ['nombre_completo', 'email', 'profesor_encargado', 'monitor_encargado']
for col in columnas_prohibidas:
    if col in df.columns:
        print(f"🚨 ALERTA PELIGRO: La columna {col} sigue viva.")

# print("\nMuestra de IDs de Estudiantes:")
# print(df['estudiante_id'].head())

###
# PRUEBA 2: CARDINALIDAD
###
print("\nCategorías únicas de Carreras:")
print(df['carrera'].sort_values().value_counts().unique())

# print("\nCategorías únicas de Profesores:")
# print(df['profesor_id'].sort_values().unique())

###
# PRUEBA 3: LÓGICA MATEMÁTICA (RANGOS)
###
print("\nDistribución de Semestres:")
print(df['semestre'].value_counts().sort_index())

###
# PRUEBA 4: COMPLETITUD
###
#print("\nPorcentaje de valores Nulos por columna:")
#print((df.isnull().sum() / len(df)) * 100)

###
# PRUEBA 5: TRAZABILIDAD
###
# Tomamos el ID del primer estudiante en la lista
#id_prueba = df['estudiante_id'].iloc[0]

# Filtramos todo el dataset para ver la vida de ese estudiante
#historial_estudiante = df[df['estudiante_id'] == id_prueba]
#print(f"\nHistorial del estudiante {id_prueba}:")
#print(historial_estudiante[['mes', 'curso', 'actividades', "año"]])