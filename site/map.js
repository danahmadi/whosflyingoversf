(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const names = JSON.parse($('map-brands').textContent);
  let flights = [], map, heat, lines;
  const dateFromURL = new URLSearchParams(location.search).get('date');
  const el = (tag, text) => {const node=document.createElement(tag);node.textContent=text;return node;};
  function resetDates() {
    const dates = flights.map(flight => flight.date).sort();
    $('from').value = dates[0] || ''; $('to').value = dates.at(-1) || '';
    $('tail').value = ''; $('tracks').checked = false;
  }
  function draw() {
    const invalid = $('from').value && $('to').value && $('from').value > $('to').value;
    const selected = invalid ? [] : flights.filter(flight => (!$('from').value || flight.date >= $('from').value) && (!$('to').value || flight.date <= $('to').value) && (!$('tail').value || flight.tail === $('tail').value));
    if (heat) map.removeLayer(heat);
    heat = L.heatLayer(selected.flatMap(flight => flight.track.map(point => [...point,0.5])),{radius:14,blur:18,maxZoom:14}).addTo(map);
    lines.clearLayers();
    if ($('tracks').checked) selected.forEach(flight => {
      const content = el('div','');
      content.append(el('strong',`${flight.date} · ${flight.tail}`));
      content.append(el('p',flight.candidates.length ? 'Brands reported that day: ' + flight.candidates.map(brand => names[brand] || brand).join(', ') + '. Aircraft match unconfirmed.' : 'No dated brand report in this archive.'));
      const report = el('a','Add evidence for this date');
      report.href = 'https://github.com/danahmadi/whosflyingoversf/issues/new?' + new URLSearchParams({template:'sighting.yml',date:flight.date});content.append(report);
      L.polyline(flight.track,{color:'#C2380B',weight:2,opacity:.7}).bindPopup(content).addTo(lines);
    });
    $('map-status').textContent = invalid ? 'Choose an end date on or after the start date.' : selected.length ? `${selected.length} candidate track${selected.length === 1 ? '' : 's'} across ${new Set(selected.map(flight => flight.date)).size} date${new Set(selected.map(flight => flight.date)).size === 1 ? '' : 's'}.` : 'No tracks match these filters. Try a wider date range.';
  }
  async function load() {
    $('retry-map').hidden=true; $('map-status').textContent='Loading flight tracks…';
    try {
      if (!window.L || !L.heatLayer) throw new Error('Map library unavailable');
      const response=await fetch('/data/flights.json'); if(!response.ok)throw new Error('Track download failed');
      flights=await response.json();
      if (!map) {
        map=L.map('map').setView([37.77,-122.43],12);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'}).addTo(map);
        lines=L.layerGroup().addTo(map);
      }
      $('tail').replaceChildren(new Option('All tracked aircraft',''));
      [...new Set(flights.map(flight=>flight.tail))].sort().forEach(tail=>$('tail').append(new Option(tail,tail)));
      resetDates();
      if (dateFromURL && /^\d{4}-\d{2}-\d{2}$/.test(dateFromURL)) { $('from').value=dateFromURL; $('to').value=dateFromURL; $('tracks').checked=true; }
      $('map-filters').hidden=false; draw();
    } catch {
      $('map-status').textContent='The map could not load. Check your connection, or browse the sightings archive while the map is unavailable.';
      $('retry-map').hidden=false;
    }
  }
  $('map-filters').addEventListener('submit',event=>event.preventDefault());
  $('map-filters').addEventListener('change',draw);
  $('map-filters').addEventListener('reset',event=>{event.preventDefault();resetDates();draw();});
  $('retry-map').addEventListener('click',()=>{if(!window.L||!L.heatLayer)location.reload();else load();});
  load();
})();
