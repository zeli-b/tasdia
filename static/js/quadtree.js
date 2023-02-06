function posToPath(number, length) {
  if (length === undefined) {
    length = 1;
  }

  let path = [];
  while (number) {
    path.push(number & 1);
    number >>= 1;
  }

  while (path.length < length) {
    path.push(0);
  }
  return path;
}

function pathIntToPos(pathInt, unit) {
  return parseInt((pathInt.toString(2).split('').reverse().join('') + '0'.repeat(unit)).slice(0, unit), 2);
}

class QuadTree {
  constructor(value) {
    this.value = value;

    this.children = [];
    this.parent = null;
  }

  clone() {
    let result = new QuadTree(this.value);
    result.parent = this.parent;

    if (this.isDivided()) {
      let children = [];
      this.children.forEach(child => {
        let clone = child.clone();
        clone.parent = result;
        children.push(clone);
      });
      result.children = children;
    }

    return result;
  }

  setValue(value) {
    this.value = value;
    return this;
  }

  isIdenticalWith(other) {
    if (this.value !== other.value) {
      return false;
    }

    let divided = this.isDivided();
    if (divided !== other.isDivided()) {
      return false;
    }

    if (divided) {
      for (let i = 0; i < 4; i++) {
        if (!(this.children[i].isIdenticalWith(other.children[i]))) {
          return false;
        }
      }
    }

    return true;
  }

  /*
   * ``self``에 ``self``와 같은 ``value``를 가진 자식 사분트리를 가지게 한다.
   *
   * 반대 연산은 ``self.combine``
   */
  divide() {
    this.children = [];
    for (let i = 0; i < 4; i++) {
      let child = new QuadTree(this.value);
      this.children.push(child);
      child.parent = this;
    }
    return this;
  }

  /*
   * ``self``에 children이 할당되어있는 것을 없앤다.
   *
   * 반대 연산은 ``self.divide``
   */
  combine(with_) {
    this.children = [];
    if (with_ !== undefined) {
      this.value = with_;
    }
    return this;
  }

  /*
   * ``self``가 나누어져있는 트리인지 확인한다.
   */
  isDivided() {
    return this.children.length === 4;
  }

  /*
   * ``self``로부터 더 이상 자식을 가지지 않기 위해서는 몇 세대를 거듭해야하는지 나타낸다.
   * 만약 ``self``가 자식을 가지고 있지 않다면 0을 반환한다.
   */
  getDepth() {
    if (!this.isDivided()) {
      return 0;
    }

    let max = 0;
    this.children.forEach(child => {
      let depth = child.getDepth();
      if (depth > max) {
        max = depth;
      }
    });
    return max + 1;
  }

  /*
   * 트리 면 속 특정 좌표에 할당된 트리를 출력한다.
   */
  get(xPos, yPos, unit) {
    let xPath = posToPath(xPos, unit);
    let yPath = posToPath(yPos, unit);

    let now = this;
    while (xPath.length || yPath.length) {
      let x = xPath ? xPath.shift() : 0;
      let y = yPath ? yPath.shift() : 0;
      let index = y * 2 + x;

      if (!now.isDivided()) {
        now.divide();
      }

      now = now.children[index];
    }

    return now;
  }

  set(xPos, yPos, unit, value) {
    let tree = this.get(xPos, yPos, unit);
    tree.setValue(value);
    tree.parent.simplifyUpward();
    return tree;
  }

  pathIntSet(xPath, yPath, unit, value) {
    let xPos = pathIntToPos(xPath, unit);
    let yPos = pathIntToPos(yPath, unit);
    return this.set(xPos, yPos, unit, value);
  }

