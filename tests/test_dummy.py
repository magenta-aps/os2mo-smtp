from mo_smtp.smtp_agent import settings
from ramqp.mo import MORouter
from ramqp.mo.models import MORoutingKey                                                
from ramqp.mo.models import ObjectType                                                  
from ramqp.mo.models import RequestType                                                 
from ramqp.mo.models import ServiceType                                                                                             
from ramqp.mo.models import PayloadType                                                 
from fastapi import FastAPI                                                             
                                                                                        
settings = Settings() 


def test_initial() -> None:
    print(settings)
    assert None is None


"""
def test_receive_creation() -> None:
    fastapi_router = APIRouter()
    async def send_events(request: RequestType) -> None:
        payload = {
            "givenname": "Jens",
            "surname": "Jensen",
            "name": "Jens Jensen",
            "nickname_givenname": "J-man",
            "nickname_surname": "van der Jee",
            "nickname": "J-man van der Jee",
            "seniority": "2017-01-02",
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
        }

        
"""
