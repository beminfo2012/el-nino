# 📐 Layout de Referência — Ficha Técnica Geo-Hidrológica
### Coordenadoria Municipal de Proteção e Defesa Civil — Santa Maria de Jetibá / ES

---

## 1. Visão Geral e Objetivo
Anteriormente, o arquivo `doc.kml` possuía mais de 40 MB e 283.000 linhas porque cada um dos 63 pontos continha um layout HTML idêntico e repetitivo embutido em sua descrição. Isso tornava a edição manual inviável.

Agora, os dados foram desacoplados do layout:
- **Arquivos de Texto Puro (GeoJSON):**
  - `dados/pontos_educacao.geojson` (Escolas municipais)
  - `dados/pontos_saude.geojson` (Unidades de saúde e apoio)
  - Também sincronizados em `static/geojson/`
- **Tamanho:** Reduzido de **40 MB** para apenas **~76 KB** (Educação) e **~42 KB** (Saúde).
- **Layout de Referência Único:** O frontend (Leaflet) possui uma função centralizada `gerarPopupFichaTecnica(properties)` que gera o card visual elegante automaticamente para qualquer ponto.

---

## 2. Estrutura Padrão de um Ponto (Modelo GeoJSON)
Para editar um ponto existente ou adicionar uma nova escola ou unidade de saúde, basta seguir a estrutura abaixo no arquivo `.geojson`:

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [-40.745040, -20.021722]
  },
  "properties": {
    "id": 1,
    "codigo": "Nº 01 / 34",
    "nome": "Nome da Unidade ou Equipamento",
    "tipo": "Saúde",
    "style": "style_proximo",
    "classificacao": "ATENÇÃO PRÓXIMO (<50m)",
    "referencia": "Mapeamento da Rede Municipal de Saúde e Apoio",
    "risco_geologico": {
      "status": "FORA",
      "diagnostico": "Nenhum risco no raio de 50m",
      "fonte": "CPRM / SEDURB"
    },
    "risco_hidrologico": {
      "status": "FORA",
      "diagnostico": "Nenhum risco no raio de 50m",
      "fonte": "Modelagem TR 5-100a"
    },
    "suscetibilidade_inundacao": {
      "status": "PRÓXIMO",
      "diagnostico": "Distância: 24.7m",
      "fonte": "Carta de Suscetibilidade SMJ"
    },
    "movimento_massa": {
      "status": "PRÓXIMO",
      "diagnostico": "Distância: 39.8m",
      "fonte": "Carta de Suscetibilidade SMJ"
    }
  }
}
```

> **Atenção:** No GeoJSON, a ordem das coordenadas em `coordinates` é sempre `[Longitude (X), Latitude (Y)]`!

---

## 3. Tabela de Estilos e Cores de Marcador

| Valor do campo `style` | Cor no Mapa | Classificação Padrão | Quando Usar |
| :--- | :--- | :--- | :--- |
| `style_risco_direto` | 🔴 Vermelho | `RISCO DIRETO (CRÍTICO)` | Ponto dentro da mancha de inundação ou raio imediato de risco geológico/mov. massa. |
| `style_proximo` | 🟡 Amarelo/Âmbar | `ATENÇÃO PRÓXIMO (< 50m)` | Ponto no raio de amortecimento (< 50m) de qualquer área de risco mapeada. |
| `style_isento` | 🟢 Verde | `ISENTO DE RISCO MAPEADO` | Ponto fora de todas as zonas de risco (> 50m). |

---

## 4. Layout Visual de Referência (Template HTML Gerado Dinamicamente)
Este é o layout exato renderizado pelo sistema ao clicar em qualquer ponto:

```html
<div style="font-family: Arial, Helvetica, sans-serif; font-size: 12px; color: #1f2937; max-width: 520px; line-height: 1.4;">
  <!-- Cabeçalho Institucional -->
  <div style="background: linear-gradient(135deg, #1e3a8a, #1e40af); color: #ffffff; padding: 12px 14px; border-radius: 6px 6px 0 0; text-align: center;">
    <div style="font-size: 9.5px; text-transform: uppercase; letter-spacing: 0.8px; opacity: 0.9; font-weight: bold;">COMPDEC • SANTA MARIA DE JETIBÁ / ES</div>
    <div style="font-size: 15px; font-weight: bold; margin-top: 3px; color: #ffffff;">{{ nome }}</div>
    <div style="font-size: 11px; margin-top: 2px; color: #bfdbfe;">Ficha Técnica de Avaliação de Riscos Geo-Hidrológicos</div>
  </div>

  <!-- Faixa de Classificação Geral -->
  <div style="background-color: #fef3c7; color: #92400e; padding: 7px 12px; font-size: 11.5px; font-weight: bold; text-align: center; border-left: 1px solid #d1d5db; border-right: 1px solid #d1d5db; border-bottom: 1px solid #e5e7eb;">
    CLASSIFICAÇÃO GERAL: {{ classificacao }}
  </div>

  <!-- Tabela de Identificação e Coordenadas -->
  <table style="width: 100%; border-collapse: collapse; font-size: 11px; border-left: 1px solid #d1d5db; border-right: 1px solid #d1d5db; border-bottom: 1px solid #d1d5db; background-color: #f9fafb;">
    <tr>
      <td style="padding: 5px 10px; font-weight: bold; width: 32%; color: #4b5563; border-bottom: 1px solid #e5e7eb;">Identificação (ID):</td>
      <td style="padding: 5px 10px; color: #111827; border-bottom: 1px solid #e5e7eb;">{{ codigo }}</td>
    </tr>
    <tr>
      <td style="padding: 5px 10px; font-weight: bold; color: #4b5563; border-bottom: 1px solid #e5e7eb;">Coordenadas:</td>
      <td style="padding: 5px 10px; color: #111827; border-bottom: 1px solid #e5e7eb; font-family: monospace;">Lat: {{ latitude }} | Lon: {{ longitude }}</td>
    </tr>
    <tr>
      <td style="padding: 5px 10px; font-weight: bold; color: #4b5563;">Referência:</td>
      <td style="padding: 5px 10px; color: #111827;">{{ referencia }}</td>
    </tr>
  </table>

  <!-- Título da Seção de Risco -->
  <div style="margin-top: 10px; margin-bottom: 5px; font-weight: bold; font-size: 11px; color: #1f2937; text-transform: uppercase; letter-spacing: 0.5px;">
    Diagnóstico Espacial por Camada de Risco
  </div>

  <!-- Matriz de Riscos 4D -->
  <table style="width: 100%; border-collapse: collapse; font-size: 10.5px; border: 1px solid #d1d5db; border-radius: 4px; overflow: hidden; background-color: #ffffff;">
    <thead>
      <tr style="background-color: #1f2937; color: #ffffff;">
        <th style="padding: 6px 8px; text-align: left; font-size: 10px; text-transform: uppercase;">Tipologia de Risco</th>
        <th style="padding: 6px 8px; text-align: center; font-size: 10px; text-transform: uppercase;">Status</th>
        <th style="padding: 6px 8px; text-align: left; font-size: 10px; text-transform: uppercase;">Diagnóstico / Distância</th>
        <th style="padding: 6px 8px; text-align: left; font-size: 10px; text-transform: uppercase;">Fonte de Dados</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Risco Geológico</td>
        <td><span class="badge">{{ risco_geologico.status }}</span></td>
        <td>{{ risco_geologico.diagnostico }}</td>
        <td>{{ risco_geologico.fonte }}</td>
      </tr>
      <tr>
        <td>Risco Hidrológico</td>
        <td><span class="badge">{{ risco_hidrologico.status }}</span></td>
        <td>{{ risco_hidrologico.diagnostico }}</td>
        <td>{{ risco_hidrologico.fonte }}</td>
      </tr>
      <tr>
        <td>Suscetibilidade Inundação</td>
        <td><span class="badge">{{ suscetibilidade_inundacao.status }}</span></td>
        <td>{{ suscetibilidade_inundacao.diagnostico }}</td>
        <td>{{ suscetibilidade_inundacao.fonte }}</td>
      </tr>
      <tr>
        <td>Movimento de Massa</td>
        <td><span class="badge">{{ movimento_massa.status }}</span></td>
        <td>{{ movimento_massa.diagnostico }}</td>
        <td>{{ movimento_massa.fonte }}</td>
      </tr>
    </tbody>
  </table>

  <!-- Rodapé Institucional -->
  <div style="font-size: 9px; color: #6b7280; text-align: right; margin-top: 6px; font-style: italic;">
    Defesa Civil Municipal • Santa Maria de Jetibá - ES • 2026
  </div>
</div>
```

---

## 5. Como Editar ou Lançar Novos Pontos

1. Abra o arquivo desejado no VS Code ou bloco de notas:
   - Educação: `dados/pontos_educacao.geojson`
   - Saúde: `dados/pontos_saude.geojson`
2. Copie um bloco `{ "type": "Feature", ... }` e cole no final da lista `features`.
3. Preencha o nome da unidade, as coordenadas `[lon, lat]`, o `style` (`style_risco_direto`, `style_proximo` ou `style_isento`) e os detalhes dos 4 riscos.
4. Salve o arquivo. As alterações são refletidas instantaneamente no mapa sem necessidade de reiniciar o servidor.
