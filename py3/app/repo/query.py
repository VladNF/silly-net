class WhereBuilder:
    def __init__(self, var_index=1) -> None:
        self.conditions = []
        self.variables = []
        self.var_index = var_index

    def with_fields_eq(self, **kwargs):
        for field_name, field_value in kwargs.items():
            self.conditions += [f"{field_name} = ${self.var_index}"]
            self.variables += [field_value]
            self.var_index += 1

    def with_fields_like(self, **kwargs):
        for field_name, field_value in kwargs.items():
            if not field_value:
                continue

            self.conditions += [f"{field_name} ILIKE ${self.var_index}"]
            self.variables += [f"%{field_value}%"]
            self.var_index += 1

    def with_fields_prefix(self, **kwargs):
        for field_name, field_value in kwargs.items():
            if not field_value:
                continue

            self.conditions += [f"lower({field_name}) LIKE ${self.var_index}"]
            self.variables += [f"{field_value.lower()}%"]
            self.var_index += 1

    def build(self):
        if not self.conditions:
            return ""

        return f"WHERE {' AND '.join(self.conditions)}"


class InsertBuilder:
    def __init__(self, map_func, var_index=1) -> None:
        assert map_func, "map_func is required"
        self.map_func = map_func
        self.expressions = []
        self.variables = []
        self.var_index = var_index

    def with_values(self, *fields):
        assert fields, "at least one value required"
        placeholders = [f"${i}" for i in range(self.var_index, self.var_index + len(fields))]
        self.expressions += [f"({', '.join(placeholders)})"]
        self.variables += fields
        self.var_index += len(fields)
        return self

    def with_object(self, o):
        return self.with_values(*self.map_func(o))

    def with_object_multi(self, batch):
        for o in batch:
            self.with_values(*self.map_func(o))
        return self

    def build(self):
        if not self.expressions:
            return ""

        return f"{', '.join(self.expressions)}"
