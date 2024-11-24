# src/models/tender.py
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from src.database.base import Base

from .enum import (
    AdministrativeActType,
    Currency,
    EstimationType,
    PaymentModality,
    TenderType,
    TimeUnit,
    PaymentType,
)

class Tender(Base):
    __tablename__ = "tenders"

    # Identificación y datos básicos
    code = Column(String, primary_key=True, doc="Código único de la licitación")
    name = Column(String, nullable=True, doc="Nombre de la licitación")
    description = Column(String, nullable=True, doc="Descripción detallada de la licitación")
    status = Column(String, nullable=True, doc="Estado actual de la licitación")
    status_code = Column(Integer, nullable=True, doc="Código numérico del estado")
    api_version = Column(String, nullable=True, doc="Versión de la API")

    # Clasificación y tipo
    tender_type = Column(
        SQLAlchemyEnum(TenderType), nullable=True, doc="Tipo de licitación según monto UTM"
    )
    currency = Column(SQLAlchemyEnum(Currency), nullable=True, doc="Moneda de la licitación")
    bidding_stages = Column(Integer, nullable=True, doc="Número de etapas (1 o 2)")
    bidding_stages_status = Column(Integer, nullable=True, doc="Estado de las etapas")

    # Información financiera
    estimated_amount = Column(BigInteger, nullable=True, doc="Monto estimado de la licitación")
    estimation_type = Column(
        SQLAlchemyEnum(EstimationType), nullable=True, doc="Tipo de estimación del monto"
    )
    amount_visibility = Column(Boolean, nullable=True, doc="Visibilidad del monto estimado")
    payment_modality = Column(
        SQLAlchemyEnum(PaymentModality), nullable=True, doc="Modalidad de pago"
    )
    payment_type = Column(
        SQLAlchemyEnum(PaymentType),
        nullable=True,
        doc="Tipo de pago que se realizará"
    )
    financing_source = Column(String, nullable=True, doc="Fuente de financiamiento")

    # Información de la organización compradora
    organization = Column(String, nullable=True, doc="Nombre del organismo comprador")
    organization_code = Column(String, nullable=True, doc="Código del organismo")
    organization_tax_id = Column(String, nullable=True, doc="RUT del organismo")
    buying_unit = Column(String, nullable=True, doc="Nombre de la unidad compradora")
    buying_unit_code = Column(String, nullable=True, doc="Código de la unidad compradora")
    buying_unit_address = Column(String, nullable=True, doc="Dirección de la unidad compradora")
    buying_unit_region = Column(String, nullable=True, doc="Región de la unidad compradora")
    buying_unit_commune = Column(String, nullable=True, doc="Comuna de la unidad compradora")

    # Información del usuario responsable
    user_tax_id = Column(String, nullable=True, doc="RUT del usuario responsable")
    user_code = Column(String, nullable=True, doc="Código del usuario")
    user_name = Column(String, nullable=True, doc="Nombre del usuario")
    user_position = Column(String, nullable=True, doc="Cargo del usuario")

    # Fechas importantes
    creation_date = Column(DateTime, nullable=True, doc="Fecha de creación")
    publication_date = Column(DateTime, nullable=True, doc="Fecha de publicación")
    closing_date = Column(DateTime, nullable=True, doc="Fecha de cierre")
    questions_deadline = Column(DateTime, nullable=True, doc="Fecha límite de preguntas")
    answers_publication_date = Column(
        DateTime, nullable=True, doc="Fecha de publicación de respuestas"
    )
    technical_opening_date = Column(DateTime, nullable=True, doc="Fecha de apertura técnica")
    economic_opening_date = Column(DateTime, nullable=True, doc="Fecha de apertura económica")
    award_date = Column(DateTime, nullable=True, doc="Fecha de adjudicación")
    estimated_award_date = Column(DateTime, nullable=True, doc="Fecha estimada de adjudicación")
    site_visit_date = Column(DateTime, nullable=True, doc="Fecha de visita a terreno")
    background_delivery_date = Column(
        DateTime, nullable=True, doc="Fecha de entrega de antecedentes"
    )
    physical_support_date = Column(DateTime, nullable=True, doc="Fecha de soporte físico")
    evaluation_date = Column(DateTime, nullable=True, doc="Fecha de evaluación")
    estimated_signing_date = Column(DateTime, nullable=True, doc="Fecha estimada de firma")
    user_defined_date = Column(DateTime, nullable=True, doc="Fecha definida por usuario")

    # Unidades de tiempo
    evaluation_time_unit = Column(
        SQLAlchemyEnum(TimeUnit), nullable=True, doc="Unidad de tiempo para evaluación"
    )
    contract_time_unit = Column(
        SQLAlchemyEnum(TimeUnit), nullable=True, doc="Unidad de tiempo del contrato"
    )

    # Información de contacto
    payment_responsible_name = Column(String, nullable=True, doc="Nombre del responsable de pago")
    payment_responsible_email = Column(String, nullable=True, doc="Email del responsable de pago")
    contract_responsible_name = Column(
        String, nullable=True, doc="Nombre del responsable del contrato"
    )
    contract_responsible_email = Column(
        String, nullable=True, doc="Email del responsable del contrato"
    )
    contract_responsible_phone = Column(
        String, nullable=True, doc="Teléfono del responsable del contrato"
    )

    # Información del contrato
    allows_subcontracting = Column(Boolean, nullable=True, doc="Permite subcontratación")
    contract_duration = Column(Integer, nullable=True, doc="Duración del contrato")
    contract_duration_type = Column(String, nullable=True, doc="Tipo de duración del contrato")
    is_renewable = Column(Boolean, nullable=True, doc="Es renovable")
    renewal_time_value = Column(Integer, nullable=True, doc="Valor tiempo de renovación")
    renewal_time_period = Column(String, nullable=True, doc="Período de tiempo de renovación")

    # Control y regulación
    requires_comptroller = Column(
        Boolean, nullable=True, doc="Requiere toma de razón de Contraloría"
    )
    technical_offer_publicity = Column(Integer, nullable=True, doc="Publicidad de oferta técnica")
    publicity_justification = Column(String, nullable=True, doc="Justificación de publicidad")
    hiring_prohibition = Column(String, nullable=True, doc="Prohibición de contratación")
    amount_justification = Column(String, nullable=True, doc="Justificación del monto")
    deadline_extension = Column(Integer, nullable=True, doc="Extensión de plazo")

    # Flags y estados
    is_public_bid = Column(Boolean, nullable=True, doc="Es licitación pública")
    is_informed = Column(Boolean, nullable=True, doc="Está informada")
    is_base_type = Column(Boolean, nullable=True, doc="Es tipo base")

    # Información de adjudicación
    award_type = Column(
        SQLAlchemyEnum(AdministrativeActType), nullable=True, doc="Tipo de acto administrativo"
    )
    award_document_number = Column(String, nullable=True, doc="Número de documento de adjudicación")
    award_document_date = Column(DateTime, nullable=True, doc="Fecha del documento de adjudicación")
    number_of_bidders = Column(Integer, nullable=True, doc="Número de oferentes")
    award_act_url = Column(String, nullable=True, doc="URL del acta de adjudicación")
    complaint_count = Column(Integer, nullable=True, doc="Cantidad de reclamos")

    # Datos adicionales
    items = Column("items", JSON, nullable=True, doc="Información de ítems en formato JSON")
    awarded_suppliers = Column(JSON, nullable=True, doc="Información de proveedores adjudicados")

    # Relaciones
    tender_items = relationship("TenderItem", back_populates="tender", cascade="all, delete-orphan")

    # Fechas de creación y actualización
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                       doc="Date when the tender was first added to the database")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                       onupdate=datetime.utcnow,
                       doc="Date when the tender was last updated in the database")


    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'code': self.code,
            'name': self.name,
            'status': self.status,
            'organization': self.organization,
            'closing_date': self.closing_date.isoformat() if self.closing_date else None,
            'estimated_amount': float(self.estimated_amount) if self.estimated_amount else None,
            'tender_type': str(self.tender_type.value) if self.tender_type else None
        }

    def get_payment_description(self) -> str:
        """Returns a human-readable payment modality description"""
        return self.payment_modality.description if self.payment_modality else "No especificado"

    def get_duration_description(self) -> str:
        """Returns a formatted duration description"""
        if self.contract_duration and self.contract_time_unit:
            return f"{self.contract_duration} {self.contract_time_unit.description}"
        return "No especificado"

    def is_high_value_tender(self) -> bool:
        """Checks if this is a high-value tender"""
        return self.tender_type in [TenderType.LQ, TenderType.LR] if self.tender_type else False

    def get_status_description(self) -> str:
        """Returns a human-readable status description"""
        status_map = {
            1: "Publicada",
            2: "Cerrada",
            3: "Desierta",
            4: "Adjudicada",
            5: "Revocada",
            6: "Suspendida",
            7: "En Evaluación",
        }
        return status_map.get(self.status_code, "Estado desconocido")

    def get_payment_type_description(self) -> str:
        """Returns a human-readable payment type description"""
        return self.payment_type.description if self.payment_type else "No especificado"

    def __repr__(self):
        """String representation of the tender"""
        return (
            f"<Tender(code={self.code}, name={self.name}, status={self.get_status_description()})>"
        )


class TenderItem(Base):
    __tablename__ = "tender_items"

    id = Column(Integer, primary_key=True)
    tender_code = Column(String, ForeignKey("tenders.code"))
    correlative = Column(String, nullable=True)
    category_code = Column(String, nullable=True)
    category_name = Column(String, nullable=True)
    product_code = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(Float, nullable=True)
    unit = Column(String, nullable=True)

    # Relationship
    tender = relationship("Tender", back_populates="tender_items")
