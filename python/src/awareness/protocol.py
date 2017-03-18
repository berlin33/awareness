from abc import ABCMeta, abstractproperty, abstractmethod
import misc
import affinity as i_affinity
import algorithm as i_algorithm
import backend as i_backend
import data as i_data
import operator as i_operator


class Protocol:
    __metaclass__ = ABCMeta

    @abstractmethod
    def capabilities(self, connection):
        raise NotImplementedError()

    @abstractmethod
    def search(self, connection, propagationLimit, trainingSet, testSet, progressCallback=None):
        raise NotImplementedError()

    @abstractmethod
    def process(self, index, inputSet, progressCallback=None):
        raise NotImplementedError()


    @abstractmethod
    def provide(self, listener, operator):
        raise NotImplementedError()



class Protocol0(Protocol, misc.Protocol0Constants):


    def capabilities(self, connection):
        
        self.send(connection, self.BLANK, self.CAPABILITIES, (), ())

        unitType = None
        while unitType != self.CAPABILITIES:
            unitType, requestedType, pres, datums = self.receive(connection, self.validProviderToAccessor)

        return datums


    def search(self, connection, propagationLimit, trainingSet, testSet, progressCallback=None):
        
        pass

    def process(self, connection, index, inputSet, progressCallback=None):

        pass


    def send(self, connection, unitType, requestedType, pres, datums):

        unitPreStruct = self.unitPreStructs[unitType]
        unitDatumStruct = self.unitDatumStructs[unitType]

        tranDatums = ''
        tranPres = unitPreStruct.pack(pres)

        for datum in datums:
            tranDatums.append(unitDatumStruct.pack(datum))


        tranHeader = self.pduHeaderStruct.pack(self.VERSION_BYTE, unitType, requestedType, len(tranDatums)+len(tranPres))

        connection.sendall(tranHeader)
        connection.sendall(tranPres)
        connection.sendall(tranDatums)


    def receive(self, connection, valid):

        recvHeader =  connection.recv(self.pduHeaderStruct.size)
        version, unitType, requestedType, dataLen = self.pduHeaderStruct.unpack(recvHeader)
        recvData = connection.recv(dataLen)

        if version != self.VERSION_BYTE:
            self.send(connection, self.UNIT_ERROR, self.NOTHING, (), ())
            return None

        if unitType not in valid or requestedType not in valid[unitType]:
            self.send(connection, self.UNIT_ERROR, self.NOTHING, (), ())
            return None


        try:
            unitPreStruct = self.unitPreStructs[unitType]
            unitDatumStruct = self.unitDatumStructs[unitType]
        except:
            self.send(connection, self.UNIT_ERROR, self.NOTHING, (), ())
            return None


        try:
            pres = unitPreStruct.unpack(recvData[:unitPreStruct.size])
            datums = []
            for i in range(len(recvData[unitPreStruct.size:])):
                startDataIndex = unitPreStruct.size + (i*unitDatumStruct.size)
                dataRoi = recvData[startDataIndex:startDataIndex + unitDatumStruct.size]
                datums.append(unitDatumStruct.unpack(dataRoi))
        except:
            self.send(connection, self.DATA_ERROR, self.NOTHING, (), ())
            return None


        return unitType, requestedType, pres, datums



    def provide(self, listener, operator):

        def handle(self, connection):
            pass
        
        connection, address = listener.accept()

        operator.backend.threadingAsync(handle, (connection))
