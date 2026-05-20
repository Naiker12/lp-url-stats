# lp-url-stats

Servicio serverless para consultar estadisticas diarias de URLs acortadas con Python 3.12, AWS Lambda, API Gateway HTTP API, DynamoDB y Terraform.

## Endpoint

```http
GET /stats?from=YYYY-MM-DD&to=YYYY-MM-DD
GET /stats/{codigo}?from=YYYY-MM-DD&to=YYYY-MM-DD
```

`GET /stats` devuelve estadisticas agregadas de todas las URLs. `GET /stats/{codigo}` filtra una URL corta puntual.

Si no envias `from` ni `to`, el servicio consulta los ultimos 30 dias.

## Respuesta exitosa

```json
{
  "codigo": "<CODIGO>",
  "total_clicks": 0,
  "daily": [
    {
      "fecha": "<YYYY-MM-DD>",
      "clicks": 0
    },
    {
      "fecha": "<YYYY-MM-DD>",
      "clicks": 0
    }
  ]
}
```

Cuando un codigo no tiene visitas en el rango, `daily` vuelve como `[]` y `total_clicks` como `0`.

## Validar antes de deploy

```powershell
python -m venv .venv
pip install -r requirements.txt
$env:STATS_TABLE_NAME="<TABLA_STATS>"
$env:URL_TABLE_NAME="<TABLA_URLS>"
python -m unittest discover tests
```

## Deploy

Primero crea `terraform/terraform.tfvars` con el id real del API Gateway. El id es la parte de la URL antes de `.execute-api`.

```hcl
aws_region       = "<REGION_AWS>"
environment      = "<AMBIENTE>"
stats_table_name = "<TABLA_STATS>"
url_table_name   = "<TABLA_URLS>"
api_gateway_id   = "<API_GATEWAY_ID>"
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
- `url_table_name`: tabla DynamoDB de URLs acortadas, con PK `codigo`.
- `api_gateway_id`: id del HTTP API existente donde se agregan `GET /stats` y `GET /stats/{codigo}`.
- `environment`: ambiente usado para nombrar recursos.

## Recursos creados

- Lambda Python 3.12.
- Integracion con la tabla DynamoDB compartida de estadisticas diarias con PK `codigo` y SK `fecha`.
- Validacion contra la tabla DynamoDB de URLs acortadas para diferenciar codigos inexistentes.
- IAM role con permisos minimos de logs, `dynamodb:Query`, `dynamodb:Scan` y `dynamodb:GetItem`.
- Rutas `GET /stats` y `GET /stats/{codigo}` en API Gateway HTTP API existente.
