from zope.interface import implements
from zope.component import adapts

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.Field import BooleanField as BaseBooleanField
from Products.Archetypes.Widget import BooleanWidget
from Products.Archetypes.interfaces import IFieldDefaultProvider

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from pcommerce.core import PCommerceMessageFactory as _
from pcommerce.core.content.product import Product

class BooleanField(ExtensionField, BaseBooleanField):
    """ BooleanField
    """

class ProductExtender(object):
    implements(ISchemaExtender)
    adapts(Product)

    fields = [
        BooleanField(
            name='outofstock_checkout',
            required=0,
            searchable=0,
            default='',
            widget=BooleanWidget(
                label = _(u'label_outofstock_checkout', default=u'Allow checkout if this product is out of stock'),
            ),
            schemata='default',
        ),
    ]

    def __init__(self, context):
         self.context = context

    def getFields(self):
        if self.context.__class__ is Product:
            return self.fields
        return []

class OutofstockCheckoutDefault(object):
    implements(IFieldDefaultProvider)
    adapts(Product)
    def __init__(self, context):
        self.context = context
    def __call__(self):
        return getToolByName(self.context, 'portal_properties').pcommerce_properties.getProperty('allow_outofstock_checkout', True)
