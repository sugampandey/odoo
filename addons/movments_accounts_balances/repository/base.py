from typing import Any, Dict, List, Optional, Union
from odoo import models

class BaseOdooService:
    def __init__(self, env):
        self.env = env

    def _get_model(self) -> models.Model:
        raise NotImplementedError("Model name must be defined in child class")

    def create(self, values: Dict[str, Any]) -> models.Model:
        model = self._get_model()
        return model.create(values)
    
    def browse(self, record_ids: Union[int, List[int]]) -> Union[models.Model, List[models.Model]]:
        model = self._get_model()
        return model.browse(record_ids)

    def read(self, record_id: int, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        model = self._get_model()
        record = model.browse(record_id)
        if fields:
            return record.read(fields)[0]
        return record.read()[0]

    def search(self, domain: List, offset: int = 0, limit: Optional[int] = None,
               order: Optional[str] = None, count=False) -> List[int]:
        model = self._get_model()
        return model.search(
            domain=domain,
            offset=offset,
            limit=limit,
            order=order,
            count=count
        )

    def search_read(self, domain: List, fields: Optional[List[str]] = None, 
                   offset: int = 0, limit: Optional[int] = None, 
                   order: Optional[str] = None) -> List[Dict[str, Any]]:
        model = self._get_model()
        return model.search_read(
            domain=domain,
            fields=fields,
            offset=offset,
            limit=limit,
            order=order
        )
    
    
    def search_count(self, domain: List) -> int:
        model = self._get_model()
        return model.search_count(domain)

    def update(self, record_id: int, values: Dict[str, Any]) -> bool:
        model = self._get_model()
        record = model.browse(record_id)
        return record.write(values)

    def delete(self, record_id: int) -> bool:
        model = self._get_model()
        record = model.browse(record_id)
        return record.unlink()


