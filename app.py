from flask import Flask, request, send_from_directory, make_response
from flask_cors import CORS
import yagmail
import os

app = Flask(__name__)
CORS(app)

EMAIL = 'mwvmedicina80@gmail.com'
SENHA = 'pbhg pedb rskz awhv'

@app.route('/')
def index():
    return make_response("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Consentimento Informado</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 30px; line-height: 1.6; }
    h2 { text-align: center; }
    canvas { border: 1px solid #000; display: block; margin: 20px auto; }
    input, button { display: block; margin: 10px auto; padding: 10px; width: 90%; max-width: 500px; }
    textarea { width: 100%; height: 450px; margin-top: 20px; white-space: pre-wrap; }
  </style>
</head>
<body>

<h2>CONSENTIMENTO INFORMADO PARA TRATAMENTO PSIQUIÁTRICO</h2>

<input type="text" id="nome" placeholder="Nome completo do paciente" required>
<input type="text" id="nascimento" placeholder="Data de nascimento" required>
<input type="text" id="responsavel" placeholder="Responsável legal (se aplicável)">
<input type="email" id="email" placeholder="E-mail do paciente" required>

<textarea id="texto" readonly></textarea>

<canvas id="assinatura" width="480" height="180"></canvas>
<button onclick="limparAssinatura()">Limpar Assinatura</button>
<button onclick="enviar()">Enviar Consentimento</button>
<p id="status"></p>

<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script>
  const canvas = document.getElementById('assinatura');
  const ctx = canvas.getContext('2d');
  let desenhando = false;

  const textoPadrao = `
Nome do(a) paciente: {NOME}, email: {EMAIL}
Data de nascimento: {NASCIMENTO}
Responsável legal (se aplicável): {RESPONSAVEL}

Nome do médico psiquiatra: Dr. Marcelo Wagner Viana – CRM/MG 50288 – RQE 44764

Eu, acima identificado(a), ou responsável legal, declaro que fui devidamente informado(a) pelo médico psiquiatra quanto ao diagnóstico, natureza, objetivos e opções de tratamento, incluindo os riscos, benefícios, efeitos colaterais possíveis, alternativas terapêuticas disponíveis e consequências da não realização do tratamento proposto.

1. Natureza do Tratamento
Trata-se de acompanhamento psiquiátrico com possibilidade de uso de medicação psicotrópica (antidepressivos, ansiolíticos, antipsicóticos, estabilizadores de humor ou outros), bem como psicoterapia ou encaminhamento para outros profissionais ou exames complementares, conforme avaliação médica.

2. Objetivo do Tratamento
Promover melhora do quadro clínico psiquiátrico, alívio dos sintomas, prevenção de recaídas e promoção da qualidade de vida, com o menor risco possível ao paciente.

3. Possíveis Efeitos Colaterais ou Reações Adversas
Fui informado(a) sobre os efeitos colaterais possíveis relacionados às medicações, que podem incluir, entre outros: sonolência, ganho de peso, insônia, náuseas, agitação, alterações sexuais, tremores, entre outros.
Fui orientado(a) a comunicar ao médico qualquer efeito colateral ou reação adversa para adequação do tratamento.

4. Confidencialidade e Sigilo Médico
Todas as informações compartilhadas serão mantidas em sigilo profissional, exceto nos casos previstos por lei (como risco à vida do paciente ou de terceiros, determinação judicial ou suspeita de crimes legalmente previstos).

5. Consentimento e Autonomia
Declaro que este consentimento é livre e esclarecido, podendo ser revogado a qualquer momento. Entendo que posso interromper o tratamento, solicitar esclarecimentos adicionais ou buscar uma segunda opinião, se desejar.

6. Compromisso do(a) paciente
Comprometo-me a seguir as orientações médicas, fazer uso adequado das medicações prescritas e comparecer às consultas conforme agendamento. Estou ciente de que a interrupção abrupta do tratamento pode acarretar prejuízos à minha saúde.

7. Tratamento Involuntário ou Internação (se aplicável)
Fui informado(a) de que, em casos excepcionais, de risco iminente à minha integridade ou à de terceiros, pode ser necessária a internação psiquiátrica, inclusive contra minha vontade, conforme prevê a Lei nº 10.216/2001.

Declaro que todas as minhas dúvidas foram esclarecidas e que estou de acordo com o tratamento proposto.

Local: Bom Sucesso, 19 de April de 2025
  `;

  document.getElementById('texto').value = textoPadrao;

  canvas.addEventListener('mousedown', e => {
    desenhando = true;
    ctx.moveTo(e.offsetX, e.offsetY);
  });
  canvas.addEventListener('mousemove', e => {
    if (desenhando) {
      ctx.lineTo(e.offsetX, e.offsetY);
      ctx.stroke();
    }
  });
  canvas.addEventListener('mouseup', () => desenhando = false);
  canvas.addEventListener('touchstart', e => {
    e.preventDefault();
    desenhando = true;
    const rect = canvas.getBoundingClientRect();
    const touch = e.touches[0];
    ctx.moveTo(touch.clientX - rect.left, touch.clientY - rect.top);
  });
  canvas.addEventListener('touchmove', e => {
    e.preventDefault();
    if (desenhando) {
      const rect = canvas.getBoundingClientRect();
      const touch = e.touches[0];
      ctx.lineTo(touch.clientX - rect.left, touch.clientY - rect.top);
      ctx.stroke();
    }
  });
  canvas.addEventListener('touchend', () => desenhando = false);

  function limparAssinatura() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.beginPath();
  }

  async function enviar() {
    const nome = document.getElementById('nome').value;
    const nascimento = document.getElementById('nascimento').value;
    const responsavel = document.getElementById('responsavel').value;
    const email = document.getElementById('email').value;
    const texto = textoPadrao
      .replace("{NOME}", nome)
      .replace("{EMAIL}", email)
      .replace("{NASCIMENTO}", nascimento)
      .replace("{RESPONSAVEL}", responsavel || "-");

    const { jsPDF } = window.jspdf;
const pdf = new jsPDF();
pdf.setFontSize(12);

// Calcula a altura do texto dinamicamente
const lineHeight = 7;
const linhas = texto.split('\n');
const alturaTexto = linhas.length * lineHeight;

// Adiciona o texto
pdf.text(texto, 10, 10, { maxWidth: 190 });

// Calcula onde colocar a assinatura
const posY = 10 + alturaTexto + 10;

const assinatura = document.getElementById('assinatura');
const imgData = assinatura.toDataURL('image/png');
pdf.addImage(imgData, 'PNG', 10, posY, 180, 50);

    const blob = pdf.output('blob');
    const formData = new FormData();
    formData.append('emailPaciente', email);
    formData.append('pdf', blob, 'consentimento.pdf');

    document.getElementById('status').innerText = "Enviando consentimento...";

    try {
      const response = await fetch("/enviar-consentimento", {
        method: 'POST',
        body: formData
      });
      const resultado = await response.json();
      if (response.ok) {
        document.getElementById('status').innerText = resultado.mensagem;
      } else {
        document.getElementById('status').innerText = resultado.mensagem || "Erro ao enviar o consentimento.";
      }
    } catch (error) {
      document.getElementById('status').innerText = "Erro ao conectar com o servidor.";
    }
  }
</script>

</body>
</html>""", 200)

@app.route('/enviar-consentimento', methods=['POST'])
def enviar_email():
    if 'pdf' not in request.files:
        return {'mensagem': 'Arquivo PDF não encontrado.'}, 400

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
        return {'mensagem': 'PDF enviado com sucesso!'}, 200
    except Exception as e:
        print("Erro ao enviar e-mail:", str(e))
        return {'mensagem': f'Erro ao enviar e-mail: {str(e)}'}, 500
    finally:
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
