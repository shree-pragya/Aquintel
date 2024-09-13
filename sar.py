# -*- coding: utf-8 -*-
"""SAR.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mOlue86sFJ-xfCwdlclfA_lpfvp6PSmq
"""

from google.colab import drive
drive.mount('/content/gdrive', force_remount=True)

!pip install tensorflow torch torchvision opencv-python matplotlib

!pip install tensorflow keras opencv-python scikit-learn matplotlib

import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam

from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, concatenate, Conv2DTranspose
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import tensorflow as tf

import cv2
import os
import matplotlib.pyplot as plt


original_folder = "/content/gdrive/MyDrive/SARDATA/original"
ground_truth_folder = "/content/gdrive/MyDrive/SARDATA/ground truth"
IMG_SIZE = 256


def visualize_original_and_ground_truth(img_idx):

    img_path = os.path.join(original_folder, f"im ({img_idx}).jpg")
    img = cv2.imread(img_path)
    img_resized = cv2.resize(img, (IMG_SIZE, IMG_SIZE))


    gt_path = os.path.join(ground_truth_folder, f"{img_idx}.jpg")
    gt = cv2.imread(gt_path)
    gt_resized = cv2.resize(gt, (IMG_SIZE, IMG_SIZE))


    plt.figure(figsize=(10, 5))


    plt.subplot(1, 2, 1)
    plt.title(f"Original SAR Image im({img_idx}).jpg")
    plt.imshow(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
    plt.axis('off')


    plt.subplot(1, 2, 2)
    plt.title(f"Ground Truth Image {img_idx}.jpg")
    plt.imshow(cv2.cvtColor(gt_resized, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    plt.show()


visualize_original_and_ground_truth(103)

def unet_model(input_size=(256, 256, 1)):
    inputs = Input(input_size)

    # Contracting Path (Encoder)
    conv1 = Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
    conv1 = Conv2D(64, (3, 3), activation='relu', padding='same')(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = Conv2D(128, (3, 3), activation='relu', padding='same')(pool1)
    conv2 = Conv2D(128, (3, 3), activation='relu', padding='same')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    conv3 = Conv2D(256, (3, 3), activation='relu', padding='same')(pool2)
    conv3 = Conv2D(256, (3, 3), activation='relu', padding='same')(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

    conv4 = Conv2D(512, (3, 3), activation='relu', padding='same')(pool3)
    conv4 = Conv2D(512, (3, 3), activation='relu', padding='same')(conv4)
    pool4 = MaxPooling2D(pool_size=(2, 2))(conv4)

    # Bottom of U-Net
    conv5 = Conv2D(1024, (3, 3), activation='relu', padding='same')(pool4)
    conv5 = Conv2D(1024, (3, 3), activation='relu', padding='same')(conv5)

    # Expanding Path (Decoder)
    up6 = Conv2DTranspose(512, (2, 2), strides=(2, 2), padding='same')(conv5)
    up6 = concatenate([up6, conv4])
    conv6 = Conv2D(512, (3, 3), activation='relu', padding='same')(up6)
    conv6 = Conv2D(512, (3, 3), activation='relu', padding='same')(conv6)

    up7 = Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same')(conv6)
    up7 = concatenate([up7, conv3])
    conv7 = Conv2D(256, (3, 3), activation='relu', padding='same')(up7)
    conv7 = Conv2D(256, (3, 3), activation='relu', padding='same')(conv7)

    up8 = Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(conv7)
    up8 = concatenate([up8, conv2])
    conv8 = Conv2D(128, (3, 3), activation='relu', padding='same')(up8)
    conv8 = Conv2D(128, (3, 3), activation='relu', padding='same')(conv8)

    up9 = Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(conv8)
    up9 = concatenate([up9, conv1])
    conv9 = Conv2D(64, (3, 3), activation='relu', padding='same')(up9)
    conv9 = Conv2D(64, (3, 3), activation='relu', padding='same')(conv9)

    outputs = Conv2D(1, (1, 1), activation='sigmoid')(conv9)

    model = Model(inputs=[inputs], outputs=[outputs])

    return model

unet = unet_model()


unet.compile(optimizer=Adam(learning_rate=1e-4), loss='binary_crossentropy', metrics=['accuracy'])

unet.summary()

original_folder = "/content/gdrive/MyDrive/SARDATA/original"
ground_truth_folder = "/content/gdrive/MyDrive/SARDATA/ground truth"
IMG_SIZE = 256
def load_data_for_unet(img_folder, gt_folder, img_size):
    images = []
    masks = []

    #range cyan
    lower_cyan = np.array([180, 180, 0])  # LB
    upper_cyan = np.array([255, 255, 100])  # UB

    for i in range(1, 790):
        # original
        img_path = os.path.join(img_folder, f"im ({i}).jpg")
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (img_size, img_size))

        # ground truth
        gt_path = os.path.join(gt_folder, f"{i}.jpg")
        gt = cv2.imread(gt_path)
        gt = cv2.resize(gt, (img_size, img_size))

        # binary mask banaraha
        cyan_mask = cv2.inRange(gt, lower_cyan, upper_cyan)

        # Normalize and append the SAR image and mask
        images.append(img / 255.0)
        masks.append(cyan_mask / 255.0)

    return np.array(images).reshape(-1, img_size, img_size, 1), np.array(masks).reshape(-1, img_size, img_size, 1)


X, y = load_data_for_unet(original_folder, ground_truth_folder, IMG_SIZE)


X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

history = unet.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=30,
    batch_size=8
)

#test
val_loss, val_acc = unet.evaluate(X_val, y_val)
print(f"Validation Accuracy: {val_acc * 100:.2f}%")


def predict_oil_spill_unet(img):
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE)) / 255.0
    img = img.reshape(1, IMG_SIZE, IMG_SIZE, 1)
    prediction_mask = unet.predict(img)
    return prediction_mask[0]

test_img = cv2.imread("/content/gdrive/MyDrive/SARDATA/original/im (1).jpg", cv2.IMREAD_GRAYSCALE)
predicted_mask = predict_oil_spill_unet(test_img)


plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.title('Original Image')
plt.imshow(test_img, cmap='gray')
plt.subplot(1, 2, 2)
plt.title('Predicted Oil Spill Mask')
plt.imshow(predicted_mask.squeeze(), cmap='gray')
plt.show()

unet.save('unet_SAR.keras', include_optimizer=False)

from keras.models import load_model
from keras.optimizers import Adam

#
unet = load_model('/content/unet_SAR.keras')


unet.compile(optimizer=Adam(learning_rate=1e-4), loss='binary_crossentropy', metrics=['accuracy'])

# Evaluate the model on the validation set
val_loss, val_accuracy = unet.evaluate(X_val, y_val)

print(f"Validation Loss: {val_loss}")
print(f"Validation Accuracy: {val_accuracy}")

def preprocess_image_for_unet(img_path, img_size):
    # Load and preprocess the test SAR image
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (img_size, img_size))
    img = img / 255.0  # Normalize
    img = np.expand_dims(img, axis=-1)  # Add channel dimension
    img = np.expand_dims(img, axis=0)   # Add batch dimension
    return img

