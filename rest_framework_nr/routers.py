from django.conf.urls import patterns, url
from rest_framework.routers import Route, DynamicDetailRoute, SimpleRouter

class SimpleNestedRouter(SimpleRouter):

    def register(self, prefix, viewset, base_name=None, **kwargs):
        """Register a viewset for dynamic URL generation

        Keyword arguments:
        parent_view - viewset corresponding to the child's dependent resource
        nested_name - overrides the default prefix for nested urls
        child_style - `list` returns multiple objects, `detail` one object
        platform    - adds a parent-list url as well
        """

        if base_name is None:
            base_name = self.get_default_base_name(viewset)

        kwargs.update({'nested_name': kwargs.get('nested_name', None)})
        entry = (prefix, viewset, base_name, kwargs)
        self.registry.append(entry)

    def get_entry_by_viewset(self, viewset):
        entry = [entry for entry in self.registry if entry[1] == viewset]
        return self.route_or_exception(entry)

    def get_entry_by_prefix(self, prefix):
        entry = [entry for entry in self.registry if entry[0] == prefix]
        return self.route_or_exception(entry)

    def route_or_exception(self, entry_list):
        try:
            return Route(*entry_list[0])
        except:
            raise RuntimeError('registered resource not found')

    def get_urls(self):
        """
        Use the registered viewsets to generate a list of URL patterns.
        """
        ret = []

        for prefix, viewset, basename, initkwargs in self.registry:
            lookup = self.get_lookup_regex(viewset)
            routes = self.get_routes(viewset)

            parent_view = getattr(viewset, 'parent', None)
            child_style = getattr(viewset, 'style', 'list')
            platform = getattr(viewset, 'platform', None)

            for route in routes:
                # Only actions which actually exist on the viewset will be bound
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                view = viewset.as_view(mapping, **route.initkwargs)
                name = route.name.format(basename=basename)

                urlkw = {}
                # nested routes under the parent for create and list
                if parent_view and route.initkwargs.get('suffix') == 'List':
                    child_prefix = initkwargs.get('nested_name') or prefix
                    parent = self.get_entry_by_viewset(parent_view)
                    u = r'^{parent}/{lookup}/{prefix}{trailing_slash}$'
                    urlkw['parent'] = parent.url
                    urlkw['child'] = child_prefix
                    regex = u.format(
                        parent=parent.url,
                        lookup=self.get_parent_lookup_regex(parent_view),
                        prefix=child_prefix,
                        trailing_slash=self.trailing_slash,
                        )
                    name = route.name.format(basename=basename+"-nested")

                    if platform:
                        # Add a root list resource as well
                        platform_regex = route.url.format(
                            prefix=prefix,
                            lookup=lookup,
                            trailing_slash=self.trailing_slash
                            )
                        platform_name = route.name.format(basename=basename)
                        ret.append(
                            url(platform_regex, view, name=platform_name)
                            )
                else:
                    # Build the url pattern
                    regex = route.url.format(
                        prefix=prefix,
                        lookup=lookup,
                        trailing_slash=self.trailing_slash
                        )

                ret.append(url(regex, view, urlkw, name=name))

        return ret

    def get_parent_lookup_regex(self, parent_view):
        # Can implment get_lookup_regex?
        lookup_regex = getattr(parent_view, 'lookup_value_regex', '[^/.]+')
        return "(?P<parent_pk>{0})".format(lookup_regex)


