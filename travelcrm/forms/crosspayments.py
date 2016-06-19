# -*-coding: utf-8 -*-

from decimal import Decimal

import colander

from . import (
    Date,
    ResourceSchema, 
    BaseForm,
    BaseSearchForm,
    ResourceSearchSchema,
)

from ..resources.crosspayments import CrosspaymentsResource
from ..models.crosspayment import Crosspayment
from ..models.subaccount import Subaccount
from ..models.cashflow import Cashflow
from ..models.note import Note
from ..models.task import Task
from ..lib.qb.crosspayments import CrosspaymentsQueryBuilder
from ..lib.bl.cashflows import get_account_balance
from ..lib.utils.common_utils import cast_int, parse_datetime
from ..lib.utils.common_utils import translate as _


@colander.deferred
def subaccount_from_validator(node, kw):
    request = kw.get('request')

    def validator(node, value):
        date = parse_datetime(request.params.get('date'))
        sum = request.params.get('sum', 0) or 0
        sum = Decimal(sum)
        subaccount = Subaccount.get(value)
        balance = get_account_balance(subaccount.account_id, None, date)
        if balance < sum:
            raise colander.Invalid(
                node,
                _(u'Max sum for transfer %s' % balance),
            )
        subaccount_to_id = cast_int(request.params.get('subaccount_to_id'))
        if not any(
            [value, subaccount_to_id]
        ):
            raise colander.Invalid(
                node,
                _(u'Set at least subaccount from any section'),
            )
    return colander.All(validator,)


@colander.deferred
def subaccount_to_validator(node, kw):
    request = kw.get('request')

    def validator(node, value):
        subaccount_id = cast_int(request.params.get('subaccount_from_id'))
        subaccount = Subaccount.get(value)
        subaccount_from = Subaccount.get(subaccount_id)
        if(
            subaccount 
            and subaccount_from 
            and (
                subaccount.account_id != subaccount_from.account_id
                or (
                    subaccount.account.currency_id 
                    != subaccount_from.account.currency.id
                )
            )
        ):
            raise colander.Invalid(
                node,
                _(u'Cashflow with same currency allowed only'),
            )
    return colander.All(validator,)


class _CrosspaymentSchema(ResourceSchema):

    date = colander.SchemaNode(
        Date(),
    )
    subaccount_from_id = colander.SchemaNode(
        colander.Integer(),
        validator=subaccount_from_validator,
        missing=None,
    )
    subaccount_to_id = colander.SchemaNode(
        colander.Integer(),
        validator=subaccount_to_validator,
        missing=None,
    )
    account_item_id = colander.SchemaNode(
        colander.Integer(),
    )
    sum = colander.SchemaNode(
        colander.Money(),
    )
    descr = colander.SchemaNode(
        colander.String(255),
        missing=None,
    )


class _CrosspaymentSearchSchema(ResourceSearchSchema):
    subaccount_from_id = colander.SchemaNode(
        colander.Integer(),
        missing=None,
    )
    subaccount_to_id = colander.SchemaNode(
        colander.Integer(),
        missing=None,
    )
    account_item_id = colander.SchemaNode(
        colander.Integer(),
        missing=None,
    )
    date_from = colander.SchemaNode(
        Date(),
        missing=None
    )
    date_to = colander.SchemaNode(
        Date(),
        missing=None
    )
    sum_from = colander.SchemaNode(
        colander.Decimal(),
        missing=None
    )
    sum_to = colander.SchemaNode(
        colander.Decimal(),
        missing=None
    )


class CrosspaymentForm(BaseForm):
    _schema = _CrosspaymentSchema

    def submit(self, crosspayment=None):
        context = CrosspaymentsResource(self.request)
        if not crosspayment:
            crosspayment = Crosspayment(
                cashflow=Cashflow(),
                resource=context.create_resource()
            )
        else:
            crosspayment.resource.notes = []
            crosspayment.resource.tasks = []
        crosspayment.descr = self._controls.get('descr')
        crosspayment.cashflow.date = self._controls.get('date')
        crosspayment.cashflow.subaccount_from_id = \
            self._controls.get('subaccount_from_id')
        crosspayment.cashflow.subaccount_to_id = \
            self._controls.get('subaccount_to_id')
        crosspayment.cashflow.account_item_id = \
            self._controls.get('account_item_id')
        crosspayment.cashflow.vat = self._controls.get('vat')
        crosspayment.cashflow.sum = self._controls.get('sum')
        for id in self._controls.get('note_id'):
            note = Note.get(id)
            crosspayment.resource.notes.append(note)
        for id in self._controls.get('task_id'):
            task = Task.get(id)
            crosspayment.resource.tasks.append(task)
        return crosspayment


class CrosspaymentSearchForm(BaseSearchForm):
    _qb = CrosspaymentsQueryBuilder
    _schema = _CrosspaymentSearchSchema
