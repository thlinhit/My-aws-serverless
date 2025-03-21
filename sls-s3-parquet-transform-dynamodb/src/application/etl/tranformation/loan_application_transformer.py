from dataclasses import dataclass

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, when, lit, concat,
    date_format, from_unixtime, format_string, create_map, array, array_remove, map_filter
)

from application.etl.tranformation.base_transformer import DataTransformer, TransformationResult
from infrastructure.logger import logger


class LoanApplicationTransformer(DataTransformer):
    """
    Transformer for loan application data.
    Handles specific business rules and data cleaning for loan applications.
    """

    def transform(self, df: DataFrame) -> TransformationResult:
        """
        Transform the input DataFrame according to loan application rules.
        
        Args:
            df: Input DataFrame containing loan application data
            
        Returns:
            TransformationResult containing valid and error items
        """
        logger.info("Transforming loan application data")

        try:
            # Add error information column
            transformed_df = df.withColumn(
                "error_info",
                when(col("customer_id").isNull(), "Missing customer_id")
                .when(col("application_id").isNull(), "Missing application_id")
                .when(col("date_application_created").isNull(), "Missing date_application_created")
                .when(col("status").isNull(), "Missing status")
                .when(col("requested_amount").isNull(), "Missing requested_amount")
                .otherwise(None)
            )

            # Convert customer_id to string to prevent scientific notation
            transformed_df = transformed_df.withColumn(
                "customer_id",
                format_string("%.0f", col("customer_id"))
            )

            # Convert date fields to ISO format
            transformed_df = transformed_df.withColumn(
                "date_application_created",
                date_format(
                    from_unixtime(col("date_application_created")),
                    "yyyy-MM-dd'T'HH:mm:ss'Z'"
                )
            ).withColumn(
                "contract_date",
                when(col("contract_date").isNotNull(),
                     date_format(
                         from_unixtime(col("contract_date")),
                         "yyyy-MM-dd"
                     )
                     ).otherwise(None)
            )

            # Convert numeric fields
            transformed_df = transformed_df.withColumn(
                "requested_amount",
                col("requested_amount").cast("decimal(10,2)")
            )

            transformed_df = transformed_df.withColumn(
                "accepted_amount",
                when(col("accepted_amount").isNotNull(),
                     col("accepted_amount").cast("decimal(10,2)")
                     ).otherwise(None)
            )

            transformed_df = transformed_df.withColumn(
                "gross_income",
                when(col("gross_income").isNotNull(),
                     col("gross_income").cast("decimal(10,2)")
                     ).otherwise(None)
            )

            # Split and clean decline reasons
            transformed_df = transformed_df.withColumn(
                "decline_reasons",
                when(
                    col("status") == "Declined",
                    array_remove(
                        array(
                            when(col("decline_reason_1").isNotNull(), col("decline_reason_1")).otherwise(""),
                            when(col("decline_reason_2").isNotNull(), col("decline_reason_2")).otherwise(""),
                            when(col("decline_reason_3").isNotNull(), col("decline_reason_3")).otherwise(""),
                        ),
                        ""
                    )
                ).otherwise(None)
            )

            # Create DynamoDB item structure
            transformed_df = transformed_df.withColumn(
                "dynamodb_item",
                when(
                    col("error_info").isNull(),
                    map_filter(
                        create_map(
                            lit("pk"), concat(lit("CUS#"), col("customer_id").cast("string")),
                            lit("sk"), concat(lit("LOAN_APP#"), col("application_id").cast("string")),
                            lit("customer_id"), col("customer_id"),
                            lit("application_id"), col("application_id"),
                            lit("debtor_account_number"), col("debtor_account_number"),
                            lit("date_application_created"), col("date_application_created"),
                            lit("status"), col("status"),
                            lit("requested_amount"), col("requested_amount"),
                            lit("accepted_amount"), col("accepted_amount"),
                            lit("contract_date"), col("contract_date"),
                            lit("gross_income"), col("gross_income"),
                            lit("decline_reasons"), col("decline_reasons").cast("string")
                        ),
                        lambda k, v: v.isNotNull()
                    )
                ).otherwise(None)
            )

            # Split into valid and error items
            valid_items_df = transformed_df.filter(col("error_info").isNull())
            error_items_df = transformed_df.filter(col("error_info").isNotNull())

            # Get counts
            valid_count = valid_items_df.count()
            error_count = error_items_df.count()

            logger.info(
                f"Transformed {valid_count} loan application records "
                f"(with {error_count} errors)"
            )

            return TransformationResult(
                valid_items=valid_items_df.select("dynamodb_item"),
                error_items=error_items_df.select("dynamodb_item", "error_info"),
                total_count=df.count(),
                valid_count=valid_count,
                error_count=error_count
            )

        except Exception as e:
            logger.error(f"Error during transformation: {str(e)}")
            raise 