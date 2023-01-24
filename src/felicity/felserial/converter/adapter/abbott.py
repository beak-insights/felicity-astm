# -*- coding: utf-8 -*-

from felicity.felserial.converter.adapter.generic import ASTMBaseAdapter

# Mappings between the value of the sub-field TestID/AssayName from the
# "Universal Test ID" field from (R)esult record and the Result type sub-field
# from same field. This is used to let SENAITE know which (R)esult record must
# be considered as the final result to import.
# If no value set, system grabs the first result found
# Result Types are usually the following:
# - P: Partial
# - F: Final
# - I: Interpreted
KEYWORD_RESULT_TYPE = [
    ("SARS-COV-2", "I")
]


class AbbotM2000ASTMAdapter(ASTMBaseAdapter):
    """Adapter for Abbot m2000r messages
    H|\^&|||m2000^8.1.9.0^275022112^H1P1O1R1C1L1|||||||P|1|20190903162134
    P|1
    O|1|DBS19-002994|DBS19-002994^WS19-2459^D1|^^^HIV1mlDBS^HIV1.0mlDBS|||||||||||||||||||||F
    R|1|^^^HIV1mlDBS^HIV1.0mlDBS^489932^11790271^^F|< 839|Copies / mL||||R||naralabs^naralabs||20190902191654|275022112
    R|2|^^^HIV1mlDBS^HIV1.0mlDBS^489932^11790271^^I|Detected|||||R||naralabs^naralabs||20190902191654|275022112
    R|3|^^^HIV1mlDBS^HIV1.0mlDBS^489932^11790271^^P|28.21|cycle number||||R||naralabs^naralabs||20190902191654|275022112
    """

    def __init__(self, message):
        super(AbbotM2000ASTMAdapter, self).__init__(message)

    @property
    def header_record(self):
        """
        Returns a dict that represents the header of the message
        """
        # H|\^&|||m2000^8.1.9.0^275022146^H1P1O1R1C1L1|||||||P|1|20190703131536
        sender_info = self.get_field(self.raw_header_record, 4)
        receiver_info = self.get_field(self.raw_header_record, 9)
        return {
            "RecordType": self.get_field(self.raw_header_record, 0),
            "FieldDelimiter": self.field_delimiter,
            "RepeatDelimiter": self.repeat_delimiter,
            "ComponentDelimiter": self.component_delimiter,
            "EscapeDelimiter": self.escape_delimiter,
            "SenderName": self.get_component(sender_info, 0),
            "SoftwareVersion": self.get_component(sender_info, 1),
            "SerialNumber": self.get_component(sender_info, 2),
            "InterfaceVersion": self.get_component(sender_info, 3),
            "HostName": self.get_component(receiver_info, 0),
            "IPAddress": self.get_component(receiver_info, 1),
            "ProcessingID": self.get_field(self.raw_header_record, 11),
            "VersionNo": self.get_field(self.raw_header_record, 12),
            "DateTime": self.get_field(self.raw_header_record, 13),
        }

    @property
    def patient_record(self):
        return {
            "RecordTypeId": self.get_field(self.raw_patient_record, 0),
            "SequenceNumber": self.get_field(self.raw_patient_record, 1),
            "PracticePatientID": self.get_field(self.raw_patient_record, 2),
            "LabPatientID": self.get_field(self.raw_patient_record, 3),
            "PatientIDNo3": self.get_field(self.raw_patient_record, 4),
        }

    @property
    def order_record(self):
        # O|1|DBS19-002994|DBS19-002994^WS19-2459^D1|^^^HIV1mlDBS^HIV1.0mlDBS|||||||||||||||||||||F
        record = self.raw_order_record
        return {
            "RecordTypeId": self.get_field(record, 0),
            "SequenceNumber": self.get_field(record, 1),
            "SpecimenID": self.get_record_component(record, 2, 0),
            "LocationID": self.get_record_component(record, 2, 1),
            "Position": self.get_record_component(record, 2, 2),
            "InstrumentSpecimenID": self.get_record_component(record, 3, 0),
            "InstrumentLocationID": self.get_record_component(record, 3, 1),
            "InstrumentPosition": self.get_record_component(record, 3, 2),
            "TestID": self.get_record_component(record, 4, 3),
            "AssayName": self.get_record_component(record, 4, 4),
            "AssayProtocol": self.get_record_component(record, 4, 5),
            "TestQualifier": self.get_record_component(record, 4, 6),
            "Priority": self.get_field(record, 5),
            "RequestedDateTime": self.get_field(record, 6),
            "CollectionDateTime": self.get_field(record, 7),
            "CollectionEndDateTime": self.get_field(record, 8),
            "CollectorID": self.get_field(record, 10),
            "ActionCode": self.get_field(record, 11),
            "DangerCode": self.get_field(record, 12),
            "ClinicalInformation": self.get_field(record, 13),
            "ReceivedDateTime": self.get_field(record, 14),
            "SpecimenType": self.get_record_component(record, 15, 0),
            "SpecimenSource": self.get_record_component(record, 15, 1),
            "OrderingPhysician": self.get_field(record, 16),
            "UserField1": self.get_field(record, 18),
            "UserField2": self.get_field(record, 19),
            "InstrumentSectionID": self.get_field(record, 24),
            "ReportType": self.get_field(record, 25),
            "WardCollection": self.get_field(record, 26),
        }

    @property
    def results_record(self):
        # R|1|^^^SARS-COV-2^SARS-COV-2^506956^10001049^^F|Not Detected|CN||||R||kudamakoni^kudamakoni||20200725073540|275020797
        # R|2|^^^SARS-COV-2^SARS-COV-2^506956^10001049^^I|Negative|||||R||kudamakoni^kudamakoni||20200725073540|275020797
        # R|3|^^^SARS-COV-2^SARS-COV-2^506956^10001049^^P|-1.00|cycle number||||R||kudamakoni^kudamakoni||20200725073540|275020797
        return self.get_result_metadata(self.raw_result_record)

    def get_result_metadata(self, record):
        def get(field_index, component_index=None):
            field = self.get_field(record, field_index)
            if component_index is None:
                return self.get_field(record, field_index)
            return self.get_component(field, component_index)

        return {
            "RecordTypeId": get(0),
            "SequenceNumber": get(1),
            "TestID": get(2, 3),
            "AssayName": get(2, 4),
            "AssayProtocol": get(2, 5),
            "TestQualifier": get(2, 6),
            "ResultType": get(2, 8),
            "Measurement": get(3),
            "Units": get(4),
            "ReferenceRangesRange": get(5, 0),
            "ReferenceRangesDescription": get(5, 1),
            "ResultAbnormalFlag": get(6),
            "NatureOfAbnormality": get(7),
            "ResultStatus": get(8),
            "DateChangeInstrumentValue": get(9),
            "Operator": get(10, 0),
            "Approver": get(10, 1),
            "DateTimeTestStarted": get(11),
            "DateTimeTestCompleted": get(12),
            "InstrumentIdentification": get(14),
        }

    def resolve_final_result_record(self, records):
        """Returns the result record (raw) to be considered as the final result
        """
        if len(records) == 1:
            return records[0]

        # Try to find out which (R)esult record represents the final result
        for record in records:

            # Get the metada for this raw record
            meta = self.get_result_metadata(record)
            if self.is_final_result(meta):
                return record

        # No matches found, return the first one
        return records[0]

    def is_final_result(self, meta_result, subfield_keyword=None):
        """Returns whether a (R)sult record must be considered as the final
        result or not
        """
        if not subfield_keyword:
            if self.is_final_result(meta_result, "TestID"):
                return True
            if self.is_final_result(meta_result, "AssayName"):
                return True
            return False

        # Get the test ID/keyword/name
        keyword = meta_result.get(subfield_keyword)
        if not keyword:
            return False

        # Get the result type for this keyword from the mapping
        key_types = dict(KEYWORD_RESULT_TYPE)
        result_type = key_types.get(keyword, None)
        if result_type is None:
            return False

        # Assume final result if Result Type matches
        return meta_result.get("ResultType") == result_type

    def is_supported(self):
        """Returns whether the current adapter supports the given message
        """
        if self.has_header():
            return self.header_record["SenderName"] == "m2000"
        return False

    def read(self):
        """Returns a list of ASTMDataResult objects
        """
        data = {}
        data["id"] = self.order_record["SpecimenID"]
        data["keyword"] = self.results_record["TestID"]
        data["result"] = self.results_record["Measurement"]
        data["capture_date"] = self.results_record["DateTimeTestCompleted"]
        # If Final Result is "Not detected", store the Interpreted Result
        if data["result"] == "Not detected":
            data["result"] = "Target not detected"
        return [data]
