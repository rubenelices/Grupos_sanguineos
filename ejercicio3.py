# EJERCICIO 3
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
from collections import Counter

# Clase validadora (descriptor)
class GrupoSangDescriptor:
    def __get__(self, instance, owner):
        return getattr(instance, "_grupo_sanguineo", None)

    def __set__(self, instance, value):
        value = value.upper().strip()
        if value not in ['A', 'B', 'AB', 'O']:
            raise ValueError("El grupo sanguíneo debe ser A, B, AB u O.")
        setattr(instance, "_grupo_sanguineo", value)


# Clase que maneja los grupos sanguíneos
class GrupoSanguineo:
    grupo_sanguineo = GrupoSangDescriptor()  # Descriptor

    # Mapa de grupo sanguíneo (alelos posibles)
    __alelos_por_grupo = {
        "A": [("A", "A"), ("A", "O")],
        "B": [("B", "B"), ("B", "O")],
        "AB": [("A", "B")],
        "O": [("O", "O")]
    }

    def __init__(self, grupo):
        self.grupo_sanguineo = grupo  # Validado con descriptor

    @property
    def alelos_posibles(self):
        return self.__alelos_por_grupo[self.grupo_sanguineo]


# Clase Descendencia
class Descendencia:
    __genotipo_a_fenotipo = {
        ("A", "A"): "A",
        ("A", "O"): "A",
        ("O", "A"): "A",
        ("B", "B"): "B",
        ("B", "O"): "B",
        ("O", "B"): "B",
        ("A", "B"): "AB",
        ("B", "A"): "AB",
        ("O", "O"): "O"
    }

    def __init__(self, padre, madre):
        if not isinstance(padre, GrupoSanguineo) or not isinstance(madre, GrupoSanguineo):
            raise TypeError("Padre y madre deben ser instancias de la clase GrupoSanguineo.")
        self.__padre = padre
        self.__madre = madre

    @property
    def padre(self):
        return self.__padre

    @property
    def madre(self):
        return self.__madre

    def calcular_probabilidades(self):
        """Calcula las probabilidades de cada grupo sanguíneo posible del hijo."""
        combinaciones = []

        for alelos_padre in self.__padre.alelos_posibles:
            for alelos_madre in self.__madre.alelos_posibles:
                for alelo_p in alelos_padre:
                    for alelo_m in alelos_madre:
                        genotipo = tuple(sorted((alelo_p, alelo_m)))  # normalizado
                        fenotipo = self.__genotipo_a_fenotipo.get(genotipo)
                        if fenotipo:
                            combinaciones.append(fenotipo)

        conteo = Counter(combinaciones)
        total = sum(conteo.values())
        probabilidades = {k: round((v / total) * 100, 2) for k, v in conteo.items()}
        return probabilidades

    def mostrar_resultados(self):
        """Muestra resultados por consola y gráfico circular."""
        probabilidades = self.calcular_probabilidades()

        print(f"\nPadre: {self.__padre.grupo_sanguineo} | Madre: {self.__madre.grupo_sanguineo}")
        print("Posibles grupos sanguíneos del hijo:")
        for grupo, prob in probabilidades.items():
            print(f"{grupo}: {prob}%")

        # Gráfico circular
        plt.pie(
            probabilidades.values(),
            labels=[f"{g} ({p}%)" for g, p in probabilidades.items()],
            autopct='%1.1f%%',
            startangle=90
        )
        plt.title("Probabilidades de grupo sanguíneo del descendiente")
        plt.axis('equal')
        plt.show()



#Fase 2

import json
import os
from datetime import datetime

ABO_VALIDOS = {"A", "B", "AB", "O"}

def _norm_gs(x):
    """Normaliza el grupo ABO: 0/ '0' -> 'O', case-insensitive, valida ABO."""
    if x is None:
        raise ValueError("Falta 'gs' (grupo sanguíneo).")
    # números -> string
    if isinstance(x, (int, float)):
        x = str(int(x))
    v = str(x).strip().upper()
    if v == "0":  # el fichero usa 0 para 'O'
        v = "O"
    if v not in ABO_VALIDOS:
        raise ValueError(f"Grupo sanguíneo inválido: {x!r}. Debe ser A, B, AB u O.")
    return v

