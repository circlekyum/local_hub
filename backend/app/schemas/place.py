from pydantic import BaseModel, ConfigDict


class PlaceResponse(BaseModel):
    id: str
    name: str | None = None
    region: str | None = None
    category: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    tel: str | None = None

    model_config = ConfigDict(from_attributes=True)
