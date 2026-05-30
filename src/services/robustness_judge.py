import json
import os

from models import ReporteRobustez


class RobustnessJudgeService:

    def run_validation(self):
        report = ReporteRobustez(
            score_honestidad=100,
            alucinaciones_detectadas=[],
            comentario_auditor="Prueba inicial"
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

        print("Reporte generado correctamente.")