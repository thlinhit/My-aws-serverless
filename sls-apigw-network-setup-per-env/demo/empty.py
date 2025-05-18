def handler(event, context):
    """
    Empty handler function. Not actually called as we're using HTTP proxy integration.
    """
    return {
        'statusCode': 200,
        'body': 'This handler is not used with HTTP proxy integration'
    }
