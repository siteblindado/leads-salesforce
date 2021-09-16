from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler.api_gateway import ApiGatewayResolver, CORSConfig
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.parser import BaseModel, envelopes, parse, Field
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validate

from simple_salesforce import Salesforce
import json
tracer = Tracer()
logger = Logger()
metrics = Metrics()
cors_config = CORSConfig(allow_origin="*")

app = ApiGatewayResolver(cors=cors_config)


class Lead(BaseModel):
    Name: str = Field(alias="name")
    Website__c: str = Field(alias="website")
    Company__c: str = Field(alias="company", default="")
    Email__c: str = Field(alias="email")
    Unidade_de_Negocio__c: str = Field(alias="und", default="Site Blindado")
    Status__c: str = Field(alias="status", default='Aberto')
    Description__c: str = Field(alias="message", default=" ")
    Phone__c: str = Field(alias="phone")
    CNPJ__c: str = Field(alias="cnpj", default="00000000000000")
    Amazon__c: str = Field(alias="amazon", default=" ")
    Wish__c: str = Field(alias="wish", default=" ")
    AliExpress__c: str = Field(alias="aliexpress", default=" ")
    Shopee__c: str = Field(alias="shopee", default=" ")
    Outros__c: str = Field(alias="outros", default=" ")
    Site_de_Origem__c: str = Field(alias="type", default=" ")
    Origin__c: str = Field(alias="source", default='Web-to-Lead')
    Intencao_de_mudar_ERP__c: str = Field(alias="intencao_de_mudar_erp", default=" ")


INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "Sample schema",
    "description": "The root schema comprises the entire JSON document.",
    "examples": [{"name": "hello world", "email": "lessa"}],
    "required": ["name", "email"],
    "properties": {
        "name": {
            "$id": "#/properties/message",
            "type": "string",
            "title": "The message",
            "examples": ["hello world"],
            "maxLength": 100,
        },
        "email": {
            "$id": "#/properties/username",
            "type": "string",
            "title": "The username",
            "examples": ["lessa"],
            "maxLength": 30,
        },
    },
}


@app.post("/lead")
def create_lead():
    post_data: dict = app.current_event.json_body
    validate(event=post_data, schema=INPUT)
    payload = parse(model=Lead, event=app.current_event.raw_event, envelope=envelopes.ApiGatewayEnvelope)
    sf_parameters = parameters.get_secret("sb2w-backend", transform='json')
    try:
        sf = Salesforce(instance=sf_parameters['sf_instance'],
                        username=sf_parameters['sf_username'],
                        password=sf_parameters['sf_password'],
                        security_token=sf_parameters['sf_security_token'])
        lead = sf.Lead__c.create(payload.dict())
        message = f"Lead created successfully in Salesforce: {lead.get('success')}"
    except Exception as e:
        message = f"Error creating lead in Salesforce: {e}"
    return {"message": message}


@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event, context: LambdaContext):
    try:
        return app.resolve(event, context)
    except Exception as e:
        logger.exception(e)
        raise
