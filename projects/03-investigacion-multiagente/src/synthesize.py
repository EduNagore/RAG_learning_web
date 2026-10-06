"""Sintetizador y verificador de citas."""

from orchestrator import Finding


def synthesize(question: str, findings: list[Finding]) -> str:
    """TODO: redacta el informe SOLO con los hallazgos recibidos, con una cita por afirmación.
    Marca como «no comprobado» lo que ningún sub-agente pudo verificar."""
    raise NotImplementedError("Implementa la síntesis")


def verify_citations(report: str, findings: list[Finding]) -> list[str]:
    """TODO: devuelve las citas del informe que no corresponden a ninguna fuente de `findings`."""
    raise NotImplementedError("Implementa la verificación")
