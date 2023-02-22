# -*- coding: utf-8 -*-


class ASTMBaseAdapter:

    _raw_records = None
    _field_delimiter = None
    _repeat_delimiter = None
    _component_delimiter = None
    _escape_delimiter = None

    def __init__(self, message):
        self.message = message

    @property
    def raw_records(self):
        """
        :return: List<str>
        """
        if self._raw_records is None:
            self._raw_records = list(map(lambda r: r.strip(),
                                         self.message.splitlines()))
        return self._raw_records or []

    @property
    def raw_patient_record(self):
        record = self.search_raw_records("P{}".format(self.field_delimiter))
        return record and record[0] or None

    @property
    def raw_result_record(self):
        # TODO Only 1 result per Block?
        records = self.search_raw_records("R{}".format(self.field_delimiter))
        return records and self.resolve_final_result_record(records) or None

    @property
    def raw_order_record(self):
        record = self.search_raw_records("O{}".format(self.field_delimiter))
        return record and record[0] or None

    @property
    def field_delimiter(self):
        return self.get_delimiter(self._field_delimiter, 1)

    @property
    def repeat_delimiter(self):
        return self.get_delimiter(self._repeat_delimiter, 2)

    @property
    def component_delimiter(self):
        return self.get_delimiter(self._component_delimiter, 3)

    @property
    def escape_delimiter(self):
        return self.get_delimiter(self._escape_delimiter, 4)

    @property
    def raw_header_record(self):
        record = self.search_raw_records("H")
        return record and record[0] or None

    def search_raw_records(self, prefix):
        return list(filter(lambda rec: rec.startswith(prefix), self.raw_records))

    def get_delimiter(self, delimiter_var, index):
        if delimiter_var is None:
            return self.raw_header_record[index]
        return delimiter_var

    def get_fields(self, record):
        return record and record.split(self.field_delimiter) or []

    def get_field(self, record, index, default=None):
        fields = self.get_fields(record)
        if index >= len(fields):
            return default
        return fields[index]

    def get_repeats(self, field):
        return field and field.split(self.repeat_delimiter) or []

    def get_components(self, field):
        return field and field.split(self.component_delimiter) or []

    def get_component(self, field, index, default=None):
        comp = self.get_components(field)
        if index >= len(comp):
            return default
        return comp[index]

    def get_record_component(self, record, field_index, component_index,
                             default=None):
        field = self.get_field(record, field_index)
        return self.get_component(field, component_index, default=default)

    def has_header(self):
        if self.raw_header_record:
            return True
        return False

    def resolve_final_result_record(self, records):
        return records[0]


class HL7BaseAdapter:

    _raw_records = None
    _field_delimiter = None
    _repeat_delimiter = None
    _component_delimiter = None
    _sub_component_delimiter = None
    _escape_delimiter = None

    def __init__(self, message):
        self.message = message

    @property
    def raw_records(self):
        """
        :return: List<str>
        """
        if self._raw_records is None:
            self._raw_records = list(map(lambda r: r.strip(),
                                         self.message.splitlines()))
        return self._raw_records or []

    @property
    def raw_observation_record(self):
        records = self.search_raw_records("OBX{}".format(self.field_delimiter))
        return records

    @property
    def raw_specimen_record(self):
        record = self.search_raw_records("SPM{}".format(self.field_delimiter))
        return record and record[0] or None

    @property
    def raw_test_code_record(self):
        record = self.search_raw_records("TCD{}".format(self.field_delimiter))
        return record and record[0] or None

    @property
    def raw_observation_request_record(self):
        record = self.search_raw_records("OBR{}".format(self.field_delimiter))
        return record and record[0] or None

    @property
    def field_delimiter(self):
        return self.get_delimiter(self._field_delimiter, 3)

    @property
    def repeat_delimiter(self):
        return self.get_delimiter(self._repeat_delimiter, 5)

    @property
    def component_delimiter(self):
        return self.get_delimiter(self._component_delimiter, 4)

    @property
    def escape_delimiter(self):
        return self.get_delimiter(self._escape_delimiter, 6)

    @property
    def sub_component_delimiter(self):
        return self.get_delimiter(self._escape_delimiter, 7)

    @property
    def raw_header_record(self):
        record = self.search_raw_records("MSH")
        return record and record[0] or None

    def search_raw_records(self, prefix):
        return list(filter(lambda rec: rec.startswith(prefix), self.raw_records))

    def get_delimiter(self, delimiter_var, index):
        if delimiter_var is None:
            return self.raw_header_record[index]
        return delimiter_var

    def get_fields(self, record):
        return record and record.split(self.field_delimiter) or []

    def get_field(self, record, index, default=None):
        fields = self.get_fields(record)
        if index >= len(fields):
            return default
        return fields[index]

    def get_repeats(self, field):
        return field and field.split(self.repeat_delimiter) or []

    def get_components(self, field):
        return field and field.split(self.component_delimiter) or []

    def get_component(self, field, index, default=None):
        comp = self.get_components(field)
        if index >= len(comp):
            return default
        return comp[index]

    def get_record_component(self, record, field_index, component_index,
                             default=None):
        field = self.get_field(record, field_index)
        return self.get_component(field, component_index, default=default)

    def has_header(self):
        if self.raw_header_record:
            return True
        return False

    def resolve_final_result_record(self, records):
        return records[0]
