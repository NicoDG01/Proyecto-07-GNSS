"""Módulo de back-end para carga, limpieza y diagnóstico de datos GNSS."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class ParametrosAnalisis:
    """Parámetros configurables para la evaluación de calidad GNSS."""

    umbral_hdop: float = 3.0
    umbral_error: float = 10.0
    umbral_satelites: int = 6
    ventana_movil: int = 30


class ProcesadorGNSS:
    """Procesa, limpia y diagnostica mediciones de receptores GNSS (RF-01 a RF-08)."""

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
            faltantes = ", ".join(sorted(columnas_req - set(df.columns)))
            raise ValueError(f"Faltan columnas requeridas en el CSV: {faltantes}")

        self.df_raw = df
        self._limpiar_datos()

    def _limpiar_datos(self) -> None:
        """Elimina duplicados, filtra valores negativos y gestiona SIN_FIX (RF-02, RF-03)."""
        df = self.df_raw.copy()
        total_inicial = len(df)

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["receptor"] = df["receptor"].astype(str).str.strip()
        df = df.dropna(subset=["timestamp", "receptor", "estado"])

        duplicados = int(df.duplicated().sum())
        df = df.drop_duplicates().copy()

        for col in ("satelites", "hdop", "error_m"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

        mask_err_neg = df["error_m"] < 0
        invalidos_por_rec = df[mask_err_neg].groupby("receptor").size().to_dict()
        total_invalidos = int(mask_err_neg.sum())

        df.loc[mask_err_neg, "error_m"] = np.nan
        df.loc[df["hdop"] < 0, "hdop"] = np.nan

        mask_sin_fix = df["estado"].str.strip() == "SIN_FIX"
        df.loc[mask_sin_fix, ["hdop", "error_m"]] = np.nan

        self.df_limpio = df.sort_values(["receptor", "timestamp"]).reset_index(drop=True)
        self.reporte_limpieza = {
            "total_inicial": total_inicial,
            "duplicados_eliminados": duplicados,
            "invalidos_corregidos": total_invalidos,
            "invalidos_por_receptor": invalidos_por_rec,
            "total_valido": len(self.df_limpio),
        }

    def analizar(self, params: ParametrosAnalisis) -> None:
        """Ejecuta el análisis estadístico y la detección de anomalías (RF-05, RF-07, RF-08)."""
        if self.df_limpio is None or self.df_limpio.empty:
            raise ValueError("No hay datos cargados para analizar.")

        self.resumen_receptores = []
        self.diagnosticos = []

        for rec in sorted(self.df_limpio["receptor"].unique()):
            sub = self.df_limpio[self.df_limpio["receptor"] == rec].copy()
            resumen_rec, problemas_rec = self._evaluar_receptor(rec, sub, params)
            self.resumen_receptores.append(resumen_rec)
            for prob in problemas_rec:
                self.diagnosticos.append(f"{rec}: {prob}")
                
    def calcular_calidad_global(self, params: ParametrosAnalisis) -> dict:
        """Calcula indicadores globales de la red: disponibilidad y mediciones desfavorables."""
        if self.df_limpio is None or self.df_limpio.empty:
            raise ValueError("No hay datos cargados para analizar.")

        df = self.df_limpio

        def pct_sobre(serie: pd.Series, condicion: pd.Series) -> float:
            """Porcentaje de la condición, contando solo mediciones con valor válido."""
            validas = serie.notna()
            if not validas.any():
                return 0.0
            return float(condicion[validas].mean() * 100.0)

        con_solucion = df["estado"].str.strip().isin(["FIX_2D", "FIX_3D"])
        estados = [r["estado"] for r in self.resumen_receptores]

        return {
            "disponibilidad": float(con_solucion.mean() * 100.0),
            "pct_hdop_alto": pct_sobre(df["hdop"], df["hdop"] > params.umbral_hdop),
            "pct_error_alto": pct_sobre(df["error_m"], df["error_m"] > params.umbral_error),
            "pct_sats_bajos": pct_sobre(
                df["satelites"], df["satelites"] < params.umbral_satelites
            ),
            "normal": estados.count("Normal"),
            "alerta": estados.count("Alerta"),
            "critico": estados.count("Crítico"),
        }
    
    def _evaluar_receptor(
        self, rec: str, sub: pd.DataFrame, params: ParametrosAnalisis
    ) -> tuple[dict, list[str]]:
        """Calcula métricas estadísticas y clasifica el estado de un receptor individual."""
        hdop_prom = float(sub["hdop"].mean()) if sub["hdop"].notna().any() else 0.0
        error_prom = float(sub["error_m"].mean()) if sub["error_m"].notna().any() else 0.0
        pct_sin_fix = float((sub["estado"] == "SIN_FIX").mean() * 100.0)

        problemas = self._detectar_problemas(rec, sub, params, hdop_prom, pct_sin_fix)
        estado = self._clasificar_estado(params, hdop_prom, error_prom, pct_sin_fix, problemas)

        resumen = {
            "receptor": rec,
            "hdop_prom": round(hdop_prom, 2),
            "error_prom": round(error_prom, 2),
            "pct_sin_fix": round(pct_sin_fix, 1),
            "estado": estado,
        }
        return resumen, problemas

    def _detectar_problemas(
        self,
        rec: str,
        sub: pd.DataFrame,
        params: ParametrosAnalisis,
        hdop_prom: float,
        pct_sin_fix: float,
    ) -> list[str]:
        """Identifica condiciones operativas anormales para un receptor (RF-07)."""
        problemas = []
        n_reg = len(sub)

        if n_reg < self.REGISTROS_SEMANA_COMPLETA:
            faltantes = self.REGISTROS_SEMANA_COMPLETA - n_reg
            problemas.append(f"ausencia de reportes ({faltantes} registros faltantes)")

        cant_inv = self.reporte_limpieza["invalidos_por_receptor"].get(rec, 0)
        if cant_inv > 0:
            problemas.append(f"mediciones inválidas ({cant_inv} valores negativos)")

        es_obstruccion = self._verificar_obstruccion(sub)
        if es_obstruccion:
            problemas.append("obstrucción progresiva")

        if not es_obstruccion:
            self._agregar_alertas_puntuales(
                sub, params, hdop_prom, pct_sin_fix, problemas
            )

        return problemas

    @staticmethod
    def _verificar_obstruccion(sub: pd.DataFrame) -> bool:
        """Detecta degradación progresiva de HDOP y pérdida de satélites en la semana."""
        tercio = max(1, len(sub) // 3)
        hdop_ini = sub["hdop"].iloc[:tercio].mean()
        hdop_fin = sub["hdop"].iloc[-tercio:].mean()
        sat_ini = sub["satelites"].iloc[:tercio].mean()
        sat_fin = sub["satelites"].iloc[-tercio:].mean()

        return bool(
            pd.notna(hdop_ini)
            and pd.notna(hdop_fin)
            and (hdop_fin - hdop_ini > 1.2)
            and (sat_ini - sat_fin > 2.5)
        )

    @staticmethod
    def _agregar_alertas_puntuales(
        sub: pd.DataFrame,
        params: ParametrosAnalisis,
        hdop_prom: float,
        pct_sin_fix: float,
        problemas: list[str],
    ) -> None:
        """Evalúa cortes SIN_FIX, HDOP elevado, picos de error y baja cantidad de satélites."""
        if pct_sin_fix >= 2.0:
            problemas.append(f"períodos sin solución ({pct_sin_fix:.1f}%)")
        elif pct_sin_fix > 0:
            problemas.append(f"cortes breves sin solución ({pct_sin_fix:.1f}%)")

        prop_hdop = float((sub["hdop"] > params.umbral_hdop).mean() * 100.0)
        if hdop_prom > params.umbral_hdop or prop_hdop > 5.0:
            problemas.append("HDOP elevado")

        max_err = float(sub["error_m"].max()) if sub["error_m"].notna().any() else 0.0
        prop_err = float((sub["error_m"] > params.umbral_error).mean() * 100.0)
        if max_err > (params.umbral_error * 2.0) and prop_err < 5.0:
            problemas.append(f"picos de error (máx. {max_err:.1f} m)")

        prop_sat = float((sub["satelites"] < params.umbral_satelites).mean() * 100.0)
        if prop_sat > 10.0:
            problemas.append("baja visibilidad satelital")

    @staticmethod
    def _clasificar_estado(
        params: ParametrosAnalisis,
        hdop_prom: float,
        error_prom: float,
        pct_sin_fix: float,
        problemas: list[str],
    ) -> str:
        """Asigna la categoría Normal, Alerta o Crítico según los umbrales vigentes."""
        if (
            pct_sin_fix >= 2.5
            or hdop_prom > (params.umbral_hdop * 1.3)
            or error_prom > params.umbral_error
        ):
            return "Crítico"
        if problemas:
            return "Alerta"
        return "Normal"
 
    def obtener_datos_receptor(self, receptor: str, ventana_movil: int) -> pd.DataFrame:
        """Devuelve la serie temporal de un receptor con promedio móvil (RF-04, RF-06)."""
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
