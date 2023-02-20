from dataclasses import dataclass

@dataclass
class Product:
    id: str
    name: str
    price: float
    delete: bool
    type: str
    time: float
    imageUrl: str

@dataclass
class Item:
    name: str
    price: float
    image: str