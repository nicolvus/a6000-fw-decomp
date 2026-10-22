const input = document.querySelector('#session');
const result = document.querySelector('#result');
const sessionsElement = document.querySelector('#sessions');

fetch('status.json')
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(data => {
    document.querySelector('#latest').textContent = data.latest;
    document.querySelector('#count').textContent = data.documented_count;
    document.querySelector('#physical').textContent = `${data.physical_tests.done}/${data.physical_tests.total}`;
    document.querySelector('#coverage').textContent = `${data.module_coverage.covered}/${data.module_coverage.total}`;
    document.querySelector('#index-note').textContent = `${data.documented_count} identificadores Sx con un documento localizado. El índice puede omitir sesiones con otro nombre de archivo.`;

    const byId = new Map(data.sessions.map(session => [session.id, session]));
    const check = () => {
      const query = input.value.trim().toUpperCase();
      const normalized = query.match(/^S?(\d{1,3})$/);
      result.replaceChildren();
      if (!normalized) {
        result.textContent = 'Escribe un número de sesión, por ejemplo S51.';
        return;
      }
      const id = `S${Number(normalized[1])}`;
      const session = byId.get(id);
      if (!session) {
        const exception = data.exceptions?.[id];
        if (exception) {
          const link = document.createElement('a');
          link.href = exception.source;
          link.textContent = 'Ver fuente →';
          result.append(`${id}: ${exception.label} `, link);
          return;
        }
        result.textContent = `${id}: no se localizó un informe principal en el índice. Esto no significa que la sesión no exista o esté pendiente.`;
        return;
      }
      const link = document.createElement('a');
      link.href = session.source;
      link.textContent = `${id}: ${session.title} →`;
      result.append('Documento localizado · ', link);
    };
    document.querySelector('#check').addEventListener('click', check);
    input.addEventListener('keydown', event => { if (event.key === 'Enter') check(); });

    const fragment = document.createDocumentFragment();
    for (const session of data.sessions) {
      const link = document.createElement('a');
      link.href = session.source;
      const number = document.createElement('strong');
      number.textContent = session.id;
      const label = document.createElement('span');
      label.textContent = session.title;
      link.append(number, label);
      fragment.append(link);
    }
    sessionsElement.append(fragment);
  })
  .catch(() => {
    document.querySelector('#index-note').textContent = 'El índice de sesiones no está disponible en este momento.';
    result.textContent = 'No se pudo cargar el verificador. Consulta el repositorio.';
  });
