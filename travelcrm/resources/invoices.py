# -*-coding: utf-8 -*-
from zope.interface import implementer

from ..interfaces import (
    IResourceType,
)
from ..resources import (
    ResourceTypeBase,
)


@implementer(IResourceType)
class InvoicesResource(ResourceTypeBase):

    __name__ = 'invoices'

    @property
    def allowed_settings(self):
        return True
