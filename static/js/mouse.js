let mouseX, mouseY;

function mousemove(e) {
  if (canvas === undefined) return;

  mouseX = e.clientX - canvas.offsetLeft;
  mouseY = e.clientY - canvas.offsetTop;
}

document.addEventListener('mousemove', mousemove);

let mouseLeft = false;

function mousedown(e) {
  if (mouseX > canvas.width || mouseY > canvas.height) return;
  if (mouseX < 0 || mouseY < 0) return;

  if (e.button === 0) mouseLeft = true;
}

function mouseup(e) {
  if (e.button === 0) mouseLeft = false;
}

document.addEventListener('mousedown', mousedown);
document.addEventListener('mouseup', mouseup);
