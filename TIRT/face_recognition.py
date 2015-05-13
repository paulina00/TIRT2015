#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector #import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.object_connector import InputObjectConnector, OutputObjectConnector

from ComssServiceDevelopment.service import Service, ServiceController #import modułów klasy bazowej Service oraz kontrolera usługi
import cv2 #import modułu biblioteki OpenCV
import numpy as np #import modułu biblioteki Numpy
import time

class FaceRecognitionService(Service): #klasa usługi musi dziedziczyć po ComssServiceDevelopment.service.Service
    def __init__(self):			#"nie"konstruktor, inicjalizator obiektu usługi
        super(FaceRecognitionService, self).__init__() #wywołanie metody inicjalizatora klasy nadrzędnej

        self.photos_lock = threading.RLock() #obiekt pozwalający na blokadę wątku
        self.photos_detected = 0
        self.photos_count = 0
        self.photos_recognized = 0
        self.face = None
        self.frame = None
        self.faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.authorization = 0

    def declare_outputs(self):	#deklaracja wyjść
        self.declare_output("videoOutput", OutputMessageConnector(self)) #deklaracja wyjścia "videoOutput" będącego interfejsem wyjściowym konektora msg_stream_connector
        self.declare_output("authorizationOnOutput", OutputObjectConnector(self))
        self.declare_output("photosOutput", OutputMessageConnector(self))

    def declare_inputs(self): #deklaracja wejść
        self.declare_input("videoInput", InputMessageConnector(self)) #deklaracja wejścia "videoInput" będącego interfejsem wyjściowym konektora msg_stream_connector
        self.declare_input("authorizationOnInput", InputObjectConnector(self))
        self.declare_input("photosRecognizedInput", InputObjectConnector(self))

    def watch_authorization(self):
        authorization_input = self.get_input("authorizationOnInput")
        authorization_output = self.get_output("authorizationOnOutput")
        while self.running():
            self.authorization = authorization_input.read()
            authorization_output.send(self.authorization)

    def watch_photos(self): #metoda obsługująca strumień sterujacy parametrem usługi
        photos_output = self.get_output("photosOutput")
        while self.running(): #główna pętla wątku obsługującego strumień sterujący
            with self.photos_lock:  #blokada wątku
                self.photos_count = self.get_parameter("photosCount") #pobranie wartości parametru "photosCount"
            if self.face is not None and self.frame is not None and self.authorization == 1 and self.photos_detected < self.photos_count and self.photos_detected == self.photos_recognized:
                (x, y, w, h) = self.face
                print "photo ",str(self.photos_recognized),"send!"
                photos_output.send(self.frame[y:y+h, x:x+w].dumps())
                self.photos_detected += 1
                time.sleep(2)

    def watch_photos_recognized(self):
        photos_recognized_input = self.get_input("photosRecognizedInput")
        while self.running():
            if self.authorization == 1:
                self.photos_recognized = photos_recognized_input.read()

    def run(self):	#główna metoda usługi
        threading.Thread(target=self.watch_authorization).start()
        threading.Thread(target=self.watch_photos).start() #uruchomienie wątku obsługującego strumień sterujący
        threading.Thread(target=self.watch_photos_recognized).start()

        video_input = self.get_input("videoInput")	#obiekt interfejsu wejściowego
        video_output = self.get_output("videoOutput") #obiekt interfejsu wyjściowego

        while self.running():   #pętla główna usługi
            frame_obj = video_input.read()  #odebranie danych z interfejsu wejściowego
            self.frame = np.loads(frame_obj)     #załadowanie ramki do obiektu NumPy

            if self.authorization == 1:
# Detect faces in the image
                faces = self.faceCascade.detectMultiScale(
                    self.frame,
                    scaleFactor=1.2,
                    minNeighbors=5,
                    minSize=(100, 100),
                    flags = cv2.cv.CV_HAAR_SCALE_IMAGE)

                if len(faces) > 0:
                    self.face = faces[0]
                    (x, y, w, h) = self.face
                    cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                else:
                    self.face = None

            video_output.send(self.frame.dumps()) #przesłanie ramki za pomocą interfejsu wyjściowego

if __name__=="__main__":
    sc = ServiceController(FaceRecognitionService, "face_recognition.json") #utworzenie obiektu kontrolera usługi
    sc.start() #uruchomienie usługi
