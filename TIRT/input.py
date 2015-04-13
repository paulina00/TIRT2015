#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector #import modułów konektora msg_stream_connector

from ComssServiceDevelopment.development import DevServiceController #import modułu klasy testowego kontrolera usługi

import cv2 #import modułu biblioteki OpenCV
import Tkinter as tk #import modułu biblioteki Tkinter -- okienka

service_controller = DevServiceController("filter1service.json") #utworzenie obiektu kontroletra testowego, jako parametr podany jest plik konfiguracji usługi, do której "zaślepka" jest dołączana
service_controller.declare_connection("videoInput", OutputMessageConnector(service_controller)) #deklaracja interfejsu wyjściowego konektora msg_stream_connector, należy zwrócić uwagę, iż identyfikator musi być zgodny z WEJŚCIEM usługi, do której "zaślepka" jest podłączana


def update_all(root, cam):
    read_successful, frame = cam.read() #odczyt obrazu z kamery

    frame_dump = frame.dumps() #zrzut ramki wideo do postaci ciągu bajtów
    service_controller.get_connection("videoInput").send(frame_dump) #wysłanie danych
    root.update()
    root.after(20, func=lambda: update_all(root, cam))


def authorize():
    service_controller.update_params({"authorizationOn": 1}) #zmiana wartości parametru "authorizationOn" jezeli przycisk byl kliniety


root = tk.Tk()
root.title("Autoryzacja") #utworzenie okienka

cam = cv2.VideoCapture(0) #"podłączenie" do strumienia wideo z kamerki

#obsługa przycisku
button = tk.Button(root, text="Autoryzuj", command=authorize)
button.pack()

root.after(0, func=lambda: update_all(root, cam)) #dołączenie metody update_all do głównej pętli programu, wynika ze specyfiki TKinter
root.mainloop()