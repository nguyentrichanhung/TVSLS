FROM nvidia/cuda:10.0-base
FROM nvcr.io/nvidia/pytorch:21.05-py3
FROM python:3.8

# Install linux packages
RUN apt update && apt install -y zip htop screen libgl1-mesa-glx
RUN apt update
RUN apt install software-properties-common -y

# Install python dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip uninstall -y nvidia-tensorboard nvidia-tensorboard-plugin-dlprof
RUN pip install --no-cache -r requirements.txt coremltools onnx gsutil notebook
# RUN pip install --no-cache -U torch torchvision numpy
# RUN pip install --no-cache torch==1.7.1+cu111 torchvision==0.8.2+cu111 -f https://download.pytorch.org/whl/torch_stable.html

# Create working directory
RUN mkdir -p /usr/src/Backend
# RUN source .env
WORKDIR /usr/src/Backend

# Copy contents
COPY src src
COPY ./docker-entrypoint.sh ./docker-entrypoint.sh 
# Make Entrypoint executable
RUN ls
RUN chmod +x ./docker-entrypoint.sh
RUN chmod -R 777 ./src

# Set environment variables
# ENV HOME=/usr/src/lpr
ENV PATH /usr/local/bin:$PATH
ENV FLASK_APP=src/routes.py
ENV PYTHONUNBUFFERED=1

# CMD flask run --host=0.0.0.0 --port=80
# # Run the app when the container launches
# CMD ["python3","src/routes.py"]
ENTRYPOINT  ["./docker-entrypoint.sh"]

EXPOSE 80
