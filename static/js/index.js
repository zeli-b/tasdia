function ready() {
  const mapSelect = document.querySelector('#map');

  fetch('/api/map')
    .then(r => r.json())
    .then(data => {
      Object.values(data).forEach(map => {
        let option = document.createElement("option");

        option.value = map.id;
        option.innerText = `${map.id}: ${map.description}`

        mapSelect.appendChild(option);
      });
    });
}