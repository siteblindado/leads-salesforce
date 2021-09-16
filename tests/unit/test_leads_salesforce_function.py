import json

from leads_salesforce import app


def test_lambda_handler_pre_flight(apigw_event, lambda_context):
    apigw_event['httpMethod'] = 'OPTIONS'
    ret = app.lambda_handler(apigw_event, lambda_context)
    expected = {'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Authorization,Content-Type,X-Amz-Date,X-Amz-Security-Token,X-Api-Key',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'}
    assert ret["statusCode"] == 204
    assert ret["headers"] == expected


def test_lambda_handler(apigw_event, lambda_context):
    ret = app.lambda_handler(apigw_event, lambda_context)
    expected = json.dumps({"message": "Lead created successfully in Salesforce: True"}, separators=(",", ":"))

    assert ret["statusCode"] == 200
    assert ret["body"] == expected



# OrderedDict([('id', 'a086e00001ovZSJAA2'), ('success', True), ('errors', [])])