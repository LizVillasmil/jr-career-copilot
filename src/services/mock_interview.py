import os

from google import genai
from google.genai import types


class MockInterviewService:

    def __init__(self):
        self.messages = []
        self.transcript = []

    def export_transcript(self) -> None:

        os.makedirs("output", exist_ok=True)

        with open(
            "output/interview_transcript.md",
            "w",
            encoding="utf-8"
        ) as file:

            file.write("\n".join(self.transcript))

        print(
            "[INFO] Transcripción guardada en "
            "'output/interview_transcript.md'"
        )

    def run_interactive(
        self,
        profile: dict,
        job_description: str
    ) -> None:

        print("\n[INFO] Iniciando Mock Interview...\n")

        client = genai.Client()

        system_instruction = f"""
Eres un entrevistador técnico senior.

Tu misión es realizar una entrevista técnica simulada.

REGLAS OBLIGATORIAS:

1. Solo puedes hacer preguntas relacionadas con:
   - tecnologías presentes en el perfil
   - tecnologías presentes en la vacante

2. Haz una sola pregunta por respuesta.

3. Mantén un tono profesional.

4. Máximo 7 preguntas.

5. No expliques soluciones.

6. Después de la pregunta 7 NO hagas más preguntas.

7. Cuando se solicite feedback final:
   - evalúa fortalezas
   - evalúa debilidades
   - evalúa preparación técnica
   - da recomendaciones concretas
"""

        context = f"""
PERFIL DEL CANDIDATO:

{profile}

VACANTE:

{job_description}
"""

        self.messages.append(
            {
                "role": "user",
                "parts": [{"text": context}]
            }
        )

        print("=" * 60)
        print("      MOCK INTERVIEW")
        print("=" * 60)

        for question_number in range(1, 8):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=self.messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.5
                )
            )

            question = response.text.strip()

            print(f"\n[Pregunta {question_number}]")
            print(question)

            self.transcript.append(
                f"# Pregunta {question_number}\n\n{question}\n"
            )

            answer = input("\nTu respuesta: ")

            self.transcript.append(
                f"**Respuesta del candidato:**\n\n{answer}\n"
            )

            self.messages.append(
                {
                    "role": "model",
                    "parts": [{"text": question}]
                }
            )

            self.messages.append(
                {
                    "role": "user",
                    "parts": [{"text": answer}]
                }
            )

        print("\n[INFO] Generando feedback final...\n")

        feedback_request = """
Genera el feedback final de la entrevista.

Incluye:

1. Evaluación general.
2. Fortalezas observadas.
3. Debilidades observadas.
4. Recomendaciones de mejora.
5. Calificación general sobre 10.

NO hagas más preguntas.
"""

        self.messages.append(
            {
                "role": "user",
                "parts": [{"text": feedback_request}]
            }
        )

        feedback_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=self.messages,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3
            )
        )

        feedback = feedback_response.text.strip()

        print("=" * 60)
        print("FEEDBACK FINAL")
        print("=" * 60)
        print(feedback)

        self.transcript.append(
            "\n# Feedback Final\n\n" + feedback + "\n"
        )

        self.export_transcript()