# Load the saved U-Net model
unet = load_model('unet_SAR.keras')

# Path to the new test image (example)
test_img_path = "/content/gdrive/MyDrive/SARDATA/original/im (103).jpg"

# Preprocess the test image
test_img = preprocess_image_for_unet(test_img_path, IMG_SIZE)

# Make prediction
predicted_mask = unet.predict(test_img)

# Post-process the prediction (convert to binary mask)
predicted_mask = (predicted_mask > 0.5).astype(np.uint8)  # Thresholding to get binary mask

# Visualize the test image and predicted mask
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))

# Original Test Image
plt.subplot(1, 2, 1)
plt.title("Test SAR Image")
plt.imshow(test_img[0].reshape(IMG_SIZE, IMG_SIZE), cmap='gray')

# Predicted Mask (Oil Spill Detection)
plt.subplot(1, 2, 2)
plt.title("Predicted Oil Spill Mask")
plt.imshow(predicted_mask[0].reshape(IMG_SIZE, IMG_SIZE), cmap='gray')

plt.show()

import numpy as np
import cv2
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# Define the function for preprocessing the SAR image
def preprocess_image_for_unet(img_path, img_size):
    # Load and preprocess the test SAR image
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Load in grayscale
    img = cv2.resize(img, (img_size, img_size))  # Resize to target size
    img = img / 255.0  # Normalize
    img = np.expand_dims(img, axis=-1)  # Add channel dimension
    img = np.expand_dims(img, axis=0)   # Add batch dimension
    return img

