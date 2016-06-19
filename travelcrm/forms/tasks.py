# -*-coding: utf-8 -*-

import colander

from . import (
    ResourceSchema,
    ResourceSearchSchema,
    BaseForm,
    BaseSearchForm,
    DateTime
)
from ..resources.tasks import TasksResource
from ..models.upload import Upload
from ..models.task import Task
from ..models.note import Note
from ..lib.qb.tasks import TasksQueryBuilder


class _TaskSchema(ResourceSchema):
    employee_id = colander.SchemaNode(
        colander.Integer(),
    )
    task_resource_id = colander.SchemaNode(
        colander.Integer(),
        missing=None,
    )
    title = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=2, max=128)
    )
    deadline = colander.SchemaNode(
        DateTime()
    )
    reminder = colander.SchemaNode(
        colander.Integer(),
    )
    descr = colander.SchemaNode(
        colander.String(),
    )
    status = colander.SchemaNode(
        colander.String(),
    )
    upload_id = colander.SchemaNode(
        colander.Set(),
        missing=[]
    )

    def deserialize(self, cstruct):
        if (
            'upload_id' in cstruct
            and not isinstance(cstruct.get('upload_id'), list)
        ):
            val = cstruct['upload_id']
            cstruct['upload_id'] = list()
            cstruct['upload_id'].append(val)

        return super(_TaskSchema, self).deserialize(cstruct)


class TaskSearchSchema(ResourceSearchSchema):
    performer_id = colander.SchemaNode(
        colander.Integer(),
        missing=None,
    )
    status = colander.SchemaNode(
        colander.String(),
        missing=None
    )


class TaskForm(BaseForm):
    _schema = _TaskSchema

    def submit(self, task=None):
        context = TasksResource(self.request)
        if not task:
            task = Task(
                resource=context.create_resource()
            )
        else:
            task.uploads = []
            task.resource.notes = []
        task.employee_id = self._controls.get('employee_id')
        task.title = self._controls.get('title')
        task.deadline = self._controls.get('deadline')
        task.reminder = self._controls.get('reminder')
        task.descr = self._controls.get('descr')
        task.status = self._controls.get('status')
        for id in self._controls.get('upload_id'):
            upload = Upload.get(id)
            task.uploads.append(upload)
        for id in self._controls.get('note_id'):
            note = Note.get(id)
            task.resource.notes.append(note)
        return task


class TaskSearchForm(BaseSearchForm):
    _schema = TaskSearchSchema
    _qb = TasksQueryBuilder
