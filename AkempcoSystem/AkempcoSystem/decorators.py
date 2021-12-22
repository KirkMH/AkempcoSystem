from django.core.exceptions import PermissionDenied
from admin_area.models import Feature

def xx(feature):
    def wrap(request, *args, **kwargs):
        allowed_features = request.user.userdetail.get_permissions()
        print(args)
        feature = 5 #kwargs['feature']
        if feature in allowed_features:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    # wrap.__name__ = function.__name__
    return wrap


def user_is_allowed(feature):

    def _method_wrapper(view_method):

        def _arguments_wrapper(request, *args, **kwargs) :
            allowed_features = request.user.userdetail.get_permissions()
            f = feature
            if f in allowed_features:
                return view_method(request, *args, **kwargs)
            else:
                raise PermissionDenied

        return _arguments_wrapper

    return _method_wrapper