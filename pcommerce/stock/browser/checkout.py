from Products.statusmessages.interfaces import IStatusMessage

from zope.component import getMultiAdapter

from pcommerce.core import PCommerceMessageFactory as _
from pcommerce.core.interfaces import IShoppingCart, IOrderRegistry
from pcommerce.core.browser.checkout import Checkout as BaseCheckout
from pcommerce.core.order import ORDER_SESSION_KEY

class Checkout(BaseCheckout):
    """checkout view
    """
    def __call__(self):
        registry = IOrderRegistry(self.context)
        cart = getMultiAdapter((self.context, self.request), name='cart')
        if cart.outofstock:
            statusmessage = IStatusMessage(self.request)
            statusmessage.addStatusMessage(_(u'You have items in your cart, which are either out of stock or of which are not enough available in stock. Please adjust your cart to proceed.'), 'error')
            return self.request.RESPONSE.redirect('%s/@@cart' % self.context.absolute_url())
        return super(Checkout, self).__call__()
