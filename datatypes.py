from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    delete: bool

@dataclass
class Item:
    name: str
    price: float
    image: str
