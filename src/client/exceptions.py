class FssaClientException(Exception):
    pass


class FssaAnnouncementException(FssaClientException):
    pass


class FssaEventException(FssaClientException):
    pass


class FssaDocumentException(FssaClientException):
    pass


class FssaLogException(FssaClientException):
    pass
