#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector #import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.object_connector import InputObjectConnector, OutputObjectConnector
from collections import Counter

from ComssServiceDevelopment.service import Service, ServiceController #import modułów klasy bazowej Service oraz kontrolera usługi
import cv2 #import modułu biblioteki OpenCV
import numpy as np #import modułu biblioteki Numpy
from recognize import recognize

class FaceComparatorService(Service): #klasa usługi musi dziedziczyć po ComssServiceDevelopment.service.Service
    def __init__(self):			#"nie"konstruktor, inicjalizator obiektu usługi
        super(FaceComparatorService, self).__init__() #wywołanie metody inicjalizatora klasy nadrzędnej

        self.photos_lock = threading.RLock() #obiekt pozwalający na blokadę wątku
        self.photos_count = 0
        self.photos = []
        self.authorization = 0

    def declare_outputs(self):	#deklaracja wyjść
        self.declare_output("videoOutput", OutputMessageConnector(self)) #deklaracja wyjścia "videoOutput" będącego interfejsem wyjściowym konektora msg_stream_connector
        self.declare_output("authorizationOnOutput", OutputObjectConnector(self))
        self.declare_output("userOutput", OutputMessageConnector(self))
        self.declare_output("photosRecognizedOutput", OutputObjectConnector(self))

    def declare_inputs(self): #deklaracja wejść
        self.declare_input("videoInput", InputMessageConnector(self)) #deklaracja wejścia "videoInput" będącego interfejsem wyjściowym konektora msg_stream_connector
        self.declare_input("authorizationOnInput", InputObjectConnector(self))
        self.declare_input("photosInput", InputMessageConnector(self))

    def watch_authorization(self):
        authorization_input = self.get_input("authorizationOnInput")
        authorization_output = self.get_output("authorizationOnOutput")
        while self.running():
            self.authorization = authorization_input.read()
            authorization_output.send(self.authorization)

    def watch_photos(self): #metoda obsługująca strumień sterujacy parametrem usługi
        photos_input = self.get_input("photosInput") #obiekt interfejsu wejściowego
        user_output = self.get_output("userOutput")
        photos_recognized_output = self.get_output("photosRecognizedOutput")
        while self.running(): #główna pętla wątku obsługującego strumień sterujący
            self.photos_count = self.get_parameter("photosCount") #pobranie wartości parametru "photosCount"
            if len(self.photos) < self.photos_count:
                photo = np.loads(photos_input.read())
                label,confidence, name = recognize(photo, "eigenModel.xml", 12000)
                self.photos.append(name)
                print "send output with count", str(len(self.photos)), "label: ", str(label), "confidence: ", str(confidence)
                photos_recognized_output.send(len(self.photos))
#                photos_output.send(photo.dumps())
            else:
                counter = Counter(self.photos)
                most_common = [el for el, count in counter.most_common(1)][0]
                ratio = self.photos.count(most_common)/self.photos_count;
                if ratio > 0.6:
                    print ("sending " + most_common)
                    user_output.send(most_common)
                else:
                    user_output.send("UNKNOWN")

            print str(len(self.photos)), str(self.photos_count)

    def run(self):	#główna metoda usługi
        threading.Thread(target=self.watch_authorization).start()
        threading.Thread(target=self.watch_photos).start() #uruchomienie wątku obsługującego strumień sterujący

        video_input = self.get_input("videoInput")	#obiekt interfejsu wejściowego
        video_output = self.get_output("videoOutput") #obiekt interfejsu wyjściowego

        while self.running():   #pętla główna usługi
            frame_obj = video_input.read()  #odebranie danych z interfejsu wejściowego
            frame = np.loads(frame_obj)     #załadowanie ramki do obiektu NumPy

            video_output.send(frame.dumps()) #przesłanie ramki za pomocą interfejsu wyjściowego

if __name__=="__main__":
    sc = ServiceController(FaceComparatorService, "face_comparator_service.json") #utworzenie obiektu kontrolera usługi
    sc.start() #uruchomienie usługi
