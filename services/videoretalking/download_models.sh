#!/bin/bash
# Download the pretrained weights required by OpenTalker/video-retalking.
# URLs mirror https://huggingface.co/ameerazam08/video-retalking/raw/main/download.sh
set -e

cd /video-retalking
mkdir -p checkpoints BFM

curl -L -o checkpoints/30_net_gen.pth https://github.com/vinthony/video-retalking/releases/download/v0.0.1/30_net_gen.pth
curl -L -o checkpoints/BFM.zip https://github.com/vinthony/video-retalking/releases/download/v0.0.1/BFM.zip
curl -L -o checkpoints/DNet.pt https://github.com/vinthony/video-retalking/releases/download/v0.0.1/DNet.pt
curl -L -o checkpoints/ENet.pth https://github.com/vinthony/video-retalking/releases/download/v0.0.1/ENet.pth
curl -L -o checkpoints/expression.mat https://github.com/vinthony/video-retalking/releases/download/v0.0.1/expression.mat
curl -L -o checkpoints/face3d_pretrain_epoch_20.pth https://github.com/vinthony/video-retalking/releases/download/v0.0.1/face3d_pretrain_epoch_20.pth
curl -L -o checkpoints/GFPGANv1.3.pth https://github.com/vinthony/video-retalking/releases/download/v0.0.1/GFPGANv1.3.pth
curl -L -o checkpoints/GPEN-BFR-512.pth https://github.com/vinthony/video-retalking/releases/download/v0.0.1/GPEN-BFR-512.pth
curl -L -o checkpoints/LNet.pth https://github.com/vinthony/video-retalking/releases/download/v0.0.1/LNet.pth
curl -L -o checkpoints/ParseNet-latest.pth https://github.com/vinthony/video-retalking/releases/download/v0.0.1/ParseNet-latest.pth
curl -L -o checkpoints/RetinaFace-R50.pth https://github.com/vinthony/video-retalking/releases/download/v0.0.1/RetinaFace-R50.pth
curl -L -o checkpoints/shape_predictor_68_face_landmarks.dat https://github.com/vinthony/video-retalking/releases/download/v0.0.1/shape_predictor_68_face_landmarks.dat

unzip -o -d checkpoints/BFM checkpoints/BFM.zip
