import copy
import importlib
from django.db import models
from django.db import IntegrityError
from django.urls import resolve
from rest_framework import serializers
from rest_framework.fields import Field
from rest_framework.relations import RelatedField, HyperlinkedRelatedField
from rest_framework.settings import api_settings
from rest_framework.exceptions import PermissionDenied, status
from rest_framework.reverse import reverse
from .funcs import getattr_str


class HyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    """
    """
    def __init__(self, *args, **kwargs):
        super(HyperlinkedModelSerializer, self).__init__(*args, **kwargs)

        if not self.context:
            return

        request = self.context['request']
        if request and not request.user.is_superuser:
            for field_name in getattr(self.Meta, 'superuser_fields', []):
                self.fields.pop(field_name)

        fields = request.query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def create(self, *args, **kwargs):
        try:
            return super(HyperlinkedModelSerializer, self).create(
                *args,
                **kwargs)
        except IntegrityError as e:
            from libs.exceptions import ConflictError
            raise ConflictError(str(e))
        except Exception as e:
            raise e

    def get_validators(self):
        """
        Override this nastiness that attempts to duplicate Model validation
        in the serializer.  I want it to pass through to the Model.
        """
        validators = getattr(getattr(self, 'Meta', None), 'validators', [])
        return validators


    def validate(self, *args, **kwargs):
        return super(HyperlinkedModelSerializer, self).validate(*args, **kwargs)

    class Meta:
        pass


class HateoasField(Field):
    def __init__(self, *args, **kwargs):
        kwargs['read_only'] = True
        self.view_name = kwargs.pop('view_name') #add assert
        super(HateoasField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        arg = value
        lookup_field = getattr(self.parent.Meta, 'lookup_field', 'pk')
        request = self.context.get('request')
        #if self.parent.instance:
        #    arg = getattr(self.parent.instance, lookup_field)
        #elif lookup_field in request.data:
        #    arg = request.data[lookup_field]
        #else:
        #    arg = value

        return {api_settings.URL_FIELD_NAME: reverse(
            self.view_name,
            args=[arg],
            request=request,
            )}


class HrefRelatedField(HyperlinkedRelatedField):
    def __init__(self, *args, **kwargs):
        self.url_field_name = api_settings.URL_FIELD_NAME
        self.expand = kwargs.pop('expand', None)
        self.scope = kwargs.pop('scope', None)
        super(HrefRelatedField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        # Forward reference, wrap the normal response and return
        args = [obj, view_name, request, format]
        value = super(HrefRelatedField, self).get_url(*args)
        if isinstance(value, list):
            value = [{self.url_field_name: v} for v in value]
            return value
        return {self.url_field_name: value}

    def to_internal_value(self, data):
        if isinstance(data, dict) and self.url_field_name in data:
            data = data[self.url_field_name]

        return super(HrefRelatedField, self).to_internal_value(data)

    def run_validation(self, data=''):
        value = super(HrefRelatedField, self).run_validation(data)
        if not self.scope:
            return value
        view = self.context.get('view')

        obj_domain = self._get_domain_from_path(self.parent, view.domain_path)
        field_obj = self.to_internal_value(data)
        field_domain = getattr_str(field_obj, self.scope)
        if obj_domain != field_domain:
            raise serializers.ValidationError('Domain of resource is invalid')

        return value

    def _get_domain_from_path(self, o, p):
        if p == 'self':
            return obj

        obj = copy.copy(o)
        p = p.split('.' if '.' in p else '__',1)
        field = obj[p.pop(0)]
        obj = field.to_internal_value(field.value)
        if not p:
            return obj
        elif isinstance(obj, dict):
            return obj.get(p[0])
        return getattr_str(obj, p[0])

