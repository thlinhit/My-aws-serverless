# tests/test_dynamodb_repository.py
import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.repository.dynamodb_repository import (
    get_item, find_item, get_items_by_pk, update_item,
    batch_get_items, DynamoDBTransactionHelper, _get_items
)
from src.repository.model.key import ItemKey
from src.repository.model.item import Item

# Sample fixture for mock ItemKey
@pytest.fixture
def mock_key():
    return ItemKey(pk="PK#123", sk="SK#123")

# Sample fixture for mock Item
@pytest.fixture
def mock_item(mock_key):
    item = MagicMock(spec=Item)
    item.get_key.return_value = mock_key
    item.model_dump.return_value = {"pk": mock_key.pk, "sk": mock_key.sk, "some_field": "value"}
    item.model_fields = {"some_field": MagicMock()}
    return item

# Mock DynamoDB response for tests
def mock_dynamodb_client_error(code, message="An error occurred"):
    return ClientError(
        {"Error": {"Code": code, "Message": message}},
        "DynamoDBOperation"
    )

def test_get_item_success(mock_key):
    # Mock find_item to return a valid item
    with patch("src.repository.dynamodb_repository.find_item", return_value=(True, {"pk": "PK#123", "sk": "SK#123"})):
        item = get_item("test_table", mock_key)
        assert item == {"pk": "PK#123", "sk": "SK#123"}

def test_get_item_not_found(mock_key):
    with patch("src.repository.dynamodb_repository.find_item", return_value=(False, None)):
        with pytest.raises(DomainError) as exc_info:
            get_item("test_table", mock_key)
        assert exc_info.value.domain_code == DomainCode.ITEM_NOT_FOUND

def test_find_item_success(mock_key):
    mock_response = {"Item": {"pk": "PK#123", "sk": "SK#123"}}
    with patch("src.repository.dynamodb_repository.get_table") as mock_get_table:
        mock_get_table.return_value.get_item.return_value = mock_response
        is_present, item = find_item("test_table", mock_key)
        assert is_present is True
        assert item == mock_response["Item"]

def test_find_item_exception(mock_key):
    with patch("src.repository.dynamodb_repository.get_table") as mock_get_table:
        mock_get_table.return_value.get_item.side_effect = Exception("Error")
        with pytest.raises(DomainError) as exc_info:
            find_item("test_table", mock_key)
        assert exc_info.value.domain_code == DomainCode.DYNAMODB_ERROR

def test_get_items_by_pk_success():
    with patch("src.repository.dynamodb_repository._get_dynamodb_client") as mock_client:
        mock_client.return_value.query.return_value = {"Items": [{"pk": "PK#123", "sk": "SK#123"}]}
        items = get_items_by_pk("test_table", "PK#123")
        assert items == [{"pk": "PK#123", "sk": "SK#123"}]

def test_get_items_by_pk_exception():
    with patch("src.repository.dynamodb_repository._get_dynamodb_client") as mock_client:
        mock_client.return_value.query.side_effect = Exception("Error")
        with pytest.raises(DomainError) as exc_info:
            get_items_by_pk("test_table", "PK#123")
        assert exc_info.value.domain_code == DomainCode.DYNAMODB_ERROR

def test_update_item_success(mock_item):
    with patch("src.repository.dynamodb_repository.get_table") as mock_get_table, \
         patch("src.util.datetime_util.utc_iso_now", return_value="2023-11-06T00:00:00Z"):
        mock_get_table.return_value.update_item.return_value = {"Attributes": {"pk": "PK#123", "sk": "SK#123"}}
        response = update_item("test_table", mock_item)
        assert response == {"pk": "PK#123", "sk": "SK#123"}

def test_update_item_conditional_failure(mock_item):
    with patch("src.repository.dynamodb_repository.get_table") as mock_get_table:
        mock_get_table.return_value.update_item.side_effect = mock_dynamodb_client_error("ConditionalCheckFailedException")
        with pytest.raises(DomainError) as exc_info:
            update_item("test_table", mock_item)
        assert exc_info.value.domain_code == DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR

def test_batch_get_items_success(mock_key):
    with patch("src.repository.dynamodb_repository._get_items", return_value={"Responses": {"test_table": [{"pk": "PK#123", "sk": "SK#123"}]}}):
        items = batch_get_items("test_table", [mock_key])
        assert items == [{"pk": "PK#123", "sk": "SK#123"}]

def test_batch_get_items_client_error(mock_key):
    with patch("src.repository.dynamodb_repository._get_items") as mock_get_items:
        mock_get_items.side_effect = mock_dynamodb_client_error("ProvisionedThroughputExceededException")
        with pytest.raises(DomainError) as exc_info:
            batch_get_items("test_table", [mock_key])
        assert exc_info.value.domain_code == DomainCode.DYNAMODB_ERROR

def test_dynamodb_transaction_helper_add_put_item(mock_item):
    transaction_helper = DynamoDBTransactionHelper("test_table")
    transaction_helper.add_put_item(mock_item, condition_expression="attribute_not_exists(pk)")
    assert transaction_helper.transact_items == [{
        "Put": {
            "TableName": "test_table",
            "Item": mock_item.model_dump(by_alias=True),
            "ConditionExpression": "attribute_not_exists(pk)"
        }
    }]

def test_dynamodb_transaction_helper_execute_transaction_success():
    with patch("src.repository.dynamodb_repository.dynamodb_resource.meta.client.transact_write_items", return_value={"ResponseMetadata": {"HTTPStatusCode": 200}}) as mock_transact:
        transaction_helper = DynamoDBTransactionHelper("test_table")
        transaction_helper.execute_transaction()
        mock_transact.assert_called_once()
