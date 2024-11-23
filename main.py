from typing import List, Dict, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
from datetime import datetime, date, timedelta
import logging
from dotenv import load_dotenv
from dataclasses import dataclass
import json

@dataclass
class DetailedTender:
    """Class to store detailed tender information"""
    # Basic Information
    code: str
    name: str
    description: str
    status: str
    status_code: int
    estimated_amount: float
    closing_date: datetime
    
    # Organization Information
    organization: str
    organization_code: str
    organization_tax_id: str
    buying_unit: str
    buying_unit_code: str
    buying_unit_address: str
    buying_unit_region: str
    buying_unit_commune: str
    
    # Tender Details
    tender_type: str
    currency: str
    items_quantity: int
    bidding_stages: int
    contract_type: int
    is_public_bid: bool
    
    # Dates Information
    creation_date: datetime
    publication_date: Optional[datetime]
    questions_deadline: Optional[datetime]
    answers_publication_date: Optional[datetime]
    technical_opening_date: Optional[datetime]
    economic_opening_date: Optional[datetime]
    award_date: Optional[datetime]
    estimated_award_date: Optional[datetime]
    
    # Contact Information
    payment_responsible_name: Optional[str]
    payment_responsible_email: Optional[str]
    contract_responsible_name: Optional[str]
    contract_responsible_email: Optional[str]
    contract_responsible_phone: Optional[str]
    
    # Additional Information
    allows_subcontracting: bool
    contract_duration: Optional[int]
    contract_duration_type: Optional[str]
    financing_type: Optional[str]
    complaint_count: int
    items: List[Dict[str, Any]]
    
    # Award Information (if available)
    award_type: Optional[str]
    award_document_number: Optional[str]
    award_document_date: Optional[datetime]
    awarded_suppliers: List[Dict[str, Any]]

