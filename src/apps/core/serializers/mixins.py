from rest_framework import serializers as serials


class ImmutableFieldsMixin(serials.ModelSerializer):
    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        immutable_fields = getattr(self.Meta, "immutable_fields", None)

        if self.instance and immutable_fields is not None:
            if not isinstance(immutable_fields, (list, tuple)):
                raise TypeError(
                    "The `immutable_fields` option must be a list or tuple. "
                    "Got %s." % type(immutable_fields).__name__
                )

            for field_name in immutable_fields:
                kwargs = extra_kwargs.get(field_name, {})
                kwargs["read_only"] = True
                extra_kwargs[field_name] = kwargs

        return extra_kwargs
