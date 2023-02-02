class AreaLayer {
  constructor(id, description, metadata) {
    this.id = id;
    this.description = description;
    this.metadata = metadata;
    this.tree = null;
    this.deltas = [];

    this.surface = null;
    this.visible = true;
  }

  static loads(data) {
    let id = data.id
      , description = data.description
      , metadata = data.metadata;
    return new AreaLayer(id, description, metadata);
  }

  render(x, y, width, height) {
    if (this.tree === null) return;
    if (!this.visible) return;

    if (this.surface === null) {
      this.surface = document.createElement('canvas');
      this.surface.width = 2048;
      this.surface.height = 2048;
      let surfaceContext = this.surface.getContext('2d');

      let palette = {};
      Object.values(this.metadata).forEach(metadatum => {
        palette[metadatum.id] = metadatum.color;
      });
      this.tree.render(surfaceContext, 0, 0, this.surface.width, this.surface.height, palette);
    }

    context.imageSmoothingEnabled = false;
    context.drawImage(this.surface, x, y, width, height);
  }

  toggleVisible() {
    this.visible = !this.visible;
    console.log(this);
  }
}

function mod(x, y) {
  x -= Math.floor(x / y) * y;
  return x;
}

class Camera {
  constructor() {
    this.x = 1920;
    this.y = 0;
    this.zoom = 1;
  }

  getScreenX(x) {
    return canvas.width / 2 + (x - this.x) * this.zoom;
  }

  getScreenY(y) {
    return canvas.height / 2 + (y - this.y) * this.zoom;
  }

  getScreenLength(length) {
    return length * this.zoom;
  }

  getCameraX(x) {
    return (x - canvas.width / 2) / this.zoom + this.x;
  }

  getCameraY(y) {
    return (y - canvas.height / 2) / this.zoom + this.y;
  }

  scroll(event) {
    if (event.altKey) {
      this.zoom *= Math.exp(-event.deltaY / 500);
      this.zoom = Math.min(Math.max(this.zoom, 0.1), 1000);
      return;
    }

    this.x += event.deltaX / this.zoom / 2;
    this.y += event.deltaY / this.zoom / 2;

    this.x = mod(this.x, 3840)
    this.y = Math.min(Math.max(this.y, -1080), 1080)
  }
}

let camera = new Camera();

let canvas, context;
let areaLayersList;
let infoLatitude
  , infoLongitude;

let areas = [];

function ready() {
  canvas = document.querySelector('#canvas');
  context = canvas.getContext('2d');
  areaLayersList = document.querySelector('.area-layers-list');

  resize();

  infoLatitude = document.querySelector('#info-latitude');
  infoLongitude = document.querySelector('#info-longitude');

  fetch(`/api/map/${MAP_ID}/area`)
    .then(r => r.json())
    .then(data => {
      let li;
      let check;
      let radio;

      let datum;
      for (let i = 0; i < data.length; i++) {
        datum = data[i];
        let areaLayer = AreaLayer.loads(datum);

        li = document.createElement("li");
        li.innerHTML = datum.description + '<br>';

        // 표시 여부를 나타내는 체크박스
        check = document.createElement('input');
        check.type = 'checkbox';
        check.checked = true;
        check.onchange = () => areaLayer.toggleVisible();
        li.appendChild(check);

        // 작업중 여부를 나타내는 라디오버튼
        radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'arealayer';
        radio.checked = i === 0;
        li.appendChild(radio);

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

function lerp(t, a, b, c, d) {
  return (b - t) / (b - a) * (d - c) + c;
}

/*
 * 마우스의 위치에 따라 위도·경도 정보를 표시한다.
 */
function tickGPSInfo() {
  let x = mod(camera.getCameraX(mouseX), 3840);
  let y = camera.getCameraY(mouseY);

  let side, degree, minutes, seconds;
  if (Math.abs(y) > 1080) {
    infoLatitude.innerText = '-';
    infoLongitude.innerText = '-';
    return;
  }

  side = y <= 0 ? '북위' : '남위';
  degree = lerp(Math.abs(y), 0, 1080, 90, 0);
  [degree, minutes] = [Math.floor(degree), degree % 1 * 60];
  [minutes, seconds] = [Math.floor(minutes), Math.floor(minutes % 1 * 600) / 10];
  infoLatitude.innerText = `${side} ${degree}° ${minutes}′ ${seconds}″`;

  x = mod(x + 1920, 3840) - 1920;
  side = x >= 0 ? '동경' : '서경';
  degree = lerp(Math.abs(x), 0, 1920, 180, 0);
  [degree, minutes] = [Math.floor(degree), degree % 1 * 60];
  [minutes, seconds] = [Math.floor(minutes), Math.floor(minutes % 1 * 600) / 10];
  infoLongitude.innerText = `${side} ${degree}° ${minutes}′ ${seconds}″`;
}

/*
 * 화면 계산
 */
function tick() {
  if (canvas === undefined) return;

  tickGPSInfo();
}

function renderBackground() {
  context.fillStyle = '#2c2c2c';
  context.fillRect(0, 0, canvas.width, canvas.height);
}

function renderAreas() {
  let x = Math.floor(camera.getCameraX(0) / 3840);
  let endX = camera.getCameraX(canvas.width) / 3840;
  for (let i = x; i <= endX; i++) {
    areas.forEach(area => {
      area.render(
        camera.getScreenX(3840 * i), camera.getScreenY(-1080),
        camera.getScreenLength(3840), camera.getScreenLength(2160)
      );
    });
  }
}

/*
 * 화면 출력
 */
function render() {
  if (context === undefined) return;

  renderBackground();
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

  renderBackground();
}

window.addEventListener('resize', resize);

window.addEventListener('wheel', e => camera.scroll(e));
