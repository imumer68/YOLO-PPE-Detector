import streamlit as st
from ultralytics import YOLO
import cv2
from PIL import Image
import numpy as np
import tempfile

# Load your model
model = YOLO('best.pt')

# Function to process the frame and perform predictions
def process_frame(frame):
  results = model.predict(source=frame, save=False, show=False)
  for result in results:
    boxes = result.boxes
    for box in boxes:
      coords = box.xyxy[0].tolist()
      x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
      cls = int(box.cls.item())
      conf = box.conf.item()
      label = f'{model.names[cls]}: {conf:.2f}'  # Use model.names for class labels
      cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
      cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
  return frame

# Streamlit App
st.title('YOLO Object Detection')
st.write('Upload an image or video and the model detects the objects and shows the output.')

uploaded_file = st.file_uploader("Choose an image or video...", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])

if uploaded_file is not None:
  # If the uploaded file is an image
  if uploaded_file.type in ["image/jpg", "image/jpeg", "image/png"]:
    image = Image.open(uploaded_file)
    frame = np.array(image)
    processed_frame = process_frame(frame)
    st.image(processed_frame, caption='Processed Image', use_column_width=True)

  # If the uploaded file is a video
  elif uploaded_file.type in ["video/mp4", "video/avi", "video/mov"]:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    cap = cv2.VideoCapture(tfile.name)
    stframe = st.empty()

    while cap.isOpened():
      ret, frame = cap.read()
      if not ret:
        break
      # Convert BGR frame to RGB
      frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      processed_frame = process_frame(frame_rgb)
      stframe.image(processed_frame, channels="RGB")

    cap.release()
