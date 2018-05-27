from apistar import validators


class UUID(validators.String):
    def validate(self, value, definitions=None, allow_coerce=False):
        return super().validate(str(value), definitions, allow_coerce)
