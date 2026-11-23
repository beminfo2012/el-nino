document.addEventListener("DOMContentLoaded", function() {
    
    // Register datalabels plugin
    Chart.register(ChartDataLabels);

    // Global Chart Defaults
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = "#718096";
    Chart.defaults.scale.grid.color = "#EDF2F7";

    // Standard white datalabels for all charts
    if (typeof ChartDataLabels !== 'undefined') {
        Chart.defaults.set('plugins.datalabels', {
            color: '#FFFFFF',
            font: { weight: 'bold', family: "'Inter', sans-serif", size: 11 },
            display: function(context) {
                const val = context.dataset.data[context.dataIndex];
                return val !== 0 && val !== null && val !== undefined;
            }
        });
    }

    function safeCreateChart(id, config) {
        const el = document.getElementById(id);
        if (!el) return null;
        const existingChart = Chart.getChart(el);
        if (existingChart) existingChart.destroy();
        return new Chart(el, config);
    }

    // Fetch Weather Open-Meteo
    fetch('/api/weather')
        .then(response => response.json())
        .then(data => {
            const statEl = document.getElementById('weather-status');
            if (data.error) {
                document.getElementById('weather-temp').innerText = "--";
                statEl.innerText = "Falha ao carregar";
                statEl.style.color = "#EF4444";
            } else {
                document.getElementById('weather-temp').innerText = Math.round(data.temp);
                document.getElementById('weather-chuva').innerText = data.chuva;
                document.getElementById('weather-umidade').innerText = data.umidade;
                document.getElementById('weather-vento').innerText = data.vento;
                statEl.innerText = "Tempo Real";
                statEl.style.color = "#10B981";

                // Renderizar previsão de 7 dias
                if (data.forecast && data.forecast.length > 0) {
                    const container = document.getElementById('weather-forecast');
                    container.innerHTML = '';
                    data.forecast.forEach((day, i) => {
                        const icon = getWeatherIcon(day.code, day.chuva);
                        const bg = i === 0 ? 'background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border: 1px solid #BFDBFE;' : 'background: #F8FAFC;';
                        container.innerHTML += `
                            <div style="flex: 1; text-align: center; padding: 10px 6px; border-radius: 10px; ${bg}">
                                <div style="font-size: 0.72rem; font-weight: 700; color: #64748B;">${day.dia}</div>
                                <div style="font-size: 0.68rem; color: #94A3B8; margin-bottom: 5px;">${day.data}</div>
                                <div style="font-size: 1.5rem; margin: 4px 0;">${icon}</div>
                                <div style="font-size: 0.82rem; font-weight: 800; color: #DC2626;">${Math.round(day.max)}°</div>
                                <div style="font-size: 0.75rem; color: #64748B;">${Math.round(day.min)}°</div>
                                <div style="font-size: 0.65rem; color: #3B82F6; margin-top: 4px;">${day.chuva}% 🌧</div>
                            </div>`;
                    });
                }
            }
        }).catch(() => {
            document.getElementById('weather-status').innerText = "Erro";
        });

    function getWeatherIcon(code, chuva) {
        if (code === 0) return '☀️';
        if (code <= 2) return '🌤️';
        if (code <= 3) return '☁️';
        if (code <= 48) return '🌫️';
        if (code <= 57) return '🌦️';
        if (code <= 67) return '🌧️';
        if (code <= 77) return '❄️';
        if (code <= 82) return '🌧️';
        if (code <= 99) return '⛈️';
        if (chuva >= 60) return '🌧️';
        if (chuva >= 30) return '🌦️';
        return '🌤️';
    }

    // Fetch Hidroweb Telemetry
    fetch('/api/hidroweb')
        .then(response => response.json())
        .then(data => {
            const valEl = document.getElementById('hidroweb-valor');
            const statEl = document.getElementById('hidroweb-status');
            if (data.error || !data.nivel) {
                valEl.innerText = "Indisponível";
                statEl.innerText = "ANA Indisponível";
                statEl.style.color = "#EF4444";
            } else {
                valEl.innerText = data.nivel;
                if (data.vazao) document.getElementById('hidroweb-vazao').innerText = data.vazao;
                if (data.chuva) document.getElementById('hidroweb-chuva').innerText = data.chuva;
                if (data.data_hora) {
                    const dt = data.data_hora.trim().replace('  ', ' ');
                    document.getElementById('hidroweb-datahora').innerText = 'Leitura: ' + dt.substring(0, 16);
                }
                statEl.innerText = "\u2705 Dados Reais ANA";
                statEl.style.color = "#10B981";

                // Renderizar gráfico de nível mensal
                if (data.nivel_mensal) {
                    const ctxNivel = document.getElementById('hidroweb-nivelChart').getContext('2d');
                    new Chart(ctxNivel, {
                        type: 'line',
                        data: {
                            labels: data.nivel_mensal.labels,
                            datasets: [{
                                label: 'Nível (cm)',
                                data: data.nivel_mensal.values,
                                borderColor: '#0F4C81',
                                backgroundColor: 'rgba(15, 76, 129, 0.08)',
                                borderWidth: 2.5,
                                pointBackgroundColor: data.nivel_mensal.values.map((v, i) =>
                                    i === data.nivel_mensal.values.length - 1 ? '#E53E3E' : '#0F4C81'
                                ),
                                pointRadius: data.nivel_mensal.values.map((v, i) =>
                                    i === data.nivel_mensal.values.length - 1 ? 6 : 4
                                ),
                                pointBorderColor: '#fff',
                                pointBorderWidth: 2,
                                fill: true,
                                tension: 0.35
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false },
                                datalabels: { display: true, color: '#FFFFFF', font: { weight: 'bold', size: 11 } }
                            },
                            scales: {
                                y: {
                                    beginAtZero: false,
                                    grid: { color: '#EFF6FF' },
                                    ticks: { font: { size: 10 } }
                                },
                                x: { grid: { display: false }, ticks: { font: { size: 10 } } }
                            }
                        }
                    });
                }
            }
        }).catch(() => {
            document.getElementById('hidroweb-status').innerText = "Erro de Conexão";
        });

    // Fetch Dashboard Data
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            // Render Educação
            renderSection('educacao', data.educacao);
            // Render Saúde
            renderSection('saude', data.saude);
            // Render Cesan
            if(data.cesan) {
                renderCesan(data.cesan);
            }
            // Render Secmam
            if(data.secmam) {
                renderSecmam(data.secmam);
            }
            // Render Incêndios
            if(data.incendios) {
                renderIncendios(data.incendios);
            }
            // Render Drenagem
            if(data.drenagem) {
                renderDrenagem(data.drenagem);
            }
            // Render Caixas Secas (Serviços Urbanos)
            if(data.caixas_secas) {
                renderCaixasSecas(data.caixas_secas);
            }
            // Render Educação (Rede Municipal — El Niño)
            if(data.educacao_monitoramento || data.educacao_novo) {
                renderEducacaoNovo(data.educacao_monitoramento || data.educacao_novo);
            }
            // Render Assistência Social
            if(data.assistencia_social) {
                renderAssistenciaSocial(data.assistencia_social);
            }
            // Render Vigilância Vetorial
            if(data.vigilancia_vetorial) {
                renderVigilanciaVetorial(data.vigilancia_vetorial);
            }
        });

    // Renderização do Estoque Geral da Assistência Social
    function renderEstoqueGeralCards(lista) {
        const grid = document.getElementById('as-estoque-cards-grid');
        if (!grid) return;

        const badgeMap = {
            'Adequado': { bg: '#DCFCE7', color: '#15803D' },
            'Atenção':  { bg: '#FEF3C7', color: '#B45309' },
            'Crítico':  { bg: '#FEE2E2', color: '#B91C1C' }
        };

        const iconMap = {
            'cesta': '🧺',
            'limpeza': '🧼',
            'solteiro': '🛌',
            'casal': '🛏️',
            'manta': '🧶',
            'filtro': '🚰',
            'passagem': '🎫',
            'higiene': '🧴',
            'colch': '🛏️'
        };

        const getIcon = nome => {
            const n = (nome || '').toLowerCase();
            for (const [k, icon] of Object.entries(iconMap)) {
                if (n.includes(k)) return icon;
            }
            return '📦';
        };

        if (!lista || lista.length === 0) {
            grid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 28px 16px; color: #64748B; background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 10px;">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">📦</div>
                <div style="font-weight: 700; color: #334155; font-size: 0.95rem;">Nenhum insumo registrado na planilha do Google Drive.</div>
            </div>`;
            return;
        }

        grid.innerHTML = lista.map(item => {
            const bInfo = badgeMap[item.status] || { bg: '#F1F5F9', color: '#475569' };
            const icon = getIcon(item.nome || item.item);
            const qtdVal = item.quantidade !== undefined ? item.quantidade : item.qtd;

            return `
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px 16px; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.2s; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                        <span style="font-size: 1.4rem;">${icon}</span>
                        <span style="font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px; background: ${bInfo.bg}; color: ${bInfo.color};">${item.status}</span>
                    </div>
                    <div style="font-weight: 700; color: #1E293B; font-size: 0.95rem; line-height: 1.25;">${item.nome || item.item}</div>
                    <div style="font-size: 0.74rem; color: #64748B; margin-top: 2px;">Estoque Geral</div>
                </div>
                <div style="margin-top: 12px;">
                    <div style="font-size: 1.7rem; font-weight: 800; color: #0F172A; line-height: 1;">
                        ${qtdVal}
                        <span style="font-size: 0.78rem; font-weight: 600; color: #64748B;">${item.unidade_medida || 'unid.'}</span>
                    </div>
                </div>
            </div>`;
        }).join('');
    }

    function renderAssistenciaSocial(d) {
        if (!d) return;

        // Atualizar KPIs da Assistência Social
        if (d.kpis) {
            const setVal = (id, val) => {
                const el = document.getElementById(id);
                if (el) {
                    if (val !== undefined && val !== null && val !== '') {
                        el.innerText = typeof val === 'number' ? val.toLocaleString('pt-BR') : val;
                    } else {
                        el.innerText = '0';
                    }
                }
            };

            // Macroindicadores
            setVal('as-extrema-pobreza', d.kpis.cadunico_extrema_pobreza);
            setVal('as-novos-cadunico', d.kpis.cadunico_novos);
            setVal('as-total-referenciadas', d.kpis.total_referenciadas);
            setVal('as-total-acompanhamento', d.kpis.total_acompanhamento);

            // CRAS I, CRAS II, CREAS
            setVal('as-cras1-ref', d.kpis.cras1_referenciadas);
            setVal('as-cras1-paif', d.kpis.cras1_paif);
            setVal('as-cras2-ref', d.kpis.cras2_referenciadas);
            setVal('as-cras2-paif', d.kpis.cras2_paif);
            setVal('as-creas-paefi', d.kpis.creas_paefi);
            setVal('as-creas-rua', d.kpis.creas_rua);

            // Retrocompatibilidade de IDs
            setVal('as-familias', d.kpis.familias);
            setVal('as-acolhidos', d.kpis.acolhidos);
            setVal('as-beneficios', d.kpis.beneficios);
            setVal('as-atendimentos', d.kpis.atendimentos);
            setVal('as-inseguranca', d.kpis.inseguranca);
            setVal('as-pessoas-rua', d.kpis.pessoas_rua);
        }

        // Total de Estoque Geral
        const totGeral = d.estoque_totais?.consolidado || 0;
        const elBadgeTot = document.getElementById('as-estoque-total-badge');
        if (elBadgeTot) elBadgeTot.innerText = `${totGeral.toLocaleString('pt-BR')} itens`;

        // Renderizar Cards e Tabela do Estoque Geral
        const listaGeral = d.estoque_consolidado || d.estoque_grupos?.consolidado || [];
        renderEstoqueGeralCards(listaGeral);

        const matrizTbody = document.getElementById('as-estoque-matriz-tbody');
        if (matrizTbody) {
            const badgeMap = {
                'Adequado': '<span class="badge-concluido">Adequado</span>',
                'Atenção':  '<span class="badge-andamento">Atenção</span>',
                'Crítico':  '<span class="badge-construcao">Crítico</span>'
            };

            let rowsHtml = '';
            listaGeral.forEach(it => {
                const nomeItem = it.item || it.nome;
                const qtdItem = it.quantidade !== undefined ? it.quantidade : it.qtd;
                const statusItem = it.status || 'Adequado';
                rowsHtml += `
                <tr>
                    <td style="font-weight: 600; color: #1E293B;">${nomeItem}</td>
                    <td style="text-align: center; font-weight: 800; background: #F8FAFC; color: #0F172A; font-size: 0.95rem;">${qtdItem}</td>
                    <td style="text-align: center;">${badgeMap[statusItem] || '<span class="badge-andamento">' + statusItem + '</span>'}</td>
                </tr>`;
            });

            rowsHtml += `
            <tr style="background: #F1F5F9; font-weight: 800; border-top: 2px solid #CBD5E1;">
                <td style="color: #0F172A; font-weight: 800;">TOTAL GERAL DE INSUMOS</td>
                <td style="text-align: center; color: #0F172A; background: #E2E8F0; font-size: 1.05rem;">${totGeral}</td>
                <td style="text-align: center; color: #15803D;">✅ Ativo</td>
            </tr>`;

            matrizTbody.innerHTML = rowsHtml;
        }

        // Tabela de ações
        const tbody = document.getElementById('as-tbody');
        if (tbody && d.acoes && d.acoes.length) {
            tbody.innerHTML = '';
            d.acoes.forEach(r => {
                const statusBadge = r.status === 'Concluído'
                    ? `<span class="badge-concluido">${r.status}</span>`
                    : r.status === 'Em Andamento'
                        ? `<span class="badge-andamento">${r.status}</span>`
                        : `<span class="badge-manutencao">${r.status}</span>`;
                tbody.innerHTML += `<tr>
                    <td>${r.data}</td>
                    <td>${r.local}</td>
                    <td>${r.acao}</td>
                    <td>${r.familias}</td>
                    <td>${statusBadge}</td>
                </tr>`;
            });
        }

        // Estoque antigo para retrocompatibilidade
        const estoqueEl = document.getElementById('as-estoque');
        if (estoqueEl && d.estoque && d.estoque.length) {
            const badgeMap = { 'Adequado': 'badge-concluido', 'Atenção': 'badge-andamento', 'Crítico': 'badge-construcao' };
            estoqueEl.innerHTML = d.estoque.map(item => `
                <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #EFF6FF; font-size:0.82rem;">
                    <div>
                        <div style="font-weight:600; color:#1E293B;">${item.nome || item.item}</div>
                        <div style="font-size:0.72rem; color:#64748B;">${item.cobertura || item.unidade}</div>
                    </div>
                    <span class="${badgeMap[item.status] || 'badge-andamento'}">${item.status}</span>
                </div>`).join('');
        }

        // Gráfico: Demanda por Benefícios Eventuais (linha)
        if (d.beneficios_mes) {
            const tierColor = v => v < 15 ? '#2F855A' : v < 25 ? '#DD6B20' : '#E53E3E';
            const ctx = document.getElementById('as-beneficiosChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: d.beneficios_mes.labels,
                    datasets: [{
                        data: d.beneficios_mes.values,
                        borderColor: '#553C9A',
                        backgroundColor: 'rgba(85,60,154,0.08)',
                        borderWidth: 2.5, fill: true, tension: 0.35,
                        pointRadius: 5,
                        pointBackgroundColor: d.beneficios_mes.values.map(tierColor),
                        pointBorderColor: '#fff', pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false }, datalabels: { display: true, color: '#FFFFFF', font: { weight: 'bold', size: 11 } } },
                    scales: {
                        y: { beginAtZero: true, grid: { color: '#F5F3FF' }, ticks: { font: { size: 10 } } },
                        x: { grid: { display: false }, ticks: { font: { size: 10 } } }
                    }
                }
            });
        }

        // Gráfico: Atendimentos por Localidade (barra horizontal)
        if (d.atendimentos_local) {
            const ctx2 = document.getElementById('as-localidadeChart').getContext('2d');
            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: d.atendimentos_local.labels,
                    datasets: [{ data: d.atendimentos_local.values, backgroundColor: '#0F4C81', borderRadius: 5, maxBarThickness: 22 }]
                },
                options: {
                    indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false }, datalabels: { color: '#fff', align: 'end', anchor: 'end', font: { weight: 'bold' } } },
                    scales: {
                        x: { beginAtZero: true, grid: { color: '#EFF6FF' }, ticks: { font: { size: 10 } } },
                        y: { grid: { display: false }, ticks: { font: { size: 10 } } }
                    }
                }
            });
        }

        // Gráfico: Distribuição por tipo de ação (donut)
        if (d.tipo_acao) {
            const ctx3 = document.getElementById('as-tipoChart').getContext('2d');
            new Chart(ctx3, {
                type: 'doughnut',
                data: {
                    labels: d.tipo_acao.labels,
                    datasets: [{ data: d.tipo_acao.values, backgroundColor: ['#553C9A','#E53E3E','#2F855A','#0F4C81'], borderWidth: 0 }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false, cutout: '62%',
                    plugins: { legend: { position: 'bottom', labels: { font: { size: 10 }, boxWidth: 10, padding: 10 } }, datalabels: { display: true, color: '#FFFFFF', font: { weight: 'bold', size: 11 } } }
                }
            });
        }
    }

    function renderVigilanciaVetorial(d) {
        if (!d) return;

        // Atualiza KPIs da Vigilância
        if (d.kpis) {
            const elDengue = document.getElementById('vv-dengue');
            if (elDengue && d.kpis.dengue_semana !== undefined) elDengue.innerText = d.kpis.dengue_semana;

            const elLiraa = document.getElementById('vv-liraa');
            if (elLiraa && d.kpis.liraa_medio !== undefined) elLiraa.innerText = d.kpis.liraa_medio;

            const elFocos = document.getElementById('vv-focos');
            if (elFocos && d.kpis.focos_eliminados !== undefined) elFocos.innerText = d.kpis.focos_eliminados;

            const elCobertura = document.getElementById('vv-cobertura');
            if (elCobertura && d.kpis.cobertura !== undefined) elCobertura.innerText = d.kpis.cobertura;

            const elLepto = document.getElementById('vv-leptospirose');
            if (elLepto && d.kpis.leptospirose !== undefined) elLepto.innerText = d.kpis.leptospirose;

            const elDda = document.getElementById('vv-dda');
            if (elDda && d.kpis.dda !== undefined) elDda.innerText = d.kpis.dda;

            const elExaustao = document.getElementById('vv-exaustao');
            if (elExaustao && d.kpis.exaustao !== undefined) elExaustao.innerText = d.kpis.exaustao;
        }

        // Tabela de ações de controle vetorial
        const tbody = document.getElementById('vv-tbody');
        if (tbody && d.acoes && d.acoes.length) {
            tbody.innerHTML = '';
            d.acoes.forEach(r => {
                const statusBadge = r.status === 'Concluído'
                    ? `<span class="badge-concluido">${r.status}</span>`
                    : r.status === 'Em Andamento'
                        ? `<span class="badge-andamento">${r.status}</span>`
                        : `<span class="badge-manutencao">${r.status}</span>`;
                tbody.innerHTML += `<tr>
                    <td>${r.data}</td>
                    <td>${r.local}</td>
                    <td>${r.acao}</td>
                    <td>${r.focos_eliminados}</td>
                    <td>${statusBadge}</td>
                </tr>`;
            });
        }

        // Estoque de insumos estratégicos
        const estoqueEl = document.getElementById('vv-estoque');
        if (estoqueEl && d.estoque && d.estoque.length) {
            const badgeMap = { 'Adequado': 'badge-concluido', 'Atenção': 'badge-andamento', 'Crítico': 'badge-construcao' };
            estoqueEl.innerHTML = d.estoque.map(item => `
                <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #FFF1F2; font-size:0.82rem;">
                    <div>
                        <div style="font-weight:600; color:#1E293B;">${item.nome}</div>
                        <div style="font-size:0.72rem; color:#64748B;">${item.cobertura}</div>
                    </div>
                    <span class="${badgeMap[item.status] || 'badge-andamento'}">${item.status}</span>
                </div>`).join('');
        }

        // Gráfico: Evolução de casos de dengue (linha)
        if (d.casos_dengue) {
            const tierColor = v => v < 12 ? '#2F855A' : v < 20 ? '#DD6B20' : '#E53E3E';
            const ctx = document.getElementById('vv-casosChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: d.casos_dengue.labels,
                    datasets: [{
                        data: d.casos_dengue.values,
                        borderColor: '#97266D',
                        backgroundColor: 'rgba(151,38,109,0.08)',
                        borderWidth: 2.5, fill: true, tension: 0.35,
                        pointRadius: 5,
                        pointBackgroundColor: d.casos_dengue.values.map(tierColor),
                        pointBorderColor: '#fff', pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false }, datalabels: { display: true, color: '#FFFFFF', font: { weight: 'bold', size: 11 } } },
                    scales: {
                        y: { beginAtZero: true, grid: { color: '#FCE7F3' }, ticks: { font: { size: 10 } } },
                        x: { grid: { display: false }, ticks: { font: { size: 10 } } }
                    }
                }
            });
        }

        // Gráfico: Índice LIRAa por região (barra horizontal colorida)
        if (d.liraa) {
            const liraaColors = d.liraa.values.map(v => v < 1 ? '#2F855A' : v < 4 ? '#DD6B20' : '#E53E3E');
            const ctx2 = document.getElementById('vv-liraaChart').getContext('2d');
            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: d.liraa.labels,
                    datasets: [{ data: d.liraa.values, backgroundColor: liraaColors, borderRadius: 5, maxBarThickness: 22 }]
                },
                options: {
                    indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false }, datalabels: { color: '#fff', align: 'end', anchor: 'end', font: { weight: 'bold' }, formatter: v => v+'%' } },
                    scales: {
                        x: { beginAtZero: true, grid: { color: '#FCE7F3' }, ticks: { font: { size: 10 }, callback: v => v+'%' } },
                        y: { grid: { display: false }, ticks: { font: { size: 10 } } }
                    }
                }
            });
        }

        // Gráfico: Casos por localidade (barra horizontal)
        if (d.casos_local) {
            const ctx3 = document.getElementById('vv-localChart').getContext('2d');
            new Chart(ctx3, {
                type: 'bar',
                data: {
                    labels: d.casos_local.labels,
                    datasets: [{ data: d.casos_local.values, backgroundColor: '#97266D', borderRadius: 5, maxBarThickness: 22 }]
                },
                options: {
                    indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false }, datalabels: { color: '#fff', align: 'end', anchor: 'end', font: { weight: 'bold' } } },
                    scales: {
                        x: { beginAtZero: true, grid: { color: '#FCE7F3' }, ticks: { font: { size: 10 } } },
                        y: { grid: { display: false }, ticks: { font: { size: 10 } } }
                    }
                }
            });
        }
    }

    function renderEducacaoNovo(d) {
        if (!d) return;

        // ── KPIs Principais ──────────────────────────────────────────────────
        if (d.kpis) {
            const elRisco = document.getElementById('edu-kpi-risco');
            if (elRisco && d.kpis.escolas_risco !== undefined) elRisco.innerText = d.kpis.escolas_risco;

            const elClim = document.getElementById('edu-kpi-climatizacao');
            if (elClim && d.kpis.escolas_sem_climatizacao !== undefined) elClim.innerText = d.kpis.escolas_sem_climatizacao;

            const elSusp = document.getElementById('edu-kpi-suspensao');
            if (elSusp && d.kpis.dias_aula_suspensos !== undefined) elSusp.innerText = d.kpis.dias_aula_suspensos;

            const elAbs = document.getElementById('edu-kpi-absenteismo');
            if (elAbs && d.kpis.absenteismo_onda_calor !== undefined) elAbs.innerText = d.kpis.absenteismo_onda_calor;
        }

        // ── Indicadores Complementares ───────────────────────────────────────
        if (d.indicadores_complementares) {
            const elRes = document.getElementById('edu-comp-reservatorio');
            if (elRes && d.indicadores_complementares.reservatorio_insuficiente !== undefined) {
                elRes.innerText = d.indicadores_complementares.reservatorio_insuficiente;
            }

            const elRem = document.getElementById('edu-comp-remoto');
            if (elRem && d.indicadores_complementares.ensino_remoto !== undefined) {
                elRem.innerText = d.indicadores_complementares.ensino_remoto;
            }

            const elAbr = document.getElementById('edu-comp-abrigo');
            if (elAbr && d.indicadores_complementares.escola_abrigo !== undefined) {
                elAbr.innerText = d.indicadores_complementares.escola_abrigo;
            }
        }

        // ── Gráfico de Absenteísmo (linha com cores por nível) ──────────────
        const absData = d.absenteismo_semanas || d.absenteismo_semanal;
        if (absData && absData.labels && absData.values) {
            const tierColor = v => v < 5 ? '#2F855A' : v < 7 ? '#DD6B20' : '#E53E3E';
            const ctx = document.getElementById('edu-absenteismoChart');
            if (ctx) {
                safeCreateChart('edu-absenteismoChart', {
                    type: 'line',
                    data: {
                        labels: absData.labels,
                        datasets: [{
                            data: absData.values,
                            borderColor: '#2F855A',
                            backgroundColor: 'rgba(47,133,90,0.08)',
                            borderWidth: 2.5,
                            fill: true,
                            tension: 0.35,
                            pointRadius: 6,
                            pointBackgroundColor: absData.values.map(tierColor),
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            datalabels: {
                                display: true,
                                align: 'top',
                                color: ctx => tierColor(absData.values[ctx.dataIndex]),
                                font: { weight: 'bold', size: 10 },
                                formatter: v => v + '%'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { color: '#F0FDF4' },
                                ticks: { font: { size: 10 }, callback: v => v + '%' }
                            },
                            x: { grid: { display: false }, ticks: { font: { size: 10 } } }
                        }
                    }
                });
            }
        }

        // ── Tabela de Ocorrências ────────────────────────────────────────────
        const tbody = document.getElementById('edu-ocorrencias-tbody') || document.getElementById('edu-tbody');
        if (tbody && d.ocorrencias && d.ocorrencias.length) {
            const badgeMap = {
                'Concluído':    'badge-concluido',
                'Em Andamento': 'badge-andamento',
                'Planejado':    'badge-construcao'
            };
            tbody.innerHTML = '';
            d.ocorrencias.forEach(r => {
                const badgeClass = r.status_class || badgeMap[r.status] || 'badge-andamento';
                const badge = `<span class="${badgeClass}">${r.status}</span>`;
                tbody.innerHTML += `<tr>
                    <td>${r.data || ''}</td>
                    <td>${r.escola || r.local || ''}</td>
                    <td>${r.motivo || ''}</td>
                    <td>${r.acao || ''}</td>
                    <td>${badge}</td>
                </tr>`;
            });
        }

        // ── Infraestrutura e Planejamento (Item 4.6) ────────────────────────
        const infraEl = document.getElementById('edu-planejamento-lista') || document.getElementById('edu-infraestrutura');
        const acoesPlanejamento = d.indicadores_complementares?.acoes_planejamento || d.infraestrutura;
        if (infraEl && acoesPlanejamento && acoesPlanejamento.length) {
            const badgeMap = {
                'Concluído':    'badge-concluido',
                'Em Andamento': 'badge-andamento',
                'Pendente':     'badge-construcao',
                'Planejado':    'badge-construcao'
            };
            infraEl.innerHTML = acoesPlanejamento.map(item => {
                const st = item.status || 'Planejado';
                const badgeClass = item.status_class || badgeMap[st] || 'badge-andamento';
                const titulo = item.titulo || item.nome || '';
                const desc = item.descricao || '';
                return `
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding:8px 0; border-bottom:1px solid #DCFCE7; font-size:0.83rem;">
                    <div>
                        <div style="font-weight:600; color:#1E293B;">${titulo}</div>
                        <div style="font-size:0.72rem; color:#64748B; margin-top:2px;">${desc}</div>
                    </div>
                    <span class="${badgeClass}">${st}</span>
                </div>`;
            }).join('');
        }
    }

    function renderDrenagem(registros) {
        const tbody = document.getElementById('drenagem-tbody');
        if (!tbody || !registros || registros.length === 0) return;

        let totalManut = 0, totalConst = 0, totalKm = 0;

        tbody.innerHTML = '';
        registros.forEach(r => {
            const tipoBadge = r.tipo === 'Manutenção'
                ? `<span class="badge-manutencao">${r.tipo}</span>`
                : `<span class="badge-construcao">${r.tipo}</span>`;
            const statusBadge = r.status === 'Concluído'
                ? `<span class="badge-concluido">${r.status}</span>`
                : `<span class="badge-andamento">${r.status}</span>`;

            tbody.innerHTML += `<tr>
                <td>${r.data}</td>
                <td>${tipoBadge}</td>
                <td>${r.local}</td>
                <td>${r.descricao}</td>
                <td>${r.extensao_m}</td>
                <td>${statusBadge}</td>
            </tr>`;

            if (r.tipo === 'Manutenção') totalManut++;
            else totalConst++;
            totalKm += parseInt(r.extensao_m) || 0;
        });

        document.getElementById('drenagem-total').innerText = registros.length;
        document.getElementById('drenagem-manutencoes').innerText = totalManut;
        document.getElementById('drenagem-construcoes').innerText = totalConst;
        document.getElementById('drenagem-km').innerText = totalKm;

        // Gráfico por localidade
        const contagem = {};
        registros.forEach(r => { contagem[r.local] = (contagem[r.local] || 0) + 1; });
        const labels = Object.keys(contagem);
        const valores = Object.values(contagem);

        const ctx = document.getElementById('drenagem-locaisChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Intervenções',
                    data: valores,
                    backgroundColor: '#0F4C81',
                    borderRadius: 5
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, datalabels: { color: '#fff', align: 'end', anchor: 'end', font: { weight: 'bold' } } },
                scales: { x: { beginAtZero: true }, y: { grid: { display: false } } }
            }
        });
    }

    // -------------------------------------------------------------
    // CONTROLE DE ABAS E RENDERIZAÇÃO DE INCÊNDIOS (SCBV & CBMES)
    // -------------------------------------------------------------
    window.trocarAbaIncendios = function(aba) {
        const btnSplit = document.getElementById('btn-inc-split');
        const btnScbv = document.getElementById('btn-inc-scbv');
        const btnCbmes = document.getElementById('btn-inc-cbmes');
        const btnCons = document.getElementById('btn-inc-consolidado');

        [btnSplit, btnScbv, btnCbmes, btnCons].forEach(b => { if(b) b.classList.remove('active'); });

        const paneScbv = document.getElementById('pane-inc-scbv');
        const paneCbmes = document.getElementById('pane-inc-cbmes');
        const paneCons = document.getElementById('pane-inc-consolidado');

        if (aba === 'split') {
            if(btnSplit) btnSplit.classList.add('active');
            if(paneScbv) { paneScbv.style.display = 'block'; }
            if(paneCbmes) { paneCbmes.style.display = 'block'; }
            if(paneCons) { paneCons.style.display = 'none'; }
        } else if (aba === 'scbv') {
            if(btnScbv) btnScbv.classList.add('active');
            if(paneScbv) { paneScbv.style.display = 'block'; }
            if(paneCbmes) { paneCbmes.style.display = 'none'; }
            if(paneCons) { paneCons.style.display = 'none'; }
        } else if (aba === 'cbmes') {
            if(btnCbmes) btnCbmes.classList.add('active');
            if(paneScbv) { paneScbv.style.display = 'none'; }
            if(paneCbmes) { paneCbmes.style.display = 'block'; }
            if(paneCons) { paneCons.style.display = 'none'; }
        } else if (aba === 'consolidado') {
            if(btnCons) btnCons.classList.add('active');
            if(paneScbv) { paneScbv.style.display = 'none'; }
            if(paneCbmes) { paneCbmes.style.display = 'none'; }
            if(paneCons) { paneCons.style.display = 'block'; }
        }
    };

    function renderIncendios(data) {
        if (!data) return;
        const scbv = data.scbv || {
            total: 0,
            evolucao_labels: [],
            evolucao_dados: [],
            locais_labels: [],
            locais_dados: [],
            area_total_ha: 0
        };
        const cbmes = data.cbmes || {
            total: 0,
            evolucao_labels: [],
            evolucao_dados: [],
            locais_labels: [],
            locais_dados: [],
            area_total_ha: 0
        };

        const totalFocos = data.total_focos !== undefined ? data.total_focos : (scbv.total + cbmes.total);
        const areaTotal = ((scbv.area_total_ha || 0) + (cbmes.area_total_ha || 0)).toFixed(1);

        const elTotal = document.getElementById('inc-total-focos');
        const elScbv = document.getElementById('inc-total-scbv');
        const elCbmes = document.getElementById('inc-total-cbmes');
        const elArea = document.getElementById('inc-area-total');

        if(elTotal) elTotal.innerText = totalFocos;
        if(elScbv) elScbv.innerText = scbv.total;
        if(elCbmes) elCbmes.innerText = cbmes.total;
        if(elArea) elArea.innerText = areaTotal + ' ha';

        // 1. Gráfico SCBV Evolução
        safeCreateChart('incendios-scbv-evolucaoChart', {
            type: 'line',
            data: {
                labels: scbv.evolucao_labels,
                datasets: [{
                    label: 'Atendimentos SCBV',
                    data: scbv.evolucao_dados,
                    borderColor: '#EA580C',
                    backgroundColor: 'rgba(234, 88, 12, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#C2410C',
                    pointBorderColor: '#fff',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    datalabels: { color: '#C2410C', align: 'top', font: { weight: 'bold' } }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#FFEDD5' }, ticks: { stepSize: 1 } },
                    x: { grid: { display: false } }
                }
            }
        });

        // 2. Gráfico SCBV Locais
        safeCreateChart('incendios-scbv-locaisChart', {
            type: 'bar',
            data: {
                labels: scbv.locais_labels,
                datasets: [{
                    label: 'Ocorrências SCBV',
                    data: scbv.locais_dados,
                    backgroundColor: '#F97316',
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    datalabels: { color: '#fff', align: 'end', anchor: 'end', font: { weight: 'bold' } }
                },
                scales: {
                    x: { beginAtZero: true, grid: { color: '#FFEDD5' }, ticks: { stepSize: 1 } },
                    y: { grid: { display: false } }
                }
            }
        });

        // 3. Gráfico CBMES Evolução
        safeCreateChart('incendios-cbmes-evolucaoChart', {
            type: 'line',
            data: {
                labels: cbmes.evolucao_labels,
                datasets: [{
                    label: 'Atendimentos CBMES',
                    data: cbmes.evolucao_dados,
                    borderColor: '#DC2626',
                    backgroundColor: 'rgba(220, 38, 38, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#B91C1C',
                    pointBorderColor: '#fff',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    datalabels: { color: '#B91C1C', align: 'top', font: { weight: 'bold' } }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#FEE2E2' }, ticks: { stepSize: 1 } },
                    x: { grid: { display: false } }
                }
            }
        });

        // 4. Gráfico CBMES Locais
        safeCreateChart('incendios-cbmes-locaisChart', {
            type: 'bar',
            data: {
                labels: cbmes.locais_labels,
                datasets: [{
                    label: 'Ocorrências CBMES',
                    data: cbmes.locais_dados,
                    backgroundColor: '#EF4444',
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    datalabels: { color: '#fff', align: 'end', anchor: 'end', font: { weight: 'bold' } }
                },
                scales: {
                    x: { beginAtZero: true, grid: { color: '#FEE2E2' }, ticks: { stepSize: 1 } },
                    y: { grid: { display: false } }
                }
            }
        });

        // 5. Gráfico Consolidado Comparativo
        const compLabels = data.evolucao_labels || scbv.evolucao_labels;
        safeCreateChart('incendios-comparativoChart', {
            type: 'bar',
            data: {
                labels: compLabels,
                datasets: [
                    {
                        label: 'Bombeiros Voluntários (SCBV)',
                        data: scbv.evolucao_dados,
                        backgroundColor: '#EA580C',
                        borderRadius: 4
                    },
                    {
                        label: 'CBMES 6º Batalhão',
                        data: cbmes.evolucao_dados,
                        backgroundColor: '#DC2626',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true, position: 'top' },
                    datalabels: { color: '#fff', align: 'center', anchor: 'center', font: { weight: 'bold' } }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#F1F5F9' }, ticks: { stepSize: 1 } },
                    x: { grid: { display: false } }
                }
            }
        });

        // 6. Gráfico Geral Locais
        safeCreateChart('incendios-geral-locaisChart', {
            type: 'bar',
            data: {
                labels: data.locais_labels || ['Garrafão', 'Rio Possmoser', 'Caramuru', 'Alto Santa Maria'],
                datasets: [{
                    label: 'Total de Ocorrências',
                    data: data.locais_dados || [2, 1, 1, 1],
                    backgroundColor: '#B91C1C',
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    datalabels: { color: '#fff', align: 'end', anchor: 'end', font: { weight: 'bold' } }
                },
                scales: {
                    x: { beginAtZero: true, grid: { color: '#F1F5F9' }, ticks: { stepSize: 1 } },
                    y: { grid: { display: false } }
                }
            }
        });
    }

    // -------------------------------------------------------------
    // RENDERIZAÇÃO: SERVIÇOS URBANOS - CAIXAS SECAS
    // -------------------------------------------------------------
    function renderCaixasSecas(data) {
        if (!data) return;

        const elTotal = document.getElementById('caixas-total-qtd');
        const elAbertas = document.getElementById('caixas-abertas-qtd');
        const elManut = document.getElementById('caixas-manut-qtd');
        const elVolume = document.getElementById('caixas-volume-total');

        if (elTotal) elTotal.innerText = data.total_caixas || 0;
        if (elAbertas) elAbertas.innerText = data.caixas_abertura || 0;
        if (elManut) elManut.innerText = data.caixas_manutencao || 0;
        if (elVolume) elVolume.innerText = (data.volume_total_m3 || 0).toLocaleString('pt-BR') + ' m³';

        // Tabela Operacional
        const tbody = document.getElementById('caixas-tbody');
        if (tbody && data.registros && data.registros.length > 0) {
            tbody.innerHTML = '';
            data.registros.forEach(r => {
                const tipoBadge = r.tipo === 'Abertura'
                    ? `<span class="badge-abertura">Abertura</span>`
                    : `<span class="badge-manutencao">Manutenção</span>`;

                const statusBadge = r.status === 'Concluído'
                    ? `<span class="badge-concluido">Concluído</span>`
                    : (r.status === 'Em Andamento'
                        ? `<span class="badge-andamento">Em Andamento</span>`
                        : `<span class="badge-planejado" style="background:#F1F5F9; color:#475569; padding:3px 8px; border-radius:6px; font-weight:700; font-size:0.75rem;">Planejado</span>`);

                tbody.innerHTML += `<tr>
                    <td>${r.data || '—'}</td>
                    <td>${tipoBadge}</td>
                    <td><strong>${r.local || '—'}</strong></td>
                    <td style="font-size: 0.85rem; color: #475569;">${r.trecho || '—'}</td>
                    <td style="font-weight: 700; text-align: center;">${r.quantidade || 0}</td>
                    <td style="text-align: right;">${(r.volume_m3 || 0).toLocaleString('pt-BR')} m³</td>
                    <td>${statusBadge}</td>
                    <td style="font-size: 0.82rem; color: #64748B;">${r.equipe || 'Equipe SEMOSU'}</td>
                </tr>`;
            });
        }

        // Gráfico por Localidade
        safeCreateChart('caixas-locaisChart', {
            type: 'bar',
            data: {
                labels: data.locais_labels || [],
                datasets: [{
                    label: 'Caixas Secas',
                    data: data.locais_dados || [],
                    backgroundColor: '#D97706',
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    datalabels: { color: '#fff', align: 'end', anchor: 'end', font: { weight: 'bold' } }
                },
                scales: {
                    x: { beginAtZero: true, grid: { color: '#FEF3C7' }, ticks: { stepSize: 2 } },
                    y: { grid: { display: false } }
                }
            }
        });
    }

    function renderCesan(data) {
        // ── Badges de Status por Captação ────────────────────────────────────
        if (data.captacoes && data.captacoes.length) {
            const statusStyle = {
                'Normal':   { bg: '#DCFCE7', color: '#2F855A', border: '#2F855A' },
                'Atenção':  { bg: '#FEF3C7', color: '#B45309', border: '#DD6B20' },
                'Alerta':   { bg: '#FFEDD5', color: '#C2410C', border: '#DD6B20' },
                'Crítico':  { bg: '#FEE2E2', color: '#C53030', border: '#E53E3E' }
            };
            data.captacoes.forEach(cap => {
                const badgeEl = document.getElementById(`cesan-status-${cap.num}`);
                const cardEl  = badgeEl ? badgeEl.closest('.card') : null;
                const style   = statusStyle[cap.status] || statusStyle['Normal'];
                if (badgeEl) {
                    badgeEl.innerText          = cap.status.toUpperCase();
                    badgeEl.style.background   = style.bg;
                    badgeEl.style.color        = style.color;
                }
                if (cardEl) {
                    cardEl.style.borderLeftColor = style.border;
                }
            });
        }

        // ── Gráfico de Linha do Tempo ─────────────────────────────────────────
        if (!data.timeline_labels || data.timeline_labels.length === 0) return;

        const ctx = document.getElementById('cesan-timelineChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.timeline_labels,
                datasets: [{
                    label: 'Status da Captação',
                    data: data.timeline_values,
                    borderColor: '#0F4C81',
                    backgroundColor: 'rgba(15, 76, 129, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: data.timeline_values.map(v => {
                        if (v === 3) return '#E53E3E'; // Crítico
                        if (v === 2) return '#DD6B20'; // Alerta
                        if (v === 1) return '#FCD34D'; // Atenção
                        return '#2F855A';              // Normal
                    }),
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    datalabels: {
                        display: true,
                        align: 'top',
                        color: '#1E293B',
                        font: { weight: 'bold' },
                        formatter: function(value, context) {
                            return data.timeline_status[context.dataIndex];
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 3.5,
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                if (value === 3) return 'Crítico (3)';
                                if (value === 2) return 'Alerta (2)';
                                if (value === 1) return 'Atenção (1)';
                                if (value === 0) return 'Normal (0)';
                                return '';
                            }
                        }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    function renderSection(prefix, data) {
        initTipologia(prefix, data.tipologia_risco);
        initOcorrencias(prefix, data.ocorrencias_tipo);
        initTopLocalidades(prefix, data.top_5_localidades);
    }

    // =======================
    // EXPORTAR PDF (NOVO RELATÓRIO OFICIAL)
    // =======================
    window.exportarPDF = function() {
        const btn = document.getElementById('btn-exportar-pdf');
        btn.innerText = '⏳ Gerando Documento...';
        btn.disabled = true;

        // Abre a nova rota oficial em uma nova aba
        window.open('/relatorio', '_blank');

        setTimeout(() => {
            btn.innerText = '📄 Exportar Relatório PDF';
            btn.disabled = false;
        }, 1500);
    };

    function initTipologia(prefix, data) {
        document.getElementById(`${prefix}-tipologiaTotal`).innerText = data.total;
        
        const colors = ['#718096', '#2F855A', '#0F4C81', '#DD6B20'];
        
        // Build Legend
        const legendContainer = document.getElementById(`${prefix}-tipologiaLegend`);
        legendContainer.innerHTML = ''; // Clear existing
        data.labels.forEach((label, i) => {
            const perc = data.total > 0 ? ((data.values[i] / data.total) * 100).toFixed(1) : 0;
            legendContainer.innerHTML += `
                <div class="legend-row">
                    <div class="legend-label">
                        <span class="dot" style="background-color: ${colors[i]}"></span>
                        <div>${label} <br> <span class="val-number">${data.values[i]}</span></div>
                    </div>
                    <div class="legend-values">
                        <span class="val-perc">${perc}%</span>
                    </div>
                </div>
            `;
        });

        const ctx = document.getElementById(`${prefix}-tipologiaChart`).getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: colors,
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    datalabels: { display: true, color: '#FFFFFF', font: { weight: 'bold', size: 11 } }
                }
            }
        });
    }

    function initOcorrencias(prefix, data) {
        const ctx = document.getElementById(`${prefix}-ocorrenciasTipoChart`).getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: '#0F4C81',
                    borderRadius: 4,
                    barPercentage: 0.4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    datalabels: { 
                        display: true, 
                        anchor: 'end',
                        align: 'end',
                        color: '#1E293B',
                        font: { weight: 'bold' }
                    }
                },
                scales: {
                    x: { display: false },
                    y: { grid: { display: false }, border: {display: false} }
                }
            }
        });
    }

    function initTopLocalidades(prefix, data) {
        const ctx = document.getElementById(`${prefix}-topLocalidadesChart`).getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: '#DD6B20',
                    borderRadius: 4,
                    barPercentage: 0.4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    datalabels: { 
                        display: true, 
                        anchor: 'end',
                        align: 'end',
                        color: '#1E293B',
                        font: { weight: 'bold' }
                    }
                },
                scales: {
                    x: { display: false },
                    y: { grid: { display: false }, border: {display: false} }
                }
            }
        });
    }
    function renderCesan(data) {
        if (!data) return;
        if (data.captacoes && data.captacoes.length) {
            const statusStyle = {
                'Normal':   { bg: '#DCFCE7', color: '#2F855A', border: '#2F855A' },
                'Atenção':  { bg: '#FEF3C7', color: '#B45309', border: '#DD6B20' },
                'Alerta':   { bg: '#FFEDD5', color: '#C2410C', border: '#DD6B20' },
                'Crítico':  { bg: '#FEE2E2', color: '#C53030', border: '#E53E3E' }
            };
            const cardsContainer = document.getElementById('cesan-cards-container');
            if (cardsContainer) {
                cardsContainer.innerHTML = '';
                data.captacoes.forEach(cap => {
                    const style = statusStyle[cap.status] || statusStyle['Normal'];
                    const cardHTML = `
                        <div class="card" style="border-left: 4px solid ${style.border}; padding: 16px; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                            <div class="card-header" style="margin-bottom: 0;">
                                <h2 style="font-size: 1.1rem; line-height: 1.4; color: #1E293B;">${cap.name}</h2>
                            </div>
                            <div style="margin-top: 12px; display: flex; align-items: center; justify-content: space-between;">
                                <span style="font-size: 0.85rem; color: #64748B;">
                                    ⏱️ Último Informe: ${cap.date}
                                </span>
                                <span id="cesan-status-${cap.num}" class="badge" style="background: ${style.bg}; color: ${style.color}; font-weight: bold; padding: 4px 10px; border-radius: 9999px;">
                                    ${(cap.status || '').toUpperCase()}
                                </span>
                            </div>
                        </div>
                    `;
                    cardsContainer.insertAdjacentHTML('beforeend', cardHTML);
                });
            }
        }

        if (data.timeline_labels && data.timeline_labels.length > 0) {
            safeCreateChart('cesan-timelineChart', {
                type: 'line',
                data: {
                    labels: data.timeline_labels,
                    datasets: [{
                        label: 'Status da Captação',
                        data: data.timeline_values,
                        borderColor: '#0F4C81',
                        backgroundColor: 'rgba(15, 76, 129, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: data.timeline_values ? data.timeline_values.map(v => {
                            if (v === 3) return '#E53E3E';
                            if (v === 2) return '#F97316';
                            if (v === 1) return '#FCD34D';
                            return '#10B981';
                        }) : '#0F4C81',
                        pointRadius: 6,
                        fill: true,
                        tension: 0.2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        datalabels: { display: true, color: '#FFFFFF', font: { weight: 'bold', size: 11 } }
                    },
                    scales: {
                        y: {
                            min: 0,
                            max: 3,
                            ticks: {
                                stepSize: 1,
                                callback: function(val) {
                                    const labels = ['Normal (0)', 'Atenção (1)', 'Alerta (2)', 'Crítico (3)'];
                                    return labels[val] !== undefined ? labels[val] : val;
                                }
                            }
                        },
                        x: { grid: { display: false } }
                    }
                }
            });
        }
    }

    function renderSecmam(d) {
        if (!d) return;

        if (d.kpis) {
            let el_cadastrados = document.getElementById('secmam-cadastrados');
            if (el_cadastrados) el_cadastrados.innerText = d.kpis.cadastrados;
            
            let el_intervencoes = document.getElementById('secmam-intervencoes');
            if (el_intervencoes) el_intervencoes.innerText = d.kpis.intervencoes_pendentes;
            
            let el_critico = document.getElementById('secmam-critico');
            if (el_critico) el_critico.innerText = d.kpis.risco_critico;
            
            let el_eletrica = document.getElementById('secmam-eletrica');
            if (el_eletrica) el_eletrica.innerText = d.kpis.interferencia_edp;
        }

        if (d.distribuicao_risco) {
            safeCreateChart('secmam-riscoChart', {
                type: 'doughnut',
                data: {
                    labels: d.distribuicao_risco.labels,
                    datasets: [{
                        data: d.distribuicao_risco.values,
                        backgroundColor: d.distribuicao_risco.colors,
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '65%',
                    plugins: {
                        legend: { position: 'right', labels: { font: { size: 11, family: "'Inter', sans-serif" }, padding: 15 } },
                        datalabels: { display: true, color: '#FFFFFF', font: { weight: 'bold', size: 11 } }
                    }
                }
            });
        }

        if (d.tipos_intervencao) {
            safeCreateChart('secmam-intervencaoChart', {
                type: 'bar',
                data: {
                    labels: d.tipos_intervencao.labels,
                    datasets: [{
                        data: d.tipos_intervencao.values,
                        backgroundColor: d.tipos_intervencao.colors,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false }, datalabels: { display: true, color: '#FFFFFF', font: { weight: 'bold', size: 11 } } },
                    scales: {
                        y: { beginAtZero: true, grid: { color: '#F1F5F9' } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        if (d.interferencia_edp) {
            safeCreateChart('secmam-eletricaChart', {
                type: 'bar',
                data: {
                    labels: d.interferencia_edp.labels,
                    datasets: [{
                        data: d.interferencia_edp.values,
                        backgroundColor: d.interferencia_edp.colors,
                        borderRadius: 6,
                        barThickness: 40
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false }, datalabels: { display: true, color: '#FFFFFF', font: { weight: 'bold', size: 11 } } },
                    scales: {
                        x: { beginAtZero: true, grid: { color: '#F1F5F9' } },
                        y: { grid: { display: false } }
                    }
                }
            });
        }

        if (d.cronograma_prioridade) {
            safeCreateChart('secmam-prioridadeChart', {
                type: 'line',
                data: {
                    labels: d.cronograma_prioridade.labels,
                    datasets: [{
                        label: 'Quantidade',
                        data: d.cronograma_prioridade.values,
                        borderColor: '#1D4ED8',
                        backgroundColor: 'rgba(29, 78, 216, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#1D4ED8',
                        pointRadius: 5,
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false }, datalabels: { display: true, color: '#FFFFFF', font: { weight: 'bold', size: 11 } } },
                    scales: {
                        y: { beginAtZero: true, grid: { color: '#F1F5F9' } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        const tbody = document.getElementById('secmam-tbody');
        if (tbody && d.exemplares_criticos) {
            tbody.innerHTML = '';
            d.exemplares_criticos.forEach(item => {
                const tr = document.createElement('tr');
                let badgeRisco = 'background: #FEE2E2; color: #991B1B;';
                if (item.risco === 'Alto') badgeRisco = 'background: #FFEDD5; color: #9A3412;';

                tr.innerHTML = `
                    <td style="font-weight: 700; color: #1E293B;">${item.tombamento}</td>
                    <td>${item.especie}</td>
                    <td>${item.local}</td>
                    <td style="font-size: 0.75rem; color: #64748B;">${item.coordenadas}</td>
                    <td><span style="padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; ${badgeRisco}">${item.risco}</span></td>
                    <td>${item.intervencao}</td>
                    <td style="font-weight: 600;">${item.prazo}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    }

    // Scroll Spy robusto e fluido para destacar a guia ativa no menu
    function initScrollSpy() {
        const navBtns = document.querySelectorAll('.nav-tab-btn');
        const sections = Array.from(document.querySelectorAll('.thematic-block[id], [id^="sec-"]'));
        if (!sections.length || !navBtns.length) return;

        function updateScrollSpy() {
            const scrollPos = window.scrollY + 140; // compensação do header fixo
            let activeId = '';

            for (let i = 0; i < sections.length; i++) {
                const sec = sections[i];
                const top = sec.offsetTop;
                const height = sec.offsetHeight;
                if (scrollPos >= top && scrollPos < top + height) {
                    activeId = sec.getAttribute('id');
                    break;
                }
            }

            // Caso esteja no finalzinho da página, força ativar a última seção
            if ((window.innerHeight + window.scrollY) >= (document.documentElement.scrollHeight - 60)) {
                if (sections.length > 0) {
                    activeId = sections[sections.length - 1].getAttribute('id');
                }
            }

            if (activeId) {
                navBtns.forEach(btn => {
                    const href = btn.getAttribute('href');
                    if (href === '#' + activeId) {
                        btn.classList.add('active');
                    } else {
                        btn.classList.remove('active');
                    }
                });
            }
        }

        window.addEventListener('scroll', updateScrollSpy, { passive: true });
        window.addEventListener('resize', updateScrollSpy, { passive: true });
        updateScrollSpy();
    }

    initScrollSpy();
});


// =======================
// ABERTURA DE RELATÓRIO COMPONENTIZADO (GERAL OU SETORIAL)
// =======================
window.abrirRelatorio = function(setorId) {
    if (setorId && setorId !== 'geral') {
        window.open('/relatorio?setor=' + encodeURIComponent(setorId), '_blank');
    } else {
        window.open('/relatorio', '_blank');
    }
};

window.exportarPDF = function() {
    window.abrirRelatorio('geral');
};

// Alias para compatibilidade
window.imprimirBloco = function(targetId, tituloSetor) {
    window.abrirRelatorio(targetId);
};


