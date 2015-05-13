#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tkinter as tk
import threading

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector #import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.object_connector import InputObjectConnector

from ComssServiceDevelopment.development import DevServiceController #import modułu klasy testowego kontrolera usługi
import cv2 #import modułu biblioteki OpenCV
import numpy as np #import modułu biblioteki Numpy

service_controller = DevServiceController("face_comparator_service.json") #utworzenie obiektu kontroletra testowego, jako parametr podany jest plik konfiguracji usługi, do której "zaślepka" jest dołączana
service_controller.declare_connection("videoOutput", InputMessageConnector(service_controller)) #deklaracja interfejsu wejściowego konektora msg_stream_connector, należy zwrócić uwagę, iż identyfikator musi być zgodny z WYJŚCIEM usługi, do której "zaślepka" jest podłączana
service_controller.declare_connection("authorizationOnOutput", InputObjectConnector(service_controller))
service_controller.declare_connection("userOutput", InputMessageConnector(service_controller))

connection = service_controller.get_connection("videoOutput") #utworzenie połączenia wejściwoego należy zwrócić uwagę, iż identyfikator musi być zgodny z WYJŚCIEM usługi, do której "zaślepka" jest podłączana
connection_user = service_controller.get_connection("userOutput")


def watch_user():
    user = connection_user.read()
    print user

threading.Thread(target=watch_user).start()

while True: #główna pętla programu
    obj = connection.read() #odczyt danych z interfejsu wejściowego
    frame = np.loads(obj) #załadownaie ramki do obiektu NumPy
    cv2.imshow('Autoryzacja', frame) #wyświetlenie ramki na ekran
    cv2.waitKey(1)