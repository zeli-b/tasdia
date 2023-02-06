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
      this.surface.width = 4096;
      this.surface.height = 4096;
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

function mod(a, b) {
  a -= Math.floor(a / b) * b;
  return a;
}

const WORLD_WIDTH = 360;
const WORLD_HEIGHT = 180;

class Camera {
  constructor() {
    this.x = WORLD_WIDTH / 2;
    this.y = 0;
    this.zoom = canvas.width / WORLD_WIDTH;
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

    this.x = mod(this.x, WORLD_WIDTH)
    this.y = Math.min(Math.max(this.y, -WORLD_HEIGHT / 2), WORLD_HEIGHT / 2)
  }
}

const WM_MOVE = 'work-mode-move';
const WM_SELECT = 'work-mode-select';

let workMode = WM_MOVE;

function setWorkMode(workModeToBe) {
  let optionDiv;

  document.getElementById(workMode).className = '';
  if (workMode === WM_SELECT) {
    optionDiv = document.getElementById('work-mode-select--options');

    if (optionDiv !== null)
      optionDiv.style.display = 'none';
  }

  workMode = workModeToBe;

  document.getElementById(workMode).className = 'work-mode-selected';
  if (workMode === WM_SELECT) {
    optionDiv = document.getElementById(workMode + '--options')
    if (optionDiv !== null)
      optionDiv.style.display = 'block';
  }
}

let camera;

let canvas, context;
let areaLayersList
  , workModeList;
let infoLatitude
  , infoLongitude;
let selectModeUnitInput
  , selectModeUnit = 8
  , selectModeValueList
  , selectedAreaValue;

let areas = [];
let selectedAreaIndex = 0;

function selectAreaLayer(layerIndex) {
  selectedAreaIndex = layerIndex;

  selectModeValueList.innerHTML = '';

  let area = areas[selectedAreaIndex];
  Object.values(area.metadata).forEach(metadata => {
    let li = document.createElement('li');

    let radio = document.createElement('input');
    radio.type = 'radio';
    radio.name = 'select-area-value'
    radio.onchange = () => selectedAreaValue = metadata.id;
    radio.id = `select-area-value--${metadata.id}`;
    li.appendChild(radio);

    let label = document.createElement('label');
    label.innerText = metadata.description;
    label.setAttribute('for', radio.id);
    li.appendChild(label);

    selectModeValueList.appendChild(li);
  });
}

function ready() {
  canvas = document.querySelector('#canvas');
  context = canvas.getContext('2d');
  areaLayersList = document.querySelector('.area-layers-list');
  workModeList = document.querySelector('.work-mode-list');
  selectModeUnitInput = document.querySelector('#select-unit');
  selectModeValueList = document.querySelector('#select-area-value');

  resize();
  camera = new Camera();

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
        radio.onchange = () => selectAreaLayer(i);
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
  let x = camera.getCameraX(mouseX);
  let y = camera.getCameraY(mouseY);
  if (mouseX < 0 || mouseX > canvas.width || Math.abs(y) > WORLD_HEIGHT / 2) {
    infoLatitude.innerText = '-';
    infoLongitude.innerText = '-';
    return;
  }

  let side, degree, minutes, seconds;
  side = y <= 0 ? '북위' : '남위';
  degree = lerp(Math.abs(y), 0, WORLD_HEIGHT / 2, 90, 0);
  [degree, minutes] = [Math.floor(degree), degree % 1 * 60];
  [minutes, seconds] = [Math.floor(minutes), Math.floor(minutes % 1 * 600) / 10];
  infoLatitude.innerText = `${side} ${degree}° ${minutes}′ ${seconds}″`;

  x = mod(x + WORLD_WIDTH / 2, WORLD_WIDTH) - WORLD_WIDTH / 2;
  side = x >= 0 ? '동경' : '서경';
  degree = lerp(Math.abs(x), 0, WORLD_WIDTH / 2, 180, 0);
  [degree, minutes] = [Math.floor(degree), degree % 1 * 60];
  [minutes, seconds] = [Math.floor(minutes), Math.floor(minutes % 1 * 600) / 10];
  infoLongitude.innerText = `${side} ${degree}° ${minutes}′ ${seconds}″`;
}

function setSelectModeUnit() {
  selectModeUnit = selectModeUnitInput.value;
}

let selectAreaVisible, selectAreaWidth, selectAreaHeight, selectAreaX, selectAreaY;

function tickSelectMode() {
  selectAreaVisible = true;

  let widthUnit = WORLD_WIDTH / Math.pow(2, selectModeUnit);
  let heightUnit = WORLD_HEIGHT / Math.pow(2, selectModeUnit);

  selectAreaWidth = camera.getScreenLength(widthUnit);
  selectAreaHeight = camera.getScreenLength(heightUnit);

  let x = Math.floor(camera.getCameraX(mouseX) / widthUnit);
  let y = Math.floor(camera.getCameraY(mouseY) / heightUnit);

  selectAreaX = camera.getScreenX(x * widthUnit);
  selectAreaY = camera.getScreenY(y * heightUnit);

  y += Math.pow(2, selectModeUnit - 1);
  x %= Math.pow(2, selectModeUnit);
  y %= Math.pow(2, selectModeUnit);

  // x, y, selectedAreaValue
}

/*
 * 화면 계산
 */
function tick() {
  if (canvas === undefined) return;

  tickGPSInfo();

  if (workMode == WM_SELECT) {
    tickSelectMode();
  }
}

function renderBackground() {
  context.fillStyle = '#2c2c2c';
  context.fillRect(0, 0, canvas.width, canvas.height);
}

function renderAreas() {
  let x = Math.floor(camera.getCameraX(0) / WORLD_WIDTH);
  let endX = camera.getCameraX(canvas.width) / WORLD_WIDTH;
  for (let i = x; i <= endX; i++) {
    areas.forEach(area => {
      area.render(
        camera.getScreenX(WORLD_WIDTH * i), camera.getScreenY(-WORLD_HEIGHT / 2),
        camera.getScreenLength(WORLD_WIDTH), camera.getScreenLength(WORLD_HEIGHT)
      );
    });
  }
}

function renderSelectArea() {
  context.strokeStyle = 'black';
  context.beginPath();
  context.rect(selectAreaX, selectAreaY, selectAreaWidth, selectAreaHeight);
  context.stroke();
}

/*
 * 화면 출력
 */
function render() {
  if (context === undefined) return;

  renderBackground();
  renderAreas();
  renderSelectArea();
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
