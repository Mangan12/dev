# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    custom_desc = fields.Html('Item Description')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    custom_desc = fields.Html('Item Description')
