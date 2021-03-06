<%namespace file="../orders_items/common.mako" import="order_item_selector"/>
<%namespace file="../notes/common.mako" import="note_selector"/>
<%namespace file="../tasks/common.mako" import="task_selector"/>
<div class="dl70 easyui-dialog"
    title="${title}"
    data-options="
        modal:true,
        draggable:false,
        resizable:false,
        iconCls:'fa fa-pencil-square-o'
    ">
    ${h.tags.form(
        request.url, 
        class_="_ajax %s" % ('readonly' if readonly else ''), 
        autocomplete="off",
        hidden_fields=[
            ('csrf_token', request.session.get_csrf_token()),
        ]
    )}
        <div class="easyui-tabs h100" data-options="border:false,height:400">
            <div title="${_(u'Main')}">
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"deal date"), True, "deal_date")}
                    </div>
                    <div class="ml15">
                        ${h.fields.date_field('deal_date', item.deal_date if item else h.common.today())}
                        ${h.common.error_container(name='deal_date')}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"lead"), False, "lead_id")}
                    </div>
                    <div class="ml15">
                        ${h.fields.leads_combogrid_field(
                            request,
                            'lead_id',
                            item.lead_id if item else lead.id if lead else None,
                            show_toolbar=(not readonly if readonly else True),
                        )}
                        ${h.common.error_container(name='lead_id')}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"advertise"), True, "advsource_id")}
                    </div>
                    <div class="ml15">
                        ${h.fields.advsources_combogrid_field(
                            request,
                            'advsource_id',
                            item.advsource_id if item else lead.advsource_id if lead else None,
                            show_toolbar=(not readonly if readonly else True)
                        )}
                        ${h.common.error_container(name='advsource_id')}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"customer"), True, "customer_id")}
                    </div>
                    <div class="ml15">
                        ${h.fields.persons_combogrid_field(
                            request,
                            'customer_id',
                            item.customer_id if item else lead.customer_id if lead else None, 
                            show_toolbar=(not readonly if readonly else True)
                        )}
                        ${h.common.error_container(name="customer_id")}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"status"), True, "status")}
                    </div>
                    <div class="ml15">
                        ${h.fields.leads_statuses_combobox_field(
                            'status',
                            item.status.key if item else None
                        )}
                    </div>
                </div>
                <div class="form-field mb05">
                    <div class="dl15">
                        ${h.tags.title(_(u"description"), False, "descr")}
                    </div>
                    <div class="ml15">
                        ${h.tags.text(
            			    'descr', 
            			    item.descr if item else None, 
            			    class_="easyui-textbox w20", 
            			    data_options="multiline:true,height:80"
            			)}
                        ${h.common.error_container(name='descr')}
                    </div>
                </div>
            </div>
            <div title="${_(u'Services')}">
                <div class="easyui-panel" data-options="fit:true,border:false">
                    ${order_item_selector(
                        values=([order_item.id for order_item in item.orders_items] if item else []),
                        can_edit=(
                            not (readonly if readonly else False) and 
                            (_context.has_permision('add') if item else _context.has_permision('edit'))
                        ) 
                    )}
                </div>
            </div>
            <div title="${_(u'Notes')}">
                <div class="easyui-panel" data-options="fit:true,border:false">
                    ${note_selector(
                        values=([note.id for note in item.resource.notes] if item else []),
                        can_edit=(
                            not (readonly if readonly else False) and 
                            (_context.has_permision('add') if item else _context.has_permision('edit'))
                        ) 
                    )}
                </div>
            </div>
            <div title="${_(u'Tasks')}">
                <div class="easyui-panel" data-options="fit:true,border:false">
                    ${task_selector(
                        values=([task.id for task in item.resource.tasks] if item else []),
                        can_edit=(
                            not (readonly if readonly else False) and 
                            (_context.has_permision('add') if item else _context.has_permision('edit'))
                        ) 
                    )}
                </div>
            </div>
        </div>
        <div class="form-buttons">
            <div class="dl20 status-bar"></div>
            <div class="ml20 tr button-group">
                ${h.tags.submit('save', _(u"Save"), class_="button")}
                ${h.common.reset('cancel', _(u"Cancel"), class_="button danger")}
            </div>
        </div>
    ${h.tags.end_form()}
</div>