  /*
   *``self``부터 최상위 트리까지를 순회하며 child가 가지고 있는 값이 모두 같다면 combine한다.
   *
   * 이 메소드가 실행될 때에는 ``self``를 제외하고 그 어떤 부분에서도 자식이 모두 같은 값을 가지고 있지만 divide되어있는 트리가 없음을 상정한다.
   *
   * ``self``가 병합해야 하는 트리의 자식이라면 ``self.parent``에 이 함수를 적용해야 한다.
   */
  simplifyUpward() {
    if (!this.isDivided()) {
      return;
    }

    let value = this.children[0].value;
    let divided = this.children[0].isDivided();
    for (let i = 1; i < 4; i++) {
      if (this.children[i].value !== value) {
        return;
      }
      if (this.children[i].isDivided() !== divided) {
        return;
      }
    }

    this.combine(value);

    if (this.parent !== null) {
      this.parent.simplifyUpward();
    }
  }

  /*
   * ``self``에서 ``tree``까지 이어지는 가족 계보를 반환한다.
   *
   * 만약 ``self``의 자식중에 ``tree``가 없다면 None을 반환한다.
   */
  getFamilyPath(tree) {
    let index = this.children.indexOf(tree);

    if (index === -1) {
      for (let i = 0; i < this.children.length; i++) {
        let child = this.children[i];
        let position = child.getFamilyPath(tree);
        if (position) {
          let [y, x] = [Math.floor(i / 2), i % 2];
          return [[x, y]].concat(position);
        }
      }
    } else {
      let [y, x] = [Math.floor(index / 2), index % 2];
      return [[x, y]];
    }
  }

  /*
   * 트리를 JSON 형식으로 반환합니다.
   */
  saves() {
    let result = [self.value];
    if (!this.isDivided()) {
      return result;
    }

    this.children.forEach(child => {
      result.push(child.saves());
    });
    return result;
  }

  /*
   * JSON 형식의 트리를 ``QuadTree``로 변환하여 반환합니다.
   */
  static loads(data) {
    let result = new QuadTree(data[0]);
    if (data.length <= 1) {
      return result;
    }

    let children = [];
    for (let i = 1; i <= 4; i++) {
      children.push(QuadTree.loads(data[i]));
    }
    result.children = children;

    return result;
  }

  /*
   * 사분트리에 사분트리 차이를 적용한 결과를 출력한다.
   *
   * ``self``의 내용을 바꾸지 않고 복사본을 만들어 출력한다.
   */
  apply(delta) {
    let result = this.clone();
    if (delta.value !== null) {
      result.value = delta.value;
      result.children = [];
    }

    if (!delta.isDivided()) {
      return result;
    }

    if (!result.isDivided()) {
      result.divide();
    }

    let children = [];
    for (let i = 0; i < 4; i++) {
      children.push(result.children[i].apply(delta.children[i]));
    }
    result.children = children;
    result.simplifyUpward();
    return result;
  }

  /*
   * 사분트리에 사분트리 차이를 추적한 결과를 출력한다.
   */
  trace(delta, clone) {
    if (clone === undefined) {
      clone = false;
    }

    if (!clone) {
      delta = delta.clone();
    }

    if (delta.value !== null) {
      delta = this.clone();
      return delta;
    }

    if (delta.isDivided()) {
      let originallyCombined = this.isDivided();
      if (originallyCombined) {
        this.divide();
      }

      let children = [];
      for (let i = 0; i < 4; i++) {
        children.push(this.children[i].trace(delta.children[i], true));
      }
      delta.children = children;

      if (originallyCombined) {
        this.combine();
      }
    }

    return delta;
  }

  render(context, x, y, width, height, palette) {
    if (!this.isDivided()) {
      if (this.value === null)
        return;

      context.fillStyle = palette[this.value];
      context.fillRect(x, y, width, height);
      return;
    }

    width /= 2;
    height /= 2;
    for (let i = 0; i < 4; i++) {
      let [yi, xi] = [Math.floor(i / 2), i % 2];
      this.children[i].render(
        context,
        x + width * xi, y + height * yi,
        width, height,
        palette);
    }
  }
}