const input = document.querySelector('#session');
const result = document.querySelector('#result');
const sessionsElement = document.querySelector('#sessions');
let check = null;

document.querySelector('#check').addEventListener('click', () => check?.());
input.addEventListener('keydown', event => { if (event.key === 'Enter') check?.(); });

fetch(new URL('../status.json', document.currentScript.src))
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(data => {
    document.querySelector('#latest').textContent = data.latest;
    document.querySelector('#count').textContent = data.documented_count;
    document.querySelector('#physical').textContent = `${data.physical_tests.done}/${data.physical_tests.total}`;
    document.querySelector('#coverage').textContent = `${data.module_coverage.covered}/${data.module_coverage.total}`;
    document.querySelector('#index-note').textContent = `${data.documented_count} Sx identifiers with a located document. The index may miss sessions filed under another name.`;

    const byId = new Map(data.sessions.map(session => [session.id, session]));
    check = () => {
      const query = input.value.trim().toUpperCase();
      const normalized = query.match(/^S?(\d{1,3})$/);
      result.replaceChildren();
      if (!normalized) {
        result.textContent = 'Type a session number, for example S51.';
        return;
      }
      const id = `S${Number(normalized[1])}`;
      const session = byId.get(id);
      if (!session) {
        const exception = data.exceptions?.[id];
        if (exception) {
          const link = document.createElement('a');
          link.href = exception.source;
          link.textContent = 'See source →';
          result.append(`${id}: ${exception.label} `, link);
          return;
        }
        result.textContent = `${id}: no main report was found in the index. That does not mean the session does not exist or is pending.`;
        return;
      }
      const link = document.createElement('a');
      link.href = session.source;
      link.textContent = `${id}: ${session.title} →`;
      result.append('Document found · ', link);
    };

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
    document.querySelector('#index-note').textContent = 'The session index is not available right now.';
    result.textContent = 'The lookup could not load. Check the repository.';
  });
