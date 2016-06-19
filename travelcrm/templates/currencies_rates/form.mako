<%namespace file="../notes/common.mako" import="note_selector"/>
<%namespace file="../tasks/common.mako" import="task_selector"/>
<div class="dl60 easyui-dialog"
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
        hidden_fields=[('csrf_token', request.session.get_csrf_token())]
    )}
        <div class="easyui-tabs" data-options="border:false,height:400">
            <div title="${_(u'Main')}">
                 <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"date"), True, "date")}
                    </div>
                    <div class="ml15">
                        ${h.fields.date_field('date', item.date if item else h.common.today())}
                        ${h.common.error_container(name='date')}
                    </div>
                </div>
               <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"currency"), True, "currency_id")}
                    </div>
                    <div class="ml15">
                        ${h.fields.currencies_combogrid_field(
                            request,
                            'currency_id',
                            item.currency_id if item else None,
                            show_toolbar=(not readonly if readonly else True)
                        )}
                        ${h.common.error_container(name='currency_id')}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"supplier"), True, "supplier_id")}
                    </div>
                    <div class="ml15">
                        ${h.fields.suppliers_combogrid_field(
                            request,
                            'supplier_id',
                            item.supplier_id if item else None,
                            show_toolbar=(not readonly if readonly else True)
                        )}
                        ${h.common.error_container(name='supplier_id')}
                    </div>
                </div>
                <div class="form-field mb05">
                    <div class="dl15">
                        ${h.tags.title(_(u"rate"), True, "rate")}
                    </div>
                    <div class="ml15">
                        ${h.tags.text('rate', item.rate if item else None, class_="easyui-textbox w20 easyui-numberbox", data_options="min:0,precision:4")}
                        ${h.common.error_container(name='rate')}
                    </div>
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
