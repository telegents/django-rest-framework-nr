from django.urls import reverse
from rest_framework import authentication, permissions, viewsets
from rest_framework import status, exceptions
from rest_framework.response import Response


class ScopedViewSet(viewsets.ModelViewSet):
    """
    Scopes all requests by authorization by domain access

    Specify key paths using the following example:
        <field>_path (i.e. domain_path = 'extension__domain'
    """

    def __init__(self, *args, **kwargs):
        super(ScopedViewSet, self).__init__(*args, **kwargs)

    def list(self, request, parent=None, parent_pk=None, child=None):
        if child:
            basename = self._get_basename_from_resource(parent)
            lookup_field = self.parent.lookup_field

            parent_key = getattr(self, '{0}_path'.format(basename), basename)
            parent_path = '{0}__{1}'.format(parent_key, lookup_field)
            self.request._filter = {parent_path: parent_pk}

        if child and self._get_childstyle() == 'detail':
            try:
                obj = self.queryset.get(**self.request._filter)
            except:
                NOT_FOUND = status.HTTP_404_NOT_FOUND
                return Response({'detail': 'Not found'}, status=NOT_FOUND)

            ser = self.serializer_class(obj, context={'request': request})
            return Response(ser.data)

        return super(ScopedViewSet, self).list(request)

    def create(self, request, parent=None, parent_pk=None, child=None):
        import pdb; pdb.set_trace()
        if parent_pk and child:
            # Verify the child (this view) is not a platform resource or 403
            if getattr(self, 'platform', None):
                FORBIDDEN = status.HTTP_403_FORBIDDEN
                return Response({'detail': 'Not found'}, status=FORBIDDEN)

            # Load the parent uri and update the request data
            basename = self._get_basename_from_resource(parent)
            parent_uri = self._get_parent_uri(request, basename, parent_pk)

            # Use Middleware instead of overriding Django's protection?
            if hasattr(request.data, '_mutable'):
                request.data._mutable = True
            request.data[basename] = parent_uri
        return super(ScopedViewSet, self).create(request)

    def update(self, request, *args, **kwargs):
        return super(ScopedViewSet, self).update(request, *args, **kwargs)

    def get_queryset(self):
        # apply a _filter if specified on the request
        _filter = getattr(self.request, '_filter', {})
        filter_fields = getattr(self, 'filter_fields', ())
        for key in self.request.query_params:
            params = key.split('__')

            # Verify that filtered fields are allowed
            if params[0] not in filter_fields:
                raise exceptions.ParseError(
                    detail='Filtering on %s not allowed' % params[0])

            allowed = filter_fields[params[0]]

            # Verify the filter params attached are allowed
            if allowed  == 'all':
                # allow any filter if the setting is all
                # re-visit this because it allows deep nesting
                pass
            elif len(params) > 1:
                if not all([p in filter_fields[params[0]] for p in params[1:]]):
                    raise exceptions.ParseError(
                        detail='Filter params specified not allowed')
                pass
            elif allowed == 'exact':
                pass
            else:
                raise exceptions.ParseError(detail='Filter not allowed')

            value = self.request.query_params[key]
            _filter[key] = None if value == 'None' else value

        return self.queryset.filter(**_filter)

    def _get_parent_uri(self, request, basename, pk):
        lookup_field = self.parent.lookup_field
        return request.build_absolute_uri(
            reverse('%s-detail' % basename, kwargs={lookup_field: pk})
            )

    def _get_childstyle(self):
        return getattr(self, 'style', 'list')

    def _get_basename_from_resource(self, name):
        import sys
        from django.conf import settings
        router = sys.modules[settings.ROOT_URLCONF].router
        view = [r[2] for r in router.registry if r[0] == name]
        return view[0] if view else None


