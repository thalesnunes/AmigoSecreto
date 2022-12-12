from datetime import datetime
import json
import logging
import random
from typing import Any, Dict, Optional, List


ANO = datetime.now().year
EMAIL_FORMATO = """
Fala pessoal!! Chegou o nosso querido Amigo Secreto de {ano}!
Então, {nome}, a pessoa que você tirou foi: {tirou}!

Fizemos o nosso sorteio através de uma ferramenta que nós mesmos desenvolvemos (Thales, Davi e Lucas)!
Então, caso haja algum problema, ou seu nome não esteja correto, contate a gente!
"""


class Pessoa:
    def __init__(self, nome: str, email: str) -> None:
        self.nome = nome
        self.email = email
        self.tirou = None

    def __repr__(self) -> None:
        return str(self.__dict__)


class Bilhete:
    def __init__(self, nome_escrito: str) -> None:
        self.nome_escrito = nome_escrito


def email_connect(keys_from: Dict[str, str]) -> Any:
    """Cria um cliente SMTP do google com as chaves passadas.
    Args:
        keys_from (Dict[str, str]): Chaves de acesso ao cliente SMTP.
    Returns:
        Any: Conexão do servidor SMTP.
    """

    import smtplib

    logging.info("Starting Gmail connection")
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    server.ehlo()
    server.login(keys_from["email"], keys_from["password"])
    return server


def send_list_to_email(
    lista: List[Any], keys_from: Dict[str, str], content_fmt: Optional[str] = "*"
) -> None:

    from time import sleep
    from email.message import EmailMessage

    server = email_connect(keys_from)
    logging.info("Começando o envio de emails")

    for row in lista:
        msg = EmailMessage()

        msg["From"] = keys_from["email"]
        msg["To"] = row.email
        msg["Subject"] = f"{row.nome}, seu Amigo Secreto chegou!"
        msg.set_content(content_fmt.format(ano=ANO, **row.__dict__))

        first_stop = True
        while True:
            try:
                server.send_message(msg)
                logging.info(f"Email enviado para {row.nome}.")
            except Exception:
                sleep(10)
                if first_stop:
                    sleep(120)
                    first_stop = False
                server.close()
                server = email_connect(keys_from)
            else:
                break
    server.close()
    logging.info("Todos os emails foram enviados!!")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s||%(levelname)s||%(message)s"
    )

    with open("participantes.txt", "r") as file:
        participantes = [linha.strip().split("\t") for linha in file.readlines()]

    with open("email.json", "r") as file:
        keys_email = json.load(file)

    pessoas_lista = []
    for pessoa in participantes:
        pessoas_lista.append(Pessoa(*pessoa))

    saquinho_bilhetes = []
    for pessoa in pessoas_lista:
        saquinho_bilhetes.append(Bilhete(pessoa.nome))

    logging.info("Jogo criado com sucesso!")
    logging.info("Começando a escolher amigos secretos")

    for pessoa in pessoas_lista:
        valido = False
        while not valido:
            bilhete_escolhido = random.choice(saquinho_bilhetes)
            if pessoa.nome != bilhete_escolhido.nome_escrito:
                pessoa.tirou = bilhete_escolhido.nome_escrito
                saquinho_bilhetes.remove(bilhete_escolhido)
                valido = True

    logging.info("Escolha finalizada")
    for pessoa in pessoas_lista:
        logging.info(str(pessoa))
    logging.info("Enviando os emails para cada um dos participantes")

    send_list_to_email(pessoas_lista, keys_email, EMAIL_FORMATO)

    logging.info("Envio finalizado")


if __name__ == "__main__":
    main()
