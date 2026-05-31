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

        system_instruction = """
Eres un entrevistador técnico senior.

REGLAS OBLIGATORIAS:

1. Haz únicamente una pregunta a la vez.
2. Haz máximo 7 preguntas.
3. Solo pregunta sobre tecnologías presentes en el perfil o en la vacante.
4. Mantén un tono profesional y amigable.
5. Nunca expliques tu razonamiento.
6. Nunca muestres análisis internos.
7. Nunca muestres cadenas de pensamiento.
8. Nunca escribas frases como:
   - SILENT THOUGHT
   - INTERNAL REASONING
   - THINKING
   - ANALYSIS
9. Responde únicamente con la pregunta que deseas hacer.
10. Después de la séptima pregunta espera la solicitud de feedback final.
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
            
            for forbidden in [
               "SILENT THOUGHT",
               "INTERNAL REASONING",
               "THINKING",
               "ANALYSIS"
            ]:
              if forbidden in question.upper():
                question = question.split("\n\n")[-1].strip()

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