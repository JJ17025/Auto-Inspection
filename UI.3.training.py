from datetime import datetime
import time

print(datetime.now())

x = datetime(2023, 11, 7, 3, 0, 0)
print(x)

while True:
    now = datetime.now()
    print((x - now))
    if x < now:
        break
    time.sleep(5)

'''
ปรับให้สร้างภาพขนาดเล็กที่ใช้สร้างโมเดล ที่ละโมเดล
จากเดิม ที่สร้างภาพขนาดเล็ก ทุก class ให้เสร็จก่อน ถึงจะสร้างโมเดล
'''
import json
import os
from datetime import datetime
import shutil
import cv2
import numpy as np
import tensorflow as tf
import keras
from keras import layers, optimizers, models
from keras.models import Sequential, load_model

import pathlib
import matplotlib.pyplot as plt
from Frames import Frames
from Frames import BLACK, FAIL, GREEN, WARNING, BLUE, PINK, CYAN, ENDC, BOLD, ITALICIZED, UNDERLINE
from keras.applications import VGG16


def mkdir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

PCB_name = 'D07'

IMG_FULL_PATH = f'data/{PCB_name}/img_full'
IMG_FRAME_PATH = f'data/{PCB_name}/img_frame'
IMG_FRAME_LOG_PATH = f'data/{PCB_name}/img_frame_log'
MODEL_PATH = f'data/{PCB_name}/model'
frames = Frames(PCB_name)

mkdir(IMG_FULL_PATH)
mkdir(IMG_FRAME_PATH)
mkdir(IMG_FRAME_LOG_PATH)
mkdir(MODEL_PATH)

batch_size = 32
img_height = 180
img_width = 180
epochs = 5
# img_height = 250
# img_width = 250
# epochs = 8
MODEL_SET = 1  # 1,2,3


# MODEL_SET = 1.4

def controller(img, brightness=255, contrast=127):
    brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
    contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            max = 255
        else:
            shadow = 0
            max = 255 + brightness
        al_pha = (max - shadow) / 255
        ga_mma = shadow
        cal = cv2.addWeighted(img, al_pha, img, 0, ga_mma)
    else:
        cal = img

    if contrast != 0:
        Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
        Gamma = 127 * (1 - Alpha)
        cal = cv2.addWeighted(cal, Alpha, cal, 0, Gamma)
    return cal


def corp_img(model_name, frames):
    img_full_namefile_list = os.listdir(IMG_FULL_PATH)
    img_full_namefile_list = list(set(file.split('.')[0] for file in img_full_namefile_list if file.endswith('.png')) &
                                  set(file.split('.')[0] for file in img_full_namefile_list if file.endswith('.txt')))
    img_full_namefile_list = sorted(img_full_namefile_list, reverse=True)
    for i, file_name in enumerate(img_full_namefile_list, start=1):

        # file_name is 0807 143021, ...
        frames_list = open(fr"{IMG_FULL_PATH}/{file_name}.txt").readlines()
        print(f'{i}/{len(img_full_namefile_list)} {file_name}')
        for data_text in frames_list:
            data_list = data_text.strip().split(':')
            frame_name = data_list[0]  # ___________________________________________ ชื่อใน .txt
            status = data_list[1]
            if frame_name not in frames.frames.keys():  # __________________________ ชื่อใน .txt ไม่ตรง
                print((f'{WARNING}{frame_name} not in frames{ENDC}'))
                continue

            x = frames.frames[frame_name].x
            y = frames.frames[frame_name].y
            dx = frames.frames[frame_name].dx
            dy = frames.frames[frame_name].dy

            if frames.frames[frame_name].model_used == model_name:
                print('    ', model_name, frame_name, status, x, y, dx, dy)

                img = cv2.imread(fr"{IMG_FULL_PATH}/{file_name}.png")
                pixels_Y, pixels_X, _ = img.shape

                x1, x2 = int((x - dx / 2) * pixels_X), int((x + dx / 2) * pixels_X)
                y1, y2 = int((y - dy / 2) * pixels_Y), int((y + dy / 2) * pixels_Y)

                img_crop_namefile = f'{status} {frame_name} {file_name}.png'
                mkdir(fr"{IMG_FRAME_PATH}/{model_name}")
                mkdir(fr"{IMG_FRAME_PATH}/{model_name}/{status}")
                mkdir(fr"{IMG_FRAME_LOG_PATH}/{model_name}")

                img_crop = img[y1:y2, x1:x2]
                cv2.imwrite(fr"{IMG_FRAME_LOG_PATH}/{model_name}/{img_crop_namefile}", img_crop)

                for shift_y in [-4, -3, -2, -1, 0, 1, 2, 3, 4]:
                    for shift_x in [-4, -3, -2, -1, 0, 1, 2, 3, 4]:
                        img_crop = img[y1 + shift_y:y2 + shift_y, x1 + shift_x:x2 + shift_x]

                        # add contran blige
                        brightness = [230, 242, 255, 267, 280]
                        contrast = [114, 120, 127, 133, 140]
                        for b in brightness:
                            for c in contrast:
                                img_crop_BC = img_crop.copy()
                                img_crop_BC = controller(img_crop_BC, b, c)

                                # features.append(img_crop_BC)
                                # labels.append(class_names.index(status))
                                img_crop_namefile = f'{file_name} {frame_name} {status} {shift_y} {shift_x} {b} {c}.png'
                                cv2.imwrite(fr"{IMG_FRAME_PATH}/{model_name}/{status}/{img_crop_namefile}", img_crop_BC)

                # # เมื่อcrop img เสร็จ ให้จดชื่อ ภาพที่ crop ไปแล้วไว้
                # with open(fr"{IMG_FRAME_PATH}/{k} Name of the cropped image file.txt", 'a') as file:
                #     file.write(f'{file_name}\n')


