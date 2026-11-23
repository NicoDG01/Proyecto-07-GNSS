import pandas as pd
import numpy as np


class ProcesadorGNSS:
    """Módulo de procesamiento, limpieza y diagnóstico de mediciones GNSS."""

    RECEPTORES_ESPERADOS = [f"R{i:02d}" for i in range(1, 11)]
    INTERVALO_MINUTOS = 10
    REGISTROS_SEMANA_COMPLETA = 7 * 24 * 6  # 1008 mediciones cada 10 min

    def __init__(self):
        self.df_raw = None
        self.df_limpio = None
        self.resumen_receptores = []
        self.diagnosticos = []
        self.reporte_limpieza = {}

    def cargar_csv(self, ruta_archivo: str) -> None:
        """Carga y valida la estructura básica del archivo CSV (RF-01, RNF-04)."""
        columnas_req = {"timestamp", "receptor", "satelites", "hdop", "error_m", "estado"}
        df = pd.read_csv(ruta_archivo)

        if not columnas_req.issubset(set(df.columns)):
            faltantes = columnas_req - set(df.columns)
            raise ValueError(f"El archivo CSV no contiene las columnas requeridas: {', '.join(faltantes)}")

        self.df_raw = df
        self._limpiar_datos()

    def _limpiar_datos(self) -> None:
        """Elimina duplicados, trata valores negativos y gestiona registros SIN_FIX (RF-02, RF-03)."""
        df = self.df_raw.copy()
        total_inicial = len(df)

        # 1. Convertir timestamp a datetime y descartar filas con fecha/receptor corruptos
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["receptor"] = df["receptor"].astype(str).str.strip()
        df = df.dropna(subset=["timestamp", "receptor", "estado"])

        # 2. Identificar y eliminar registros duplicados exactos
        duplicados = int(df.duplicated().sum())
        df = df.drop_duplicates().copy()

        # 3. Convertir columnas numéricas de forma segura
        df["satelites"] = pd.to_numeric(df["satelites"], errors="coerce")
        df["hdop"] = pd.to_numeric(df["hdop"], errors="coerce")
        df["error_m"] = pd.to_numeric(df["error_m"], errors="coerce")

        # 4. Contabilizar mediciones inválidas (error_m < 0 o hdop < 0) por receptor antes de anularlas
        mask_err_neg = df["error_m"] < 0
        invalidos_por_receptor = df[mask_err_neg].groupby("receptor").size().to_dict()
        total_invalidos = int(mask_err_neg.sum())

        # Reemplazar valores negativos con NaN para no distorsionar promedios ni gráficos
        df.loc[mask_err_neg, "error_m"] = np.nan
        df.loc[df["hdop"] < 0, "hdop"] = np.nan

        # 5. Gestionar estado SIN_FIX (RF-03): asegurar que sin solución no compute precisión válida
        mask_sin_fix = df["estado"].str.strip() == "SIN_FIX"
        df.loc[mask_sin_fix, ["hdop", "error_m"]] = np.nan

        # Ordenar cronológicamente
        df = df.sort_values(["receptor", "timestamp"]).reset_index(drop=True)

        self.df_limpio = df
        self.reporte_limpieza = {
            "total_inicial": total_inicial,
            "duplicados_eliminados": duplicados,
            "invalidos_corregidos": total_invalidos,
            "invalidos_por_receptor": invalidos_por_receptor,
            "total_valido": len(df),
        }

    def analizar(self, umbral_hdop: float, umbral_error: float, umbral_satelites: int, ventana_movil: int) -> None:
        """Ejecuta el análisis estadístico y la detección de anomalías (RF-05, RF-07, RF-08)."""
        if self.df_limpio is None or self.df_limpio.empty:
            raise ValueError("No hay datos cargados para analizar.")

        self.resumen_receptores = []
        self.diagnosticos = []

        receptores = sorted(self.df_limpio["receptor"].unique())

        for rec in receptores:
            sub = self.df_limpio[self.df_limpio["receptor"] == rec].copy()
            n_registros = len(sub)

            hdop_prom = float(sub["hdop"].mean()) if sub["hdop"].notna().any() else 0.0
            error_prom = float(sub["error_m"].mean()) if sub["error_m"].notna().any() else 0.0
            pct_sin_fix = float((sub["estado"] == "SIN_FIX").mean() * 100.0)

            # Detección de problemas operativos (RF-07)
            problemas_rec = []

            # a) Ausencia de reportes (brechas temporales respecto a los 1008 registros esperados)
            if n_registros < self.REGISTROS_SEMANA_COMPLETA:
                faltantes = self.REGISTROS_SEMANA_COMPLETA - n_registros
                problemas_rec.append(f"ausencia de reportes ({faltantes} registros faltantes)")

            # b) Mediciones inválidas detectadas en limpieza
            cant_inv = self.reporte_limpieza["invalidos_por_receptor"].get(rec, 0)
            if cant_inv > 0:
                problemas_rec.append(f"mediciones inválidas ({cant_inv} valores negativos)")

            # c) Obstrucción progresiva (degradación sostenida entre la primera y última parte de la semana)
            tercio = max(1, n_registros // 3)
            hdop_inicio = sub["hdop"].iloc[:tercio].mean()
            hdop_fin = sub["hdop"].iloc[-tercio:].mean()
            sat_inicio = sub["satelites"].iloc[:tercio].mean()
            sat_fin = sub["satelites"].iloc[-tercio:].mean()

            es_obstruccion = (
                pd.notna(hdop_inicio)
                and pd.notna(hdop_fin)
                and (hdop_fin - hdop_inicio > 1.2)
                and (sat_inicio - sat_fin > 2.5)
            )
            if es_obstruccion:
                problemas_rec.append("obstrucción progresiva")

            # d) Períodos sin solución (SIN_FIX)
            if pct_sin_fix >= 2.0 and not es_obstruccion:
                problemas_rec.append(f"períodos sin solución ({pct_sin_fix:.1f}%)")
            elif pct_sin_fix > 0 and not es_obstruccion:
                problemas_rec.append(f"cortes breves sin solución ({pct_sin_fix:.1f}%)")

            # e) HDOP elevado (promedio o proporción significativa sobre umbral)
            prop_hdop_alto = float((sub["hdop"] > umbral_hdop).mean() * 100.0)
            if (hdop_prom > umbral_hdop or prop_hdop_alto > 5.0) and not es_obstruccion:
                problemas_rec.append("HDOP elevado")

            # f) Picos de error (error puntual extremo > 2x umbral sin ser obstrucción ni HDOP sostenido)
            max_error = float(sub["error_m"].max()) if sub["error_m"].notna().any() else 0.0
            prop_error_alto = float((sub["error_m"] > umbral_error).mean() * 100.0)
            if max_error > (umbral_error * 2.0) and prop_error_alto < 5.0 and not es_obstruccion:
                problemas_rec.append(f"picos de error (máx. {max_error:.1f} m)")

            # g) Baja cantidad de satélites
            prop_sat_bajo = float((sub["satelites"] < umbral_satelites).mean() * 100.0)
            if prop_sat_bajo > 10.0 and not es_obstruccion:
                problemas_rec.append("baja visibilidad satelital")

            # Clasificación de estado general del receptor (Normal, Alerta, Crítico)
            if pct_sin_fix >= 2.5 or hdop_prom > (umbral_hdop * 1.3) or error_prom > umbral_error:
                estado_general = "Crítico"
            elif problemas_rec or hdop_prom > (umbral_hdop * 0.42) or error_prom > (umbral_error * 0.28):
                estado_general = "Alerta"
            else:
                estado_general = "Normal"

            self.resumen_receptores.append(
                {
                    "receptor": rec,
                    "hdop_prom": round(hdop_prom, 2),
                    "error_prom": round(error_prom, 2),
                    "pct_sin_fix": round(pct_sin_fix, 1),
                    "estado": estado_general,
                }
            )

            for prob in problemas_rec:
                self.diagnosticos.append(f"{rec}: {prob}")

    def obtener_datos_receptor(self, receptor: str, ventana_movil: int) -> pd.DataFrame:
        """Devuelve la serie temporal de un receptor con su promedio móvil calculado (RF-04, RF-06)."""
        if self.df_limpio is None:
            return pd.DataFrame()

        sub = self.df_limpio[self.df_limpio["receptor"] == receptor].copy()
        if sub.empty:
            return sub

        ventana = max(1, int(ventana_movil))
        sub["hdop_suavizado"] = sub["hdop"].rolling(window=ventana, min_periods=1).mean()
        sub["error_suavizado"] = sub["error_m"].rolling(window=ventana, min_periods=1).mean()
        sub["satelites_suavizado"] = sub["satelites"].rolling(window=ventana, min_periods=1).mean()

        mapa_estado = {"SIN_FIX": 0, "FIX_2D": 1, "FIX_3D": 2}
        sub["estado_num"] = sub["estado"].map(mapa_estado).fillna(0)
        return sub