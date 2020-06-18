import boto3
import json

print('Loading function')
dynamo = boto3.client('dynamodb')


def dy2json(data):
    if isinstance(data, str):
        return data
    if isinstance(data, list):
        temp = []
        for item in data:
            a = dy2json(item)
            temp.append(a)
        return temp
    if isinstance(data, dict):
        if len(data) == 1:
            for k, v in data.items():
                if k == 'S':
                    return v
                if k == 'L':
                    return dy2json(v)
                if k == 'M':
                    return dy2json(v)
                if k == 'N':
                    return eval(v)
        else:
            res = {}
            for k, v in data.items():
                res[k] = dy2json(v)
            return res


def respond(err, res=None):
    body = json.dumps(res.get('Items', {}))
    items = []
    for item in json.loads(body):
        items.append(dy2json(item))

    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(items),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'access-control-allow-credentials': True,
        },
    }


def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    # print("Received event: " + json.dumps(event, indent=2))

    operations = {
        'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        'GET': lambda dynamo, x: dynamo.scan(**x),
        'POST': lambda dynamo, x: dynamo.put_item(**x),
        'PUT': lambda dynamo, x: dynamo.update_item(**x),
    }

    operation = event['httpMethod']
    if operation in operations:
        payload = event['queryStringParameters'] if operation == 'GET' else json.loads(event['body'])
        return respond(None, operations[operation](dynamo, payload))
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))

