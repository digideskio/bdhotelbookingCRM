# -*-coding: utf-8 -*-

import colander

from . import (
    DateTime,
)
from ..forms.orders_items import (
    OrderItemSchema, 
    OrderItemForm
)
from ..resources.tickets import TicketsResource
from ..models.ticket import Ticket
from ..models.person import Person
from ..lib.utils.common_utils import cast_int
from ..lib.utils.common_utils import translate as _


@colander.deferred
def adults_validator(node, kw):
    request = kw.get('request')

    def validator(node, value):
        if (value + int(cast_int(request.params.get('children')))) == 0:
            raise colander.Invalid(
                node,
                _(u'Adult or Children must be more than 0'),
            )
    return validator


class _TicketSchema(OrderItemSchema):
    adults = colander.SchemaNode(
        colander.Integer(),
        validator=adults_validator,
    )
    children = colander.SchemaNode(
        colander.Integer(),
    )
    start_location_id = colander.SchemaNode(
        colander.Integer(),
    )
    end_location_id = colander.SchemaNode(
        colander.Integer(),
    )
    ticket_class_id = colander.SchemaNode(
        colander.Integer(),
    )
    transport_id = colander.SchemaNode(
        colander.Integer(),
    )
    start_additional_info = colander.SchemaNode(
        colander.String(),
        missing=None,
        validator=colander.Length(max=128),
    )
    end_additional_info = colander.SchemaNode(
        colander.String(),
        missing=None,
        validator=colander.Length(max=128),
    )
    start_dt = colander.SchemaNode(
        DateTime()
    )
    end_dt = colander.SchemaNode(
        DateTime()
    )
    descr = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=255),
        missing=None
    )


class TicketForm(OrderItemForm):
    _schema = _TicketSchema

    def submit(self, ticket=None):
        order_item = super(TicketForm, self).submit(ticket and ticket.order_item)
        context = TicketsResource(self.request)
        if not ticket:
            ticket = Ticket(
                resource=context.create_resource()
            )
        ticket.order_item = order_item
        ticket.adults = self._controls.get('adults')
        ticket.children = self._controls.get('children')
        ticket.start_location_id = self._controls.get('start_location_id')
        ticket.end_location_id = self._controls.get('end_location_id')
        ticket.start_dt = self._controls.get('start_dt')
        ticket.end_dt = self._controls.get('end_dt')
        ticket.ticket_class_id = self._controls.get('ticket_class_id')
        ticket.transport_id = self._controls.get('transport_id')
        ticket.start_additional_info = self._controls.get('start_additional_info')
        ticket.end_additional_info = self._controls.get('end_additional_info')

        ticket.descr = self._controls.get('descr')

        for id in self._controls.get('person_id'):
            person = Person.get(id)
            ticket.order_item.persons.append(person)
        return ticket