# Load the saved U-Net model
unet = load_model('unet_SAR.keras')

# Paths to test image and its corresponding ground truth mask
test_img_path = "/content/gdrive/MyDrive/dividing data for NN/train-/without oil spill_images/img_0028.jpg"
test_img_mask_path = "/content/gdrive/MyDrive/dividing data for NN/train-/without oil spill_mask/img_0028.png"

# Preprocess the test image
test_img = preprocess_image_for_unet(test_img_path, IMG_SIZE)

# Load the ground truth mask without preprocessing (as an RGB image)
test_img_mask = cv2.imread(test_img_mask_path)  # Load as it is (without conversion to grayscale)

# Make prediction on the preprocessed SAR image
predicted_mask = unet.predict(test_img)

# Post-process the prediction (convert to binary mask)
predicted_mask = (predicted_mask > 0.5).astype(np.uint8)  # Threshold to get binary mask

# Visualize the SAR image, ground truth mask, and predicted mask
plt.figure(figsize=(15, 5))

# Original SAR Image
plt.subplot(1, 3, 1)
plt.title("Original SAR Image")
plt.imshow(test_img[0].reshape(IMG_SIZE, IMG_SIZE), cmap='gray')
plt.axis('off')

# Ground Truth Mask
plt.subplot(1, 3, 2)
plt.title("Ground Truth Mask")
test_img_mask_rgb = cv2.cvtColor(test_img_mask, cv2.COLOR_BGR2RGB)  # Convert to RGB for proper color display
plt.imshow(test_img_mask_rgb)
plt.axis('off')

# Predicted Mask (Oil Spill Detection)
plt.subplot(1, 3, 3)
plt.title("Predicted Oil Spill Mask")
plt.imshow(predicted_mask[0].reshape(IMG_SIZE, IMG_SIZE), cmap='gray')
plt.axis('off')

plt.show()

import numpy as np
import cv2
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# Define the function for preprocessing the SAR image
def preprocess_image_for_unet(img_path, img_size):
    # Load and preprocess the test SAR image
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Load in grayscale
    img = cv2.resize(img, (img_size, img_size))  # Resize to target size
    img = img / 255.0  # Normalize
    img = np.expand_dims(img, axis=-1)  # Add channel dimension
    img = np.expand_dims(img, axis=0)   # Add batch dimension
    return img

# Load the saved U-Net model
unet = load_model('unet_SAR.keras')

# Paths to test image and its corresponding ground truth mask
test_img_path = "/content/gdrive/MyDrive/dividing data for NN/train-/without oil spill_images/img_0045.jpg"
test_img_mask_path = "/content/gdrive/MyDrive/dividing data for NN/train-/without oil spill_mask/img_0045.png"

# Preprocess the test image
test_img = preprocess_image_for_unet(test_img_path, IMG_SIZE)

# Load the ground truth mask without preprocessing (as an RGB image)
test_img_mask = cv2.imread(test_img_mask_path)  # Load as it is (without conversion to grayscale)

# Make prediction on the preprocessed SAR image
predicted_mask = unet.predict(test_img)

# Post-process the prediction (convert to binary mask)
predicted_mask = (predicted_mask > 0.5).astype(np.uint8)  # Threshold to get binary mask

# Visualize the SAR image, ground truth mask, and predicted mask
plt.figure(figsize=(15, 5))

# Original SAR Image
plt.subplot(1, 3, 1)
plt.title("Original SAR Image")
plt.imshow(test_img[0].reshape(IMG_SIZE, IMG_SIZE), cmap='gray')
plt.axis('off')

# Ground Truth Mask
plt.subplot(1, 3, 2)
plt.title("Ground Truth Mask")
test_img_mask_rgb = cv2.cvtColor(test_img_mask, cv2.COLOR_BGR2RGB)  # Convert to RGB for proper color display
plt.imshow(test_img_mask_rgb)
plt.axis('off')

