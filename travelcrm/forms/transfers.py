# -*-coding: utf-8 -*-

import colander

from . import(
    ResourceSchema, 
    BaseForm,
    BaseSearchForm,
)
from ..resources.transfers import TransfersResource
from ..models.transfer import Transfer
from ..models.note import Note
from ..models.task import Task
from ..lib.qb.transfers import TransfersQueryBuilder
from ..lib.utils.common_utils import translate as _


@colander.deferred
def name_validator(node, kw):
    request = kw.get('request')

    def validator(node, value):
        transfer = Transfer.by_name(value)
        if (
            transfer
            and str(transfer.id) != request.params.get('id')
        ):
            raise colander.Invalid(
                node,
                _(u'Transfer with the same name exists'),
            )
    return colander.All(colander.Length(max=255), validator,)


class _TransferSchema(ResourceSchema):
    name = colander.SchemaNode(
        colander.String(),
        validator=name_validator,
    )


class TransferForm(BaseForm):
    _schema = _TransferSchema

    def submit(self, transfer=None):
        context = TransfersResource(self.request)
        if not transfer:
            transfer = Transfer(
                resource=context.create_resource()
            )
        else:
            transfer.resource.notes = []
            transfer.resource.tasks = []
        transfer.name = self._controls.get('name')
        for id in self._controls.get('note_id'):
            note = Note.get(id)
            transfer.resource.notes.append(note)
        for id in self._controls.get('task_id'):
            task = Task.get(id)
            transfer.resource.tasks.append(task)
        return transfer


class TransferSearchForm(BaseSearchForm):
    _qb = TransfersQueryBuilder
