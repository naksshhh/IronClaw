const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");
const { tapArgs, swipeArgs, keyeventArgs } = require("./input");

test("tap builds an argv list and stays inside the device", () => {
    assert.deepEqual(tapArgs(0.5, 0.25, 1080, 1920), ["shell", "input", "tap", "540", "480"]);
    assert.equal(tapArgs("../../x", 0.2, 1080, 1920), null);
    assert.equal(tapArgs(2, 0.2, 1080, 1920), null);
});

test("swipe rejects a duration that is not a plain integer", () => {
    assert.deepEqual(
        swipeArgs(0, 0, 1, 1, 300, 100, 200),
        ["shell", "input", "swipe", "0", "0", "100", "200", "300"],
    );
    assert.equal(swipeArgs(0, 0, 1, 1, "300; id", 100, 200), null);
    assert.equal(swipeArgs(0, 0, 1, 1, 0, 100, 200), null);
});

test("key names are mapped and shell strings are rejected", () => {
    assert.deepEqual(keyeventArgs("home"), ["shell", "input", "keyevent", "3"]);
    assert.deepEqual(keyeventArgs(4), ["shell", "input", "keyevent", "4"]);
    assert.equal(keyeventArgs("4; id"), null);
    assert.equal(keyeventArgs("back; rm -rf /"), null);
    assert.equal(keyeventArgs(-1), null);
});

test("mirror servers pass adb input as argv", () => {
    for (const filename of ["server.js", "server-h264-fmp4.js"]) {
        const source = fs.readFileSync(path.join(__dirname, filename), "utf8");
        assert.equal(source.includes("input keyevent ${"), false, filename);
        assert.equal(source.includes("input tap ${"), false, filename);
        assert.equal(source.includes("input swipe ${"), false, filename);
        assert.equal(source.includes("keyeventArgs"), true, filename);
    }
});
