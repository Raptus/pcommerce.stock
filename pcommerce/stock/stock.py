try:
    from itertools import product
except ImportError: # python < 2.6
    def product(*args, **kwds):
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)

from persistent.dict import PersistentDict

from zope.interface import implements
from zope.component import adapts
from zope.annotation import IAnnotations

from pcommerce.core.interfaces import IProduct, IVariation

from pcommerce.stock.interfaces import IStock

ANNOTATIONS_KEY = 'pcommerce.stock'

class Stock(object):
    """ Adapter to provide stock information of a product
    """
    implements(IStock)
    adapts(IProduct)
    
    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        if not annotations.has_key(ANNOTATIONS_KEY):
            annotations[ANNOTATIONS_KEY] = PersistentDict()
        self.storage = annotations[ANNOTATIONS_KEY]
    
    def _sorted_variation_key(self, key):
        if isinstance(key, basestring):
            key = self._get_uids_from_key(key)
        if isinstance(key, tuple):
            key = list(key)
        return ''.join(sorted(key))
    
    def _get_uids_from_key(self, key):
        keys = []
        while len(key):
            keys.append(key[:32])
            key = key[32:]
        return keys
    
    def stockable(self, KEY=False):
        """ Returns a list of the stockable variation combinations of a product
        """
        variations = {}
        ids = self.context.objectIds()
        if not KEY:
            variations_by_uid = {}
        for id in ids:
            obj = self.context._getOb(id)
            if not IVariation.providedBy(obj):
                continue
            type = obj.getType()
            if not variations.has_key(type):
                variations[type] = []
            uid = obj.UID()
            if not KEY:
                variations_by_uid[uid] = obj
            variations[type].append(uid)
        if len(variations.keys()) > 1: # multiple variation types (creating cartesian product)
            comp = product(*variations.values())
            if KEY:
                return [self._sorted_variation_key(keys) for keys in comp]
            return [[variations_by_uid[uid] for uid in keys] for keys in comp]
        elif len(variations.keys()) == 1: # one variation type
            if KEY:
                return variations.values()[0]
            return [[variations_by_uid[uid],] for uid in variations.values()[0]]
        else: # no variations at all
            return None
    
    def stock(self):
        """ Overall number of items in stock
        """
        stock = 0
        keys = self.stockable(KEY=True)
        if keys is None:
            keys = [self.context.UID(),]
        for key in keys:
            stock += self.storage.get(key, 0)
        return stock
    
    def variationStock(self, variation):
        """ Number of items available of a variation or combination
            of multiple variations
        """
        if IVariation.providedBy(variation):
            stock = 0
            key = variation.UID()
            for k, v in self.storage.items():
                if key in self._get_uids_from_key(k):
                    stock += v
            return stock
        else:
            key = self._sorted_variation_key([IVariation.providedBy(v) and v.UID() or v for v in variation])
            return self.storage.get(key, 0)
    
    def setStock(self, stock):
        """ Set the overall number of items in stock
        """
        self.storage[self.context.UID()] = stock
    
    def setVariationStock(self, stock, variation):
        """ Set the number of items available of a variation or combination
            of multiple variations
        """
        if IVariation.providedBy(variation):
            key = variation.UID()
        else:
            key = self._sorted_variation_key([IVariation.providedBy(v) and v.UID() or v for v in variation])
        self.storage[key] = stock
    
    def outOfStockCheckoutAllowed(self):
        """ Returns whether checking out if this product is out of stock is allowed or not
        """
        return self.context.Schema()['outofstock_checkout'].get(self.context)
