import re

class URID:
    @staticmethod
    def generate(region, id):
        return region.upper() + '_' + str(id)

    @staticmethod
    def getId(urid):
        return int(re.sub(r'[A-Z]+_', '', urid))

    @staticmethod
    def getRegion(urid):
        return re.search('[A-Z]+', urid).group(0)
