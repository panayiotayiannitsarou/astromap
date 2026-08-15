import os
from openai import OpenAI

# Το μοντέλο και το όριο εξόδου μπορούν να αλλάξουν χωρίς αλλαγή κώδικα:
#   ASTROCHECK_MODEL=gpt-5.6 ASTROCHECK_MAX_OUTPUT_TOKENS=60000 streamlit run app.py
DEFAULT_MODEL = os.getenv("ASTROCHECK_MODEL", "gpt-5.4")
DEFAULT_MAX_OUTPUT_TOKENS = int(os.getenv("ASTROCHECK_MAX_OUTPUT_TOKENS", "40000"))


def generate_analysis(api_key: str, prompt: str, model: str | None = None,
                       max_output_tokens: int | None = None) -> str:
    """Καλεί το OpenAI Responses API και επιστρέφει το τελικό κείμενο.

    Ελέγχει ρητά ότι η απάντηση ολοκληρώθηκε και ότι δεν είναι κενή --
    και τα δύο πραγματικά, τεκμηριωμένα σενάρια αποτυχίας όταν το
    reasoning effort είναι υψηλό και δεν έχει οριστεί όριο εξόδου.
    """
    model = model or DEFAULT_MODEL
    max_output_tokens = max_output_tokens or DEFAULT_MAX_OUTPUT_TOKENS
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        input=prompt,
        reasoning={"effort": "high"},
        text={"verbosity": "high"},
        max_output_tokens=max_output_tokens,
    )

    status = getattr(response, "status", "completed")
    if status != "completed":
        details = getattr(response, "incomplete_details", None)
        reason = getattr(details, "reason", details) if details else "άγνωστη αιτία"
        raise RuntimeError(
            f"Η παραγωγή δεν ολοκληρώθηκε (κατάσταση: {status}, αιτία: {reason}). "
            f"Δοκίμασε να αυξήσεις το ASTROCHECK_MAX_OUTPUT_TOKENS (τρέχον: {max_output_tokens}) "
            f"ή να μειώσεις το reasoning effort."
        )

    analysis = (response.output_text or "").strip()
    if not analysis:
        raise RuntimeError(
            "Το μοντέλο επέστρεψε κενή ανάλυση παρότι η κλήση ολοκληρώθηκε. "
            "Δοκίμασε ξανά ή αύξησε το όριο εξόδου."
        )
    return analysis
