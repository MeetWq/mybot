function Drawer() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    this.ctx.lineJoin = 'round';
    this.ctx.lineCap = 'round';

    this.topText = new TopText(this.ctx);
    this.bottomText = new BottomText(this.ctx);

    this.useTransparent = false;
    this.lang = "";
}

Drawer.prototype.refresh = function() {
    if (this.lang == "ja") {
        this.topText.font = "100px notobk";
        this.bottomText.font = "100px notoserifbk";
    } else {
        this.topText.font = "100px 'Noto Sans SC'";
        this.bottomText.font = "100px 'Noto Serif SC'";
    }
    this.topText.init();
    this.bottomText.init();
    this.canvas.width = Math.max(this.topText.x + this.topText.w, this.bottomText.x + this.bottomText.w);
    this.canvas.height = 290;
    this.clear();
}

Drawer.prototype.clear = function() {
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    if (!this.useTransparent) {
        this.ctx.fillStyle = `white`;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    } else {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

Drawer.prototype.createImage = function() {
    this.topText.draw();
    this.bottomText.draw();

    const a = document.createElement("a");
    a.href = this.canvas.toDataURL("image/png");
    document.body.appendChild(a);
}
