# This file is part of the stock_shipment_update_product_cost_price module for
# Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.transaction import Transaction
from trytond.pool import PoolMeta
__all__ = ['Move']

__metaclass__ = PoolMeta


class Move:
    __name__ = 'stock.move'

    def _update_product_cost_price(self, direction):
        if not Transaction().context.get('update_product_cost_price'):
            return
        super(Move, self)._update_product_cost_price(direction)
