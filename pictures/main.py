import cv2

video = cv2.VideoCapture("output.avi")

cnt_img = 0
while True:
    ret, frame = video.read()
    if not ret:
        break
    inv_frame = cv2.bitwise_not(frame)
    gray = cv2.cvtColor(inv_frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 2 and cv2.contourArea(contours[0]) > 70000 and cv2.contourArea(contours[1]) > 70000:
        cnt_img += 1
        cv2.imshow("Frame", frame)
    if cv2.waitKey(2) & 0xFF == ord('q'):
        break
video.release()
cv2.destroyAllWindows()
print(cnt_img)