const express = require('express');
const cors = require('cors');
const multer = require('multer');
const nodemailer = require('nodemailer');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors()); // Permite requisições do seu frontend
app.use(express.json()); // Permite ler JSON no corpo da requisição

// Configuração do Multer (mantém o arquivo PDF na memória para envio rápido)
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Configuração do Transporte de E-mail (Gmail)
// Substitua pelos seus dados reais. Para o Gmail, gere uma "Senha de App" nas configurações de segurança da sua conta.
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: 'SEU_EMAIL@gmail.com',
        pass: 'SUA_SENHA_DE_APP'
    }
});

// Rota POST para receber e enviar o currículo
app.post('/send-resume', upload.single('resumePdf'), async (req, res) => {
    try {
        const { candidateName, targetEmail } = req.body;
        const resumeFile = req.file;

        // Validação básica
        if (!candidateName || !targetEmail || !resumeFile) {
            return res.status(400).json({
                success: false,
                message: 'Parâmetros ausentes. Forneça o nome do candidato, e-mail de destino e o arquivo PDF do currículo.'
            });
        }

        // Opções do e-mail
        const mailOptions = {
            from: 'SEU_EMAIL@gmail.com', // Deve ser o mesmo do auth.user
            to: targetEmail,
            subject: `Candidatura para vaga - ${candidateName}`,
            text: `Olá,\n\nSegue em anexo o currículo de ${candidateName}.\n\nAtenciosamente,\nJobHunter Auto-Apply`,
            attachments: [
                {
                    filename: resumeFile.originalname,
                    content: resumeFile.buffer
                }
            ]
        };

        // Envia o e-mail efetivamente
        const info = await transporter.sendMail(mailOptions);
        console.log('E-mail enviado:', info.response);

        // Resposta de sucesso em JSON (para o front-end)
        return res.status(200).json({
            success: true,
            message: `Currículo enviado com sucesso para ${targetEmail}`,
            messageId: info.messageId
        });

    } catch (error) {
        console.error('Erro ao enviar e-mail:', error);
        return res.status(500).json({
            success: false,
            message: `Erro interno no servidor ao enviar o currículo: ${error.message}`
        });
    }
});

// Inicia o servidor
app.listen(PORT, () => {
    console.log(`Servidor Node.js rodando em http://localhost:${PORT}`);
});
