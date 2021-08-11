function Drawer(canvas) {
    this.canvas = canvas;

    this.ctx = canvas.getContext('2d');
    this.ctx.lineJoin = 'round';
    this.ctx.lineCap = 'round';
    this.ctx.fillStyle = 'white';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    this.topText = new TopText(this.ctx);
    this.bottomText = new BottomText(this.ctx);

    this.useTransparent = false;
    this.lang = "";
}

Drawer.prototype.refresh = function() {
    this.clear();

    if (this.lang == "ja") {
        this.topText.font = "100px notobk";
        this.bottomText.font = "100px notoserifbk";
    } else {
        this.topText.font = "100px 'Noto Sans SC'";
        this.bottomText.font = "100px 'Noto Serif SC'";
    }

    this.topText.draw();
    this.bottomText.draw();
}

Drawer.prototype.clear = function() {
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    if (!this.useTransparent) {
        this.ctx.fillStyle = `white`;
        this.ctx.fillRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);
    } else {
        this.ctx.clearRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);
    }
}

Drawer.prototype.saveImage = function() {
    const width = Math.max(this.topText.x + this.topText.w, this.bottomText.x + this.bottomText.w);
    const height = this.ctx.canvas.height;

    const data = this.ctx.getImageData(0, 0, width, height);
    const canvas = document.createElement('canvas');
    canvas.width = data.width;
    canvas.height = data.height;

    const ctx = canvas.getContext('2d');
    ctx.putImageData(data, 0, 0);

    const a = document.createElement("a");
    a.href = canvas.toDataURL("image/png");
    document.body.appendChild(a);
}
