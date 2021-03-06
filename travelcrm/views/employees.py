# -*-coding: utf-8-*-

import logging

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

from . import BaseView
from ..models import DBSession
from ..models.resource import Resource
from ..models.employee import Employee
from ..lib.helpers.fields import employees_combogrid_field
from ..lib.utils.common_utils import translate as _

from ..forms.employees import (
    EmployeeForm,
    EmployeeSearchForm
)


log = logging.getLogger(__name__)


@view_defaults(
    context='..resources.employees.EmployeesResource',
)
class EmployeesView(BaseView):

    @view_config(
        request_method='GET',
        renderer='travelcrm:templates/employees/index.mako',
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
        form = EmployeeSearchForm(self.request, self.context)
        form.validate()
        qb = form.submit()
        return {
            'total': qb.get_count(),
            'rows': qb.get_serialized()
        }

    @view_config(
        name='view',
        request_method='GET',
        renderer='travelcrm:templates/employees/form.mako',
        permission='view'
    )
    def view(self):
        if self.request.params.get('rid'):
            resource_id = self.request.params.get('rid')
            employee = Employee.by_resource_id(resource_id)
            return HTTPFound(
                location=self.request.resource_url(
                    self.context, 'view', query={'id': employee.id}
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
        renderer='travelcrm:templates/employees/form.mako',
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
        form = EmployeeForm(self.request)
        if form.validate():
            employee = form.submit()
            DBSession.add(employee)
            DBSession.flush()
            return {
                'success_message': _(u'Saved'),
                'response': employee.id
            }
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }

    @view_config(
        name='edit',
        request_method='GET',
        renderer='travelcrm:templates/employees/form.mako',
        permission='edit'
    )
    def edit(self):
        employee = Employee.get(self.request.params.get('id'))
        return {
            'item': employee, 
            'title': self._get_title(_(u'Edit')),
        }

    @view_config(
        name='edit',
        request_method='POST',
        renderer='json',
        permission='edit'
    )
    def _edit(self):
        employee = Employee.get(self.request.params.get('id'))
        form = EmployeeForm(self.request)
        if form.validate():
            form.submit(employee)
            return {
                'success_message': _(u'Saved'),
                'response': employee.id
            }
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }

    @view_config(
        name='delete',
        request_method='GET',
        renderer='travelcrm:templates/employees/delete.mako',
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
                items = DBSession.query(Employee).filter(
                    Employee.id.in_(ids)
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
        name='combobox',
        request_method='POST',
        permission='view'
    )
    def _combobox(self):
        value = None
        resource = Resource.get(self.request.params.get('resource_id'))
        if resource:
            value = resource.employee.id
        return Response(
            employees_combogrid_field(
                self.request, self.request.params.get('name'), value
            )
        )