def _norm_rh(x):
    """Normaliza Rh a '+' o '-', o devuelve None si no viene."""
    if x is None:
        return None
    v = str(x).strip()
    if v not in {"+", "-"}:
        # Si viniera algo raro, lo ignoramos (no afecta al cálculo ABO)
        return None
    return v

def leer_registros_json(ruta: str):
    """
    Soporta dos formatos de entrada:
    1) Lista: [{"padre":"A","madre":"B"}, ...]
    2) Objeto con 'parents': [{"father":{"gs":"A","rh":"+"},"mother":{"gs":"B","rh":"-"}} , ...]
    Devuelve siempre una lista de dicts: {'padre','madre','rh_padre','rh_madre'} (Rh opcional).
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No existe el archivo de entrada: {ruta}")

    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)

    registros = []

    # Formato 2: {"parents": [ { "father": {...}, "mother": {...} }, ... ]}
    if isinstance(data, dict) and "parents" in data:
        parents = data["parents"]
        if not isinstance(parents, list):
            raise ValueError("La clave 'parents' debe contener una lista de registros.")
        for i, item in enumerate(parents, 1):
            try:
                father = item.get("father", {})
                mother = item.get("mother", {})
                gs_p = _norm_gs(father.get("gs"))
                gs_m = _norm_gs(mother.get("gs"))
                rh_p = _norm_rh(father.get("rh"))
                rh_m = _norm_rh(mother.get("rh"))
                registros.append({
                    "padre": gs_p, "madre": gs_m,
                    "rh_padre": rh_p, "rh_madre": rh_m
                })
            except Exception as e:
                raise ValueError(f"Registro #{i} inválido en 'parents': {e}") from e
        return registros

    # Formato 1: lista plana [{"padre":"A","madre":"B"}, ...]
    if not isinstance(data, list):
        raise ValueError("El JSON de entrada debe ser una lista o un objeto con clave 'parents'.")

    for i, item in enumerate(data, 1):
        if not isinstance(item, dict) or "padre" not in item or "madre" not in item:
            raise ValueError(f"Registro #{i} inválido. Debe tener claves 'padre' y 'madre'.")
        registros.append({
            "padre": _norm_gs(item["padre"]),
            "madre": _norm_gs(item["madre"]),
            "rh_padre": _norm_rh(item.get("rh_padre")),
            "rh_madre": _norm_rh(item.get("rh_madre")),
        })
    return registros


def analizar_registros(registros):
    """
    Toma [{'padre','madre','rh_padre','rh_madre'}, ...] y devuelve análisis:
    fecha_analisis, ABO padre/madre, Rh (si vino) y porcentajes ABO del descendiente.
    """
    resultados = []
    for item in registros:
        try:
            padre = GrupoSanguineo(item["padre"])
            madre = GrupoSanguineo(item["madre"])
            desc = Descendencia(padre, madre)
            porcentajes = desc.calcular_probabilidades()

            resultados.append({
                "fecha_analisis": datetime.now().isoformat(timespec="seconds"),
                "padre": padre.grupo_sanguineo,
                "madre": madre.grupo_sanguineo,
                # eco del Rh si venía en el fichero (NO afecta a los cálculos ABO)
                "rh_padre": item.get("rh_padre"),
                "rh_madre": item.get("rh_madre"),
                "porcentajes": porcentajes
            })
        except Exception as e:
            resultados.append({
                "fecha_analisis": datetime.now().isoformat(timespec="seconds"),
                "padre": item.get("padre"),
                "madre": item.get("madre"),
                "rh_padre": item.get("rh_padre"),
                "rh_madre": item.get("rh_madre"),
                "error": str(e)
            })
    return resultados


def guardar_resultados_json(ruta_salida: str, resultados, append: bool = True):
    """
    Escribe los 'resultados' en JSON. Si append=True y el archivo ya existe,
    agrega al final preservando el historial.
    """
    existentes = []
    if append and os.path.exists(ruta_salida):
        try:
            with open(ruta_salida, "r", encoding="utf-8") as f:
                existentes = json.load(f)
                if not isinstance(existentes, list):
                    existentes = []
        except Exception:
            existentes = []

    payload = existentes + resultados
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return ruta_salida



# FASE 3


import os
import json
import shutil
import matplotlib.pyplot as plt
from datetime import datetime

def graficar_estadisticas_individuales(resultados, carpeta_graficos="data/resultados/graficos"):
    """
    Genera un gráfico circular para cada pareja (padre, madre) en el orden original del archivo.
    Guarda cada gráfico como imagen PNG numerada para conservar el orden de registro.
    """
    os.makedirs(carpeta_graficos, exist_ok=True)
    total = len(resultados)

    for i, r in enumerate(resultados, start=1):
        porcentajes = r.get("porcentajes")
        if not porcentajes:
            continue

        padre = r["padre"]
        madre = r["madre"]

        plt.figure(figsize=(6, 6))
        plt.pie(
            porcentajes.values(),
            labels=[f"{g} ({p}%)" for g, p in porcentajes.items()],
            startangle=90,
            autopct="%1.1f%%"
        )
        plt.title(f"Padre {padre} × Madre {madre}")
        plt.axis("equal")

        # Prefijo numérico con ceros a la izquierda, ej: 001, 002, 003...
        prefijo = str(i).zfill(len(str(total)))
        nombre_archivo = f"{prefijo}_{padre}_{madre}.png".replace("/", "_")
        ruta_img = os.path.join(carpeta_graficos, nombre_archivo)
        plt.savefig(ruta_img)
        plt.close()

    print(f"{len(resultados)} gráficos generados en orden en '{carpeta_graficos}'.")


def fase3_procesar_registros(base_dir="data"):
    """
    Procesa todos los archivos JSON en 'data/pending/', guarda los resultados en
    'data/resultados/resultados.json', genera gráficos, y mueve los archivos procesados a 'data/done/'.
    """
    carpeta_pending = os.path.join(base_dir, "pending")
    carpeta_done = os.path.join(base_dir, "done")
    carpeta_resultados = os.path.join(base_dir, "resultados")
    ruta_resultados_json = os.path.join(carpeta_resultados, "resultados.json")

    # Crear las carpetas si no existen
    os.makedirs(carpeta_pending, exist_ok=True)
    os.makedirs(carpeta_done, exist_ok=True)
    os.makedirs(carpeta_resultados, exist_ok=True)

    archivos = [f for f in os.listdir(carpeta_pending) if f.endswith(".json")]
    if not archivos:
        print("No hay archivos pendientes para procesar, se ha creado la carpeta 'data/pending' si no existía. Introuzca en la carpeta pending los archivos JSON a procesar.")
        return

    print(f"Archivos pendientes encontrados: {archivos}")

    for archivo in archivos:
        ruta_in = os.path.join(carpeta_pending, archivo)
        print(f"\nProcesando archivo: {archivo}")

        try:
            registros = leer_registros_json(ruta_in)
            resultados = analizar_registros(registros)
            guardar_resultados_json(ruta_resultados_json, resultados, append=True)

            # Generar gráficos individuales
            graficar_estadisticas_individuales(resultados, carpeta_graficos=os.path.join(carpeta_resultados, "graficos"))

            # Mover archivo a "done"
            destino = os.path.join(carpeta_done, archivo)
            shutil.move(ruta_in, destino)
            print(f"Archivo movido a: {destino}")

        except Exception as e:
            print(f"Error procesando {archivo}: {e}")

    print("\nTodos los archivos pendientes han sido procesados correctamente.")
    print(f"Resultados acumulados en: {ruta_resultados_json}")


# BLOQUE PRINCIPAL: permite ejecutar la Fase 3 desde consola


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Ejercicio 3: procesar y analizar grupos sanguíneos")
    parser.add_argument("--fase3", action="store_true", help="Ejecutar la Fase 3 (procesar todos los JSON de data/pending/)")
    args, extras = parser.parse_known_args()

    if args.fase3:
        fase3_procesar_registros()
    else:
        print("Usa el argumento --fase3 para ejecutar la automatización.")
