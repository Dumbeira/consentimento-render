from flask import Flask, request
import yagmail
import os

app = Flask(__name__)

# Configurações do yagmail com sua senha de app do Gmail
EMAIL = 'mwvmedicina80@gmail.com'
SENHA = 'lbey cvxr dklv frsz'

@app.route('/enviar-consentimento', methods=['POST'])
def enviar_email():
    if 'pdf' not in request.files:
        return 'Arquivo PDF não encontrado.', 400

    email_paciente = request.form.get('emailPaciente')
    arquivo = request.files['pdf']
    caminho_temp = os.path.join('/tmp', arquivo.filename)
    arquivo.save(caminho_temp)

    try:
        yag = yagmail.SMTP(EMAIL, SENHA)
        yag.send(
            to=[EMAIL, email_paciente],
            subject='Consentimento Informado Assinado',
            contents='Segue em anexo o consentimento assinado pelo paciente.',
            attachments=caminho_temp
        )
        print("E-mail enviado com sucesso.")
        return 'PDF enviado com sucesso!', 200
    except Exception as e:
        print("Erro ao enviar e-mail:", str(e))
        return 'Erro ao enviar e-mail.', 500
    finally:
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
