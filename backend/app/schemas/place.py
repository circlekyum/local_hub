from pydantic import BaseModel


class PlaceResponse(BaseModel):
    name: str
    category: str
    region: str
    address: str | None = None
    latitude: float
    longitude: float
    description: str | None = None
