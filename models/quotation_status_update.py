# -*- coding: utf-8 -*-
from odoo import models, api


class QuotationUpdate(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(QuotationUpdate, self).action_confirm()
        for order in self:
            if order.opportunity_id:
                lead = order.opportunity_id
                won_stage = self.env['crm.stage'].search([('name', '=', 'Won')], limit=1)
                if won_stage:
                    lead.stage_id = won_stage.id
        return res

    def get_l1_image(self):
        product = self.order_line.product_id[:1]
        if product.image_1920:
            return f"/web/image/product.product/{product.id}/image_1920"
        return "/web/static/src/img/placeholder.png"

    def get_l1_name(self):
        product = self.order_line.product_id[:1]
        return product.name

    def _get_prod_descr(self, prod_id):
        return prod_id.custom_desc if prod_id.custom_desc else prod_id.product_tmpl_id.custom_desc

    def get_default_l2(self):
        data = list()

        # FORMAT
        # [SECTION=1/0, SR_NO, PRODUCT, QTY, UNIT_PRICE, TAX, SUBTOTAL, DESCR]

        # L1
        sr_no = 1
        l1_id = self.order_line.filtered(lambda p: p.product_id.item_type == 'l1')
        if not l1_id:
            return data
        else:
            qty = str(l1_id.product_uom_qty) + ' ' + str(l1_id.product_uom.name)
            taxes = l1_id.tax_id.mapped('name') or ''
            tax_names = ', '.join(taxes)
            l1_desc = self._get_prod_descr(l1_id.product_id)
            l1_line = [0, sr_no, l1_id.name, qty, l1_id.price_unit, tax_names, l1_id.price_subtotal, l1_desc]
            data.append(l1_line)
            sr_no += 1

        # L2 DEFAULT
        bom_id = self.env['mrp.bom'].search([('product_tmpl_id', '=', l1_id.product_id.product_tmpl_id.id)])
        if not bom_id:
            return data
        default_l2_ids = bom_id.bom_line_ids.filtered(lambda p: p.product_type == 'mandatory')
        if not default_l2_ids:
            return data
        for l2_id in default_l2_ids:
            l2_desc = self._get_prod_descr(l2_id.product_id)
            l2_line = [0, sr_no, l2_id.product_id.name, l2_id.product_qty, '', '', '', l2_desc]
            data.append(l2_line)
            sr_no += 1
        # L2 OPTIONAL MANDATORY
        mand_header = [1, 'SELECTABLE/ MANDATORY PRODUCTS']
        data.append(mand_header)
        mand_l2 = l1_id.product_id.product_template_variant_value_ids
        for attr in mand_l2:
            attr_name = attr.attribute_id.name + ' - ' + attr.name
            l2_mand_line = [0, sr_no, attr_name, '', '', '', '', '']
            data.append(l2_mand_line)
            sr_no += 1

        # L2 OPTIONAL
        opt_header = [1, 'OPTIONAL PRODUCTS']
        data.append(opt_header)
        opt_l2_ids = self.order_line.filtered(lambda p: p.product_id.item_type != 'l1')
        for opt_l2 in opt_l2_ids:
            opt_l2_qty = str(opt_l2.product_uom_qty) + ' ' + str(opt_l2.product_uom.name)
            opt_l2_taxes = opt_l2.tax_id.mapped('name') or ''
            opt_l2tax_names = ', '.join(opt_l2_taxes)
            opt_l2_desc = self._get_prod_descr(opt_l2.product_id)
            opt_l2_line = [0, sr_no, opt_l2.name, opt_l2_qty, opt_l2.price_unit, opt_l2tax_names, opt_l2.price_subtotal, opt_l2_desc]
            data.append(opt_l2_line)
            sr_no += 1
        return data

