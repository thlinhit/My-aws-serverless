import os
import uuid
from decimal import Decimal
from src.shared.repository.dynamodb_repository import put_item

DYNAMO_DB_TABLE = os.environ["DYNAMO_DB_TABLE"]
def handler(event, context):
    transaction_id = "PARTNER_TXN_ID_pay_2oXYFwvM99Rj9ehNtKgREgrk_" + str(uuid.uuid4())
    product_code = "MCA#PARTNER_NAME"
    put_item(DYNAMO_DB_TABLE, {
        "PK": "CUSTOMER_TXN#BANK_NAME#MCA#PARTNER_NAME#20240101",
        "SK": transaction_id,
        "product_code": product_code,
        "transaction_amount": Decimal(str(99.99)),
        "identity_id": "merchant_id_" + str(uuid.uuid4()),  #The unique identifier of the merchant
        "identity_type": "PARTNER_NAME",
        "transaction_id": transaction_id,
        "transaction_date": "2024-01-01",
    })