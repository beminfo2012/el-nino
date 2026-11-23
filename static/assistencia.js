document.addEventListener('DOMContentLoaded', () => {
    // Inicializar Mapa
    const map = L.map('map').setView([-20.0461, -40.7456], 12); // Centro provisório de SMJ

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Tentar carregar o KMZ se a lib omnivore estiver funcionando bem
    // Omnivore carrega KML nativamente, para KMZ precisa ser unzipado ou servido como KML.
    // Usaremos KML puro se necessário, mas por ora vamos tentar carregar o arquivo KMZ com custom omnivore plugin se tivermos, senão focamos nos marcadores.
    try {
        const customLayer = L.geoJson(null, {
            style: function(feature) {
                return { color: '#ef4444', weight: 2, fillOpacity: 0.2 };
            }
        });
        omnivore.kml('/static/mapa_assistencia.kmz', null, customLayer).addTo(map);
    } catch(e) {
        console.warn("Nao foi possivel ler KMZ nativamente pelo browser. Será exibido apenas os marcadores.");
    }

    const tableBody = document.getElementById('tableBody');
    const loading = document.getElementById('loading');
    const searchInput = document.getElementById('searchInput');

    let globalData = [];
    let markers = [];

    // Função auxiliar de badges
    function getBadgeClass(str) {
        if (!str) return 'none';
        const s = str.toLowerCase();
        if (s.includes('alto') || s.includes('critico') || s.includes('crítico')) return 'alto';
        if (s.includes('médio') || s.includes('medio')) return 'medio';
        if (s.includes('baixo')) return 'baixo';
        return 'none';
    }

    // Carregar Dados da API
    fetch('/api/assistencia_data')
        .then(res => res.json())
        .then(res => {
            if (res.status === 'success') {
                globalData = res.data;
                renderTable(globalData);
                renderMarkers(globalData);
                
                if (markers.length > 0) {
                    const group = new L.featureGroup(markers);
                    map.fitBounds(group.getBounds());
                }
            } else {
                console.error("Erro na API:", res.message);
                tableBody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:red;">Erro ao carregar dados</td></tr>`;
            }
            loading.style.display = 'none';
        })
        .catch(err => {
            console.error(err);
            loading.style.display = 'none';
        });

    function renderTable(data) {
        tableBody.innerHTML = '';
        data.forEach((item, index) => {
            const tr = document.createElement('tr');
            
            // Tratamento de badges
            const bGeol = getBadgeClass(item.risco_geol_grau);
            const bHidro = getBadgeClass(item.risco_hidro_grau);

            const rGeolText = (item.risco_geol_grau && item.risco_geol_grau !== 'nan') ? item.risco_geol_grau : '-';
            const rHidroText = (item.risco_hidro_grau && item.risco_hidro_grau !== 'nan') ? item.risco_hidro_grau : '-';

            tr.innerHTML = `
                <td><strong>${item.localidade !== 'nan' ? item.localidade : 'Não Informado'}</strong><br><small style="color:#94a3b8">${item.codigo}</small></td>
                <td>${item.tipo !== 'nan' ? item.tipo : '-'}</td>
                <td><span class="badge ${bGeol}">${rGeolText}</span></td>
                <td><span class="badge ${bHidro}">${rHidroText}</span></td>
            `;

            // Ao clicar na linha da tabela, foca no mapa
            tr.addEventListener('click', () => {
                if (item.lat && item.lon && item.lat !== 'nan') {
                    map.setView([item.lat, item.lon], 18);
                    // Procura o marker correspondente e abre popup
                    if(item.markerRef) {
                        item.markerRef.openPopup();
                    }
                }
            });

            tableBody.appendChild(tr);
        });
    }

    function renderMarkers(data) {
        markers.forEach(m => map.removeLayer(m));
        markers = [];

        data.forEach(item => {
            if (item.lat && item.lon && !isNaN(item.lat) && !isNaN(item.lon)) {
                let color = '#3b82f6'; // blue default
                
                const g = getBadgeClass(item.risco_geol_grau);
                const h = getBadgeClass(item.risco_hidro_grau);
                
                if (g === 'alto' || h === 'alto') color = '#ef4444';
                else if (g === 'medio' || h === 'medio') color = '#f59e0b';
                
                const markerHtmlStyles = `
                  background-color: ${color};
                  width: 14px;
                  height: 14px;
                  display: block;
                  border-radius: 50%;
                  border: 2px solid white;
                  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                `;

                const customIcon = L.divIcon({
                  className: "custom-pin",
                  html: `<span style="${markerHtmlStyles}"></span>`
                });

                const m = L.marker([item.lat, item.lon], {icon: customIcon}).addTo(map);
                
                const popupContent = `
                    <div style="font-family:'Inter',sans-serif; min-width: 200px;">
                        <h4 style="margin:0 0 5px 0; color:#1e293b;">${item.localidade !== 'nan' ? item.localidade : 'Localidade Desconhecida'}</h4>
                        <p style="margin:0 0 10px 0; font-size:0.8rem; color:#64748b;">Código: ${item.codigo}</p>
                        
                        <div style="font-size:0.85rem;">
                            <strong>Uso:</strong> ${item.tipo !== 'nan' ? item.tipo : 'N/A'}<br>
                            <strong>Risco Geológico:</strong> ${item.risco_geol_grau !== 'nan' ? item.risco_geol_grau : '-'}<br>
                            <strong>Risco Hidrológico:</strong> ${item.risco_hidro_grau !== 'nan' ? item.risco_hidro_grau : '-'}
                        </div>
                    </div>
                `;
                m.bindPopup(popupContent);
                item.markerRef = m;
                markers.push(m);
            }
        });
    }

    // Filtro de busca na tabela
    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.toLowerCase();
        const filtered = globalData.filter(item => {
            const str = Object.values(item).join(' ').toLowerCase();
            return str.includes(val);
        });
        renderTable(filtered);
    });

});
