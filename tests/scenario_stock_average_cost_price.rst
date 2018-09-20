========================
Stock Average Cost Price
========================

=============
General Setup
=============

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install stock Module::

    >>> Module = Model.get('ir.module')
    >>> modules = Module.find([('name', '=', 'stock')])
    >>> Module.install([x.id for x in modules], config.context)
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create supplier::

    >>> Party = Model.get('party.party')
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()

Create category::

    >>> ProductCategory = Model.get('product.category')
    >>> category = ProductCategory(name='Category')
    >>> category.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'Product'
    >>> template.category = category
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('300')
    >>> template.cost_price = Decimal('80')
    >>> template.cost_price_method = 'average'
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Get stock locations::

    >>> Location = Model.get('stock.location')
    >>> warehouse_loc, = Location.find([('code', '=', 'WH')])
    >>> supplier_loc, = Location.find([('code', '=', 'SUP')])
    >>> input_loc, = Location.find([('code', '=', 'IN')])
    >>> storage_loc, = Location.find([('code', '=', 'STO')])

Create Shipment In::

    >>> ShipmentIn = Model.get('stock.shipment.in')
    >>> shipment_in = ShipmentIn()
    >>> shipment_in.supplier = supplier
    >>> shipment_in.planned_date = today
    >>> shipment_in.supplier = supplier
    >>> shipment_in.warehouse = warehouse_loc
    >>> shipment_in.save()

Add a shipment line with 2 units with price 100::

    >>> StockMove = Model.get('stock.move')
    >>> move = StockMove()
    >>> move.product = product
    >>> move.uom = unit
    >>> move.quantity = 2
    >>> move.from_location = supplier_loc
    >>> move.to_location = input_loc
    >>> move.unit_price = Decimal('100')
    >>> move.shipment = shipment_in
    >>> move.save()

Set the shipment state to waiting::

    >>> ShipmentIn.receive([shipment_in.id], config.context)

Check Cost Price is 100::

    >>> product.reload()
    >>> product.template.cost_price
    Decimal('100.0000')
    >>> ShipmentIn.done([shipment_in.id], config.context)

Create Shipment In::

    >>> ShipmentIn = Model.get('stock.shipment.in')
    >>> shipment_in = ShipmentIn()
    >>> shipment_in.supplier = supplier
    >>> shipment_in.planned_date = today
    >>> shipment_in.supplier = supplier
    >>> shipment_in.warehouse = warehouse_loc

Add two shipment lines of 1 unit of product with price 50::

    >>> StockMove = Model.get('stock.move')
    >>> shipment_in.incoming_moves.extend([StockMove(), StockMove()])
    >>> for move in shipment_in.incoming_moves:
    ...     move.product = product
    ...     move.uom =unit
    ...     move.quantity = 1
    ...     move.from_location = supplier_loc
    ...     move.to_location = input_loc
    ...     move.unit_price = Decimal('50')
    >>> shipment_in.save()

Set the shipment state to waiting::

    >>> ShipmentIn.receive([shipment_in.id], config.context)

Check Cost Price is 75::

    >>> product.reload()
    >>> product.template.cost_price
    Decimal('75.0000')
    >>> ShipmentIn.done([shipment_in.id], config.context)

Create Shipment In Return::

    >>> ShipmentInReturn = Model.get('stock.shipment.in.return')
    >>> shipment_in_r = ShipmentInReturn()
    >>> shipment_in_r.supplier = supplier
    >>> shipment_in_r.planned_date = today
    >>> shipment_in_r.from_location = storage_loc
    >>> shipment_in_r.to_location = supplier_loc

Add two shipment lines of 1 unit of product with price 50::

    >>> StockMove = Model.get('stock.move')
    >>> shipment_in_r.moves.extend([StockMove(), StockMove()])
    >>> for move in shipment_in_r.moves:
    ...     move.product = product
    ...     move.uom =unit
    ...     move.quantity = 1
    ...     move.from_location = storage_loc
    ...     move.to_location = supplier_loc
    ...     move.unit_price = Decimal('50')
    >>> shipment_in_r.save()

Set the shipment state to waiting, assign and done::

    >>> ShipmentInReturn.wait([shipment_in_r.id], config.context)
    >>> ShipmentInReturn.assign_try([shipment_in_r.id], config.context)
    True
    >>> ShipmentInReturn.done([shipment_in_r.id], config.context)

Check Cost Price is 100::

    >>> product.reload()
    >>> product.template.cost_price
    Decimal('100.0000')

Create Shipment In Return::

    >>> shipment_in_r = ShipmentInReturn()
    >>> shipment_in_r.supplier = supplier
    >>> shipment_in_r.planned_date = today
    >>> shipment_in_r.from_location = storage_loc
    >>> shipment_in_r.to_location = supplier_loc
    >>> shipment_in_r.save()

Add a shipment line with 2 units with price 300::

    >>> move = StockMove()
    >>> move.product = product
    >>> move.uom = unit
    >>> move.quantity = 2
    >>> move.from_location = storage_loc
    >>> move.to_location = supplier_loc
    >>> move.unit_price = Decimal('300')
    >>> move.shipment = shipment_in_r
    >>> move.save()

Set the shipment state to waiting, assign and done::

    >>> ShipmentInReturn.wait([shipment_in_r.id], config.context)
    >>> ShipmentInReturn.assign_try([shipment_in_r.id], config.context)
    True
    >>> ShipmentInReturn.done([shipment_in_r.id], config.context)

Check Cost Price is 100 (because product stock is zero)::

    >>> product.reload()
    >>> product.template.cost_price
    Decimal('100.0000')
