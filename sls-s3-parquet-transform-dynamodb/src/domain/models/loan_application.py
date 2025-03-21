from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator, model_validator
from decimal import Decimal
import decimal


class LoanApplication(BaseModel):
    """Pydantic model for loan application data with validation."""
    
    # Required fields
    customer_id: str
    application_id: str
    debtor_account_number: str
    
    # Date fields with validation
    date_application_created: Optional[datetime] = None
    contract_date: Optional[datetime] = None
    
    # Status and amount fields
    status: str = "UNKNOWN"
    requested_amount: Optional[Decimal] = None
    accepted_amount: Optional[Decimal] = None
    gross_income: Optional[Decimal] = None
    
    # Decline reasons
    decline_reason_1: Optional[str] = None
    decline_reason_2: Optional[str] = None
    decline_reason_3: Optional[str] = None
    
    # Parsed fields (not in input, but computed during validation)
    application_date: Optional[datetime] = None
    contract_date_parsed: Optional[datetime] = None
    status_normalized: str = "UNKNOWN"
    decline_reasons: List[str] = Field(default_factory=list)
    
    @validator('date_application_created')
    def parse_application_date(cls, v, values):
        """Parse application date in DD-MM-YYYY HH:MM:SS format."""
        if not v:
            return v
            
        try:
            # Parse as DD-MM-YYYY HH:MM:SS
            date_obj = datetime.strptime(v, "%d-%m-%Y %H:%M:%S")
            values['application_date'] = date_obj
            return v
        except (ValueError, TypeError):
            # We'll just store the original string, a root_validator will handle defaults
            return v
    
    @validator('contract_date')
    def parse_contract_date(cls, v, values):
        """Parse contract date in DD/MM/YYYY format."""
        if not v:
            return v
            
        try:
            # Parse as DD/MM/YYYY
            date_obj = datetime.strptime(v, "%d/%m/%Y")
            values['contract_date_parsed'] = date_obj
            return v
        except (ValueError, TypeError):
            return v
    
    @validator('status')
    def normalize_status(cls, v):
        """Normalize status values to standard format."""
        if not v:
            return "UNKNOWN"
            
        status = v.strip()
        status_map = {
            'approved': 'APPROVED',
            'rejected': 'DECLINED',
            'declined': 'DECLINED',
            'pending': 'PENDING'
        }
        
        return status_map.get(status.lower(), status.upper())
    
    @validator('requested_amount', 'accepted_amount', 'gross_income', pre=True)
    def convert_to_decimal(cls, v):
        if v is None:
            return None
            
        try:
            if isinstance(v, Decimal):
                decimal_value = v
            elif isinstance(v, (int, float)):
                decimal_value = Decimal.from_float(float(v))
            elif isinstance(v, str):
                decimal_value = Decimal(v)
            else:
                raise ValueError(f"Unsupported type for conversion to Decimal: {type(v)}")
            
            if decimal_value < 0:
                raise ValueError(f"Amount cannot be negative: {decimal_value}")
            
            return decimal_value.quantize(Decimal('0.01'), rounding=Decimal.ROUND_HALF_UP)
            
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            raise ValueError(f"Invalid amount value: {v}. Error: {str(e)}")
    
    @model_validator(mode='after')
    def set_derived_fields(self) -> 'LoanApplication':
        """Set derived fields after individual validations."""
        # Set default application date if not parsed
        if not self.application_date:
            self.application_date = datetime.now()
        
        # Collect decline reasons
        decline_reasons = []
        for i in range(1, 4):
            reason_key = f'decline_reason_{i}'
            reason_value = getattr(self, reason_key)
            if reason_value:
                decline_reasons.append(reason_value)
        
        self.decline_reasons = decline_reasons
        self.status_normalized = self.status
        
        return self
    
    def to_dynamodb_item(self, 
                         partition_key_pattern: str = "CUS#{customer_id}",
                         sort_key_pattern: str = "LOAN_APP#{application_id}") -> Dict[str, Any]:
        """
        Convert to DynamoDB item format.
        
        Args:
            partition_key_pattern: Pattern for partition key
            sort_key_pattern: Pattern for sort key
            
        Returns:
            Dictionary formatted for DynamoDB
        """
        # Create partition and sort keys
        partition_key = partition_key_pattern.replace("{customer_id}", str(self.customer_id))
        sort_key = sort_key_pattern.replace("{application_id}", str(self.application_id))
        
        # Calculate timestamp for GSI
        application_date_epoch = int(self.application_date.timestamp())
        application_date_iso = self.application_date.isoformat()
        
        # Convert Decimal values to strings for DynamoDB
        def format_decimal(value: Optional[Decimal]) -> Optional[str]:
            if value is None:
                return None
            return str(value)
        
        # Build DynamoDB item with base fields
        item = {
            # Dictionary representation of the model
            **self.dict(exclude={'application_date', 'contract_date_parsed'}),
            
            # DynamoDB keys
            'PK': partition_key,
            'SK': sort_key,
            'GSI1_PK': "LOAN_APPS",
            'GSI1_SK': f"{application_date_epoch}#{self.application_id}",
            
            # Metadata and transformed fields
            'entity_type': 'LOAN_APPLICATION',
            'status': self.status_normalized,
            'application_date': application_date_iso,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            
            # Format decimal values for DynamoDB
            'requested_amount': format_decimal(self.requested_amount),
            'accepted_amount': format_decimal(self.accepted_amount),
            'gross_income': format_decimal(self.gross_income),
        }
        
        # Add contract date in ISO format if available
        if self.contract_date_parsed:
            item['contract_date_iso'] = self.contract_date_parsed.isoformat()
        else:
            item['contract_date_iso'] = None
        
        # Set TTL for 3 years (retention policy)
        ttl_date = datetime.now() + timedelta(days=3*365)
        item['ttl'] = int(ttl_date.timestamp())
        
        # Add status-based dates
        if self.status_normalized == 'APPROVED':
            item['approved_date'] = application_date_iso
        elif self.status_normalized == 'DECLINED':
            item['declined_date'] = application_date_iso
        
        return item 