# Predicted Mask (Oil Spill Detection)
plt.subplot(1, 3, 3)
plt.title("Predicted Oil Spill Mask")
plt.imshow(predicted_mask[0].reshape(IMG_SIZE, IMG_SIZE), cmap='gray')
plt.axis('off')

plt.show()

import numpy as np
import cv2
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# Define the function for preprocessing the SAR image
def preprocess_image_for_unet(img_path, img_size):
    # Load and preprocess the test SAR image
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Load in grayscale
    img = cv2.resize(img, (img_size, img_size))  # Resize to target size
    img = img / 255.0  # Normalize
    img = np.expand_dims(img, axis=-1)  # Add channel dimension
    img = np.expand_dims(img, axis=0)   # Add batch dimension
    return img

# Load the saved U-Net model
unet = load_model('unet_SAR.keras')

# Paths to test image and its corresponding ground truth mask
test_img_path = "/content/gdrive/MyDrive/dividing data for NN/train-/with oil spill_images/img_0999.jpg"
test_img_mask_path = "/content/gdrive/MyDrive/dividing data for NN/train-/with oil spill_mask/img_0999.png"

# Preprocess the test image
test_img = preprocess_image_for_unet(test_img_path, IMG_SIZE)

# Load the ground truth mask without preprocessing (as an RGB image)
test_img_mask = cv2.imread(test_img_mask_path)  # Load as it is (without conversion to grayscale)

# Make prediction on the preprocessed SAR image
predicted_mask = unet.predict(test_img)

# Post-process the prediction (convert to binary mask)
predicted_mask = (predicted_mask > 0.5).astype(np.uint8)  # Threshold to get binary mask

# Visualize the SAR image, ground truth mask, and predicted mask
plt.figure(figsize=(15, 5))

# Original SAR Image
plt.subplot(1, 3, 1)
plt.title("Original SAR Image")
plt.imshow(test_img[0].reshape(IMG_SIZE, IMG_SIZE), cmap='gray')
plt.axis('off')

# Ground Truth Mask
plt.subplot(1, 3, 2)
plt.title("Ground Truth Mask")
test_img_mask_rgb = cv2.cvtColor(test_img_mask, cv2.COLOR_BGR2RGB)  # Convert to RGB for proper color display
plt.imshow(test_img_mask_rgb)
plt.axis('off')

# Predicted Mask (Oil Spill Detection)
plt.subplot(1, 3, 3)
plt.title("Predicted Oil Spill Mask")
plt.imshow(predicted_mask[0].reshape(IMG_SIZE, IMG_SIZE), cmap='gray')
plt.axis('off')

plt.show()

def preprocess_image_for_unet(img_path, img_size):
    # Load and preprocess the test SAR image
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (img_size, img_size))
    img = img / 255.0  # Normalize
    img = np.expand_dims(img, axis=-1)  # Add channel dimension
    img = np.expand_dims(img, axis=0)   # Add batch dimension
    return img

# Load the saved U-Net model
unet = load_model('unet_SAR.keras')

# Path to the new test image (example)
test_img_path = "/content/gdrive/MyDrive/dividing data for NN/test-/without oil spill_image/img_0002.jpg"

# Preprocess the test image
test_img = preprocess_image_for_unet(test_img_path, IMG_SIZE)

# Make prediction
predicted_mask = unet.predict(test_img)

# Post-process the prediction (convert to binary mask)
predicted_mask = (predicted_mask > 0.5).astype(np.uint8)  # Thresholding to get binary mask

# Visualize the test image and predicted mask
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))

# Original Test Image
plt.subplot(1, 2, 1)
plt.title("Test SAR Image")
plt.imshow(test_img[0].reshape(IMG_SIZE, IMG_SIZE), cmap='gray')

# Predicted Mask (Oil Spill Detection)
plt.subplot(1, 2, 2)
plt.title("Predicted Oil Spill Mask")
plt.imshow(predicted_mask[0].reshape(IMG_SIZE, IMG_SIZE), cmap='gray')

plt.show()
