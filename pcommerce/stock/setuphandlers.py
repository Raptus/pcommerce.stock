from Products.CMFCore.utils import getToolByName

from pcommerce.stock.extender import ProductExtender

def install(context):
    if context.readDataFile('pcommerce.stock_install.txt') is None:
        return
    portal = context.getSite()
    
    sm = portal.getSiteManager()
    sm.registerAdapter(ProductExtender, name='pcommerce.stock')

def uninstall(context):
    if context.readDataFile('pcommerce.stock_uninstall.txt') is None:
        return
    portal = context.getSite()
    
    sm = portal.getSiteManager()
    sm.unregisterAdapter(ProductExtender, name='pcommerce.stock')
