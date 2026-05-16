# lp-url-stats

Servicio serverless para consultar estadisticas diarias de URLs acortadas con Python 3.12, AWS Lambda, API Gateway HTTP API, DynamoDB y Terraform.

## Endpoint

```http
GET /stats/{codigo}?from=YYYY-MM-DD&to=YYYY-MM-DD
```

Si no envias `from` ni `to`, el servicio consulta los ultimos 30 dias.

## Respuesta exitosa

```json
{
  "codigo": "Ab3xY9",
  "total_clicks": 8,
  "daily": [
    {
      "fecha": "2026-05-14",
      "clicks": 3
    },
    {
      "fecha": "2026-05-15",
      "clicks": 5
    }
  ]
}
```

Cuando un codigo no tiene visitas en el rango, `daily` vuelve como `[]` y `total_clicks` como `0`.

## Validar antes de deploy

```powershell
python -m venv .venv
pip install -r requirements.txt
$env:STATS_TABLE_NAME="lp-url-stats-dev-url-stats"
python -m unittest discover tests
```

## Deploy

Primero crea `terraform/terraform.tfvars` con el id real del API Gateway. El id es la parte de la URL antes de `.execute-api`.

Ejemplo para `https://fqltkzf336.execute-api.us-east-1.amazonaws.com`:

```hcl
aws_region       = "us-east-1"
environment      = "dev"
stats_table_name = "lp-url-stats-dev-url-stats"
api_gateway_id   = "fqltkzf336"
```

```bash
terraform init
terraform validate
terraform plan
terraform apply
terraform destroy
```

## Variables necesarias

- `stats_table_name`: tabla DynamoDB de estadisticas diarias, con PK `codigo` y SK `fecha`.
- `api_gateway_id`: id del HTTP API existente donde se agrega `GET /stats/{codigo}`.
- `environment`: ambiente usado para nombrar recursos.

## Recursos creados

- Lambda Python 3.12.
- Tabla DynamoDB para estadisticas diarias con PK `codigo` y SK `fecha`.
- IAM role con permisos minimos de logs y `dynamodb:Query`.
- Ruta `GET /stats/{codigo}` en API Gateway HTTP API existente.
