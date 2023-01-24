# -*- coding: utf-8 -*-

from felicity.felserial.converter.adapter.generic import ASTMBaseAdapter


class RocheASTMPlusAdapter(ASTMBaseAdapter):
    """Adapter for Roche ASTM+ messages
    """

    def __init__(self, message):
        super(RocheASTMPlusAdapter, self).__init__(message)

    @property
    def header_record(self):
        """
        Returns a dict that represents the header of the message
        """
        sender_info = self.get_field(self.raw_header_record, 4)
        receiver_info = self.get_field(self.raw_header_record, 9)
        return {
            "RecordTypeId": self.get_field(self.raw_header_record, 0),
            "FieldDelimiter": self.field_delimiter,
            "RepeatDelimiter": self.repeat_delimiter,
            "ComponentDelimiter": self.component_delimiter,
            "EscapeDelimiter": self.escape_delimiter,
            "SenderName": self.get_component(sender_info, 0),
            "Manufacturer": self.get_component(sender_info, 1),
            "InstrumentType": self.get_component(sender_info, 2),
            "SoftwareVersion": self.get_component(sender_info, 3),
            "ProtocolVersion": self.get_component(sender_info, 4),
            "SerialNumber": self.get_component(sender_info, 5),
            "SenderNetworkAddress": self.get_component(sender_info, 6),
            "ReceiverName": self.get_component(receiver_info, 0),
            "ReceiverNetworkAddress": self.get_component(receiver_info, 1),
            "ProcessingID": self.get_field(self.raw_header_record, 11),
            "VersionNo": self.get_field(self.raw_header_record, 12),
        }

    @property
    def patient_record(self):
        # P|1
        return {
            "RecordTypeId": self.get_field(self.raw_patient_record, 0),
            "SequenceNumber": self.get_field(self.raw_patient_record, 1),
            "PracticePatientID": self.get_field(self.raw_patient_record, 2),
            "LabPatientID": self.get_field(self.raw_patient_record, 3),
            "PatientIDNo3": self.get_field(self.raw_patient_record, 4),
        }

    @property
    def order_record(self):
        # O|1|627318rr|627318|^^^ALL||20190708091041|||||A
        order_comp = self.get_field(self.raw_order_record, 3)
        test_comp = self.get_field(self.raw_order_record, 4)
        volume = self.get_field(self.raw_order_record, 9)
        return {
            "RecordTypeId": self.get_field(self.raw_order_record, 0),
            "SequenceNumber": self.get_field(self.raw_order_record, 1),
            "SpecimenID": self.get_field(self.raw_order_record, 2),
            "OrderID": self.get_component(order_comp, 0),
            "RackCarrierID": self.get_component(order_comp, 1),
            "PositionOnRackCarrier": self.get_component(order_comp, 2),
            "TrayOrLocationID": self.get_component(order_comp, 3),
            "RackCarrierType": self.get_component(order_comp, 4),
            "TubeContainerType": self.get_component(order_comp, 5),
            "TestID": self.get_component(test_comp, 3),
            "TreatmentType": self.get_component(test_comp, 4),
            "Pre-TreatmentType": self.get_component(test_comp, 5),
            "ResultEvaluationType": self.get_component(test_comp, 6),
            "Priority": self.get_field(self.raw_order_record, 5),
            "RequestedDateTime": self.get_field(self.raw_order_record, 6),
            "CollectionDateTime": self.get_field(self.raw_order_record, 7),
            "CollectionEndDateTime": self.get_field(self.raw_order_record, 8),
            "CollectionVolume.Value": self.get_component(volume, 0),
            "CollectionVolume.Unit": self.get_component(volume, 1),
            "CollectorID": self.get_field(self.raw_order_record, 10),
            "ActionCode": self.get_field(self.raw_order_record, 11),
            "DangerCode": self.get_field(self.raw_order_record, 12),
            "ClinicalInformation": self.get_field(self.raw_order_record, 13),
            "ReceivedDateTime": self.get_field(self.raw_order_record, 14),
        }

    @property
    def results_record(self):
        # R|1|^^^HI2QLD96|Detected DBS||-1^-1^TiterRanges|N||V||BANHWA|20190708165238|2019
        rec = self.raw_result_record
        test_comp = self.get_field(rec, 2)
        result_comp = self.get_field(rec, 3)
        limit_comp = self.get_field(rec, 5)
        return {
            "RecordTypeId": self.get_field(rec, 0),
            "SequenceNumber": self.get_field(rec, 1),
            "TestID": self.get_component(test_comp, 3),
            "TreatmentType": self.get_component(test_comp, 4),
            "Pre-TreatmentType": self.get_component(test_comp, 5),
            "ResultEvaluationType": self.get_component(test_comp, 6),
            "DataMeasurementResultScalar": self.get_component(result_comp, 0),
            "DataMeasurementResultValUnit": self.get_field(rec, 4),
            "DataCutOffIndex": self.get_component(result_comp, 1),
            "LowerLimit": self.get_component(limit_comp, 0),
            "UpperLimit": self.get_component(limit_comp, 1),
            "LimitName": self.get_component(limit_comp, 2),
            "ResultAbnormalFlag": self.get_field(rec, 6),
            "NatureOfAbnormality": self.get_field(rec, 7),
            "ResultStatus": self.get_field(rec, 8),
            "DateChangeInstrumentValue": self.get_field(rec, 9),
            "Operator": self.get_field(rec, 10),
            "DateTimeTestStarted": self.get_field(rec, 11),
            "DateTimeTestCompleted": self.get_field(rec, 12),
            "InstrumentIdentification": self.get_field(rec, 13),
        }

    def is_supported(self):
        """Returns whether the current adapter supports the given message
        """
        if self.has_header():
            return self.header_record["ProtocolVersion"] == "Roche ASTM+"
        return False

    def read(self):
        """Returns a list of ASTMDataResult objects
        """
        data = {}
        data["id"] = self.order_record["SpecimenID"]
        data["keyword"] = self.results_record["TestID"]
        data["result"] = self.results_record["DataMeasurementResultScalar"]
        data["capture_date"] = self.results_record["DateTimeTestCompleted"]

        return [data]
