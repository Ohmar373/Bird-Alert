import requests
from typing import Optional

def get_location_name(latitude: float, longitude: float) -> str:
  
    try:
        #using an api to locate any named locations using coordinates
        url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json&zoom=18"
        headers = {'User-Agent': 'BirdAlert/1.0'}
        response = requests.get(url, headers=headers)
        
        data = response.json()
        
        
        if data.get('address'):
            address = data['address']

            def with_state(name: str) -> str:
                if address.get('state'):
                    return f"{name}, {address['state']}"
                return name

            if address.get('protected_area'):
                return with_state(address['protected_area'])
            elif address.get('national_park'):
                return with_state(address['national_park'])
            elif address.get('nature_reserve'):
                return with_state(address['nature_reserve'])
            elif address.get('park'):
                return with_state(address['park'])
            if address.get('university'):
                return with_state(address['university'])
            elif address.get('city'):
                return with_state(address['city'])
            elif address.get('town'):
                return with_state(address['town'])
            elif address.get('county'):
                return with_state(address['county'])
            elif address.get('state'):
                return address['state']
        
        return f"{latitude:.4f}, {longitude:.4f}"
        
    except Exception as e:
        #if the api is down or cant find location -> uses coordinates
        return f"{latitude:.4f}, {longitude:.4f}"
