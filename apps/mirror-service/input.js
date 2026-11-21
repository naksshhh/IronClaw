/**
 * Build adb argv for touch, swipe, and key injection.
 * Callers must pass the array to spawn(), never to a shell.
 */

const KEYCODES = {
    back: 4,
    home: 3,
    recent: 187,
    power: 26,
    volume_up: 24,
    volume_down: 25,
};

function unitInterval(value) {
    const n = Number(value);
    if (!Number.isFinite(n) || n < 0 || n > 1) {
        return null;
    }
    return n;
}

function deviceCoord(normal, size) {
    const n = unitInterval(normal);
    const s = Number(size);
    if (n === null || !Number.isFinite(s) || s <= 0) {
        return null;
    }
    return String(Math.round(n * s));
}

function tapArgs(x, y, width, height) {
    const dx = deviceCoord(x, width);
    const dy = deviceCoord(y, height);
    if (dx === null || dy === null) {
        return null;
    }
    return ["shell", "input", "tap", dx, dy];
}

function swipeArgs(startX, startY, endX, endY, duration, width, height) {
    const sx = deviceCoord(startX, width);
    const sy = deviceCoord(startY, height);
    const ex = deviceCoord(endX, width);
    const ey = deviceCoord(endY, height);
    const d = Number(duration);
    if (sx === null || sy === null || ex === null || ey === null) {
        return null;
    }
    if (!Number.isInteger(d) || d < 1 || d > 10000) {
        return null;
    }
    return ["shell", "input", "swipe", sx, sy, ex, ey, String(d)];
}

function keyeventArgs(keycode) {
    if (typeof keycode === "string" && Object.prototype.hasOwnProperty.call(KEYCODES, keycode)) {
        return ["shell", "input", "keyevent", String(KEYCODES[keycode])];
    }
    if (typeof keycode === "number" && Number.isInteger(keycode) && keycode >= 0 && keycode <= 999) {
        return ["shell", "input", "keyevent", String(keycode)];
    }
    return null;
}

module.exports = {
    KEYCODES,
    tapArgs,
    swipeArgs,
    keyeventArgs,
};
