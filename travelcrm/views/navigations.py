# -*-coding: utf-8-*-

import logging
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from . import BaseView
from ..models import DBSession
from ..models.position import Position
from ..models.navigation import Navigation
from ..lib.utils.common_utils import translate as _
from ..forms.navigations import (
    NavigationForm,
    NavigationSearchForm,
    NavigationCopyForm,
)


log = logging.getLogger(__name__)


@view_defaults(
    context='..resources.navigations.NavigationsResource',
)
class NavigationsView(BaseView):

    @view_config(
        request_method='GET',
        renderer='travelcrm:templates/navigations/index.mako',
        permission='view'
    )
    def index(self):
        position = Position.get(self.request.params.get('id'))
        return {
            'position': position,
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
        form = NavigationSearchForm(self.request, self.context)
        form.validate()
        qb = form.submit()
        return qb.get_serialized()

    @view_config(
        name='view',
        request_method='GET',
        renderer='travelcrm:templates/navigations/form.mako',
        permission='view'
    )
    def view(self):
        if self.request.params.get('rid'):
            resource_id = self.request.params.get('rid')
            navigation = Navigation.by_resource_id(resource_id)
            return HTTPFound(
                location=self.request.resource_url(
                    self.context, 'view', query={'id': navigation.id}
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
        renderer='travelcrm:templates/navigations/form.mako',
        permission='add'
    )
    def add(self):
        position = Position.get(
            self.request.params.get('position_id')
        )
        return {
            'position': position,
            'title': self._get_title(_(u'Add')),
        }

    @view_config(
        name='add',
        request_method='POST',
        renderer='json',
        permission='add'
    )
    def _add(self):
        form = NavigationForm(self.request)
        if form.validate():
            navigation = form.submit()
            DBSession.add(navigation)
            return {'success_message': _(u'Saved')}
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }

    @view_config(
        name='edit',
        request_method='GET',
        renderer='travelcrm:templates/navigations/form.mako',
        permission='edit'
    )
    def edit(self):
        navigation = Navigation.get(
            self.request.params.get('id')
        )
        position = navigation.position
        return {
            'title': self._get_title(_(u'Edit')),
            'position': position,
            'item': navigation
        }

    @view_config(
        name='edit',
        request_method='POST',
        renderer='json',
        permission='edit'
    )
    def _edit(self):
        navigation = Navigation.get(self.request.params.get('id'))
        form = NavigationForm(self.request)
        if form.validate():
            form.submit(navigation)
            return {'success_message': _(u'Saved')}
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }

    @view_config(
        name='delete',
        request_method='GET',
        renderer='travelcrm:templates/navigations/delete.mako',
        permission='delete'
    )
    def delete(self):
        return {
            'title': self._get_title(_(u'Delete')),
            'id': self.request.params.get('id')
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
                items = DBSession.query(Navigation).filter(
                    Navigation.id.in_(ids)
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

    @view_config(
        name='up',
        request_method='POST',
        renderer='json',
        permission='edit'
    )
    def _up(self):
        navigation = Navigation.get(
            self.request.params.get('id')
        )
        if navigation:
            navigation.change_sort_order('up')

    @view_config(
        name='down',
        request_method='POST',
        renderer='json',
        permission='edit'
    )
    def _down(self):
        navigation = Navigation.get(
            self.request.params.get('id')
        )
        if navigation:
            navigation.change_sort_order('down')

    @view_config(
        name='copy',
        request_method='GET',
        renderer='travelcrm:templates/navigations/copy.mako',
        permission='edit'
    )
    def copy(self):
        position = Position.get(self.request.params.get('position_id'))
        return {
            'position': position,
            'title': self._get_title(_(u'Copy')),
        }

    @view_config(
        name='copy',
        request_method='POST',
        renderer='json',
        permission='edit'
    )
    def _copy(self):
        form = NavigationCopyForm(self.request)
        if form.validate():
            form.submit()
            return {'success_message': _(u'Copied')}
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }