FROM ubuntu:20.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y install build-essential g++ libssl-dev cmake git

# see https://github.com/awslabs/aws-iot-device-client/blob/3fdf72b7eb1f5a0a3c21d4d3b938cac93cf49501/.github/build.sh#L89
RUN git clone https://github.com/awslabs/aws-iot-device-client.git && \
    cd aws-iot-device-client && \
    git checkout v1.5 && \
    mkdir build && \
    cd build && \
    cmake ../ \
        -DCMAKE_BUILD_TYPE=MinSizeRel \
        -DBUILD_SDK=ON \
        -DLINK_DL=ON \
        -DEXCLUDE_JOBS=ON \
        -DEXCLUDE_DD=ON \
        -DEXCLUDE_FP=ON \
        -DEXCLUDE_SAMPLES=ON \
        -DEXCLUDE_SHADOW=ON \
        -DEXCLUDE_CONFIG_SHADOW=ON \
        -DEXCLUDE_SAMPLE_SHADOW=ON \
        -DDISABLE_MQTT=ON \
        && \
    cmake --build . --target aws-iot-device-client

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=true

RUN apt-get update && apt-get install -y python3 python3-pip openssl
RUN python3 -m pip install awsiotsdk==1.9.2

RUN mkdir /app
WORKDIR /app/

COPY secure_tunnel_watcher.py ./
COPY --from=builder /aws-iot-device-client/build/aws-iot-device-client ./

CMD [ "python3", "/app/secure_tunnel_watcher.py"]
