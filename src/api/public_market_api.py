from datetime import date, timedelta
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config.settings import API_BASE_URL, API_TICKET
from src.models.enum import (
    AdministrativeActType,
    Currency,
    EstimationType,
    PaymentModality,
    TenderType,
    TimeUnit,
    PaymentType,
)
from src.models.tender import Tender
from src.utils.logger import setup_logger
from src.utils.safe_load import parse_date, safe_bool, safe_float, safe_int, remove_accents


class PublicMarketAPI:
    """Class to interact with the Public Market API"""

    def __init__(self):
        """Initialize API with configuration"""
        self.ticket = API_TICKET
        self.base_url = API_BASE_URL
        self.logger = setup_logger(__name__)

        # Configure session with retry strategy
        self.session = self._configure_session()

    def _configure_session(self) -> requests.Session:
        """
        Configure requests session with retry strategy

        Returns:
            requests.Session: Configured session object
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    def _make_request(self, params: Dict) -> Optional[Dict]:
        """
        Makes an API request with error handling and detailed logging

        Args:
            params: Dictionary with request parameters

        Returns:
            Optional[Dict]: JSON response from the API or None if request fails

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        try:
            self.logger.debug(f"Making request with parameters: {params}")
            response = self.session.get(self.base_url, params=params, timeout=(5, 30))
            response.raise_for_status()

            data = response.json()
            self.logger.debug(f"Number of tenders in response: {data.get('Cantidad', 0)}")
            return data

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
            return None

    def get_tender_details(self, code: str) -> Optional[Dict]:
        """
        Get detailed information for a specific tender

        Args:
            code: Tender code to search

        Returns:
            Optional[Dict]: Detailed tender information or None if not found
        """
        if not code:
            return None

        params = {"ticket": self.ticket, "codigo": code}

        try:
            self.logger.debug(f"Getting details for tender {code}")
            data = self._make_request(params)

            if not data or "Listado" not in data or not data["Listado"]:
                self.logger.warning(f"No valid details found for tender {code}")
                return None

            tender_data = data["Listado"][0]
            if not isinstance(tender_data, dict):
                self.logger.warning(f"Invalid data format for tender {code}")
                return None

            return tender_data

        except Exception as e:
            self.logger.error(f"Error getting tender details for {code}: {str(e)}")
            return None

    def search_tenders(self, include_keywords: List[str], exclude_keywords: List[str] = None, 
                    days_back: int = 30, status: str = "publicada") -> List[Tender]:
        """
        Searches for tenders containing specified keywords
        
        Args:
            include_keywords: List of keywords to search for
            exclude_keywords: List of keywords to exclude (optional)
            days_back: Number of days to look back
            status: Status of tenders to search. Options are:
                "publicada", "cerrada", "desierta", "adjudicada", 
                "revocada", "suspendida", "todos"
                Default is "publicada"
            
        Returns:
            List[Tender]: List of found tenders
        """
        # Validate status
        valid_statuses = {
            "publicada", "cerrada", "desierta", "adjudicada", 
            "revocada", "suspendida", "todos"
        }
        
        if status.lower() not in valid_statuses:
            self.logger.warning(f"Invalid status '{status}'. Using default 'publicada'")
            status = "publicada"
        
        exclude_keywords = exclude_keywords or []
        found_tenders = []
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)

        self.logger.info(f"Searching tenders from {start_date} to {end_date}")
        self.logger.info(f"Include keywords: {include_keywords}")
        self.logger.info(f"Exclude keywords: {exclude_keywords}")
        self.logger.info(f"Status filter: {status}")

        current_date = start_date
        while current_date <= end_date:
            try:
                params = {
                    "ticket": self.ticket,
                    "fecha": current_date.strftime("%d%m%Y"),
                    "codigo": None,
                    "estado": None if status.lower() == "todos" else status.lower()
                }

                data = self._make_request(params)
                if not data:
                    current_date += timedelta(days=1)
                    continue

                if "Listado" not in data:
                    self.logger.warning(f"No listing found for date {current_date}")
                    current_date += timedelta(days=1)
                    continue

                tenders = data["Listado"]
                self.logger.info(f"Tenders found for {current_date}: {len(tenders)}")

                for tender_data in tenders:
                    try:
                        if self._matches_keyword_criteria(tender_data, include_keywords, exclude_keywords):
                            tender_code = tender_data.get("CodigoExterno")
                            if not tender_code:
                                continue

                            detailed_data = self.get_tender_details(tender_code)
                            if not detailed_data:
                                continue

                            tender = self._parse_tender(detailed_data)
                            if tender:
                                found_tenders.append(tender)
                                self.logger.debug(
                                    f"Tender {tender.code} matched keywords and was added"
                                )
                    except Exception as e:
                        self.logger.error(f"Error processing tender: {str(e)}")
                        continue

            except Exception as e:
                self.logger.error(f"Error processing date {current_date}: {str(e)}")

            current_date += timedelta(days=1)

        self.logger.info(f"Process completed. Total found: {len(found_tenders)}")
        return found_tenders

    def _contains_keywords(self, tender: Dict, keywords: List[str]) -> bool:
        """
        Check if tender contains any of the keywords

        Args:
            tender: Tender data dictionary
            keywords: List of keywords to search

        Returns:
            bool: True if any keyword is found
        """
        if not tender or not keywords:
            return False

        search_text = (f"{tender.get('Nombre', '')} " f"{tender.get('Descripcion', '')}").lower()

        return any(keyword.lower() in search_text for keyword in keywords)

    def _parse_tender(self, tender_data: Dict) -> Optional[Tender]:
        """
        Parse tender data into Tender object

        Args:
            tender_data: Raw tender data from API

        Returns:
            Optional[Tender]: Parsed tender object or None if parsing fails
        """
        if not tender_data or not isinstance(tender_data, dict):
            self.logger.warning("Invalid or empty tender data received")
            return None

        try:
            # Get nested dictionaries with safe defaults
            comprador = tender_data.get("Comprador") or {}
            fechas = tender_data.get("Fechas") or {}
            adjudicacion = tender_data.get("Adjudicacion") or {}
            items_data = tender_data.get("Items") or {}

            # Verificar código obligatorio
            code = tender_data.get("CodigoExterno")
            if not code:
                self.logger.warning("Tender data missing required code")
                return None

            # Parse items and awarded suppliers
            try:
                items = self._parse_items(items_data)
            except Exception as e:
                self.logger.warning(f"Error parsing items: {str(e)}")
                items = None

            try:
                awarded_suppliers = self._parse_awarded_suppliers(tender_data)
            except Exception as e:
                self.logger.warning(f"Error parsing awarded suppliers: {str(e)}")
                awarded_suppliers = None

            return Tender(
                # Identificación y datos básicos
                code=code,
                name=tender_data.get("Nombre"),
                description=tender_data.get("Descripcion"),
                status=tender_data.get("Estado"),
                status_code=safe_int(tender_data.get("CodigoEstado")),
                api_version=tender_data.get("Version"),
                # Clasificación y tipo
                tender_type=TenderType.from_value(tender_data.get("Tipo")),
                currency=Currency.from_value(tender_data.get("Moneda")),
                bidding_stages=safe_int(tender_data.get("Etapas")),
                bidding_stages_status=safe_int(tender_data.get("EstadoEtapas")),
                # Información financiera
                estimated_amount=safe_float(tender_data.get("MontoEstimado")),
                estimation_type=EstimationType.from_value(tender_data.get("Estimacion")),
                amount_visibility=safe_bool(tender_data.get("VisibilidadMonto")),
                payment_modality=PaymentModality.from_value(tender_data.get("Modalidad")),
                payment_type=PaymentType.from_value(tender_data.get("TipoPago")),
                financing_source=str(tender_data.get('FuenteFinanciamiento')) if tender_data.get('FuenteFinanciamiento') else None,
                # Información de la organización
                organization=comprador.get("NombreOrganismo"),
                organization_code=comprador.get("CodigoOrganismo"),
                organization_tax_id=comprador.get("RutUnidad"),
                buying_unit=comprador.get("NombreUnidad"),
                buying_unit_code=comprador.get("CodigoUnidad"),
                buying_unit_address=comprador.get("DireccionUnidad"),
                buying_unit_region=comprador.get("RegionUnidad"),
                buying_unit_commune=comprador.get("ComunaUnidad"),
                # Información del usuario
                user_tax_id=comprador.get("RutUsuario"),
                user_code=comprador.get("CodigoUsuario"),
                user_name=comprador.get("NombreUsuario"),
                user_position=comprador.get("CargoUsuario"),
                # Fechas
                creation_date=parse_date(fechas.get("FechaCreacion")),
                publication_date=parse_date(fechas.get("FechaPublicacion")),
                closing_date=parse_date(fechas.get("FechaCierre")),
                questions_deadline=parse_date(fechas.get("FechaFinal")),
                answers_publication_date=parse_date(fechas.get("FechaPubRespuestas")),
                technical_opening_date=parse_date(fechas.get("FechaActoAperturaTecnica")),
                economic_opening_date=parse_date(fechas.get("FechaActoAperturaEconomica")),
                award_date=parse_date(fechas.get("FechaAdjudicacion")),
                estimated_award_date=parse_date(fechas.get("FechaEstimadaAdjudicacion")),
                site_visit_date=parse_date(fechas.get("FechaVisitaTerreno")),
                background_delivery_date=parse_date(fechas.get("FechaEntregaAntecedentes")),
                physical_support_date=parse_date(fechas.get("FechaSoporteFisico")),
                evaluation_date=parse_date(fechas.get("FechaTiempoEvaluacion")),
                estimated_signing_date=parse_date(fechas.get("FechaEstimadaFirma")),
                user_defined_date=parse_date(fechas.get("FechasUsuario")),
                # Unidades de tiempo
                evaluation_time_unit=TimeUnit.from_value(tender_data.get("UnidadTiempo")),
                contract_time_unit=TimeUnit.from_value(
                    tender_data.get("UnidadTiempoContratoLicitacion")
                ),
                # Información de contacto
                payment_responsible_name=tender_data.get("NombreResponsablePago"),
                payment_responsible_email=tender_data.get("EmailResponsablePago"),
                contract_responsible_name=tender_data.get("NombreResponsableContrato"),
                contract_responsible_email=tender_data.get("EmailResponsableContrato"),
                contract_responsible_phone=tender_data.get("FonoResponsableContrato"),
                # Información del contrato
                allows_subcontracting=safe_bool(tender_data.get("SubContratacion")),
                contract_duration=safe_int(tender_data.get("TiempoDuracionContrato")),
                contract_duration_type=tender_data.get("TipoDuracionContrato"),
                is_renewable=safe_bool(tender_data.get("EsRenovable")),
                renewal_time_value=safe_int(tender_data.get("ValorTiempoRenovacion")),
                renewal_time_period=tender_data.get("PeriodoTiempoRenovacion"),
                # Control y regulación
                requires_comptroller=safe_bool(tender_data.get("TomaRazon")),
                technical_offer_publicity=safe_int(tender_data.get("EstadoPublicidadOfertas")),
                publicity_justification=tender_data.get("JustificacionPublicidad"),
                hiring_prohibition=tender_data.get("ProhibicionContratacion"),
                amount_justification=tender_data.get("JustificacionMontoEstimado"),
                deadline_extension=safe_int(tender_data.get("ExtensionPlazo")),
                # Flags y estados
                is_public_bid=safe_bool(tender_data.get("TipoConvocatoria")),
                is_informed=safe_bool(tender_data.get("Informada")),
                is_base_type=safe_bool(tender_data.get("EsBaseTipo")),
                # Información de adjudicación
                award_type=AdministrativeActType.from_value(adjudicacion.get("Tipo")),
                award_document_number=adjudicacion.get("Numero"),
                award_document_date=parse_date(adjudicacion.get("Fecha")),
                number_of_bidders=safe_int(adjudicacion.get("NumeroOferentes")),
                award_act_url=adjudicacion.get("UrlActa"),
                complaint_count=safe_int(tender_data.get("CantidadReclamos")),
                # Datos adicionales
                items=items,
                awarded_suppliers=awarded_suppliers,
            )

        except Exception as e:
            self.logger.error(f"Error parsing tender details: {str(e)}")
            return None

    def _parse_items(self, items_data: Dict) -> List[Dict]:
        """
        Parse items data into a structured format

        Args:
            items_data: Raw items data from API

        Returns:
            List[Dict]: List of parsed items
        """
        items = []

        # Return empty list if items_data is None
        if not items_data:
            return items

        # Get listado with empty list as default
        listado = items_data.get("Listado", []) or []

        for item in listado:
            if not isinstance(item, dict):
                continue

            parsed_item = {
                "correlative": item.get("Correlativo"),
                "category_code": item.get("CodigoCategoria"),
                "category_name": item.get("Categoria"),
                "product_code": item.get("CodigoProducto"),
                "product_name": item.get("NombreProducto"),
                "description": item.get("Descripcion"),
                "quantity": safe_float(item.get("Cantidad")),
                "unit": item.get("UnidadMedida"),
                "tender_status_code": safe_int(item.get("CodigoEstadoLicitacion")),
            }

            # Only add award information if it exists
            adjudicacion = item.get("Adjudicacion")
            if isinstance(adjudicacion, dict):
                parsed_item["award"] = {
                    "supplier_tax_id": adjudicacion.get("RutProveedor"),
                    "supplier_name": adjudicacion.get("NombreProveedor"),
                    "awarded_quantity": safe_float(adjudicacion.get("CantidadAdjudicada")),
                    "unit_price": safe_float(adjudicacion.get("MontoUnitario")),
                }

            items.append(parsed_item)

        return items

    def _parse_awarded_suppliers(self, tender_data: Dict) -> List[Dict]:
        """
        Parse awarded suppliers data

        Args:
            tender_data: Raw tender data from API

        Returns:
            List[Dict]: List of awarded suppliers
        """
        awarded_suppliers = []

        # Return empty list if tender_data is None
        if not tender_data:
            return awarded_suppliers

        # Get items data safely
        items_data = tender_data.get("Items", {})
        if not items_data:
            return awarded_suppliers

        # Get listado with empty list as default
        items = items_data.get("Listado", []) or []

        for item in items:
            if not isinstance(item, dict):
                continue

            adjudicacion = item.get("Adjudicacion")
            if not isinstance(adjudicacion, dict):
                continue

            supplier = {
                "tax_id": adjudicacion.get("RutProveedor"),
                "name": adjudicacion.get("NombreProveedor"),
                "item_correlative": item.get("Correlativo"),
                "awarded_quantity": safe_float(adjudicacion.get("CantidadAdjudicada")),
                "unit_price": safe_float(adjudicacion.get("MontoUnitario")),
            }

            # Only add if we have at least tax_id or name
            if supplier["tax_id"] or supplier["name"]:
                if supplier not in awarded_suppliers:
                    awarded_suppliers.append(supplier)

        return awarded_suppliers

    def _matches_keyword_criteria(self, tender: Dict, include_keywords: List[str], 
                                exclude_keywords: List[str]) -> bool:
        """
        Check if tender matches keyword criteria
        
        Args:
            tender: Tender data dictionary
            include_keywords: List of keywords that should be included
            exclude_keywords: List of keywords that should be excluded
            
        Returns:
            bool: True if tender matches criteria
        """
        if not tender:
            return False

        # Create normalized search text without accents
        search_text = remove_accents(
            f"{tender.get('Nombre', '')} {tender.get('Descripcion', '')}"
        ).lower()

        # Normalize keywords
        normalized_exclude = [remove_accents(keyword).lower() for keyword in exclude_keywords]
        normalized_include = [remove_accents(keyword).lower() for keyword in include_keywords]

        # Check if any exclude keyword is present
        if any(keyword in search_text for keyword in normalized_exclude):
            self.logger.debug(f"Tender excluded due to matching exclude keyword")
            return False

        # If no include keywords, accept all non-excluded
        if not normalized_include:
            return True

        # Check if any include keyword is present
        matches = any(keyword in search_text for keyword in normalized_include)
        if matches:
            self.logger.debug(f"Tender matched include keyword")
        
        return matches
