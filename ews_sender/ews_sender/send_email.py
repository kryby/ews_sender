#!/usr/bin/env python
"""CLI para enviar correos via EWS."""

import argparse
import json
import sys

from ews_sender import EWSClient, EmailMessage, Attachment, Importance, BodyType


def load_config(config_path: str) -> dict:
    """Cargar configuración desde archivo JSON."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Archivo de configuración no encontrado: {config_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Enviar email via EWS/Exchange Online")
    parser.add_argument("--config", required=True, help="Ruta al archivo JSON de configuración")
    parser.add_argument("--to", required=True, nargs="+", help="Destinatarios")
    parser.add_argument("--cc", nargs="+", help="Destinatarios CC")
    parser.add_argument("--bcc", nargs="+", help="Destinatarios BCC")
    parser.add_argument("--subject", required=True, help="Asunto del email")
    parser.add_argument("--body", required=True, help="Cuerpo del email")
    parser.add_argument("--body-type", choices=["html", "plain"], default="html", help="Tipo de cuerpo (default: html)")
    parser.add_argument("--importance", choices=["low", "normal", "high"], default="normal", help="Importancia (default: normal)")
    parser.add_argument("--attachments", nargs="+", help="Archivos adjuntos")

    args = parser.parse_args()

    config = load_config(args.config)

    tenant_id = config.get("tenant_id")
    client_id = config.get("client_id")
    client_secret = config.get("client_secret")
    account_email = config.get("account_email")

    if not all([tenant_id, client_id, client_secret, account_email]):
        print("La configuración debe incluir: tenant_id, client_id, client_secret, account_email", file=sys.stderr)
        sys.exit(1)

    importance_map = {
        "low": Importance.LOW,
        "normal": Importance.NORMAL,
        "high": Importance.HIGH,
    }
    body_type_map = {
        "html": BodyType.HTML,
        "plain": BodyType.PLAIN,
    }

    attachments = [Attachment(path=path) for path in (args.attachments or [])]

    msg = EmailMessage(
        to=list(args.to),
        subject=args.subject,
        body=args.body,
        cc=list(args.cc) if args.cc else [],
        bcc=list(args.bcc) if args.bcc else [],
        attachments=attachments,
        importance=importance_map[args.importance],
        body_type=body_type_map[args.body_type],
    )

    client = EWSClient(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
        account_email=account_email,
    )

    try:
        client.connect()
        client.send(msg)
        print(f"Email enviado exitosamente a {list(args.to)}")
    except Exception as e:
        print(f"Error al enviar email: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
