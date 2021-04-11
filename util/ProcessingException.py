from service.cleanup_service import CleanUpService

cleanupService = CleanUpService()


class ProcessingException(Exception):
    def __init__(self, provisioned_resources):
        print("Received a processing exception. Cleaning up provisioned resources")
        cleanupService.cleanup_resources(provisioned_resources)
        raise Exception("There was a processing exception")
