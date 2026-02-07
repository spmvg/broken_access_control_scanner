# Example AWS Lambda handlers

import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')


def get_user_handler(event, context):
    user_id = event['pathParameters']['user_id']
    requesting_user = event['requestContext']['authorizer']['claims']['sub']

    if user_id != requesting_user:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Not authorized'})
        }

    response = table.get_item(Key={'user_id': user_id})
    return {
        'statusCode': 200,
        'body': json.dumps(response.get('Item', {}))
    }


def update_user_handler(event, context):
    user_id = event['pathParameters']['user_id']
    body = json.loads(event['body'])

    table.update_item(
        Key={'user_id': user_id},
        UpdateExpression='SET #n = :name, email = :email',
        ExpressionAttributeNames={'#n': 'name'},
        ExpressionAttributeValues={
            ':name': body['name'],
            ':email': body['email']
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Updated'})
    }


def delete_user_handler(event, context):
    user_id = event['pathParameters']['user_id']

    table.delete_item(Key={'user_id': user_id})

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Deleted'})
    }


def admin_list_users_handler(event, context):
    response = table.scan()

    return {
        'statusCode': 200,
        'body': json.dumps(response.get('Items', []))
    }
