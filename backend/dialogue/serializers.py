from collections.abc import Mapping

from rest_framework import serializers

from .npc_data import get_npc


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


class HistoryEntrySerializer(StrictObjectSerializer):
    role = StrictTextField(trim_whitespace=False)
    content = StrictTextField(max_length=4000)

    def validate_role(self, value):
        if value not in ('user', 'assistant'):
            raise serializers.ValidationError('Must be user or assistant.')
        return value


class HistoryField(serializers.ListField):
    def to_internal_value(self, data):
        if not isinstance(data, list):
            self.fail('not_a_list', input_type=type(data).__name__)
        # Inspect raw strings so trimming cannot bypass the total size limit.
        total = sum(
            len(entry['content']) for entry in data
            if isinstance(entry, Mapping) and isinstance(entry.get('content'), str)
        )
        if total > 20000:
            raise serializers.ValidationError('History must not exceed 20,000 characters.')
        return super().to_internal_value(data)


class DialogueMessageSerializer(StrictObjectSerializer):
    npc_id = StrictTextField(trim_whitespace=False)
    message = StrictTextField(max_length=1000)
    history = HistoryField(child=HistoryEntrySerializer(), max_length=20)

    def validate_history(self, value):
        if len(value) % 2:
            raise serializers.ValidationError('History must contain completed exchanges.')
        for index, entry in enumerate(value):
            expected = 'user' if index % 2 == 0 else 'assistant'
            if entry['role'] != expected:
                raise serializers.ValidationError(
                    'History must alternate user and assistant, starting with user.'
                )
        return value

    def validate(self, attrs):
        # Resolve only after every field and history constraint has passed.
        get_npc(attrs['npc_id'])
        return attrs
