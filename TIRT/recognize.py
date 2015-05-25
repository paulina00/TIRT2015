__author__ = 'Agnieszka'
import os
import cv2
import numpy as np

THRESHOLD = 10000.0;


def recognize(image, model_path, confidence):
    model = cv2.createEigenFaceRecognizer(threshold=THRESHOLD)
    model.load(model_path)
    image = cv2.resize(image, (256,256))
    [p_label, p_confidence] = model.predict(image)

    print "Predicted label = %d (confidence=%.2f)" % (p_label, p_confidence)

    path = os.path.join(os.path.dirname(__file__), 'faces')
    subject = "UNKNOWN";
    # If the model found something, print the file path
    if p_label > -1:
        count = 0
        for dirname, dirnames, filenames in os.walk(path):
            for subdirname in dirnames:
                subject_path = os.path.join(dirname, subdirname)
                if (count == p_label):
                    for filename in os.listdir(subject_path):
                        subject = subdirname

                count = count+1
    if (p_confidence < confidence):
        print "hello %s" %subject
    else:
        print "not authorized"
        p_label = -1
    return p_label, p_confidence, subject

#https://shkspr.mobi/blog/2014/06/which-painting-do-you-look-like-comparing-faces-using-python-and-opencv/
if __name__ == "__main__":
    model = cv2.createEigenFaceRecognizer(threshold=THRESHOLD)

    # Load the model
    model.load("eigenModel.xml")

    # Read the image we're looking for
    sampleImage = cv2.imread("Paulina3.png", cv2.IMREAD_GRAYSCALE)
    sampleImage = cv2.resize(sampleImage, (256,256))

    # Look through the model and find the face it matches
    [p_label, p_confidence] = model.predict(sampleImage)

    # Print the confidence levels
    print "Predicted label = %d (confidence=%.2f)" % (p_label, p_confidence)

    path = os.path.join(os.path.dirname(__file__), 'faces')
    subject = "";
    # If the model found something, print the file path
    if (p_label > -1):
        count = 0
        for dirname, dirnames, filenames in os.walk(path):
            for subdirname in dirnames:
                subject_path = os.path.join(dirname, subdirname)
                if (count == p_label):
                    for filename in os.listdir(subject_path):
                        subject = subdirname

                count = count+1

    if (p_confidence < 2000):
        print "hello %s" %subject;
    else:
        print "not authorized";