class PublicMarketAPI:
    """Class to interact with the Public Market API"""
    
    BASE_URL = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
    
    def __init__(self):
        """Initialize API with configuration from .env"""
        load_dotenv()
        self.ticket = os.getenv('TICKET_KEY')
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tender_search.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

    def _make_request(self, params: Dict) -> Dict:
        """
        Makes an API request with error handling and detailed logging
        
        Args:
            params: Dictionary with request parameters
            
        Returns:
            Dict: JSON response from the API
        """
        try:
            self.logger.debug(f"Making request with parameters: {params}")
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=(5, 30)
            )
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"Number of tenders in response: {data.get('Cantidad', 0)}")
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
            raise

    def search_tenders(self, keywords: List[str], days_back: int = 30) -> List[DetailedTender]:
        """
        Searches for tenders containing specified keywords
        
        Args:
            keywords: List of keywords to search
            days_back: Number of days to look back
            
        Returns:
            List[DetailedTender]: List of found tenders
        """
        try:
            found_tenders = []
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            self.logger.info(f"Searching tenders from {start_date} to {end_date}")
            
            current_date = start_date
            while current_date <= end_date:
                params = {
                    'ticket': self.ticket,
                    'fecha': current_date.strftime("%d%m%Y"),
                    'codigo': None
                }
                
                self.logger.info(f"Querying tenders for date: {current_date}")
                
                try:
                    data = self._make_request(params)
                    
                    if 'Listado' not in data:
                        self.logger.warning(f"No listing found for date {current_date}")
                        current_date += timedelta(days=1)
                        continue

                    tenders = data['Listado']
                    self.logger.info(f"Tenders found for {current_date}: {len(tenders)}")

                    for tender in tenders:
                        if self._contains_keywords(tender, keywords):
                            detailed_tender = self._parse_tender(tender)
                            found_tenders.append(detailed_tender)

                except Exception as e:
                    self.logger.error(f"Error processing date {current_date}: {str(e)}")
                
                current_date += timedelta(days=1)

            self.logger.info(f"Process completed. Total found: {len(found_tenders)}")
            return found_tenders
            
        except Exception as e:
            self.logger.error(f"Search error: {str(e)}")
            raise
            
    def _contains_keywords(self, tender: Dict, keywords: List[str]) -> bool:
        """Check if tender contains any of the keywords"""
        search_text = (
            f"{tender.get('Nombre', '')} "
            f"{tender.get('Descripcion', '')}"
        ).lower()
        
        return any(keyword.lower() in search_text for keyword in keywords)
    
    def _parse_tender(self, tender: Dict) -> DetailedTender:
        """Parse tender data into DetailedTender object with extended information"""
        try:
            # Helper function to safely parse dates
            def parse_date(date_str: Optional[str]) -> Optional[datetime]:
                if date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return None

            # Helper function to safely get nested dictionary values
            def get_nested(dictionary: Dict, *keys, default=None):
                for key in keys:
                    if not isinstance(dictionary, dict):
                        return default
                    dictionary = dictionary.get(key, default)
                    if dictionary is None:
                        return default
                return dictionary

            comprador = tender.get('Comprador', {})
            fechas = tender.get('Fechas', {})
            adjudicacion = tender.get('Adjudicacion', {})
            
            # Parse items information
            items = []
            for item in tender.get('Items', {}).get('Listado', []):
                parsed_item = {
                    'correlative': item.get('Correlativo'),
                    'category_code': item.get('CodigoCategoria'),
                    'category_name': item.get('Categoria'),
                    'product_code': item.get('CodigoProducto'),
                    'product_name': item.get('NombreProducto'),
                    'description': item.get('Descripcion'),
                    'quantity': item.get('Cantidad'),
                    'unit': item.get('UnidadMedida'),
                }
                
                # Add award information if available
                if 'Adjudicacion' in item:
                    parsed_item['award'] = {
                        'supplier_tax_id': item['Adjudicacion'].get('RutProveedor'),
                        'supplier_name': item['Adjudicacion'].get('NombreProveedor'),
                        'awarded_quantity': item['Adjudicacion'].get('CantidadAdjudicada'),
                        'unit_price': item['Adjudicacion'].get('MontoUnitario')
                    }
                
                items.append(parsed_item)

            # Parse awarded suppliers
            awarded_suppliers = []
            if 'NumeroOferentes' in adjudicacion:
                awarded_suppliers = [{
                    'tax_id': get_nested(tender, 'Items', 'Listado', 'Adjudicacion', 'RutProveedor'),
                    'name': get_nested(tender, 'Items', 'Listado', 'Adjudicacion', 'NombreProveedor'),
                }]

            return DetailedTender(
                # Basic Information
                code=tender.get('CodigoExterno', ''),
                name=tender.get('Nombre', ''),
                description=tender.get('Descripcion', ''),
                status=tender.get('Estado', ''),
                status_code=tender.get('CodigoEstado', 0),
                estimated_amount=float(tender.get('MontoEstimado', 0)),
                closing_date=parse_date(tender.get('FechaCierre')),
                
                # Organization Information
                organization=comprador.get('NombreOrganismo', ''),
                organization_code=comprador.get('CodigoOrganismo', ''),
                organization_tax_id=comprador.get('RutUnidad', ''),
                buying_unit=comprador.get('NombreUnidad', ''),
                buying_unit_code=comprador.get('CodigoUnidad', ''),
                buying_unit_address=comprador.get('DireccionUnidad', ''),
                buying_unit_region=comprador.get('RegionUnidad', ''),
                buying_unit_commune=comprador.get('ComunaUnidad', ''),
                
                # Tender Details
                tender_type=tender.get('Tipo', ''),
                currency=tender.get('Moneda', ''),
                items_quantity=tender.get('Items', {}).get('Cantidad', 0),
                bidding_stages=tender.get('Etapas', 1),
                contract_type=tender.get('Contrato', 0),
                is_public_bid=tender.get('TipoConvocatoria', 0) == 1,
                
                # Dates Information
                creation_date=parse_date(fechas.get('FechaCreacion')),
                publication_date=parse_date(fechas.get('FechaPublicacion')),
                questions_deadline=parse_date(fechas.get('FechaFinal')),
                answers_publication_date=parse_date(fechas.get('FechaPubRespuestas')),
                technical_opening_date=parse_date(fechas.get('FechaActoAperturaTecnica')),
                economic_opening_date=parse_date(fechas.get('FechaActoAperturaEconomica')),
                award_date=parse_date(fechas.get('FechaAdjudicacion')),
                estimated_award_date=parse_date(fechas.get('FechaEstimadaAdjudicacion')),
                
                # Contact Information
                payment_responsible_name=tender.get('NombreResponsablePago'),
                payment_responsible_email=tender.get('EmailResponsablePago'),
                contract_responsible_name=tender.get('NombreResponsableContrato'),
                contract_responsible_email=tender.get('EmailResponsableContrato'),
                contract_responsible_phone=tender.get('FonoResponsableContrato'),
                
                # Additional Information
                allows_subcontracting=tender.get('SubContratacion', False),
                contract_duration=tender.get('TiempoDuracionContrato'),
                contract_duration_type=tender.get('TipoDuracionContrato'),
                financing_type=tender.get('FuenteFinanciamiento'),
                complaint_count=tender.get('CantidadReclamos', 0),
                items=items,
                
                # Award Information
                award_type=adjudicacion.get('Tipo'),
                award_document_number=adjudicacion.get('Numero'),
                award_document_date=parse_date(adjudicacion.get('Fecha')),
                awarded_suppliers=awarded_suppliers
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing tender details: {str(e)}")
            raise

def save_to_json(tenders: List[DetailedTender], filename: str):
    """
    Save tenders to a JSON file
    
    Args:
        tenders: List of DetailedTender objects
        filename: Name of the output JSON file
    """
    try:
        tender_list = []
        for tender in tenders:
            # Convert datetime objects to ISO format strings
            tender_dict = {
                # Basic Information
                'code': tender.code,
                'name': tender.name,
                'description': tender.description,
                'status': tender.status,
                'status_code': tender.status_code,
                'estimated_amount': tender.estimated_amount,
                'closing_date': tender.closing_date.isoformat() if tender.closing_date else None,
                
                # Organization Information
                'organization': tender.organization,
                'organization_code': tender.organization_code,
                'organization_tax_id': tender.organization_tax_id,
                'buying_unit': tender.buying_unit,
                'buying_unit_address': tender.buying_unit_address,
                'buying_unit_region': tender.buying_unit_region,
                'buying_unit_commune': tender.buying_unit_commune,
                
                # Dates
                'creation_date': tender.creation_date.isoformat() if tender.creation_date else None,
                'publication_date': tender.publication_date.isoformat() if tender.publication_date else None,
                'award_date': tender.award_date.isoformat() if tender.award_date else None,
                
                # Contact Information
                'contract_responsible_name': tender.contract_responsible_name,
                'contract_responsible_email': tender.contract_responsible_email,
                'contract_responsible_phone': tender.contract_responsible_phone,
                
                # Items and Awards
                'items': tender.items,
                'awarded_suppliers': tender.awarded_suppliers
            }
            tender_list.append(tender_dict)
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tender_list, f, ensure_ascii=False, indent=4)
            
        logging.info(f"Successfully saved {len(tenders)} tenders to {filename}")
    except Exception as e:
        logging.error(f"Error saving to JSON: {str(e)}")
        raise

