# ews_sender

Envío de correos electrónicos via EWS (Exchange Web Services) para Microsoft 365 / Exchange Online.

## Requisitos Previos

### Registrar App en Azure AD

1. Ve a [Azure Portal](https://portal.azure.com) → **Azure Active Directory** → **App registrations**
2. Click en **New registration**
3. Nombre: `ews_sender`
4. Supported account types: **Accounts in this organizational directory only**
5. Click **Register**
6. Copia el **Application (client) ID** y **Directory (tenant) ID**
7. En **Certificates & secrets** → **New client secret** → copia el valor
8. En **API permissions** → **Add a permission** → **Exchange** → **EWS.AccessAsUser.All** (Application)
9. Grant admin consent si es necesario

## Instalación

### Python (pip)

```bash
pip install ews_sender
```

### Executable Portable

Descarga `send-email.exe` de la carpeta `dist/` y cópialo a tu ubicación preferida.

## Configuración

Crea un archivo `config.json` con las credenciales:

```json
{
    "tenant_id": "tu-tenant-id",
    "client_id": "tu-client-id",
    "client_secret": "tu-client-secret",
    "account_email": "remitente@tuempresa.com"
}
```

## Uso desde Consola

### send-email (CLI via pip)

```bash
send-email --config config.json --to destinatario@empresa.com --subject "Asunto" --body "<p>Mensaje HTML</p>"
```

### send-email.exe (Executable portable)

```powershell
.\send-email.exe --config config.json --to destinatario@empresa.com --subject "Asunto" --body "<p>Mensaje</p>"
```

## Opciones del CLI

| Opción | Requerido | Descripción |
|--------|-----------|-------------|
| `--config` | Sí | Ruta al archivo JSON de configuración |
| `--to` | Sí | Destinatarios (múltiples separados por espacio) |
| `--cc` | No | Destinatarios en copia (múltiples separados por espacio) |
| `--bcc` | No | Destinatarios en copia oculta (múltiples separados por espacio) |
| `--subject` | Sí | Asunto del email |
| `--body` | Sí | Cuerpo del mensaje (HTML o texto plano según --body-type) |
| `--body-type` | No | Tipo de cuerpo: `html` (default) o `plain` |
| `--importance` | No | Importancia: `low`, `normal` (default), `high` |
| `--attachments` | No | Archivos adjuntos (múltiples separados por espacio) |

## Ejemplos

### Email simple

```powershell
send-email --config config.json --to persona@empresa.com --subject "Hola" --body "<p>Hola mundo</p>"
```

### Múltiples destinatarios

```powershell
send-email --config config.json --to a@empresa.com b@empresa.com c@empresa.com --subject "Reunión" --body "<p>Confirmamos la reunión para mañana</p>"
```

### Con CC y BCC

```powershell
send-email --config config.json --to destinatario@empresa.com --cc supervisor@empresa.com --bcc auditor@empresa.com --subject "Informe" --body "<p>Adjunto el informe mensual</p>"
```

### Con adjuntos

```powershell
send-email --config config.json --to persona@empresa.com --subject "Documentos" --body "<p>Adjunto los documentos solicitados</p>" --attachments archivo1.pdf documento2.xlsx imagen.png
```

### Importancia alta y cuerpo plano

```powershell
send-email --config config.json --to a@empresa.com --subject "URGENTE" --body "Este es un mensaje urgente que requiere atención inmediata" --body-type plain --importance high
```

### Todo junto

```powershell
send-email --config config.json --to destinatario@empresa.com copia@empresa.com --cc gerente@empresa.com --subject "Reporte Mensual" --body "<h1>Reporte</h1><p>Adjunto el reporte de ventas del mes.</p>" --attachments reporte.pdf graficos.xlsx --importance high --body-type html
```

## Uso Programático (Python)

```python
from ews_sender import EWSClient, EmailMessage, Attachment, Importance

client = EWSClient(
    tenant_id="tu-tenant-id",
    client_id="tu-client-id",
    client_secret="tu-secret",
    account_email="remitente@empresa.com"
)

msg = EmailMessage(
    to=["destinatario@empresa.com"],
    subject="Asunto",
    body="<html><body><h1>Mensaje HTML</h1></body></html>",
    cc=["copia@empresa.com"],
    attachments=[Attachment("documento.pdf")],
    importance=Importance.HIGH
)

client.connect()
client.send(msg)
client.close()
```

## Códigos de Retorno

- `0` - Email enviado exitosamente
- `1` - Error (mensaje de error escrito a stderr)

## Integración con Otros Lenguajes

### PowerShell

```powershell
& .\send-email.exe --config config.json --to persona@empresa.com --subject "Test" --body "<p>Mensaje</p>"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Email enviado"
} else {
    Write-Host "Error al enviar"
}
```

### Batch

```batch
send-email.exe --config config.json --to persona@empresa.com --subject "Test" --body "Mensaje"
```

### Python

```python
import subprocess

result = subprocess.run([
    "send-email.exe",
    "--config", "config.json",
    "--to", "persona@empresa.com",
    "--subject", "Asunto",
    "--body", "<p>Mensaje</p>"
], capture_output=True, text=True)

if result.returncode == 0:
    print("Enviado exitosamente")
else:
    print(f"Error: {result.stderr}")
```

## Estructura del Proyecto

```
ews_sender/
├── ews_sender/              # Paquete Python
│   ├── __init__.py
│   ├── client.py            # EWSClient
│   ├── exceptions.py        # Excepciones personalizadas
│   ├── message.py           # EmailMessage, Attachment
│   ├── utils.py             # Helpers
│   └── send_email.py        # CLI
├── tests/
│   └── test_ews_sender.py   # Tests unitarios
├── dist/
│   └── send-email.exe       # Executable portable
├── pyproject.toml
└── README.md
```

## Licencia

MIT
