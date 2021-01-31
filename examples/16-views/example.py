import kopf


"""
Views automatically maintain a dict-like in-memory structure representing
the current state of matching resources in the cluster.

When a resource is added or starts satisfying the filters, a key-value pair
is added to the view; when the resource is deleted or stops satisfying
the filters, it is removed. On every change of the resource, the stored value
is recalculated.

The key must remain the same throughout the whole lifecycle of the resource. 
The default key is a named tuple ``(resource, namespace, name)``,
which is both unique and immutable (these are the parts used in K8s API URLs).

The default key of the dictionary can be overriden with a ``key=`` option,
which must be a callback that accepts the standard :doc:`kwargs` and returns
a hashable immutable value to be used as a dictionary key.

The value retuned by the handler is the value stored in the view.
By default, if no value is returned, the stored value is ``None``.
Such a view can be used for listing the matching resources.

The views are then available to all the handlers of the operator via
the :kwarg:`views` kwarg, which itself is a dictionary, with the view names
(the function names or handler ids) as the keys, and the views as the values.

If the view is declared, there is no need to additionally pre-check for its
existence -- the views exist immediately even if no resources can be viewed yet.

The views are stored purely in-memory and are not persisted anywhere (in this,
the views are similar to :kwarg:`memo` -- a per-resource in-memory container).
On restarts, the views are fully recalculated from the existing resources. 
If persistence is needed, it must be explicitly implemented: for example,
in a timer or a daemon of another resource that persists the data.
"""

# @kopf.view('pods', labels={'viewable': kopf.PRESENT})
@kopf.view('pods', labels={'excluded': kopf.ABSENT})
def pod_phases(status, **_) -> str:
    return status.get('phase')


@kopf.timer('kex', interval=3)
def intervalled(patch, views: kopf.Views, **_):
    patch.status['scheduled-children'] = {
        f"{pod_namespace}/{pod_name}": pod_phase
        for (_, pod_namespace, pod_name), pod_phase in views['pod_phases'].items()
        # if pod_phase == 'Running'
    }
    print(patch.status['scheduled-children'])


# @kopf.daemon('kex')
# async def realtime(patch, views: kopf.Views, **_):
#
#     # Wait until changed. It can take a second or hours. It is cancellable here!
#     await views['pod_phases'].changed.wait()  # asyncio.Condition
#
#     # Do something
#     patch.status['realtime-children'] = {
#         f"{pod_namespace}/{pod_name}": pod_phase
#         for (_, pod_namespace, pod_name), pod_phase in views['pod_phases'].items()
#         # if pod_phase == 'Running'
#     }
#     print(patch.status['realtime-children'])
#
#     # Restart for the next wait.
#     raise kopf.TemporaryError("Need to restart.", delay=None)
