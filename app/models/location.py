# app/models/location.py
from dataclasses import dataclass
from typing import List, Optional, Dict
import json

@dataclass
class Location:
    lat: float
    lng: float
    address: str
    city: str
    state: str
    country: str
    postal_code: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'lat': self.lat,
            'lng': self.lng,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code
        }
    
    @classmethod
    def from_foursquare_data(cls, data: Dict) -> 'Location':
        """Create Location from Foursquare API response"""
        geocodes = data.get('geocodes', {}).get('main', {})
        location_data = data.get('location', {})
        
        return cls(
            lat=geocodes.get('latitude', 0.0),
            lng=geocodes.get('longitude', 0.0),
            address=location_data.get('formatted_address', ''),
            city=location_data.get('locality', ''),
            state=location_data.get('region', ''),
            country=location_data.get('country', ''),
            postal_code=location_data.get('postcode')
        )

@dataclass
class Business:
    fsq_id: str
    name: str
    location: Location
    categories: List[str]
    rating: Optional[float] = None
    popularity: Optional[float] = None
    price: Optional[int] = None
    hours: Optional[Dict] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'fsq_id': self.fsq_id,
            'name': self.name,
            'location': self.location.to_dict(),
            'categories': self.categories,
            'rating': self.rating,
            'popularity': self.popularity,
            'price': self.price,
            'hours': self.hours,
            'website': self.website,
            'phone': self.phone
        }
    
    @classmethod
    def from_foursquare_data(cls, data: Dict) -> 'Business':
        """Create Business from Foursquare API response"""
        location = Location.from_foursquare_data(data)
        categories = [cat.get('name', '') for cat in data.get('categories', [])]
        
        return cls(
            fsq_id=data.get('fsq_id', ''),
            name=data.get('name', ''),
            location=location,
            categories=categories,
            rating=data.get('rating'),
            popularity=data.get('popularity'),
            price=data.get('price'),
            hours=data.get('hours'),
            website=data.get('website'),
            phone=data.get('tel')
        )