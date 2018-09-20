# This file is part of the stock_shipment_update_product_cost_price module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import shipment
from . import move


def register():
    Pool.register(
        shipment.ShipmentIn,
        shipment.ShipmentInReturn,
        move.Move,
        module='stock_shipment_update_product_cost_price', type_='model')
