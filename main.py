import re
import sys
from datetime import datetime
from os import path
from pathlib import Path

import cv2
import imagehash
from PIL import Image


def dict_by_value(dict, value):
    for name, age in dict.items():
        if age == value:
            return name


def write_fingerprint(path, fingerprint):
    path = "frames/" + replace(path) + "/aa_fingerprint.txt"
    with open(path, "w+") as text_file:
        text_file.write(fingerprint)


def replace(s):
    return re.sub('[^A-Za-z0-9]+', '', s)


def create_frame_fingerprint(image_path):
    image = Image.open(image_path)
    h = str(imagehash.dhash(image))
    return h


def create_video_fingerprint(path):
    video_fingerprint = ""
    video = cv2.VideoCapture(path)
    fps = video.get(cv2.CAP_PROP_FPS)
    success, image = video.read()
    count = 0
    while count < int(300.0 * fps) + 1:
        frame_path = "frames/" + replace(path)
        Path(frame_path).mkdir(parents=True, exist_ok=True)
        cv2.imwrite(frame_path + "/frame%d.jpg" % count, image)  # save frame as JPEG file
        frame_fingerprint = create_frame_fingerprint(frame_path + "/frame%d.jpg" % count)
        video_fingerprint += frame_fingerprint
        print(path + " " + str(count) + "/" + str(int(300.0 * fps) + 1) + " " + frame_fingerprint, success)
        success, image = video.read()
        count += sample_frame
    return video_fingerprint


def get_unique_frames_fingerprint(video_fingerprints):
    unique_frames = []
    for video_fingerprint in video_fingerprints:
        for frame_fingerprint in re.findall('................', video_fingerprint):
            unique_frames.append(frame_fingerprint)
    unique_frames = list(set(unique_frames))
    return unique_frames


def create_matrix(unique_frames):
    unique_frame_tokens = {}
    for i in range(62, len(unique_frames)):
        unique_frame_tokens[unique_frames[i]] = chr(i)
    return unique_frame_tokens


def tokenize_fingerprints(video_fingerprints):
    unique_frames = get_unique_frames_fingerprint(video_fingerprints)
    frame_matrix = create_matrix(unique_frames)
    token_video_fingerprints = []
    for video_fingerprint in video_fingerprints:
        token_video_fingerprint = ""
        for frame_fingerprint in re.findall('................', video_fingerprint):
            try:
                token_video_fingerprint += frame_matrix[frame_fingerprint]
            except Exception as e:
                print(e)
        token_video_fingerprints.append(token_video_fingerprint)
    pass


def for_files(files):
    fingerprints = []
    for file in files:
        if path.exists("frames/" + replace(file) + "/aa_fingerprint.txt"):
            print(file + " fingerprint exists - loading it")
            with open("frames/" + replace(file) + "/aa_fingerprint.txt", "r") as text_file:
                fingerprint = text_file.read()
        else:
            print(file + " fingerprint does not exist - loading it")
            fingerprint = create_video_fingerprint(file)
            write_fingerprint(file, fingerprint)
        fingerprints.append(fingerprint)
    tokenize_fingerprints(fingerprints)


print(datetime.now())
seconds_from_start = 300  # 5 minuets
sample_frame = 1  # take every X frame
paths = [
]
for_files(paths)

print(datetime.now())
