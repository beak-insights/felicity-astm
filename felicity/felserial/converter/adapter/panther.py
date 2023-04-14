# -*- coding: utf-8 -*-
#
# This file is part of NMRL.LIMS.
#
# Copyright 2019-2020 National Microbiology Reference Laboratory (NMRL).

from felicity.felserial.converter.adapter.generic import ASTMBaseAdapter


class PantherASTMAdapter(ASTMBaseAdapter):
    """Adapter for Panther ASTM messages

    H|\^&|||Panther|||||Host||P|1|
    P|1||||^^|||||||||||^|^|||||||||||||||^|^|
    O|1|662047|40ee8544-6076-4046-8dc0-601c18863cd7^37468|^^^qHIV-1^HIV-1^^1|R|20190808013102|||||||||||||||||||F
    R|1|^^^qHIV-1^HIV-1^^1|Not Detected|copies/mL||||F||||20190808052856
    R|2|^^^qHIV-1^ICResult^^1|15|||||F||||20190808052856
    R|3|^^^qHIV-1^ResultValid^^1|Valid|||||F||||20190808052856
    R|4|^^^qHIV-1^HIV-1LogBase10^^1|Not Detected|||||F||||20190808052856
    P|2||||^^|||||||||||^|^|||||||||||||||^|^|
    O|1|1203695|32d27901-3d12-4a21-97d5-ea003015f86b^37470|^^^qHIV-1^HIV-1^^1|R|20190808013102|||||||||||||||||||F
    R|1|^^^qHIV-1^HIV-1^^1|Not Detected|copies/mL||||F||||20190808052855
    R|2|^^^qHIV-1^ICResult^^1|14|||||F||||20190808052855
    R|3|^^^qHIV-1^ResultValid^^1|Valid|||||F||||20190808052855
    R|4|^^^qHIV-1^HIV-1LogBase10^^1|Not Detected|||||F||||20190808052855
    P|3||||^^|||||||||||^|^|||||||||||||||^|^|
    O|1|1203665|8df52f67-2aa4-4fc5-a301-551f7d222423^37471|^^^qHIV-1^HIV-1^^1|R|20190808013102|||||||||||||||||||F
    R|1|^^^qHIV-1^HIV-1^^1|59|copies/mL||||F||||20190808052856
    R|2|^^^qHIV-1^ICResult^^1|15|||||F||||20190808052856
    R|3|^^^qHIV-1^ResultValid^^1|Valid|||||F||||20190808052856
    R|4|^^^qHIV-1^HIV-1LogBase10^^1|1.77|||||F||||20190808052856
    P|4||||^^|||||||||||^|^|||||||||||||||^|^|
    """

    def __init__(self, message):
        super(PantherASTMAdapter, self).__init__(message)

    @property
    def header_record(self):
        """
        Returns a dict that represents the header of the message
        """
        # H|\^&|||Panther|||||Host||P|1|
        sender_info = self.get_field(self.raw_header_record, 4)
        return {
            # H|\^&|||Panther
            "RecordType": self.get_field(self.raw_header_record, 0),
            "FieldDelimiter": self.field_delimiter,
            "RepeatDelimiter": self.repeat_delimiter,
            "ComponentDelimiter": self.component_delimiter,
            "EscapeDelimiter": self.escape_delimiter,
            "SenderName": self.get_component(sender_info, 0),
        }

    @property
    def patient_record(self):
        # P|1||||^^|||||||||||^|^|||||||||||||||^|^|
        return {
            # P|1
            "RecordTypeId": self.get_field(self.raw_patient_record, 0),
            "SequenceNumber": self.get_field(self.raw_patient_record, 1),
        }

    @property
    def order_record(self):
        # O|1|662047|40ee8544-6076-4046-8dc0-601c18863cd7^37468|^^^qHIV-1^HIV-1^^1|R|20190808013102|||||||||||||||||||F
        record = self.raw_order_record
        return {
            # O|1|662047|
            "RecordTypeId": self.get_field(record, 0),
            "SequenceNumber": self.get_field(record, 1),
            "SpecimenID": self.get_record_component(record, 2, 0),

            # ^^^qHIV-1^HIV-1^^1
            "TestID": self.get_record_component(record, 4, 3),
            "AssayName": self.get_record_component(record, 4, 4),
            "AssayProtocol": self.get_record_component(record, 4, 5),
            "TestQualifier": self.get_record_component(record, 4, 6),

            # R|20190808013102
            "Priority": self.get_field(record, 5),
            "RequestedDateTime": self.get_field(record, 6),
        }

    def resolve_final_result_record(self, records):
        test_id = self.order_record["TestID"]
        assay_name = self.order_record["AssayName"]
        target = "|^^^{}^{}^".format(test_id, assay_name)
        if test_id == "HPV":
            assay_name = "OverallInterpretation"
        target = "|^^^{}^{}^".format(test_id, assay_name)
        for record in records:
            if target in record and record.index(target) >= 3:
                return record
        return records[0]

    @property
    def results_record(self):
        # R|1|^^^qHIV-1^HIV-1^^1|Not Detected|copies/mL||||F||||20190808052856
        # R|2|^^^qHIV-1^ICResult^^1|15|||||F||||20190808052856
        # R|3|^^^qHIV-1^ResultValid^^1|Valid|||||F||||20190808052856
        # R|4|^^^qHIV-1^HIV-1LogBase10^^1|Not Detected|||||F||||20190808052856

        def get(field_index, component_index=None):
            record = self.raw_result_record
            field = self.get_field(record, field_index)
            if component_index is None:
                return self.get_field(record, field_index)
            return self.get_component(field, component_index)

        return {
            # R|1|
            "RecordTypeId": get(0),
            "SequenceNumber": get(1),
            # ^^^qHIV-1^HIV-1^^1
            "TestID": get(2, 3),
            "AssayName": get(2, 4),
            # Not Detected|copies/mL
            "Measurement": get(3),
            "Units": get(4),
            # 20190808052856
            "DateTimeTestCompleted": get(12),
        }

    def is_supported(self):
        """Returns whether the current adapter supports the given message
        """
        return self.header_record.get("SenderName", None) == "Panther"

    def split_samples(self):
        """Hologic Panther sends multiple samples in a single header
        """
        header = self.raw_header_record

        # Remove the header from the message (will be added later)
        msg_wo_header = self.message.replace(header, "").strip()

        # Split by P| blocks and join again
        split_by = "\nP{}".format(self.field_delimiter)
        msgs = filter(None, msg_wo_header.split(split_by))
        return map(lambda msg: "{}{}{}".format(header, split_by, msg), msgs)

    def read(self):
        """Returns a list of ASTMDataResult objects
        """
        # Note Hologic Panther sends multiple samples with a single Header, so
        # we need to split the raw_message by Order
        out_data = []
        for msg in self.split_samples():
            ad = PantherASTMAdapter(msg)
            data = {}
            data["id"] = ad.order_record["SpecimenID"]
            data["keyword"] = ad.results_record["TestID"]
            data["result"] = ad.results_record["Measurement"]
            data["capture_date"] = ad.results_record["DateTimeTestCompleted"]
            data["raw_message"] = msg
            out_data.append(data)
        return out_data
