from zope.interface import Interface

class IStockable(Interface):
    """ Browser layer
    """

class IStock(Interface):
    """ Provider for stock information of Products
    """
    
    def stockable():
        """ Returns a list of the stockable variation combinations of a product
        """
    
    def stock():
        """ Overall number of items in stock
        """
    
    def variationStock(variation):
        """ Number of items available of a variation or combination
            of multiple variations
        """
    
    def setStock(stock):
        """ Set the overall number of items in stock
        """
    
    def setVariationStock(stock, variation):
        """ Set the number of items available of a variation or combination
            of multiple variations
        """
    
    def outOfStockCheckoutAllowed():
        """ Returns whether checking out if this product is out of stock is allowed or not
        """
