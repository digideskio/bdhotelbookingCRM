# -*-coding: utf-8 -*-

import colander

from . import (
    ResourceSchema, 
    BaseForm, 
    BaseSearchForm
)
from ..resources.locations import LocationsResource
from ..models import DBSession
from ..models.location import Location
from ..models.note import Note
from ..models.task import Task
from ..lib.qb.locations import LocationsQueryBuilder
from ..lib.utils.common_utils import translate as _


@colander.deferred
def name_validator(node, kw):
    request = kw.get('request')

    def validator(node, value):
        location = (
            DBSession.query(Location)
            .filter(
                Location.region_id == request.params.get('region_id'),
                Location.name == value
            )
            .first()
        )
        if (
            location
            and (
                str(location.id) != request.params.get('id')
                or (
                    str(location.id) == request.params.get('id')
                    and request.view_name == 'copy'
                )
            )
        ):
            raise colander.Invalid(
                node,
                _(u'Location with the same name exists'),
            )
    return colander.All(colander.Length(max=128), validator,)


class _LocationSchema(ResourceSchema):
    region_id = colander.SchemaNode(
        colander.Integer(),
    )
    name = colander.SchemaNode(
        colander.String(),
        validator=name_validator
    )


class LocationForm(BaseForm):
    _schema = _LocationSchema

    def submit(self, location=None):
        context = LocationsResource(self.request)
        if not location:
            location = Location(
                resource=context.create_resource()
            )
        else:
            location.resource.notes = []
            location.resource.tasks = []
        location.name = self._controls.get('name')
        location.region_id = self._controls.get('region_id')
        for id in self._controls.get('note_id'):
            note = Note.get(id)
            location.resource.notes.append(note)
        for id in self._controls.get('task_id'):
            task = Task.get(id)
            location.resource.tasks.append(task)
        return location


class LocationSearchForm(BaseSearchForm):
    _qb = LocationsQueryBuilder
