from django.core.exceptions import ObjectDoesNotExist
from rest_framework import relations
from rest_framework import serializers as serials
from rest_framework.utils import field_mapping


class HyperlinkedReprnRelatedField(serials.HyperlinkedRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_object(
                view_name=self.view_name,
                view_args=None,
                view_kwargs={self.lookup_url_kwarg: data},
            )
        except (
            ObjectDoesNotExist,
            relations.ObjectValueError,
            relations.ObjectTypeError,
        ):
            self.fail("does_not_exist")


class HyperlinkedReprnModelSerializer(serials.HyperlinkedModelSerializer):
    serializer_related_field = HyperlinkedReprnRelatedField

    def build_nested_field(self, field_name, relation_info, nested_depth):
        class NestedSerializer(HyperlinkedReprnModelSerializer):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = "__all__"

        field_class = NestedSerializer
        field_kwargs = field_mapping.get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs
