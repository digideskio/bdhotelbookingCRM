# -*-coding: utf-8-*-

import logging

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from . import BaseView
from ..models import DBSession
from ..models.supplier_type import SupplierType
from ..lib.utils.common_utils import translate as _

from ..forms.suppliers_types import (
    SupplierTypeForm, 
    SupplierTypeSearchForm
)


log = logging.getLogger(__name__)


@view_defaults(
    context='..resources.suppliers_types.SuppliersTypesResource',
)
class SuppliersTypesView(BaseView):

    @view_config(
        request_method='GET',
        renderer='travelcrm:templates/suppliers_types/index.mako',
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
        form = SupplierTypeSearchForm(self.request, self.context)
        form.validate()
        qb = form.submit()
        return {
            'total': qb.get_count(),
            'rows': qb.get_serialized()
        }

    @view_config(
        name='view',
        request_method='GET',
        renderer='travelcrm:templates/suppliers_types/form.mako',
        permission='view'
    )
    def view(self):
        if self.request.params.get('rid'):
            resource_id = self.request.params.get('rid')
            supplier_type = SupplierType.by_resource_id(resource_id)
            return HTTPFound(
                location=self.request.resource_url(
                    self.context, 'view', query={'id': supplier_type.id}
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
        renderer='travelcrm:templates/suppliers_types/form.mako',
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
        form = SupplierTypeForm(self.request)
        if form.validate():
            supplier_type = form.submit()
            DBSession.add(supplier_type)
            DBSession.flush()
            return {
                'success_message': _(u'Saved'),
                'response': supplier_type.id
            }
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }

    @view_config(
        name='edit',
        request_method='GET',
        renderer='travelcrm:templates/suppliers_types/form.mako',
        permission='edit'
    )
    def edit(self):
        supplier_type = SupplierType.get(self.request.params.get('id'))
        return {
            'item': supplier_type, 
            'title': self._get_title(_(u'Edit')),
        }

    @view_config(
        name='edit',
        request_method='POST',
        renderer='json',
        permission='edit'
    )
    def _edit(self):
        supplier_type = SupplierType.get(self.request.params.get('id'))
        form = SupplierTypeForm(self.request)
        if form.validate():
            form.submit(supplier_type)
            return {
                'success_message': _(u'Saved'),
                'response': supplier_type.id
            }
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }

    @view_config(
        name='delete',
        request_method='GET',
        renderer='travelcrm:templates/suppliers_types/delete.mako',
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
                items = DBSession.query(SupplierType).filter(
                    SupplierType.id.in_(ids)
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
