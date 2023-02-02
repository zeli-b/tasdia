class AreaLayer {
  constructor(id, description, metadata) {
    this.id = id;
    this.description = description;
    this.metadata = metadata;
    this.tree = null;
    this.deltas = [];
  }

  static loads(data) {
    let id = data.id
      , description = data.description
      , metadata = data.metadata;
    return new AreaLayer(id, description, metadata);
  }

  render(x, y, width, height) {
    let palette = {};
    Object.values(this.metadata).forEach(metadatum => {
      palette[metadatum.id] = metadatum.color;
    });
    this.tree.render(context, x, y, width, height, palette);
  }
}

let canvas;
let context;
let areaLayersList;

let areas = [];

function ready() {
  canvas = document.querySelector('#canvas');
  context = canvas.getContext('2d');
  areaLayersList = document.querySelector('.area-layers-list');

  resize();

  fetch(`/api/map/${MAP_ID}/area`)
    .then(r => r.json())
    .then(data => {
      let li;
      let check;
      let radio;

      let datum;
      for (let i = 0; i < data.length; i++) {
        datum = data[i];

        li = document.createElement("li");
        li.innerHTML = datum.description + '<br>';

        // 표시 여부를 나타내는 체크박스
        check = document.createElement('input');
        check.type = 'checkbox';
        check.checked = true;
        li.appendChild(check);

        // 작업중 여부를 나타내는 라디오버튼
        radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'arealayer';
        radio.checked = i === 0;
        li.appendChild(radio);

        let areaLayer = AreaLayer.loads(datum);
        fetch(`/api/map/${MAP_ID}/area/${datum.id}/tree`)
          .then(r => r.json())
          .then(areaData => {
            areaLayer.tree = QuadTree.loads(areaData);
          });
        areas.push(areaLayer);

        areaLayersList.appendChild(li);
      }
    });
}

/*
 * 화면 계산
 */
function tick() {
}

function renderAreas() {
  areas.forEach(area => {
    area.render(0, 0, 384, 216);
  })
}

/*
 * 화면 출력
 */
function render() {
  renderAreas();
}

let fps = 60;
setInterval(() => {
  tick();
  render();
}, 1000 / fps);

/*
 * 화면 크기 변경 시 canvas 사이즈를 조정한다.
 */
function resize() {
  const toolsFrame = document.querySelector('.tools-frame');
  const optionsFrame = document.querySelector('.options-frame');

  canvas.width = window.innerWidth - toolsFrame.clientWidth - optionsFrame.clientWidth;
  canvas.height = window.innerHeight;

  context.fillStyle = '#2c2c2c';
  context.fillRect(0, 0, canvas.width, canvas.height);
}

window.addEventListener('resize', resize);
