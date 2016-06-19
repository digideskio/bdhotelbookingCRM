# -*-coding: utf-8-*-

import logging

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from . import BaseView
from ..models import DBSession
from ..models.user import User
from ..lib.utils.common_utils import translate as _

from ..forms.users import (
    UserAddForm,
    UserEditForm,
    UserSearchForm,
)
from ..lib.events.users import (
    UserCreated,
    UserEdited,
    UserDeleted
)


log = logging.getLogger(__name__)


@view_defaults(
    context='..resources.users.UsersResource',
)
class UsersView(BaseView):

    @view_config(
        request_method='GET',
        xhr='True',
        renderer='travelcrm:templates/users/index.mako',
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
        form = UserSearchForm(self.request, self.context)
        form.validate()
        qb = form.submit()
        return {
            'total': qb.get_count(),
            'rows': qb.get_serialized()
        }

    @view_config(
        name='view',
        request_method='GET',
        renderer='travelcrm:templates/users/form.mako',
        permission='view'
    )
    def view(self):
        if self.request.params.get('rid'):
            resource_id = self.request.params.get('rid')
            user = User.by_resource_id(resource_id)
            return HTTPFound(
                location=self.request.resource_url(
                    self.context, 'view', query={'id': user.id}
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
        renderer='travelcrm:templates/users/form.mako',
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
        form = UserAddForm(self.request)
        if form.validate():
            user = form.submit()
            DBSession.add(user)
            DBSession.flush()

            event = UserCreated(self.request, user)
            self.request.registry.notify(event)

            return {
                'success_message': _(u'Saved'),
                'response': user.id
            }
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }

    @view_config(
        name='edit',
        request_method='GET',
        renderer='travelcrm:templates/users/form.mako',
        permission='edit'
    )
    def edit(self):
        user = User.get(self.request.params.get('id'))
        return {
            'item': user, 
            'title': self._get_title(_(u'Edit')),
        }

    @view_config(
        name='edit',
        request_method='POST',
        renderer='json',
        permission='edit'
    )
    def _edit(self):
        user = User.get(self.request.params.get('id'))
        form = UserEditForm(self.request)
        if form.validate():
            form.submit(user)

            event = UserEdited(self.request, user)
            self.request.registry.notify(event)

            return {
                'success_message': _(u'Saved'),
                'response': user.id
            }
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }

    @view_config(
        name='delete',
        request_method='GET',
        renderer='travelcrm:templates/users/delete.mako',
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
                items = DBSession.query(User).filter(User.id.in_(ids))
                for item in items:
                    DBSession.delete(item)
                    event = UserDeleted(self.request, item)
                    self.request.registry.notify(event)
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
