from pydantic import BaseModel, ConfigDict


class CategoriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_categoria: int
    nombre: str