######################################################################################################################


def create_model(model_name):
    data_dir = pathlib.Path(rf'{IMG_FRAME_PATH}/{model_name}')

    image_count = len(list(data_dir.glob('*/*.png')))
    plog(f'image_count = {image_count}')

    print('data_dir is ', data_dir)
    train_ds, val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="both",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    class_names = train_ds.class_names
    print('class_names =', class_names)
    with open(fr'{MODEL_PATH}/{model_name}.json', 'w') as file:
        file.write(json.dumps(class_names, indent=4))

    # Visualize the data
    plt.figure(figsize=(20, 10))
    for images, labels in train_ds.take(1):
        for i in range(32):
            ax = plt.subplot(4, 8, i + 1)
            plt.imshow(images[i].numpy().astype("uint8"))
            plt.title(class_names[labels[i]])
            plt.axis("off")
    plt.savefig(f'{MODEL_PATH}/{model_name}.png')

    for image_batch, labels_batch in train_ds:
        print(image_batch.shape)
        print(labels_batch.shape)
        break

    # Configure the dataset for performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    # Standardize the data
    # normalization_layer = layers.Rescaling(1. / 255)

    # normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
    # image_batch, labels_batch = next(iter(normalized_ds))
    # first_image = image_batch[0]
    # # Notice the pixel values are now in `[0,1]`.
    # print(np.min(first_image), np.max(first_image))

    # Create the model
    num_classes = len(class_names)
    cp = True
    if MODEL_SET == 1:
        model = Sequential([
            layers.Rescaling(1. / 255, input_shape=(img_height, img_width, 3)),
            layers.Conv2D(16, (3,3), padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(32, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Dropout(0.2),
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dense(num_classes)
        ])
    if MODEL_SET == 1.4:
        base_model = VGG16(include_top=False, weights='imagenet', input_shape=(img_height, img_width, 3))
        base_model.trainable = False

        model = Sequential([
            base_model,
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ])

    if MODEL_SET == 1.5:
        base_model = tf.keras.applications.ResNet50(include_top=False, weights='imagenet',
                                                    input_shape=(img_height, img_width, 3))

        model = Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(128, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ])

        initial_learning_rate = 0.001
        lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
            initial_learning_rate, decay_steps=10000, decay_rate=0.9
        )

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=lr_schedule),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
            metrics=['accuracy']
        )
        cp = False

    if MODEL_SET == 2:
        model = models.Sequential([
            layers.Input(shape=(img_height, img_width, 3)),
            layers.Conv2D(64, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(256, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation='softmax')
        ])
    if MODEL_SET == 3:
        model = Sequential([
            layers.Rescaling(1. / 255, input_shape=(img_height, img_width, 3)),
            layers.Conv2D(64, 3, padding='same', activation='relu'),
            layers.Conv2D(64, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, padding='same', activation='relu'),
            layers.Conv2D(128, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(256, 3, padding='same', activation='relu'),
            layers.Conv2D(256, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation='softmax')
        ])

    if cp:
        model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])
    model.summary()
    history = model.fit(train_ds, validation_data=val_ds, epochs=epochs)

    # Visualize training results
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    loss = [1 if a > 1 else a for a in loss]
    val_loss = [1 if a > 1 else a for a in val_loss]

    epochs_range = range(epochs)
    plt.figure(figsize=(10, 8))
    plt.plot(epochs_range, val_acc, label='Validation Accuracy', c=(0, 0.8, 0.5))
    plt.plot(epochs_range, acc, label='Training Accuracy', ls='--', c=(0, 0, 1))
    plt.plot(epochs_range, val_loss, label='Validation Loss', c=(1, 0.5, 0.1))
    plt.plot(epochs_range, loss, label='Training Loss', c='r', ls='--')
    plt.legend(loc='right')
    plt.title(model_name)

    # plt.show()
    plt.savefig(fr'{MODEL_PATH}/{model_name}_graf.png')
    model.save(os.path.join(MODEL_PATH, f'{model_name}.h5'))
    # delete IMG_FRAME_PATH
    shutil.rmtree(fr"{IMG_FRAME_PATH}/{model_name}")


def plog(string):
    print(f"{PINK}{string}{ENDC}")
    with open(fr'log.txt', 'a', encoding='utf8') as file:
        file.write(f'{datetime.now().strftime("%m%d-%H%M%S")}| {string}\n')


def f(model_name, model, frames):
    try:
        # if True:
        t1 = datetime.now()
        plog('--------  >>> corp_img <<<  ---------')
        corp_img(model_name, frames)
        t2 = datetime.now()
        plog(f'{t2 - t1} เวลาที่ใช้ในการเปลียน img_full เป็น shift_img ')

        plog('------- >>> training... <<< ---------')
        create_model(model_name)
        t3 = datetime.now()
        plog(f'{t2 - t1} เวลาที่ใช้ในการเปลียน img_full เป็น shift_img ')
        plog(f'{t3 - t2} เวลาที่ใช้ในการ training ')
        plog(f'{t3 - t1} เวลาที่ใช้ทั้งหมด')
    except:
        print(f'{WARNING}model_name error{ENDC}')


print(frames)
model_list = os.listdir(MODEL_PATH)
model_list = [file.split('.')[0] for file in model_list if file.endswith('.h5')]
plog(f'model_list (ที่มี) {len(model_list)} {model_list}')

for name, model in frames.models.items():
    plog(f'\n{model} MODEL_SET={MODEL_SET} | img_height_width={img_height}, {img_width}')
    if name in model_list:
        print(f'{WARNING}continue{ENDC}')
        continue

    f(name, model, frames)
