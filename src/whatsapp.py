import re
from typing import Any


def normalize_phone(phone: str) -> str:
    """
    Normaliza telefone para dígitos.
    Ex.: '(47) 99687-6878' -> '47996876878'
    """
    return re.sub(r"\D", "", str(phone or "").strip())


def is_valid_whatsapp_phone(phone: str) -> bool:
    """
    Validação simples para BR:
    - 10 ou 11 dígitos
    - DDD + número
    """
    digits = normalize_phone(phone)
    return len(digits) in {10, 11}


def format_whatsapp_phone(phone: str, default_country_code: str = "55") -> str:
    """
    Retorna número no padrão internacional simples, sem '+'.
    Ex.: '47996876878' -> '5547996876878'
    """
    digits = normalize_phone(phone)
    if not digits:
        return ""

    if digits.startswith(default_country_code) and len(digits) in {12, 13}:
        return digits

    if len(digits) in {10, 11}:
        return f"{default_country_code}{digits}"

    return digits


def send_bulk_whatsapp_simulated(
    recipients: list[dict[str, Any]],
    message_template: str | None = None,
) -> list[dict[str, Any]]:
    """
    Envio simulado de WhatsApp.
    Não chama provedor externo.
    Retorna resultado por destinatário no mesmo estilo do mailer.
    """
    results: list[dict[str, Any]] = []

    for item in recipients:
        nome = str(item.get("nome", "")).strip()
        telefone_original = str(item.get("telefone", "")).strip()
        mensagem = str(item.get("mensagem", "")).strip() or str(message_template or "").strip()

        if not telefone_original:
            results.append(
                {
                    "ok": False,
                    "nome": nome,
                    "telefone": telefone_original,
                    "telefone_formatado": "",
                    "provider": "simulado",
                    "erro": "Telefone ausente.",
                }
            )
            continue

        if not mensagem:
            results.append(
                {
                    "ok": False,
                    "nome": nome,
                    "telefone": telefone_original,
                    "telefone_formatado": "",
                    "provider": "simulado",
                    "erro": "Mensagem ausente.",
                }
            )
            continue

        if not is_valid_whatsapp_phone(telefone_original):
            results.append(
                {
                    "ok": False,
                    "nome": nome,
                    "telefone": telefone_original,
                    "telefone_formatado": "",
                    "provider": "simulado",
                    "erro": "Telefone inválido para WhatsApp.",
                }
            )
            continue

        telefone_formatado = format_whatsapp_phone(telefone_original)

        results.append(
            {
                "ok": True,
                "nome": nome,
                "telefone": telefone_original,
                "telefone_formatado": telefone_formatado,
                "provider": "simulado",
                "mensagem": mensagem,
            }
        )

    return results
