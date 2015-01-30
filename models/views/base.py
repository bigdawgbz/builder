from openerp import models, api, fields, _

__author__ = 'one'

FIELD_WIDGETS_ALL = [
    ('barchart', "FieldBarChart"),
    ('binary', "FieldBinaryFile"),
    ('boolean', "FieldBoolean"),
    ('char', "FieldChar"),
    ('char_domain', "FieldCharDomain"),
    ('date', "FieldDate"),
    ('datetime', "FieldDatetime"),
    ('email', "FieldEmail"),
    ('float', "FieldFloat"),
    ('float_time', "FieldFloat"),
    ('html', "FieldTextHtml"),
    ('image', "FieldBinaryImage"),
    ('integer', "FieldFloat"),
    ('kanban_state_selection', "KanbanSelection"),
    ('many2many', "FieldMany2Many"),
    ('many2many_binary', "FieldMany2ManyBinaryMultiFiles"),
    ('many2many_checkboxes', "FieldMany2ManyCheckBoxes"),
    ('many2many_kanban', "FieldMany2ManyKanban"),
    ('many2many_tags', "FieldMany2ManyTags"),
    ('many2one', "FieldMany2One"),
    ('many2onebutton', "Many2OneButton"),
    ('monetary', "FieldMonetary"),
    ('one2many', "FieldOne2Many"),
    ('one2many_list', "FieldOne2Many"),
    ('percentpie', "FieldPercentPie"),
    ('priority', "Priority"),
    ('progressbar', "FieldProgressBar"),
    ('radio', "FieldRadio"),
    ('reference', "FieldReference"),
    ('selection', "FieldSelection"),
    ('statinfo', "StatInfo"),
    ('statusbar', "FieldStatus"),
    ('text', "FieldText"),
    ('url', "FieldUrl"),
    ('x2many_counter', "X2ManyCounter"),
]

class ViewSelector(models.TransientModel):
    _name = 'builder.views.selector'

    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    model_id = fields.Many2one('builder.ir.model', 'Model', ondelete='cascade', required=True)
    special_states_field_id = fields.Many2one('builder.ir.model.fields', 'States Field', related='model_id.special_states_field_id')
    model_groups_date_field_ids = fields.One2many('builder.ir.model.fields', string='Has Date Fields', related='model_id.groups_date_field_ids')
    type = fields.Selection([
                                ('form', 'Form'),
                                ('tree', 'Tree'),
                                ('calendar', 'Calendar'),
                                ('gantt', 'Gantt'),
                                ('kanban', 'Kanban'),
                                ('graph', 'Graph'),
                                ('search', 'Search'),
                                ('diagram', 'Diagram'),
    ], 'Type', required=True, default='form')

    @api.multi
    def action_show_view(self):

        view_type_names = {
            'form': _('Form View View'),
            'tree': _('Tree View View'),
            'search': _('Search View View'),
            'graph': _('Graph View View'),
            'gantt': _('Gantt View View'),
            'kanban': _('Kanban View View'),
            'calendar': _('Calendar View View'),
        }

        return {
            'name': view_type_names[self.type],
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'builder.views.' + self.type,
            'views': [(False, 'form')],
            'res_id': False,
            'target': 'new',
            'context': {
                'default_model_id': self.model_id.id,
                'default_special_states_field_id': self.special_states_field_id.id,
                'default_module_id': self.model_id.module_id.id,
            },
        }


VIEW_TYPES = {
    'calendar': 'builder.views.calendar',
    'form': 'builder.views.form',
    'gantt': 'builder.views.gantt',
    'graph': 'builder.views.graph',
    'kanban': 'builder.views.kanban',
    'search': 'builder.views.search',
    'tree': 'builder.views.tree',
    'qweb': 'builder.ir.ui.view',
    'diagram': 'builder.ir.ui.view',
}

class View(models.Model):
    _name = 'builder.ir.ui.view'
    _rec_name = 'xml_id'

    _inherit = ['ir.mixin.polymorphism.superclass']

    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='CASCADE')
    model_id = fields.Many2one('builder.ir.model', ondelete='cascade')
    special_states_field_id = fields.Many2one('builder.ir.model.fields', 'States Field', related='model_id.special_states_field_id')
    model_groups_date_field_ids = fields.One2many('builder.ir.model.fields', string='Has Date Fields', related='model_id.groups_date_field_ids')

    # type = fields.Char('View Type')
    type = fields.Selection([
                                ('form', 'Form'),
                                ('tree', 'Tree'),
                                ('calendar', 'Calendar'),
                                ('gantt', 'Gantt'),
                                ('kanban', 'Kanban'),
                                ('graph', 'Graph'),
                                ('search', 'Search'),
                                ('diagram', 'Diagram'),
    ], 'Type', required=True, default='form')

    name = fields.Char('View Name', required=True)
    arch = fields.Text('Arch')
    custom_arch = fields.Boolean('Customize', default=True)
    xml_id = fields.Char('View ID', required=True)
    priority = fields.Integer('Sequence')

    inherit_id = fields.Many2one('builder.ir.ui.view', 'Inherited View', ondelete='cascade', select=True)
    inherit_children_ids = fields.One2many('builder.ir.ui.view','inherit_id', 'Inherit Views')
    field_parent = fields.Char('Child Field')

    @api.multi
    def action_open_view(self):
        model = self.pool.get(self._name)
        action = model.get_formview_action(self.env.cr, self.env.uid, self.ids, self.env.context)
        action.update({'target': 'new'})
        return action

    # @api.multi
    # def write(self, vals):
    #     vals['custom_arch'] = True
    #     return super(View, self).write(vals)
    #
    #
    # @api.model
    # @api.returns('self', lambda value: value.id)
    # def create(self, vals):
    #     vals['custom_arch'] = True
    #     return super(View, self).create(vals)

    # @api.multi
    # def _get_view_arch(self):
    #     if self._name == self.subclass_model:
    #         return self.arch
    #     else:
    #         return self.env[self.subclass_model].search(self.subclass_id)._get_view_arch()

    @api.multi
    def action_save(self):
        return {'type': 'ir.actions.act_window_close'}



class AbstractViewField(models.AbstractModel):
    _name = 'builder.views.abstract.field'

    _rec_name = 'field_id'
    _order = 'view_id, sequence'

    view_id = fields.Many2one('builder.ir.ui.view', string='Name', ondelete='cascade')
    sequence = fields.Integer('Sequence')
    field_id = fields.Many2one('builder.ir.model.fields', string='Field', required=True, ondelete='cascade')
    field_ttype = fields.Char(string='Field Type', compute='_compute_field_type')
    model_id = fields.Many2one('builder.ir.model', related='view_id.model_id', string='Model')
    special_states_field_id = fields.Many2one('builder.ir.model.fields', related='view_id.model_id.special_states_field_id', string='States Field')
    module_id = fields.Many2one('builder.ir.model', related='view_id.model_id.module_id', string='Module')


    @api.one
    @api.depends('field_id.ttype', 'view_id')
    def _compute_field_type(self):
        if self.field_id:
            self.field_ttype = self.field_id.ttype


class CustomViewAbstract(models.AbstractModel):
    _name = 'builder.views.abstract'

    @api.multi
    def action_save(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def write(self, vals):
        ret = super(CustomViewAbstract, self).write(vals)
        super(CustomViewAbstract, self).write({
            'arch': self._get_view_arch()
        })
        return ret


    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        ret = super(CustomViewAbstract, self).create(vals)
        ret.write({
            'arch': self._get_view_arch()
        })
        return ret

    @api.multi
    def _get_view_arch(self):
        if self.custom_arch:
            return self.arch
        else:
            return False