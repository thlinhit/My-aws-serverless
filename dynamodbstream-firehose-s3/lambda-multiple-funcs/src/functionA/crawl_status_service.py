import os

from boto3.dynamodb.conditions import Attr

from src.shared.dynamodb import dynamodb_repository
from src.shared.exception.domain_code import DomainCode
from src.shared.exception.domain_error import DomainError

PARTNER_NAME = os.getenv("PARTNER_NAME", "PAYMONGO")
TABLE_NAME = os.environ["DYNAMO_DB_TABLE"]


def find_crawl_item(tenant: str, date: str, version: int):
    pk = __build_pk(tenant, date)
    sk = __build_version_sk(version)
    is_present, item = dynamodb_repository.find_item(TABLE_NAME, pk, sk)
    return is_present, item


def create_crawl_item(tenant: str, date: str, version: int, data: dict):
    for key in ["trigger_timestamp"]:
        if key not in data or data[key] is None:
            raise DomainError(DomainCode.REQUIRED_FIELD_ERROR, key)

    version_item = {
        "tenant_id": tenant,
        "status": "CRAWLING",
        "partner": PARTNER_NAME,
        "path": f"{PARTNER_NAME.lower()}/mca/PAYMONGO/{date}",
        **data,
    }

    try:
        dynamodb_repository.put_item_if_not_exists(TABLE_NAME, {"pk": __build_pk(tenant, date), "sk": __build_version_sk(version), **version_item})
    except DomainError as domain_error:
        if domain_error.domain_code != DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR:
            raise domain_error
    return version_item


def get_latest_file_metadata(tenant: str, date: str, version: int) -> tuple[bool, object]:
    pk = __build_pk(tenant, date)
    sk_prefix = __build_file_sk_prefix(version)
    is_present, item = dynamodb_repository.find_latest_by_sort_key_prefix(TABLE_NAME, pk, sk_prefix)
    return is_present, item


def save_file_metadata(tenant: str, date: str, version: int, file_metadata: dict):
    for key in ["name", "from_offset", "to_offset", "num_txns", "order"]:
        if key not in file_metadata or file_metadata[key] is None:
            raise DomainError(DomainCode.REQUIRED_FIELD_ERROR, key)

    pk = __build_pk(tenant, date)
    sk = f"VERSION#{version}#FILE#{file_metadata['order']}"

    try:
        dynamodb_repository.put_item_if_not_exists(TABLE_NAME, {"pk": pk, "sk": sk, **file_metadata})
    except DomainError as domain_error:
        if domain_error.domain_code != DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR:
            raise domain_error

    return file_metadata


def get_all_file_metadata(tenant: str, date: str, version: int) -> list[dict]:
    pk = __build_pk(tenant, date)
    sk_prefix = __build_file_sk_prefix(version)
    return dynamodb_repository.find_by_sort_key_prefix(TABLE_NAME, pk, sk_prefix)


def mark_crawled(crawl_item: dict, num_txns: int):
    crawl_item["status"] = "CRAWLED"
    crawl_item["num_txns"] = num_txns
    dynamodb_repository.put_item_conditionally(TABLE_NAME, crawl_item, Attr("status").eq("CRAWLING"))


def mark_metadata_generated(crawl_item: dict):
    crawl_item["status"] = "METADATA_GENERATED"
    dynamodb_repository.put_item_conditionally(TABLE_NAME, crawl_item, Attr("status").eq("CRAWLED"))


def is_completed(crawl_item: dict) -> bool:
    return crawl_item["status"] == "METADATA_GENERATED"


def continue_to_crawl(crawl_item: dict) -> bool:
    return crawl_item["status"] == "CRAWLING"


def __build_pk(tenant: str, date: str) -> str:
    return f"MERCH_TXN#{tenant}#{PARTNER_NAME}#{date}"


def __build_file_sk_prefix(version: int) -> str:
    return f"VERSION#{version}#FILE#"


def __build_version_sk(version: int) -> str:
    return f"VERSION#{version}"
