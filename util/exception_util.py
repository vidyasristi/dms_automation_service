from service.cleanup_service import CleanUpService

cleanupService = CleanUpService()


class ProcessingException(Exception):
    def __init__(self, provisioned_resources, exception):
        #TODO:Do kwargs here and dont delete rep instance if it in inputs. given arn, should not delete isntance
        print("Received a processing exception. Cleaning up provisioned resources: " + str(exception))
        cleanupService.cleanup_resources(provisioned_resources)
        raise Exception("Exception occurred while creating DMS migration: " + str(exception))
