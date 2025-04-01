import cv2
cap = cv2.VideoCapture("rtsp://admin:Amb034Ay@10.5.29.54/cam/realmonitor?channel=1&subtype=0")
#rtsp://admin:Amb034Ay@10.5.29.54/cam/realmonitor?channel=1&subtype=0
while cap.isOpened():
    ret, frame = cap.read()
    print(ret)
    if ret:
        cv2.imshow("ev2_cam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
cap.release()