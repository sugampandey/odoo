from .schema_generator import ResponseSchemaGenerator
from typing import List, Optional
import time

class ErrorDetail(ResponseSchemaGenerator):
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        detail: Optional[str] = None,
        element: Optional[str] = None
    ):
        self.message = message
        self.detail = detail
        self.code = code
        self.element = element

    def to_dict(self) -> dict:
        return {
            'message': self.message,
            'detail': self.detail,
            'code': self.code,
            'element': self.element
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            message=data.get('message', ''),
            detail=data.get('detail'),
            code=data.get('code', ''),
            element=data.get('element')
        )

class FaultModel(ResponseSchemaGenerator):
    def __init__(
        self,
        error: List[ErrorDetail],
        type: Optional[str] = None
    ):
        self.error = error
        self.type = type

    def to_dict(self) -> dict:
        return {
            'error': [error.to_dict() for error in self.error],
            'type': self.type
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            error=[ErrorDetail.from_dict(error) for error in data.get('error', [])],
            type=data.get('type', '')
        )

class ResponseHeaderModel(ResponseSchemaGenerator):
    def __init__(
        self,
        status: int,
        message: str,
        intuitTid: Optional[str] = None,
        realmID: Optional[str] = None
    ):
        self.status = status
        self.message = message
        self.intuitTid = intuitTid
        self.realmID = realmID

    def to_dict(self) -> dict:
        return {
            'status': self.status,
            'message': self.message,
            'intuitTid': self.intuitTid,
            'realmID': self.realmID
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            status=data.get('status', 0),
            message=data.get('message', ''),
            intuitTid=data.get('intuitTid', ''),
            realmID=data.get('realmID', '')
        )

class ResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        fault: Optional[FaultModel],
        # time: int,
        batchItemResponse: Optional[List[dict]] = None,
        attachableResponse: Optional[List[dict]] = None,
        warnings: Optional[dict] = None,
        intuitObject: Optional[dict] = None,
        report: Optional[dict] = None,
        queryResponse: Optional[dict] = None,
        syncErrorResponse: Optional[dict] = None,
        requestId: Optional[str] = None,
        status: Optional[str] = None,
        cdcresponse: Optional[List[dict]] = None,
    ):
        self.warnings = warnings
        self.intuitObject = intuitObject
        self.fault = fault
        self.report = report
        self.queryResponse = queryResponse
        self.batchItemResponse = batchItemResponse
        self.attachableResponse = attachableResponse
        self.syncErrorResponse = syncErrorResponse
        self.requestId = requestId
        self.time = int(time.time() * 1000)
        self.status = status
        self.cdcresponse = cdcresponse

    def to_dict(self) -> dict:
        return {
            'warnings': self.warnings,
            'intuitObject': self.intuitObject,
            'fault': self.fault.to_dict() if self.fault else None,
            'report': self.report,
            'queryResponse': self.queryResponse,
            'batchItemResponse': self.batchItemResponse,
            'attachableResponse': self.attachableResponse,
            'syncErrorResponse': self.syncErrorResponse,
            'requestId': self.requestId,
            'time': self.time,
            'status': self.status,
            'cdcresponse': self.cdcresponse
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            warnings=data.get('warnings'),
            intuitObject=data.get('intuitObject'),
            fault=FaultModel.from_dict(data['fault']) if data.get('fault') else None,
            report=data.get('report'),
            queryResponse=data.get('queryResponse'),
            batchItemResponse=data.get('batchItemResponse', []),
            attachableResponse=data.get('attachableResponse', []),
            syncErrorResponse=data.get('syncErrorResponse'),
            requestId=data.get('requestId'),
            time=data.get('time', 0),
            status=data.get('status'),
            cdcresponse=data.get('cdcresponse', [])
        )

class ErrorResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        responseHeader: ResponseHeaderModel,
        response: ResponseModel
    ):
        self.responseHeader = responseHeader
        self.response = response

    def to_dict(self) -> dict:
        return {
            'responseHeader': self.responseHeader.to_dict(),
            'response': self.response.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            responseHeader=ResponseHeaderModel.from_dict(data.get('responseHeader', {})),
            response=ResponseModel.from_dict(data.get('response', {}))
        )

ERROR_SCHEMA = ErrorResponseModel.get_schema()