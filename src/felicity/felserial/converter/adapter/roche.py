# -*- coding: utf-8 -*-

from felicity.felserial.converter.adapter.generic import ASTMBaseAdapter, HL7BaseAdapter


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
        data["raw_message"] = self.message

        return [data]


class RocheCOBAS68008800Hl7Adapter(HL7BaseAdapter):
    """Adapter for COBAS 6800/8800 HL7 messages
    """

    def __init__(self, message):
        super(RocheCOBAS68008800Hl7Adapter, self).__init__(message)

    @property
    def header_record(self):
        """
        Returns a dict that represents the header of the message
        """
        # MSH|^~\&|COBAS6800/8800||LIS||20230123104355||OUL^R22|13968052-baa9-474c-91bb-f7cf19d988fe|P|2.5||||||ASCII
        message_type = self.get_field(self.raw_header_record, 8)
        return {
            "RecordTypeId": self.get_field(self.raw_header_record, 0),
            "FieldDelimiter": self.field_delimiter,
            "RepeatDelimiter": self.repeat_delimiter,
            "ComponentDelimiter": self.component_delimiter,
            "SubComponentDelimiter": self.sub_component_delimiter,
            "EscapeDelimiter": self.escape_delimiter,
            "SendingApplication": self.get_field(self.raw_header_record, 2),
            "ReceivingApplication": self.get_field(self.raw_header_record, 4),
            "DateTimeOfMessage": self.get_field(self.raw_header_record, 6),
            "MesageCode": self.get_component(message_type, 0),
            "TriggerEvent": self.get_component(message_type, 1),
            "MessageControlId": self.get_field(self.raw_header_record, 9),
            "ProcessingId": self.get_field(self.raw_header_record, 10),
            "VersionId": self.get_field(self.raw_header_record, 11),
            "CharacterSet": self.get_field(self.raw_header_record, 17),
        }

    @property
    def patient_record(self):
        return {}

    @property
    def specimen_record(self):
        # SPM||BP23-04444||PLAS^plasma^HL70487|||||||P||||||||||||||||
        specimen_type = self.get_field(self.raw_specimen_record, 4)
        return {
            "RecordTypeId": self.get_field(self.raw_specimen_record, 0),
            "SpecimenId": self.get_field(self.raw_specimen_record, 2),
            "SpecimenTypeIdentifier": self.get_component(specimen_type, 0),
            "SpecimenTypeText": self.get_component(specimen_type, 1),
            "SpecimenTypeCoding": self.get_component(specimen_type, 2),
            "SpecimenRole": self.get_field(self.raw_specimen_record, 11),
        }

    @property
    def observation_request_record(self):
        # OBR|1|||70241-5^HIV^LN|||||||A
        universal_service = self.get_field(
            self.raw_observation_request_record, 4)
        return {
            "RecordTypeId": self.get_field(self.raw_observation_request_record, 0),
            "UniversalServiceIdentifier": self.get_component(universal_service, 0),
            "UniversalServiceText": self.get_component(universal_service, 1),
            "UniversalServiceCoding": self.get_component(universal_service, 2),
            "SpecimenActionCode": self.get_field(self.raw_observation_request_record, 11),
        }

    @property
    def test_code_record(self):
        # TCD|70241-5^HIV^LN|^1^:^0
        universal_service = self.get_field(
            self.raw_test_code_record, 1)
        return {
            "RecordTypeId": self.get_field(self.raw_test_code_record, 0),
            "UniversalServiceIdentifier": self.get_component(universal_service, 0),
            "UniversalServiceText": self.get_component(universal_service, 1),
            "UniversalServiceCoding": self.get_component(universal_service, 2),
            "AutoDilutionFactor": self.get_field(self.raw_test_code_record, 2),
        }

    def get_result_metadata(self, record):
        # OBX|1|ST|HIV^HIV^99ROC||ValueNotSet|||BT|||F|||||Lyna||C6800/8800^Roche^^~Unknown^Roche^^~ID_000000000012076380^IM300-002765^^|20230120144614|||||||||386_neg^^99ROC~385_pos^^99ROC
        # OBX|2|NA|HIV^HIV^99ROC^S_OTHER^Other Supplemental^IHELAW||41.47^^37.53||||||F|||||Lyna||C6800/8800^Roche^^~Unknown^Roche^^~ID_000000000012076380^IM300-002765^^|20230120144614|||||||||386_neg^^99ROC~385_pos^^99ROC
        # OBX|3|ST|70241-5^HIV^LN|1/1|ValueNotSet|||RR|||F|||||Lyna||C6800/8800^Roche^^~Unknown^Roche^^~ID_000000000012076380^IM300-002765^^|20230120144614|||||||||386_neg^^99ROC~385_pos^^99ROC
        # OBX|4|ST|70241-5^HIV^LN|1/2|< Titer min|||""|||F|||||Lyna||C6800/8800^Roche^^~Unknown^Roche^^~ID_000000000012076380^IM300-002765^^|20230120144614|||||||||386_neg^^99ROC~385_pos^^99ROC
        return {
            "RecordTypeId": self.get_field(record, 0),
            "ValueType": self.get_field(record, 2),
            "ObservationSubID": self.get_field(record, 4),
            "ObservationValue": self.get_field(record, 5),
            "Units": self.get_field(record, 6),
            "ReferenceRange": self.get_field(record, 7),
            "AbnormalFlags": self.get_field(record, 8),
            "ObservationResultStatus": self.get_field(record, 11),
            "ResponsibleObserver": self.get_field(record, 16),
            "DateTimeofAnalysis": self.get_field(record, 19),
        }

    def resolve_final_result_record(self, records):
        """Returns the result record (raw) to be considered as the final result
        """
        if isinstance(records, dict):
            return records

        if len(records) == 1:
            return self.get_result_metadata(records[0])

        for record in records:
            meta = self.get_result_metadata(record)
            if self.is_final_result(meta):
                if meta["ObservationValue"] == "Titer":
                    return self.get_result_metadata(records[0])
                return meta

        return self.get_result_metadata(records[0])

    def is_final_result(self, meta_result):
        """Returns whether a (R)sult record must be considered as the final result or not
        """
        if meta_result["ObservationSubID"] == "1/2":
            return True
        return False

    @property
    def observation_record(self):
        return self.resolve_final_result_record(self.raw_observation_record)

    def is_supported(self):
        """Returns whether the current adapter supports the given message
        """
        if self.has_header():
            return self.header_record["SendingApplication"] == "COBAS6800/8800"
        return False

    def read(self):
        """Returns a list of ASTMDataResult objects
        """
        data = {}
        data["id"] = self.specimen_record["SpecimenId"]
        data["keyword"] = self.test_code_record["UniversalServiceText"]
        data["result"] = self.observation_record["ObservationValue"]
        data["capture_date"] = self.observation_record["DateTimeofAnalysis"]
        data["raw_message"] = self.message
        return [data]
