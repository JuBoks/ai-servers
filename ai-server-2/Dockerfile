FROM python:3.9

WORKDIR /app/
COPY . /app/

RUN pip install fastapi uvicorn opencv-python numpy tensorflow keras scikit-learn matplotlib Keras-Preprocessing torch pandas psutil torchvision pyyaml tqdm seaborn python-dotenv
RUN apt-get update
RUN apt-get -y install libgl1-mesa-glx

CMD uvicorn --host=0.0.0.0 --port 8000 main:app
