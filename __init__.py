# This file is part of the stock_shipment_update_product_cost_price module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .shipment import *
from .move import *


def register():
    Pool.register(
        ShipmentIn,
        ShipmentInReturn,
        Move,
        module='stock_shipment_update_product_cost_price', type_='model')
