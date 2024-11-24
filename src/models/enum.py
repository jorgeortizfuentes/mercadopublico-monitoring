# src/models/enum.py
from enum import Enum
from typing import Optional, Any

class BaseEnum(Enum):
    """Base Enum class with common functionality"""
    @classmethod
    def from_value(cls, value: Any) -> Optional['BaseEnum']:
        """
        Convert a value to enum member, returning None if invalid
        
        Args:
            value: The value to convert
            
        Returns:
            Optional[BaseEnum]: The enum member or None if not found
        """
        if value is None:
            return None
        try:
            return cls(value)
        except (ValueError, TypeError):
            return None


    @classmethod
    def get_default(cls) -> 'BaseEnum':
        """Get the default value for this enum"""
        return list(cls)[0]

class TenderType(BaseEnum):
    """Types of tenders based on UTM amounts"""
    L1 = "L1", "Licitación Pública Menor a 100 UTM"
    LE = "LE", "Licitación Pública igual o superior a 100 UTM e inferior a 1.000 UTM"
    LP = "LP", "Licitación Pública igual o superior a 1.000 UTM e inferior a 2.000 UTM"
    LQ = "LQ", "Licitación Pública igual o superior a 2.000 UTM e inferior a 5.000 UTM"
    LR = "LR", "Licitación Pública igual o superior a 5.000 UTM"
    E2 = "E2", "Licitación Privada Menor a 100 UTM"
    CO = "CO", "Licitación Privada igual o superior a 100 UTM e inferior a 1000 UTM"
    B2 = "B2", "Licitación Privada igual o superior a 1000 UTM e inferior a 2000 UTM"
    H2 = "H2", "Licitación Privada igual o superior a 2000 UTM e inferior a 5000 UTM"
    I2 = "I2", "Licitación Privada Mayor a 5000 UTM"
    LS = "LS", "Licitación Pública Servicios personales especializados"

    def __new__(cls, code: str, description: str):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.description = description
        return obj

class Currency(BaseEnum):
    """Available currencies"""
    CLP = "CLP", "Peso Chileno"
    CLF = "CLF", "Unidad de Fomento"
    USD = "USD", "Dólar Americano"
    UTM = "UTM", "Unidad Tributaria Mensual"
    EUR = "EUR", "Euro"

    def __new__(cls, code: str, description: str):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.description = description
        return obj

class EstimationType(BaseEnum):
    """Types of amount estimation"""
    AVAILABLE_BUDGET = 1, "Presupuesto Disponible"
    REFERENCE_PRICE = 2, "Precio Referencial"
    CANNOT_ESTIMATE = 3, "Monto no es posible de estimar"

    def __new__(cls, value: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class PaymentModality(BaseEnum):
    """Payment modalities"""
    DAYS_30 = 1, "Pago a 30 días"
    DAYS_30_60_90 = 2, "Pago a 30, 60 y 90 días"
    SAME_DAY = 3, "Pago al día"
    ANNUAL = 4, "Pago Anual"
    BIMONTHLY = 5, "Pago Bimensual"
    ON_DELIVERY = 6, "Pago Contra Entrega Conforme"
    MONTHLY = 7, "Pagos Mensuales"
    BY_PROGRESS = 8, "Pago Por Estado de Avance"
    QUARTERLY = 9, "Pago Trimestral"
    DAYS_60 = 10, "Pago a 60 días"

    def __new__(cls, value: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class TimeUnit(BaseEnum):
    """Time units for different durations"""
    HOURS = 1, "Horas"
    DAYS = 2, "Días"
    WEEKS = 3, "Semanas"
    MONTHS = 4, "Meses"
    YEARS = 5, "Años"

    def __new__(cls, value: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class AdministrativeActType(BaseEnum):
    """Types of administrative acts"""
    AUTHORIZATION = 1, "Autorización"
    RESOLUTION = 2, "Resolución"
    AGREEMENT = 3, "Acuerdo"
    DECREE = 4, "Decreto"
    OTHERS = 5, "Otros"

    def __new__(cls, value: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class PaymentType(BaseEnum):
    """Types of payment"""
    CASH = 1, "Pago en efectivo"
    CREDIT = 2, "Pago con crédito"
    TRANSFER = 3, "Transferencia bancaria"
    CHECK = 4, "Cheque"
    ELECTRONIC = 5, "Pago electrónico"
    OTHER = 6, "Otro tipo de pago"

    def __new__(cls, value: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj
