from collections.abc import Mapping

from rest_framework import serializers


class StrictTextField(serializers.CharField):
    """Reject coercion and enforce length before whitespace is stripped."""

    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail('invalid')
        if self.max_length is not None and len(data) > self.max_length:
            self.fail('max_length', max_length=self.max_length)
        return super().to_internal_value(data)


class StrictObjectSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            raise serializers.ValidationError({'body': ['Expected a JSON object.']})
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({
                field: ['Unknown field.'] for field in sorted(unknown)
            })
        return super().to_internal_value(data)


class StrictUUIDField(serializers.UUIDField):
    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail('invalid')
        return super().to_internal_value(data)


class DialogueMessageSerializer(StrictObjectSerializer):
    game_session_id = StrictUUIDField()
    npc_id = StrictTextField(max_length=100, trim_whitespace=False)
    message = StrictTextField(max_length=1000)