def main():
    """Main execution function"""
    api = PublicMarketAPI()
    
    # Configure your search keywords here
    keywords = ['software', 'desarrollo', 'computador', 'tecnología', 'informática']
    
    try:
        # Search tenders from last 30 days
        tenders = api.search_tenders(keywords, days_back=10)
        
        # Save results to JSON
        output_filename = f"detailed_tenders_{date.today().strftime('%Y%m%d')}.json"
        save_to_json(tenders, output_filename)
        
        print(f"\nTotal tenders found: {len(tenders)}")
        for tender in tenders:
            print("\n" + "="*100)
            print(f"BASIC INFORMATION:")
            print(f"Code: {tender.code}")
            print(f"Name: {tender.name}")
            print(f"Status: {tender.status}")
            print(f"Estimated Amount: ${tender.estimated_amount:,.2f} {tender.currency}")
            
            print(f"\nORGANIZATION:")
            print(f"Organization: {tender.organization}")
            print(f"Buying Unit: {tender.buying_unit}")
            print(f"Location: {tender.buying_unit_commune}, {tender.buying_unit_region}")
            
            print(f"\nKEY DATES:")
            print(f"Publication: {tender.publication_date}")
            print(f"Closing: {tender.closing_date}")
            print(f"Award Date: {tender.award_date or 'Not awarded yet'}")
            
            print(f"\nCONTACT INFORMATION:")
            if tender.contract_responsible_name:
                print(f"Contract Manager: {tender.contract_responsible_name}")
                print(f"Contact: {tender.contract_responsible_email} / {tender.contract_responsible_phone}")
            
            print(f"\nITEMS ({len(tender.items)}):")
            for item in tender.items:
                print(f"- {item['product_name']} ({item['quantity']} {item['unit']})")
                if 'award' in item:
                    print(f"  Awarded to: {item['award']['supplier_name']}")
                    print(f"  Unit Price: ${item['award']['unit_price']:,.2f}")
            
            print("="*100)
            
    except Exception as e:
        logging.error(f"Execution error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
