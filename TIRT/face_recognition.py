#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector #import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.object_connector import InputObjectConnector, OutputObjectConnector

from ComssServiceDevelopment.service import Service, ServiceController #import modułów klasy bazowej Service oraz kontrolera usługi
import cv2 #import modułu biblioteki OpenCV
import numpy as np #import modułu biblioteki Numpy

class FaceRecognitionService(Service): #klasa usługi musi dziedziczyć po ComssServiceDevelopment.service.Service
    def __init__(self):			#"nie"konstruktor, inicjalizator obiektu usługi
        super(FaceRecognitionService, self).__init__() #wywołanie metody inicjalizatora klasy nadrzędnej

        self.filters_lock = threading.RLock() #obiekt pozwalający na blokadę wątku
        self.faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    def declare_outputs(self):	#deklaracja wyjść
        self.declare_output("videoOutput", OutputMessageConnector(self)) #deklaracja wyjścia "videoOutput" będącego interfejsem wyjściowym konektora msg_stream_connector
        self.declare_output("authorizationOnOutput", OutputObjectConnector(self))
        self.declare_output("photosOutput", OutputMessageConnector(self))

    def declare_inputs(self): #deklaracja wejść
        self.declare_input("videoInput", InputMessageConnector(self)) #deklaracja wejścia "videoInput" będącego interfejsem wyjściowym konektora msg_stream_connector
        self.declare_input("authorizationOnInput", InputObjectConnector(self))

    def run(self):	#główna metoda usługi
        video_input = self.get_input("videoInput")	#obiekt interfejsu wejściowego
        authorization_input = self.get_input("authorizationOnInput")
        video_output = self.get_output("videoOutput") #obiekt interfejsu wyjściowego
        authorization_output = self.get_output("authorizationOnOutput")

        while self.running():   #pętla główna usługi
            frame_obj = video_input.read()  #odebranie danych z interfejsu wejściowego
            frame = np.loads(frame_obj)     #załadowanie ramki do obiektu NumPy
            authorization = authorization_input.read()
#            with self.filters_lock:     #blokada wątku
#                current_filters = self.get_parameter("filtersOn") #pobranie wartości parametru "filtersOn"

            if authorization == 1:
# Detect faces in the image
                faces = self.faceCascade.detectMultiScale(
                    frame,
                    scaleFactor=1.2,
                    minNeighbors=5,
                    minSize=(100, 100),
                    flags = cv2.cv.CV_HAAR_SCALE_IMAGE)

                for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            video_output.send(frame.dumps()) #przesłanie ramki za pomocą interfejsu wyjściowego
            authorization_output.send(authorization)

if __name__=="__main__":
    sc = ServiceController(FaceRecognitionService, "face_recognition.json") #utworzenie obiektu kontrolera usługi
    sc.start() #uruchomienie usługi
