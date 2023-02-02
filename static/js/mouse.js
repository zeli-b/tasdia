let mouseX, mouseY;

function mousemove(e) {
  if (canvas === undefined) return;

  mouseX = e.clientX - canvas.offsetLeft;
  mouseY = e.clientY - canvas.offsetTop;
}

document.addEventListener('mousemove', mousemove);
