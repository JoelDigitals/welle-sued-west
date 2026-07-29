/**
 * Fragt regelmäßig den hauseigenen Proxy-Endpunkt "/api/nowplaying/" ab
 * (der wiederum serverseitig die Studio-API abruft) und aktualisiert damit
 * alle Elemente mit den Data-Attributen unten.
 *
 * HINWEIS FÜR DIE ANPASSUNG:
 * Die genaue JSON-Struktur, die
 * https://welle-sued-west-studio.onrender.com/api/public/nowplaying
 * zurückgibt, war beim Bau dieser Seite nicht bekannt. Die Funktion
 * extractNowPlayingText() probiert deshalb mehrere gängige Feldnamen
 * (title/artist, song.title/song.artist, now_playing.song ...) der Reihe
 * nach durch. Öffne die URL einmal direkt im Browser oder mit
 *   curl https://welle-sued-west-studio.onrender.com/api/public/nowplaying
 * und passe die Feldnamen unten an das tatsächliche Format an, falls nötig.
 */

function extractNowPlayingText(data) {
  if (!data || typeof data !== 'object') return null;

  const song = data.song || data.now_playing || data.current || data;

  const title =
    song.title || song.track || song.song_title || data.title || null;
  const artist =
    song.artist || song.artist_name || data.artist || null;

  if (title && artist) return `${artist} – ${title}`;
  if (title) return title;
  if (typeof data.text === 'string') return data.text;
  if (typeof data.label === 'string') return data.label;

  return null;
}

function updateNowPlayingElements(text) {
  const nodes = document.querySelectorAll('[data-nowplaying]');
  nodes.forEach((node) => {
    node.textContent = text || 'Welle Süd-West live';
  });
}

async function refreshNowPlaying() {
  try {
    const response = await fetch('/api/nowplaying/', { cache: 'no-store' });
    if (!response.ok) throw new Error('nowplaying nicht erreichbar');
    const data = await response.json();
    const text = extractNowPlayingText(data);
    updateNowPlayingElements(text);
  } catch (err) {
    // Studio evtl. gerade im Schlafmodus (z. B. Render Free-Tier) - einfach
    // weiter mit dem zuletzt bekannten bzw. dem Fallback-Text.
    console.warn('Now-Playing-Update fehlgeschlagen:', err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  refreshNowPlaying();
  setInterval(refreshNowPlaying, 20000);
});
