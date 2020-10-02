import os
import json
import requests
import socket
import librosa
import soundfile

# Config of rasa server
RASA_HOST = "127.0.0.1"
RASA_PORT = 5005
BASE_URL = "http://{}:{}/webhooks/rest/webhook".format(RASA_HOST, RASA_PORT)

# Config of TTS module (speech synthesis)
TTS_HOST = "127.0.0.1"
TTS_PORT = 5051
TTS_URL = "http://{}:{}/synthesis".format(TTS_HOST, TTS_PORT)
TTS_DATA_PATH = "data"

# Config of STT module (speech recognition)
STT_HOST = "127.0.0.1"
STT_PORT = 5050


def get_rasa_response(message: str, sender: str = "server"):
    """
    Send message to rasa server and get response
    :param message: String to be sent
    :param sender: String that identify sender
    :return: List of dicts
    """
    responses = requests.post(BASE_URL, data=json.dumps({"sender": sender, "message": message})).json()
    return responses


def str_to_wav(input_str: str, output_dir: str = None):
    r = requests.post(TTS_URL, data=json.dumps({"text": input_str, "output_dir": output_dir}))
    print(r.json())


def wav_to_str(input_filename: str) -> str:
    """
    Convert wav file to string
    :param input_filename: file name of wav to be converted (without postfix)
    :return: converted string
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((STT_HOST, STT_PORT))

    cwd = os.getcwd()
    input_file_path = os.path.join(cwd, TTS_DATA_PATH, input_filename + ".wav")

    buffer = ""
    with open(input_file_path, "rb") as f:
        wav = f.read()
        sock.send(wav)
        received_byte = sock.recv(2048)
        received_str = str(received_byte, encoding="utf-8")
        while received_str != "\n":
            print(received_byte)
            print(received_str)
            print("--------------------------------------------")

            buffer = received_str

            received_byte = sock.recv(2048)
            received_str = str(received_byte, encoding="utf-8")

    print("Final Recognized Result: ", buffer)
    sock.close()
    return buffer


def down_sample(filename: str, sample_rate: int) -> None:
    """
    Down sample a wav file to given sample rate
    :param filename: path to the wav file to be down sampled (with postfix)
    :param sample_rate: sample rate
    :return: None
    """
    y, sr = librosa.load(filename, sr=sample_rate)
    soundfile.write(filename, y, sr, format="wav")


if __name__ == '__main__':
    print(str_to_wav("hello world!", "hw.wav"))
