from pydantic import BaseModel
from typing import Optional

class EmailExtraction(BaseModel):
    id: str
    product_line: str
    incoterm : str
    origin_port_code: str
    origin_port_name: str
    destination_port_code: str
    destination_port_name: str
    cargo_weight_kg: Optional[float]
    cargo_cbm: Optional[float]
    is_dangerous: bool = False