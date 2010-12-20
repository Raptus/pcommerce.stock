from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName

from pcommerce.core.interfaces import IShoppingCart, IOrder, IOrderRegistry
from pcommerce.core.browser.cart import Cart as BaseCart
from pcommerce.core.browser.checkout import ORDER_SESSION_KEY
from pcommerce.core.browser.portlets.cart import Renderer as BaseRenderer
from pcommerce.core.config import CheckOut

from pcommerce.stock.utils import increaseStockFromOrder, decreaseStockFromOrder
from pcommerce.stock.interfaces import IStock

class Cart(BaseCart):
    """view of the shopping cart
    """
    template = ViewPageTemplateFile('cart.pt')

    @property
    @memoize
    def products(self):
        if not hasattr(self, 'cart'):
            self.cart = IShoppingCart(self.context)
        order = None
        if self.request.SESSION.get(ORDER_SESSION_KEY, None) is not None:
            registry = IOrderRegistry(self.context)
            order = registry.getOrder(self.request.SESSION.get(ORDER_SESSION_KEY, 0))
            if order is not None:
                increaseStockFromOrder(registry, order)
        products = self.cart.getProducts()
        uid_catalog = getToolByName(self.context, 'uid_catalog')
        for product in products:
            provider = IStock(uid_catalog(UID=product['uid'])[0].getObject())
            if not len(product['variations']):
                product['stock'] = provider.stock()
            else:
                product['stock'] = provider.variationStock([uid_catalog(UID=v['uid'])[0].getObject() for v in product['variations']])
            product['outofstock'] = product['amount'] > product['stock']
            product['checkout_allowed'] = not product['outofstock'] or provider.outOfStockCheckoutAllowed()
        if order is not None:
            decreaseStockFromOrder(registry, order)
        return products
    
    @property
    @memoize
    def outofstock(self):
        for product in self.products:
            if not product['checkout_allowed']:
                return True

class Renderer(BaseRenderer):
    @property
    def checkout(self):
        portal = getMultiAdapter((self.context, self.request), name='plone_portal_state').portal()
        cart = getMultiAdapter((portal, self.request), name='cart')
        if cart.outofstock:
            return False
        return getToolByName(self.context, 'portal_membership').checkPermission(CheckOut, self.context)
