# -*-coding: utf-8 -*-

import colander

from . import(
    ResourceSchema, 
    BaseForm,
    BaseSearchForm,
)
from ..resources.roomcats import RoomcatsResource
from ..models.roomcat import Roomcat
from ..models.note import Note
from ..models.task import Task
from ..lib.qb.roomcats import RoomcatsQueryBuilder
from ..lib.utils.common_utils import translate as _


@colander.deferred
def name_validator(node, kw):
    request = kw.get('request')

    def validator(node, value):
        roomcat = Roomcat.by_name(value)
        if (
            roomcat
            and str(roomcat.id) != request.params.get('id')
        ):
            raise colander.Invalid(
                node,
                _(u'Room category with the same name exists'),
            )
    return colander.All(colander.Length(max=32), validator,)


class _RoomcatSchema(ResourceSchema):
    name = colander.SchemaNode(
        colander.String(),
        validator=name_validator
    )


class RoomcatForm(BaseForm):
    _schema = _RoomcatSchema

    def submit(self, roomcat=None):
        context = RoomcatsResource(self.request)
        if not roomcat:
            roomcat = Roomcat(
                resource=context.create_resource()
            )
        else:
            roomcat.resource.notes = []
            roomcat.resource.tasks = []
        roomcat.name = self._controls.get('name')
        for id in self._controls.get('note_id'):
            note = Note.get(id)
            roomcat.resource.notes.append(note)
        for id in self._controls.get('task_id'):
            task = Task.get(id)
            roomcat.resource.tasks.append(task)
        return roomcat


class RoomcatSearchForm(BaseSearchForm):
    _qb = RoomcatsQueryBuilder
