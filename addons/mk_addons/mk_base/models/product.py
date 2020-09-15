# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import models, api, fields, _


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Product Brand"

    name = fields.Char(string='Name', required=True)


class ProductCategory(models.Model):
    _inherit = "product.category"

    attribute_ids = fields.Many2many('product.attribute', string='Attributes', ondelete='restrict')

    sequence_id = fields.Many2one('ir.sequence', string='Code Sequence')

    @api.multi
    def get_sequence(self):
        self.ensure_one()

        def rc(categ_id):
            if categ_id.sequence_id:
                return categ_id.sequence_id.next_by_id()
            else:
                parent_id = categ_id.parent_id
                if parent_id:
                    return rc(parent_id)
                else:
                    return ''

        return rc(self)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    @api.model
    def default_get(self, fields):
        res = super(ProductAttribute, self).default_get(fields)
        res['create_variant'] = True if self.env.user.has_group('product.group_product_variant') else False
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not self.env.user.has_group('product.group_product_variant'):
            args += [('create_variant', '=', False)]
        return super(ProductAttribute, self).name_search(name=name, args=args, operator=operator, limit=limit)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_manager = fields.Many2one('res.users', 'Product Manager')
    state = fields.Selection([('', ''),
                              ('draft', 'In Development'),
                              ('sellable', 'Normal'),
                              ('end', 'End of Lifecycle'),
                              ('obsolete', 'Obsolete')], 'Status')

    brand_id = fields.Many2one('product.brand', string='Brand')
    origin_place = fields.Char(string='Origin Place')
    color = fields.Char(string='Color')

    @api.model
    def create(self, vals):
        categ_id = self.env['product.category'].browse(vals['categ_id'])
        if categ_id:
            if 'attribute_line_ids' not in vals:
                vals['attribute_line_ids'] = [(0, False, {'attribute_id': x.id}) for x in categ_id.attribute_ids]
            if 'default_code' not in vals or not vals['default_code']:
                vals['default_code'] = categ_id.get_sequence()
        res = super(ProductTemplate, self).create(vals)
        return res

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        group_hide_product_cost = self.env.user.has_group('mk_base.group_hide_product_cost')
        group_hide_product_price = self.env.user.has_group('mk_base.group_hide_product_price')
        if group_hide_product_cost or group_hide_product_price:
            bypass_fields = []
            read_fields = []
            for field in fields:
                if group_hide_product_cost and field in ['standard_price', 'seller_ids'] \
                        or group_hide_product_price and field in ['lst_price', 'list_price', 'item_ids']:
                    bypass_fields.append(field)
                else:
                    read_fields.append(field)
            result = super(ProductTemplate, self).read(read_fields, load=load)
            for row in result:
                for bypass_field in bypass_fields:
                    row[bypass_field] = False
        else:
            result = super(ProductTemplate, self).read(fields, load=load)
        return result

    @api.multi
    def write(self, vals):
        group_hide_product_cost = self.env.user.has_group('mk_base.group_hide_product_cost')
        group_hide_product_price = self.env.user.has_group('mk_base.group_hide_product_price')
        if group_hide_product_cost or group_hide_product_price:
            for field in vals.keys():
                if group_hide_product_cost and field in ['standard_price', 'seller_ids'] \
                        or group_hide_product_price and field in ['lst_price', 'list_price', 'item_ids']:
                    vals.pop(field)
        result = super(ProductTemplate, self).write(vals)
        return result

    @api.onchange('default_code')
    def onchange_duplicate_warning(self):
        if self.active and self.default_code:
            res = self.search([('default_code', '=', self.default_code), ('active', '=', True)])
            if len(res) >= 1:
                warning = {}
                title = _("Warning")
                message = _('Duplicate Product\nDefaut Code: %s') % self.default_code
                warning['title'] = title
                warning['message'] = message
                return {'warning': warning}
        return {}


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        group_hide_product_cost = self.env.user.has_group('mk_base.group_hide_product_cost')
        group_hide_product_price = self.env.user.has_group('mk_base.group_hide_product_price')
        if group_hide_product_cost or group_hide_product_price:
            bypass_fields = []
            read_fields = []
            for field in fields:
                if group_hide_product_cost and field in ['standard_price', 'seller_ids'] \
                        or group_hide_product_price and field in ['lst_price', 'list_price', 'item_ids']:
                    bypass_fields.append(field)
                else:
                    read_fields.append(field)
            result = super(ProductProduct, self).read(read_fields, load=load)
            for row in result:
                for bypass_field in bypass_fields:
                    row[bypass_field] = False
        else:
            result = super(ProductProduct, self).read(fields, load=load)
        return result

    @api.multi
    def write(self, vals):
        group_hide_product_cost = self.env.user.has_group('mk_base.group_hide_product_cost')
        group_hide_product_price = self.env.user.has_group('mk_base.group_hide_product_price')
        if group_hide_product_cost or group_hide_product_price:
            for field in vals.keys():
                if group_hide_product_cost and field in ['standard_price', 'seller_ids'] \
                        or group_hide_product_price and field in ['lst_price', 'list_price', 'item_ids']:
                    vals.pop(field)
        result = super(ProductProduct, self).write(vals)
        return result

    @api.onchange('default_code')
    def onchange_duplicate_warning(self):
        if self.active and self.default_code:
            res = self.search([('default_code', '=', self.default_code), ('active', '=', True)])
            if len(res) >= 1:
                warning = {}
                title = _("Warning")
                message = _('Duplicate Product\nDefaut Code: %s') % self.default_code
                warning['title'] = title
                warning['message'] = message
                return {'warning': warning}
        return {}

    @api.multi
    def get_attributes_description(self):
        product = self
        variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id')
        variant = product.attribute_value_ids._variant_name(variable_attributes)
        return variant
