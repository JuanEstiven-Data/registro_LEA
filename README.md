# 📊 Registro LEA - Pipeline y Análisis de Monitorías

## 🎯 Propósito

Este proyecto automatiza la consolidación, limpieza y análisis de los registros de monitorías del Laboratorio de Economía Aplicada (LEA).

Actualmente, los datos son generados a partir de formularios de Microsoft Forms y requieren limpieza manual, lo que introduce inconsistencias en variables clave como carrera, curso y semestre.

Este sistema busca:

* Estandarizar la información de monitorías
* Reducir errores humanos en la limpieza
* Generar un dataset consolidado confiable
* Proveer un dashboard descriptivo para toma de decisiones

---

## 👥 Usuarios

* Director del laboratorio (usuario principal)
* Monitores académicos (usuarios operativos)

Nivel técnico:

* Intermedio (Python básico o R)
* No se requiere conocimiento avanzado de programación

---

## ❗ Problema actual

* Limpieza manual de múltiples archivos Excel por semestre
* Inconsistencias en nombres de cursos, carreras y formatos
* Diferentes criterios de limpieza entre personas
* Dificultad para generar reportes confiables

---

## 📥 Input de datos

* Archivos Excel exportados desde Microsoft Forms
* Ubicación esperada:

```
data/raw/
```

### Supuestos

* Todos los archivos tienen la misma estructura
* El formulario no cambia su esquema
* Columnas obligatorias:

  * `curso`
  * `carrera`

---

## ⚙️ Proceso (Pipeline)

El script ejecuta las siguientes etapas:

1. **Ingesta**

   * Carga todos los archivos `.xlsx` de `data/raw/`
   * Unificación usando concatenación

2. **Estandarización**

   * Normalización de nombres de columnas
   * Limpieza de texto (minúsculas, tildes, espacios)

3. **Limpieza de variables clave**

   * Carrera
   * Curso
   * Semestre

   Incluye:

   * Normalización
   * Reglas de limpieza
   * Aplicación de diccionarios de mapeo

4. **Generación de dataset consolidado**

   * Dataset limpio listo para análisis

5. **Análisis descriptivo**

   * Generación de dashboard con matplotlib

---

## 📤 Output

### 1. Dataset consolidado

```
data/processed/registro_consolidado.xlsx
```

### 2. Dashboard descriptivo

```
data/processed/dashboard.png
```

---

## 🚀 Ejecución

### 1. Clonar repositorio

```
git clone <repo>
cd registro_LEA
```

### 2. Crear entorno virtual

```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias

```
pip install -r requirements.txt
```

### 4. Ejecutar pipeline

```
python src/pipeline/main.py
```

---

## 🌍 Portabilidad

El proyecto está diseñado para ejecutarse en:

* Windows
* Linux

Requisitos:

* Python 3.10+
* pip

---

## 🔐 Tratamiento de datos sensibles

El pipeline elimina y/o anonimiza información personal como:

- nombres
- correos electrónicos
- identificaciones

Esto garantiza que el dataset final sea apto para análisis y presentación.

---

## ⚠️ Supuestos y limitaciones

### Supuestos

* La estructura del formulario no cambia
* Los archivos se ubican correctamente en `data/raw/`
* Las columnas clave existen

### Limitaciones actuales

* No hay validación automática de estructura de archivos
* El dashboard es estático (no interactivo)
* Dependencia de mappings manuales

---

## 📊 Uso del output

El dataset y dashboard se utilizan para:

* Evaluar demanda de monitorías
* Analizar uso por curso y carrera
* Apoyar decisiones de contratación de monitores
* Identificar tendencias académicas

---

## 🧠 Arquitectura del proyecto

```
src/
├── ingestion/
├── cleaning/
├── mappings/
├── pipeline/
└── analysis/
```

---

## 🔮 Mejoras futuras

* Validación automática de estructura de input
* Dashboard interactivo (Tableau / Plotly)
* Automatización semestral del proceso
* Integración directa con fuente de datos

---