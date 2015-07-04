stock_shipment_update_product_cost_price Module
###############################################

The stock_shipment_update_product_cost_price module updates product cost prices
more efficient when a supplier shipment is received or a return supplier
shipment is done.

It computes the new cost prices for the products of the whole shipment (if the
product has the Average cost price method selected) instead of computing it for
the single product in each stock move.
