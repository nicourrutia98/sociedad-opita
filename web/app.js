/* Sociedad Opita — Cliente JS para el demo */

const API_BASE = 'https://api.sociedad.opitacode.com';
// const API_BASE = 'http://localhost:8000';  // dev local

// Cache de personas para no recargar cada vez
const personasByCity = {};

// DOM
const form = document.getElementById('sim-form');
const citySelect = document.getElementById('city');
const personaSelect = document.getElementById('persona');
const submitBtn = document.getElementById('submit');
const resultDiv = document.getElementById('result');
const resultText = document.getElementById('result-text');
const resultCost = document.getElementById('result-cost');
const resultLatency = document.getElementById('result-latency');
const resultTokens = document.getElementById('result-tokens');
const errorDiv = document.getElementById('error');

// Cargar ciudades al iniciar
async function loadCities() {
    try {
        const r = await fetch(`${API_BASE}/v1/cities`);
        const data = await r.json();
        citySelect.innerHTML = data.cities.map(c =>
            `<option value="${c.city_id}">${c.display_name} (${c.available_personas} personas)</option>`
        ).join('');
        if (data.cities.length > 0) {
            await loadPersonas(data.cities[0].city_id);
        }
    } catch (e) {
        showError(`No se pudo conectar al API: ${e.message}`);
    }
}

// Cargar personas de una ciudad
async function loadPersonas(cityId) {
    if (personasByCity[cityId]) {
        populatePersonas(personasByCity[cityId]);
        return;
    }
    try {
        const r = await fetch(`${API_BASE}/v1/cities/${cityId}/personas`);
        const data = await r.json();
        personasByCity[cityId] = data.personas;
        populatePersonas(data.personas);
    } catch (e) {
        showError(`Error cargando personas: ${e.message}`);
    }
}

function populatePersonas(personas) {
    personaSelect.innerHTML = '<option value="">-- Selecciona --</option>' +
        personas.map(p =>
            `<option value="${p.persona_id}">${p.display_name} (${p.role}, ${p.age})</option>`
        ).join('');
}

// Submit handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();
    resultDiv.classList.add('hidden');

    const payload = {
        city_id: citySelect.value,
        persona_id: personaSelect.value,
        scene: {
            time: document.getElementById('time').value,
            place: document.getElementById('place').value,
        },
        model: 'deepseek-chat',
        temperature: 1.3,
    };

    if (!payload.persona_id) {
        showError('Selecciona una persona');
        return;
    }

    const apiKey = document.getElementById('apiKey').value.trim();
    const headers = { 'Content-Type': 'application/json' };
    if (apiKey) headers['X-API-Key'] = apiKey;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Simulando';

    try {
        const r = await fetch(`${API_BASE}/v1/simulate`, {
            method: 'POST',
            headers,
            body: JSON.stringify(payload),
        });
        const data = await r.json();

        if (!r.ok) {
            showError(data.error || `HTTP ${r.status}`);
            return;
        }

        resultText.textContent = data.text;
        resultCost.textContent = `$${data.metadata.cost_usd.toFixed(5)}`;
        resultLatency.textContent = `${data.metadata.latency_ms}ms`;
        resultTokens.textContent = `${data.metadata.tokens_in}/${data.metadata.tokens_out} tokens`;
        resultDiv.classList.remove('hidden');
    } catch (e) {
        showError(`Error de red: ${e.message}`);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Simular';
    }
});

citySelect.addEventListener('change', () => loadPersonas(citySelect.value));

function showError(msg) {
    errorDiv.textContent = msg;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    errorDiv.classList.add('hidden');
}

// Init
loadCities();
