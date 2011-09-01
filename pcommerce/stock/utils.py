from Products.CMFCore.utils import getToolByName

from pcommerce.core.config import INITIALIZED, CANCELED, FAILED, SENT, PROCESSED
from pcommerce.core.interfaces import IOrderSentEvent, ISteps, IRequiredComponents, IOrderCanceledEvent, IOrderProcessingSuccessfulEvent
from pcommerce.stock.interfaces import IStock

INCREASED = 1
DECREASED = 2

def decreaseStockFromOrder(registry, order):
    if getattr(order, 'stock_state', 0) is DECREASED:
        return
    uid_catalog = getToolByName(registry.context, 'uid_catalog')
    for product in order.products:
        stock = IStock(uid_catalog(UID=product[0])[0].getObject())
        if len(product[5]): # we have variations
            variations = [v[0] for v in product[5]]
            stock.setVariationStock(stock.variationStock(variations)-product[3], variations)
        else:
            stock.setStock(stock.stock()-product[3])
    order.stock_state = DECREASED

def decreaseStockFromOrderSubscriber(event):
    order = event.order
    if not (order.state is INITIALIZED or \
            (IOrderSentEvent.providedBy(event) and order.state is CANCELED) or \
            IOrderProcessingSuccessfulEvent.providedBy(event)):
        return
    decreaseStockFromOrder(event.registry, event.order)

def increaseStockFromOrder(registry, order):
    if getattr(order, 'stock_state', 0) is INCREASED:
        return
    uid_catalog = getToolByName(registry.context, 'uid_catalog')
    for product in order.products:
        stock = IStock(uid_catalog(UID=product[0])[0].getObject())
        if len(product[5]): # we have variations
            variations = [v[0] for v in product[5]]
            stock.setVariationStock(stock.variationStock(variations)+product[3], variations)
        else:
            stock.setStock(stock.stock()+product[3])
    order.stock_state = INCREASED

def increaseStockFromOrderSubscriber(event):
    order = event.order
    if order.state in (FAILED, CANCELED,):
        return
    if IOrderCanceledEvent.providedBy(event) and order.state is INITIALIZED:
        # if we have a cancel event check if the order is in the payment process
        # and if so do not increase the stock as the event was fired by the session
        # timeout and the payment might be successfully processed, if not the payment
        # process will send a payment failed event which then will increase the stock
        steps = list(ISteps(event.registry.context))
        components = []
        for step in range(0, len(steps)):
            if not step in order.processed_steps:
                components.extend(steps[step]['components'])
        required = IRequiredComponents(event.registry.context)
        definite = True
        for component in required:
            if component in components:
                definite = False
                break
        if definite:
            return
    increaseStockFromOrder(event.registry, event.order)
