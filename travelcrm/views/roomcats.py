# -*-coding: utf-8-*-

import logging

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from . import BaseView
from ..models import DBSession
from ..models.roomcat import Roomcat
from ..lib.utils.common_utils import translate as _

from ..forms.roomcats import (
    RoomcatForm, 
    RoomcatSearchForm
)


log = logging.getLogger(__name__)


@view_defaults(
    context='..resources.roomcats.RoomcatsResource',
)
class RoomcatsView(BaseView):

    @view_config(
        request_method='GET',
        renderer='travelcrm:templates/roomcats/index.mako',
        permission='view'
    )
    def index(self):
        return {
            'title': self._get_title(),
        }

    @view_config(
        name='list',
        xhr='True',
        request_method='POST',
        renderer='json',
        permission='view'
    )
    def list(self):
        form = RoomcatSearchForm(self.request, self.context)
        form.validate()
        qb = form.submit()
        return {
            'total': qb.get_count(),
            'rows': qb.get_serialized()
        }

    @view_config(
        name='view',
        request_method='GET',
        renderer='travelcrm:templates/roomcats/form.mako',
        permission='view'
    )
    def view(self):
        if self.request.params.get('rid'):
            resource_id = self.request.params.get('rid')
            roomcat = Roomcat.by_resource_id(resource_id)
            return HTTPFound(
                location=self.request.resource_url(
                    self.context, 'view', query={'id': roomcat.id}
                )
            )
        result = self.edit()
        result.update({
            'title': self._get_title(_(u'View')),
            'readonly': True,
        })
        return result

    @view_config(
        name='add',
        request_method='GET',
        renderer='travelcrm:templates/roomcats/form.mako',
        permission='add'
    )
    def add(self):
        return {
            'title': self._get_title(_(u'Add')),
        }

    @view_config(
        name='add',
        request_method='POST',
        renderer='json',
        permission='add'
    )
    def _add(self):
        form = RoomcatForm(self.request)
        if form.validate():
            roomcat = form.submit()
            DBSession.add(roomcat)
            DBSession.flush()
            return {
                'success_message': _(u'Saved'),
                'response': roomcat.id
            }
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }

    @view_config(
        name='edit',
        request_method='GET',
        renderer='travelcrm:templates/roomcats/form.mako',
        permission='edit'
    )
    def edit(self):
        roomcat = Roomcat.get(self.request.params.get('id'))
        return {
            'item': roomcat, 
            'title': self._get_title(_(u'Edit')),
        }

    @view_config(
        name='edit',
        request_method='POST',
        renderer='json',
        permission='edit'
    )
    def _edit(self):
        roomcat = Roomcat.get(self.request.params.get('id'))
        form = RoomcatForm(self.request)
        if form.validate():
            form.submit(roomcat)
            return {
                'success_message': _(u'Saved'),
                'response': roomcat.id
            }
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }

    @view_config(
        name='delete',
        request_method='GET',
        renderer='travelcrm:templates/roomcats/delete.mako',
        permission='delete'
    )
    def delete(self):
        return {
            'title': self._get_title(_(u'Delete')),
            'rid': self.request.params.get('rid')
        }

    @view_config(
        name='delete',
        request_method='POST',
        renderer='json',
        permission='delete'
    )
    def _delete(self):
        errors = False
        ids = self.request.params.getall('id')
        if ids:
            try:
                items = DBSession.query(Roomcat).filter(
                    Roomcat.id.in_(ids)
                )
                for item in items:
                    DBSession.delete(item)
            except:
                errors=True
                DBSession.rollback()
        if errors:
            return {
                'error_message': _(
                    u'Some objects could not be delete'
                ),
            }
        return {'success_message': _(u'Deleted')}
