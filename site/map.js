(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const names = JSON.parse($('map-brands').textContent);
  let flights = [], map, heat, lines;
  const defaultCenter = [37.77, -122.43], defaultZoom = 11;
  const trackColors = ['#356578', '#59796f', '#68778d', '#95775d'];
  let selectedBrand = new URLSearchParams(location.search).get('brand') || '';
  function brandQuery() {
    const url = new URL(location.href);
    if (selectedBrand) url.searchParams.set('brand', selectedBrand); else url.searchParams.delete('brand');
    history.replaceState(null, '', url);
  }
  const embedded = !!$('map-date-label');
  const dateFromURL = new URLSearchParams(location.search).get('date');
  let selectedDay = /^\d{4}-\d{2}-\d{2}$/.test(dateFromURL || '') ? dateFromURL : '';
  function updateDayLabel() {
    if (!embedded) return;
    $('map-date-label').textContent = selectedDay ? new Date(selectedDay + 'T12:00:00').toLocaleDateString('en-US', {month:'long',day:'numeric',year:'numeric'}) : 'All recorded dates';
    $('reset-map-day').hidden = !selectedDay;
    const params = new URLSearchParams();
    if (selectedDay) params.set('date', selectedDay);
    if (selectedBrand) params.set('brand', selectedBrand);
    $('full-map-link').href = '/map' + (params.size ? '?' + params : '');
  }
  const el = (tag, text) => {const node=document.createElement(tag);node.textContent=text;return node;};
  function resetDates() {
    const dates = flights.map(flight => flight.date).sort();
    $('from').value = dates[0] || ''; $('to').value = dates.at(-1) || '';
    $('tail').value = ''; $('tracks').checked = true;
  }
  function draw() {
    const invalid = !embedded && $('from').value && $('to').value && $('from').value > $('to').value;
    const matchingDates = embedded ? flights.filter(flight => !selectedDay || flight.date === selectedDay) : invalid ? [] : flights.filter(flight => (!$('from').value || flight.date >= $('from').value) && (!$('to').value || flight.date <= $('to').value) && (!$('tail').value || flight.tail === $('tail').value));
    const selected = matchingDates.filter(flight => !selectedBrand || flight.candidates.includes(selectedBrand));
    $('brand-context').hidden = !selectedBrand;
    $('brand-context').textContent = selectedBrand ? `Tracks from days ${names[selectedBrand]} was sighted. Aircraft match unconfirmed.` : '';
    if (heat) map.removeLayer(heat);
    // Keep density as a quiet backdrop; the routes carry the detail.
    heat = L.heatLayer((embedded && selectedDay ? [] : selected).flatMap(flight => flight.track.map(point => [...point, 0.15])), {
      pane: 'heat', radius: 5, blur: 8, maxZoom: 13, max: 12, minOpacity: 0.025,
      gradient: {0.25: '#a9c4c8', 0.55: '#79a5aa', 0.8: '#c1ad86', 1: '#b78865'}
    }).addTo(map);
    lines.clearLayers();
    const focused = (embedded && !!selectedDay) || selected.length <= 8;
    // Cap the opacity of the whole overview so overlapping routes stay translucent.
    map.getPane('tracks').style.opacity = focused ? 1 : .45;
    if (embedded || $('tracks').checked) selected.forEach((flight, index) => {
      const content = el('div','');
      content.append(el('strong',`${flight.date} · ${flight.tail}`));
      content.append(el('p',flight.candidates.length ? 'Brands reported that day: ' + flight.candidates.map(brand => names[brand] || brand).join(', ') + '. Aircraft match unconfirmed.' : 'No dated brand report in this archive.'));
      const report = el('a','Add evidence for this date');
      report.href = 'https://github.com/danahmadi/whosflyingoversf/issues/new?' + new URLSearchParams({template:'sighting.yml',date:flight.date});content.append(report);
      L.polyline(flight.track,{pane:'tracks',color:trackColors[index % trackColors.length],weight:focused ? 1.8 : 1,opacity:focused ? .75 : .22,smoothFactor:1.2}).bindPopup(content).addTo(lines);
    });
    $('map-status').textContent = invalid ? 'Choose an end date on or after the start date.' : selected.length ? `${selected.length} candidate track${selected.length === 1 ? '' : 's'} across ${new Set(selected.map(flight => flight.date)).size} date${new Set(selected.map(flight => flight.date)).size === 1 ? '' : 's'}.` : embedded && selectedDay ? selectedBrand ? 'No tracks for this brand on the selected date. Try all dates or another brand.' : 'No recorded tracks for this date. A sighting can still be valid without a track.' : 'No tracks match these filters. Try a wider date range.';
    if (embedded) {
      updateDayLabel();
      map.invalidateSize();
      const points = selected.flatMap(flight => flight.track);
      if (selectedDay && points.length) map.fitBounds(points, {padding:[24,24],maxZoom:13});
      else map.setView(defaultCenter,defaultZoom);
    }
  }
  async function load() {
    $('retry-map').hidden=true; $('map-status').textContent='Loading flight tracks…';
    try {
      if (!window.L || !L.heatLayer) throw new Error('Map library unavailable');
      const response=await fetch('/data/flights.json'); if(!response.ok)throw new Error('Track download failed');
      flights=await response.json();
      if (!map) {
        map=L.map('map', {preferCanvas:true}).setView(defaultCenter,defaultZoom);
        map.createPane('heat'); map.getPane('heat').style.zIndex = 410;
        map.getPane('heat').style.opacity = .32; map.getPane('heat').style.pointerEvents = 'none';
        map.createPane('tracks'); map.getPane('tracks').style.zIndex = 420;
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'}).addTo(map);
        lines=L.layerGroup().addTo(map);
      }
      const brands = [...new Set(flights.flatMap(flight => flight.candidates))].sort((a,b)=>(names[a] || a).localeCompare(names[b] || b));
      $('map-brand').replaceChildren(new Option('All brands',''));
      brands.forEach(brand => $('map-brand').append(new Option(names[brand] || brand,brand)));
      if (!brands.includes(selectedBrand)) selectedBrand = '';
      $('map-brand').value = selectedBrand; $('map-brand').disabled = false;
      if (!embedded) {
      $('tail').replaceChildren(new Option('All tracked aircraft',''));
      [...new Set(flights.map(flight=>flight.tail))].sort().forEach(tail=>$('tail').append(new Option(tail,tail)));
      resetDates();
      if (dateFromURL && /^\d{4}-\d{2}-\d{2}$/.test(dateFromURL)) { $('from').value=dateFromURL; $('to').value=dateFromURL; $('tracks').checked=true; }
      $('map-filters').hidden=false;
      }
      draw();
    } catch {
      $('map-status').textContent='The map could not load. Check your connection, or browse the sightings archive while the map is unavailable.';
      $('retry-map').hidden=false;
    }
  }
  if (!embedded) {
  $('map-filters').addEventListener('submit',event=>event.preventDefault());
  $('map-filters').addEventListener('change',event=>{if(event.target.id!=='map-brand')draw();});
  $('map-filters').addEventListener('reset',event=>{event.preventDefault();resetDates();selectedBrand='';$('map-brand').value='';const url=new URL(location.href);url.searchParams.delete('date');history.replaceState(null,'',url);brandQuery();draw();});
  } else {
    document.addEventListener('sighting-date-selected', event => {
      selectedDay = event.detail.date || ''; updateDayLabel(); if (map) draw();
    });
    $('reset-map-day').addEventListener('click', () => document.dispatchEvent(new CustomEvent('sighting-date-selected', {detail:{date:''}})));
    updateDayLabel();
  }
  $('map-brand').addEventListener('change', () => {selectedBrand=$('map-brand').value;brandQuery();if(map)draw();});
  $('retry-map').addEventListener('click',()=>{if(!window.L||!L.heatLayer)location.reload();else load();});
  load();
})();
