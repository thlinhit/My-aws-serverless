"""
Transformer for loan application data implementing domain business rules
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, when, lit, concat, date_format, from_unixtime, format_string,
    create_map, array, array_remove, map_filter
)

from application.etl.tranformation.base_transformer import DataTransformer, TransformationResult
from infrastructure.logger import logger

DECLINED = "Declined"

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
            # Cache the DataFrame for better performance with multiple transformations
            df = df.cache()

            # Add validation error column
            transformed_df = self._add_validation_errors(df)

            # Type conversions and formatting
            transformed_df = self._apply_type_conversions(transformed_df)
            transformed_df = self._format_date_fields(transformed_df)
            transformed_df = self._convert_numeric_fields(transformed_df)

            # Business logic for decline reasons
            transformed_df = self._process_decline_reasons(transformed_df)

            # Create DynamoDB item structure
            transformed_df = self._create_dynamodb_structure(transformed_df)

            # Split into valid and error items
            valid_items_df, error_items_df = self._partition_dataframe(transformed_df)

            # Calculate statistics
            total_count = df.count()
            valid_count = valid_items_df.count()
            error_count = error_items_df.count()

            logger.info(
                f"Transformed {valid_count} loan application records "
                f"(with {error_count} errors)",
                extra={
                    "valid_count": valid_count,
                    "error_count": error_count,
                    "total_count": total_count
                }
            )

            # Optimize the return result by selecting only needed columns
            return TransformationResult(
                valid_items=valid_items_df.select("dynamodb_item"),
                error_items=error_items_df.select("dynamodb_item", "error_info"),
                total_count=total_count,
                valid_count=valid_count,
                error_count=error_count
            )

        except Exception as e:
            logger.error(f"Error during transformation: {str(e)}")
            raise

    def _add_validation_errors(self, df: DataFrame) -> DataFrame:
        """Add error information column based on validation rules"""
        return df.withColumn(
            "error_info",
            when(col("customer_id").isNull(), "Missing customer_id")
            .when(col("application_id").isNull(), "Missing application_id")
            .when(col("date_application_created").isNull(), "Missing date_application_created")
            .when(col("status").isNull(), "Missing status")
            .when(col("requested_amount").isNull(), "Missing requested_amount")
            .otherwise(None)
        )

    def _apply_type_conversions(self, df: DataFrame) -> DataFrame:
        """Apply basic type conversions to the DataFrame"""
        # Convert customer_id to string to prevent scientific notation
        return df.withColumn(
            "customer_id",
            format_string("%.0f", col("customer_id"))
        )

    def _format_date_fields(self, df: DataFrame) -> DataFrame:
        """Format date fields to ISO format"""
        return df.withColumn(
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

    def _convert_numeric_fields(self, df: DataFrame) -> DataFrame:
        """Convert numeric fields to appropriate decimal types"""
        # Apply decimal conversions - chain operations to improve code readability
        return (df
        .withColumn(
            "requested_amount",
            col("requested_amount").cast("decimal(10,2)")
        )
        .withColumn(
            "accepted_amount",
            when(col("accepted_amount").isNotNull(),
                 col("accepted_amount").cast("decimal(10,2)")
                 ).otherwise(None)
        )
        .withColumn(
            "gross_income",
            when(col("gross_income").isNotNull(),
                 col("gross_income").cast("decimal(10,2)")
                 ).otherwise(None)
        )
        )

    def _process_decline_reasons(self, df: DataFrame) -> DataFrame:
        """Process and clean decline reasons for declined applications"""
        return df.withColumn(
            "decline_reasons",
            when(
                col("status") == "DECLINED",
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

    def _create_dynamodb_structure(self, df: DataFrame) -> DataFrame:
        """Create the DynamoDB item structure for storing the data"""
        return df.withColumn(
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