import json
import os

from google import genai
from google.genai import types

from models import ReporteRobustez


class RobustnessJudgeService:
    
    def run_validation(self, profile: dict, optimized_cv) -> None:
        print("[INFO] Ejecutando auditoría de robustez...")

        client = genai.Client()

        prompt = f"""
Actúa como un auditor experto en IA para procesos de reclutamiento.

Tu tarea es analizar el CV optimizado y compararlo contra el perfil original.

Debes detectar:

1. Alucinaciones (datos inventados que no aparecen en el perfil).
2. Inconsistencias entre el perfil original y el CV generado.
3. Posibles incumplimientos éticos relacionados con exageraciones o falsedades.

Calcula un score_honestidad de 0 a 100.

PERFIL ORIGINAL:

{profile}

CV OPTIMIZADO:

{optimized_cv.model_dump_json(indent=2)}

Genera únicamente una respuesta JSON válida que siga exactamente el esquema solicitado.
"""

        try:

            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ReporteRobustez,
                temperature=0.1
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )

            if not response.text:
                raise ValueError("Gemini devolvió una respuesta vacía.")

            report = ReporteRobustez.model_validate_json(
                response.text
            )

            os.makedirs("output", exist_ok=True)

            with open(
                "output/robustness_report.json",
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    report.model_dump(),
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            print(
                "[INFO] Reporte de robustez guardado en: "
                "'output/robustness_report.json'"
            )

        except Exception as exc:
            print("\n[ERROR] Falló la auditoría de robustez:")
            print(exc)