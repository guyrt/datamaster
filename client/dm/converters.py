

from dm.datamaster import WriteableFileName

from py4j.java_gateway import JavaClass


class WriteableFileNameConverter(object):

    def can_convert(self, object):
        return isinstance(object, WriteableFileName)
    
    def convert(self, object, gateway_client):
        str_representation = str(object)
        String = JavaClass("java.lang.String", gateway_client)
        return String(str_representation)
