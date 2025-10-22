# Ejercicio 3 – Herencia de Grupos Sanguíneos  
Rubén Elices  


---

## Descripción general

Este proyecto implementa un sistema orientado a objetos en Python que permite **determinar los posibles grupos sanguíneos de un descendiente** a partir del grupo sanguíneo de sus progenitores.  
El programa calcula los porcentajes de probabilidad de cada grupo y los representa tanto en texto como mediante un **gráfico circular (tipo pie)** generado con `matplotlib`.

El ejercicio está dividido en tres fases, siguiendo las instrucciones del enunciado del tema:

---

## Fase 1 – Clases y cálculo de herencia

En esta fase se definen las clases que modelan el problema:

- **`GrupoSanguineo`**: Representa a un progenitor, validando su grupo sanguíneo mediante un descriptor.  
- **`Descendencia`**: Calcula las combinaciones posibles de alelos entre los padres y determina las probabilidades de los fenotipos resultantes (A, B, AB u O).

Al ejecutar esta fase, se pueden probar directamente distintos casos y visualizar los resultados en consola y en forma de gráfico circular.

---

## Fase 2 – Lectura y análisis desde archivos JSON

En esta fase se amplía el sistema para **leer datos desde un archivo externo en formato JSON** que contiene los grupos sanguíneos de distintos padres y madres.  
El programa:

1. Lee los registros y valida su formato.  
2. Calcula automáticamente las probabilidades de los posibles grupos sanguíneos de cada descendencia.  
3. Guarda los resultados en un nuevo archivo JSON junto con la fecha de análisis.

El código es compatible con varios formatos de entrada (tanto listas simples como estructuras anidadas con claves “father” y “mother”).

---

## Fase 3 – Gestión automática de archivos (flujo completo)

En esta última fase se implementa un flujo de trabajo automático que gestiona tres carpetas dentro del directorio `data/`:

- **`pending/`** – Archivos pendientes de analizar.  
- **`done/`** – Archivos ya procesados.  
- **`results/`** – Resultados generados en formato JSON.

El programa toma automáticamente los archivos JSON de la carpeta `data/pending/`, realiza los análisis y:
- Guarda los resultados en `data/results/`.  
- Copia los archivos analizados a `data/done/` antes de eliminarlos de `pending/`.  
- Genera los gráficos de cada análisis en orden de aparición dentro del archivo.

---

## Archivos entregados

- **`ejercicio3.py`** → Contiene las **tres fases completas** del ejercicio.  
  Este es el archivo principal y **totalmente ejecutable**.  
  Al ejecutarlo desde consola con el comando:

  ```bash
  python ejercicio3.py --fase3

el programa realiza automáticamente todo el flujo descrito (lectura, análisis, guardado de resultados y gestión de archivos).

ejercicio3.ipynb → Incluye únicamente las Fases 1 y 2 de forma independiente.
Este notebook permite ejecutar y visualizar estas fases dentro de Jupyter sin depender de argparse, ideal para comprobar su funcionamiento y entender la lógica paso a paso.
