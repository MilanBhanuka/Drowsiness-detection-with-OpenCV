# Drowsy Driver Detection System

This project detects drowsy driving by monitoring eye aspect ratios in real-time using a webcam. If the driver's eyes are detected to be closed for a prolonged period, an alarm is triggered.

## Prerequisites

Clone the repository:
```bash
git clone https://github.com/MilanBhanuka/Drowsiness-detection-with-OpenCV.git
cd Drowsiness-detection-with-OpenCV

```




Make sure you have Python 3 installed. The following packages are required:

- `numpy`
- `scipy`
- `imutils`
- `playsound`
- `argparse`
- `dlib`
- `opencv-python`
- `imutils`

You can install these dependencies using `pip`:

```bash
pip install numpy scipy imutils playsound argparse dlib opencv-python
```



## Running the Script

Download the Shape Predictor File: Download the shape_predictor_68_face_landmarks.dat file from the dlib model repository and place it in the root directory of this project.

Prepare an Alarm Sound File: Ensure you have an .mp3 file for the alarm sound. Place it in the root directory or specify its path.

To start the drowsy driver detection system, use the following command:
```bash
python test.py --shape-predictor shape_predictor_68_face_landmarks.dat --alarm alarm.mp3
```
