import os
import uuid

from src.shared.repository.dynamodb_repository import put_item

DYNAMO_DB_TABLE = os.environ["DYNAMO_DB_TABLE"]
def handler(event, context):
    transaction_id = "PARTNER_TXN_ID_pay_2oXYFwvM99Rj9ehNtKgREgrk_" + str(uuid.uuid4())
    put_item(DYNAMO_DB_TABLE, {
        "PK": "CUSTOMER_TXN#BANK_NAME#MCA#PARTNER_NAME#20240101",
        "SK": transaction_id,
        "transaction_amount": float(99.99),
        "identity_id": "merchant_id_" + str(uuid.uuid4()),  #The unique identifier of the merchant
        "identity_type": "PARTNER_NAME",
        "transaction_id": transaction_id,
        "transaction_date": "2024-01-01",
    })