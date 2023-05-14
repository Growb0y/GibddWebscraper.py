
import base64
import cv2
import requests
from matplotlib import pyplot as plt
from matplotlib.widgets import TextBox


def pass_captcha():
    """
    функция парсинга разделов "history" и "dtp" сайта ГИБДД
    :param input_vins_file_: string - название входного файла с винами
    :param output_dir_: string - название папки, куда записывется выходной файл
    :param checkType_: string - вид проверки (history/dtp)
    :return: None (функция записывает спаршенные данные в файл)
    """

    captchaWord = ''
    # получаем токен капчи
    captchaURI = "https://check.gibdd.ru/captcha"
    captcha = requests.get(captchaURI)
    token = captcha.json()["token"]

    # получаем картинку капчи
    with open("imageToSave.png", "wb") as fh:
        fh.write(base64.b64decode(
            captcha.json()["base64jpg"]
        )
        )
    preprocess = "thresh"

    def submit(text):
        nonlocal captchaWord
        plt.close()
        captchaWord = text

    image = cv2.imread("imageToSave.png")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # выводим капчу и поле ввода на экран
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.2)
    plt.imshow(image)
    axbox = plt.axes([0.3, 0.05, 0.5, 0.1])
    text_box = TextBox(axbox, 'Captcha:')
    text_box.on_submit(submit)
    plt.show()

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    if preprocess == "thresh":
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    captchaToken = token

    return {
                "captchaWord": captchaWord,
                "captchaToken": captchaToken
            }
