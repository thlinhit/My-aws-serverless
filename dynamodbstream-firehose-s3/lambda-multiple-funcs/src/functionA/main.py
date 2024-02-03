import os
import json

from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.functionA import crawl_status_service
from src.shared.exception.domain_code import DomainCode
from src.shared.exception.domain_error import DomainError
from src.shared.log.logger import logger

PARTNER_NAME = os.getenv("PARTNER_NAME", "PAYMONGO")
alb_egress_domain = os.getenv("ALB_DOMAIN", "")


@logger.inject_lambda_context
@event_source(data_class=SQSEvent)
def handle(event: SQSEvent, _: LambdaContext):
    for record in event.records:
        try:
            logger.debug(f"Received triggering record: {record}")
            body = json.loads(record.body)
            logger.debug(f"Body event: {body}")

            for key in ["date", "tenantId", "version", "partner", "triggerTimestamp"]:
                if key not in body or body[key] is None:
                    raise DomainError(DomainCode.REQUIRED_FIELD_ERROR, key)

            if body["partner"] != PARTNER_NAME:
                raise DomainError(
                    DomainCode.VALIDATION_ERROR, f"Invalid partner name, expected: {PARTNER_NAME}, actual: {body['partner']}"
                )

            date = body["date"]
            tenant_id = body["tenantId"]
            version = body["version"]
            logger.info(f"Crawling transactions for date={date}, tenant_id={tenant_id}, version={version}")

            is_present, crawl_item = crawl_status_service.find_crawl_item(tenant=tenant_id, date=date, version=version)

            logger.info(f"Crawling transactions for date={date}, tenant_id={tenant_id}, version={version}")

            if not is_present:
                logger.info(f"Creating a new crawl item for date={date}, tenant_id={tenant_id}, version={version}")
                crawl_item = crawl_status_service.create_crawl_item(
                    tenant=tenant_id,
                    date=date,
                    version=version,
                    data={
                        "trigger_timestamp": body["triggerTimestamp"],
                    },
                )
            else:
                logger.info(f"Found an existing crawl item for date={date}, tenant_id={tenant_id}, version={version}")

            if crawl_status_service.is_completed(crawl_item):
                logger.info(f"Skip as it was completed for date={date}, tenant_id={tenant_id}, version={version}")
                return

            if crawl_status_service.continue_to_crawl(crawl_item):
                logger.info(f"Crawling merchant transactions for date={date}, tenant_id={tenant_id}, version={version}")
                # has_more = transaction_file_service.build_and_upload_txn_file_to_s3()
                # if has_more is True:
                #   crawl_status_service.mark_crawled(crawl_item)
            else:
                logger.info(f"Creating metadata for date={date}, tenant_id={tenant_id}, version={version}")
                # metadata_file_service.build_and_upload_metadata_file_to_s3()
                crawl_status_service.mark_metadata_generated(crawl_item)

            logger.info(f"Crawl completed for date={date}, tenant_id={tenant_id}, version={version}")
        except DomainError as e:
            raise e
        except Exception as e:
            raise DomainError(DomainCode.UNKNOWN, str(e))
