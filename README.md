# Dashboard El Niño - Defesa Civil SMJ ⛈️📊

Painel Integrado de Monitoramento, Gestão de Riscos e Ações Preventivas - Operação El Niño da Defesa Civil Municipal de Santa Maria de Jetibá - ES.

---

## 🚀 Sobre o Projeto

O **Dashboard El Niño** consolida e visualiza em tempo real dados críticos para a tomada de decisão da Defesa Civil e Secretarias Integradas:
- **Monitoramento Meteorológico e Hidrológico:** Previsão do tempo, histórico do Rio Santa Maria da Vitória (Cesan) e alertas climáticos.
- **Setores Integrados:** Obras, Agricultura, Meio Ambiente, Saúde, Educação e Assistência Social.
- **Mapeamento e Cartografia de Risco:** Indicadores de deslizamentos, inundações, enxurradas e vulnerabilidade social.
- **Relatórios Gerenciais:** Emissão de relatórios em tempo real para boletins e auditorias (TCE-ES / Defesa Civil Estadual).

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** [Python 3](https://www.python.org/) + [Flask](https://flask.palletsprojects.com/)
- **Processamento de Dados:** [Pandas](https://pandas.pydata.org/), [OpenPyXL](https://openpyxl.readthedocs.io/) e [PyMuPDF](https://pymupdf.readthedocs.io/)
- **Frontend:** HTML5, CSS3 moderno (Design System GovTech / Defesa Civil), JavaScript Vanilla, Leaflet (mapas interativos)
- **Hospedagem & Deploy:** [Vercel](https://vercel.com/) (Serverless Python Functions)

---

## 📂 Estrutura do Projeto

```text
├── api/
│   └── index.py            # Entry point WSGI para o Vercel Serverless
├── dados/                  # Bases de dados locais, JSONs e matrizes de risco
├── static/                 # Estilos CSS, scripts JavaScript, logos e mapas
├── templates/              # Templates HTML renderizados pelo Flask
├── app.py                  # Aplicação Flask principal (rotas e processamento)
├── requirements.txt        # Dependências Python para produção
├── vercel.json             # Configuração de build e rotas da Vercel
├── .vercelignore           # Arquivos ignorados no bundle de deploy da Vercel
└── README.md
```

---

## 💻 Executando Localmente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/WillianCiurlleti/el-nino.git
   cd el-nino
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   # No Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie o servidor de desenvolvimento:**
   ```bash
   python app.py
   ```
   Acesse a aplicação no navegador em `http://localhost:5000`.

---

## ☁️ Deploy na Vercel

O projeto está 100% configurado para deploy automático na **Vercel** via integração com o GitHub:

1. Acesse o painel da [Vercel](https://vercel.com) e clique em **Add New Project**.
2. Importe o repositório `el-nino`.
3. As configurações serão detectadas automaticamente pelo arquivo `vercel.json` e `api/index.py`:
   - **Framework Preset:** Other
   - **Root Directory:** `./`
4. *(Opcional)* Configure as variáveis de ambiente em **Settings > Environment Variables**:
   - `SECRET_KEY`: Chave secreta para criptografia de sessões Flask (ex: uma chave aleatória segura).
5. Clique em **Deploy**. A cada novo `git push` para a branch `main`, a Vercel executará um deploy automático.
