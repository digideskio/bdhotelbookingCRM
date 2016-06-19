# -*-coding: utf-8 -*-

import colander

from . import (
    ResourceSchema, 
    BaseForm, 
    BaseSearchForm
)
from ..resources.addresses import AddressesResource
from ..models.address import Address
from ..lib.qb.addresses import AddressesQueryBuilder


class _AddressSchema(ResourceSchema):
    location_id = colander.SchemaNode(
        colander.Integer(),
    )
    zip_code = colander.SchemaNode(
        colander.String()
    )
    address = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=2, max=255)
    )


class AddressForm(BaseForm):
    _schema = _AddressSchema

    def submit(self, address=None):
        context = AddressesResource(self.request)
        if not address:
            address = Address(
                resource=context.create_resource()
            )
        address.location_id = self._controls.get('location_id')
        address.zip_code = self._controls.get('zip_code')
        address.address = self._controls.get('address')
        return address


class AddressSearchForm(BaseSearchForm):
    _qb = AddressesQueryBuilder
