# monkey patching TrancientObjectContainer to listen to session timeouts
from Acquisition import aq_parent, aq_inner
from OFS.Application import Application
from OFS.ObjectManager import ObjectManager

from zope.site.hooks import getSite, setSite

from Products.CMFPlone.Portal import PloneSite

from Products.Transience.Transience import TransientObjectContainer

from pcommerce.core.order import ORDER_SESSION_KEY
from pcommerce.core.interfaces import IOrderRegistry

def _setSite(sm):
    setSite(sm)

def _findInstances(root):
    instances = []
    for child in root.objectValues():
        if isinstance(child, PloneSite):
            instances.append(child)
        elif isinstance(child, ObjectManager):
            instances += _findInstances(child)
    return instances

def notifyDel(self, item):
    if item.has_key(ORDER_SESSION_KEY):
        try:
            site = getSite()
            app = self
            while not isinstance(app, Application):
                app = aq_parent(app)
            instances = _findInstances(app)
            for instance in instances:
                try:
                    _setSite(instance)
                    registry = IOrderRegistry(instance)
                    registry.cancel(item.get(ORDER_SESSION_KEY))
                except:
                    pass
        except:
            pass
        finally:
            try:
                if not site.REQUEST._lazies.has_key('SESSION'):
                    # add a lazy callable to the request to prevent KeyError
                    # as we might have a recursive call to HTTPRequest.get
                    # which will remove the before available lazy SESSION
                    # ZPublisher.HTTPRequest[1333:1339]
                    site.REQUEST.set_lazy('SESSION', lambda: 1)
                _setSite(site)
            except:
                pass
    TransientObjectContainer.__old__notifyDel(self, item)

TransientObjectContainer.__old__notifyDel = TransientObjectContainer.notifyDel
TransientObjectContainer.notifyDel = notifyDel
