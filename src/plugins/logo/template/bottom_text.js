function BottomText(ctx) {
    this.value = "";
    this.font = "";
    this.x = 250.0;
    this.y = 230.0;
    this.w = 0.0;
    this.ctx = ctx;
}

BottomText.prototype.init = function() {
    this.ctx.font = this.font;
    this.w = this.ctx.measureText(this.value).width - 40;
}

BottomText.prototype.draw = function() {
    this.ctx.font = this.font;
    this.ctx.setTransform(1, 0, -0.45, 1, 0, 0);

    // 黑色
    {
        this.ctx.strokeStyle = "#000";
        this.ctx.lineWidth = 22;
        this.ctx.strokeText(this.value, this.x + 5, this.y + 2);
    }

    // 银
    {
        const grad = this.ctx.createLinearGradient(0, this.y - 80, 0, this.y + 18);
        grad.addColorStop(0, 'rgb(0,15,36)');
        grad.addColorStop(0.25, 'rgb(250,250,250)');
        grad.addColorStop(0.5, 'rgb(150,150,150)');
        grad.addColorStop(0.75, 'rgb(55,58,59)');
        grad.addColorStop(0.85, 'rgb(25,20,31)');
        grad.addColorStop(0.91, 'rgb(240,240,240)');
        grad.addColorStop(0.95, 'rgb(166,175,194)');
        grad.addColorStop(1, 'rgb(50,50,50)');
        this.ctx.strokeStyle = grad;
        this.ctx.lineWidth = 19;
        this.ctx.strokeText(this.value, this.x + 5, this.y + 2);
    }

    // 黑色
    {
        this.ctx.strokeStyle = "#10193A";
        this.ctx.lineWidth = 17;
        this.ctx.strokeText(this.value, this.x, this.y);
    }

    // 白
    {
        this.ctx.strokeStyle = "#DDD";
        this.ctx.lineWidth = 8;
        this.ctx.strokeText(this.value, this.x, this.y);
    }

    // 绀
    {
        const grad = this.ctx.createLinearGradient(0, this.y - 80, 0, this.y);
        grad.addColorStop(0, 'rgb(16,25,58)');
        grad.addColorStop(0.03, 'rgb(255,255,255)');
        grad.addColorStop(0.08, 'rgb(16,25,58)');
        grad.addColorStop(0.2, 'rgb(16,25,58)');
        grad.addColorStop(1, 'rgb(16,25,58)');
        this.ctx.strokeStyle = grad;
        this.ctx.lineWidth = 7;
        this.ctx.strokeText(this.value, this.x, this.y);
    }

    // 银
    {
        const grad = this.ctx.createLinearGradient(0, this.y - 80, 0, this.y);
        grad.addColorStop(0, 'rgb(245,246,248)');
        grad.addColorStop(0.15, 'rgb(255,255,255)');
        grad.addColorStop(0.35, 'rgb(195,213,220)');
        grad.addColorStop(0.5, 'rgb(160,190,201)');
        grad.addColorStop(0.51, 'rgb(160,190,201)');
        grad.addColorStop(0.52, 'rgb(196,215,222)');
        grad.addColorStop(1.0, 'rgb(255,255,255)');
        this.ctx.fillStyle = grad;
        this.ctx.fillText(this.value, this.x, this.y - 3);
    }
}
