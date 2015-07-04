# This file is part of the stock_shipment_update_product_cost_price module for
# Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal

from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
__all__ = ['ShipmentIn', 'ShipmentInReturn']

__metaclass__ = PoolMeta


class ShipmentIn:
    __name__ = 'stock.shipment.in'

    @classmethod
    def receive(cls, shipments):
        cls._update_product_cost_price(shipments)
        with Transaction().set_context(update_product_cost_price=False):
            super(ShipmentIn, cls).receive(shipments)

    @classmethod
    def _update_product_cost_price(cls, shipments):
        """
        Update the cost price on the products of the given shipments.
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Product = pool.get('product.product')
        ProductTemplate = pool.get('product.template')
        Location = pool.get('stock.location')
        Currency = pool.get('currency.currency')
        Date = pool.get('ir.date')

        context = {}
        locations = Location.search([
                ('type', '=', 'storage'),
                ])
        context['locations'] = [l.id for l in locations]
        context['stock_date_end'] = Date.today()
        products = list(set([m.product for s in shipments for m in
            s.incoming_moves if m.product.cost_price_method == 'average']))
        if not products:
            return

        with Transaction().set_context(context):
            product_qty = Product.get_quantity(products, 'quantity')
        product_cost_qty = {p.id:
            p.cost_price * Decimal(str(product_qty[p.id])) for p in products}

        for s in shipments:
            for m in s.incoming_moves:
                if (m.from_location.type not in ('supplier', 'production')
                        or m.to_location.type != 'storage'
                        or m.product.cost_price_method != 'average'):
                            continue

                qty = Uom.compute_qty(m.uom, m.quantity, m.product.default_uom)

                # convert wrt currency
                with Transaction().set_context(date=m.effective_date):
                    unit_price = Currency.compute(m.currency, m.unit_price,
                        m.company.currency, round=False)
                # convert wrt to the uom
                unit_price = Uom.compute_price(m.uom, unit_price,
                    m.product.default_uom)

                product_qty[m.product.id] += qty
                product_cost_qty[m.product.id] += (unit_price *
                    Decimal(str(qty)))

        cost_prices = []
        if hasattr(Product, 'cost_price'):
            digits = Product.cost_price.digits
            for p in products:
                if product_qty[p.id] != Decimal('0.0'):
                    new_cost_price = (product_cost_qty[p.id] /
                        Decimal(str(product_qty[p.id])))
                    new_cost_price = new_cost_price.quantize(
                        Decimal(str(10.0 ** -digits[1])))
                    cost_prices.extend(([p], {
                        'cost_price': new_cost_price,
                        }))
            Product.write(*cost_prices)
        else:
            digits = ProductTemplate.cost_price.digits
            for p in products:
                if product_qty[p.id] != Decimal('0.0'):
                    new_cost_price = (product_cost_qty[p.id] /
                        Decimal(str(product_qty[p.id])))
                    new_cost_price = new_cost_price.quantize(
                        Decimal(str(10.0 ** -digits[1])))
                    cost_prices.extend(([p.template], {
                        'cost_price': new_cost_price,
                        }))
            ProductTemplate.write(*cost_prices)


class ShipmentInReturn:
    __name__ = 'stock.shipment.in.return'

    @classmethod
    def done(cls, shipments):
        cls._update_product_cost_price(shipments)
        with Transaction().set_context(update_product_cost_price=False):
            super(ShipmentInReturn, cls).done(shipments)

    @classmethod
    def _update_product_cost_price(cls, shipments):
        """
        Update the cost price on the products of the given shipments.
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Product = pool.get('product.product')
        ProductTemplate = pool.get('product.template')
        Location = pool.get('stock.location')
        Currency = pool.get('currency.currency')
        Date = pool.get('ir.date')

        context = {}
        locations = Location.search([
                ('type', '=', 'storage'),
                ])
        context['locations'] = [l.id for l in locations]
        context['stock_date_end'] = Date.today()
        products = list(set([m.product for s in shipments for m in
            s.moves if m.product.cost_price_method == 'average']))
        if not products:
            return

        with Transaction().set_context(context):
            product_qty = Product.get_quantity(products, 'quantity')
        product_cost_qty = {p.id:
            p.cost_price * Decimal(str(product_qty[p.id])) for p in products}

        for s in shipments:
            for m in s.moves:
                if (m.to_location.type != 'supplier'
                        or m.from_location.type != 'storage'
                        or m.product.cost_price_method != 'average'):
                    continue

                qty = Uom.compute_qty(m.uom, -m.quantity,
                    m.product.default_uom)

                # convert wrt currency
                with Transaction().set_context(date=m.effective_date):
                    unit_price = Currency.compute(m.currency, m.unit_price,
                        m.company.currency, round=False)
                # convert wrt to the uom
                unit_price = Uom.compute_price(m.uom, unit_price,
                    m.product.default_uom)

                product_qty[m.product.id] += qty
                product_cost_qty[m.product.id] += (unit_price *
                    Decimal(str(qty)))

        cost_prices = []
        if hasattr(Product, 'cost_price'):
            digits = Product.cost_price.digits
            for p in products:
                if product_qty[p.id] != Decimal('0.0'):
                    new_cost_price = (product_cost_qty[p.id] /
                        Decimal(str(product_qty[p.id])))
                    new_cost_price = new_cost_price.quantize(
                        Decimal(str(10.0 ** -digits[1])))
                    cost_prices.extend(([p], {
                        'cost_price': new_cost_price,
                        }))
            Product.write(*cost_prices)
        else:
            digits = ProductTemplate.cost_price.digits
            for p in products:
                if product_qty[p.id] != Decimal('0.0'):
                    new_cost_price = (product_cost_qty[p.id] /
                        Decimal(str(product_qty[p.id])))
                    new_cost_price = new_cost_price.quantize(
                        Decimal(str(10.0 ** -digits[1])))
                    cost_prices.extend(([p.template], {
                        'cost_price': new_cost_price,
                        }))
            ProductTemplate.write(*cost_prices)
