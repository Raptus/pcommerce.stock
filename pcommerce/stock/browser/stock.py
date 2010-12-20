from Acquisition import aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _p

from plone.memoize.instance import memoize

from pcommerce.core import PCommerceMessageFactory as _
from pcommerce.core.interfaces import IVariation, IProduct
from pcommerce.stock.interfaces import IStock

class Stock(BrowserView):
    """ View providing functionality to manage the stock of a product
    """
    template = ViewPageTemplateFile('stock.pt')

    def __call__(self):
        self.errors = {}
        if self.request.form.get('stock.submitted', None) is not None:
            from Products.statusmessages.interfaces import IStatusMessage
            statusmessage = IStatusMessage(self.request)
            if self.store():
                statusmessage.add(_(u'Stock information successfully stored'))
                return self.request.RESPONSE.redirect('%s/@@stock' % self.context.absolute_url())
            else:
                statusmessage.add(_(u'Failed to save some stock information'), u'error')
        return self.template()
    
    @memoize
    def stockable(self):
        provider = IStock(self.context)
        raw = provider.stockable()
        result = []
        if raw is None:
            result.append({'title': self.context.Title(),
                           'key': self.context.UID(),
                           'value': provider.stock()})
        else:
            for items in raw:
                stockable = {'objs': items,
                             'title': [],
                             'key': [],
                             'value': provider.variationStock(items)}
                for item in items:
                    stockable['key'].append(item.UID())
                    stockable['title'].append(item.Title())
                stockable['key'] = '_'.join(stockable['key'])
                stockable['title'] = ', '.join(stockable['title'])
                result.append(stockable)
        return result
    
    def store(self):
        provider = IStock(self.context)
        stockable = self.stockable()
        for item in stockable:
            try:
                value = int(self.request.form.get(item['key'], 0))
                if not item.has_key('objs'):
                    provider.setStock(value)
                else:
                    provider.setVariationStock(value, item['objs'])
            except:
                self.errors[item['key']] = _(u'There was an error when saving this stock entry')
        return len(self.errors) == 0
