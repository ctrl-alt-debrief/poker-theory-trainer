// history.test.js — tests for history.js
//
// These run in Node (not a browser), so we fake localStorage with a plain object.
// The real localStorage API has setItem/getItem/removeItem — we just implement those.

var store = {};
global.localStorage = {
  getItem:    function(k) { return store[k] !== undefined ? store[k] : null; },
  setItem:    function(k, v) { store[k] = v; },
  removeItem: function(k) { delete store[k]; }
};

// Pull in the functions we want to test.
// Because history.js doesn't use export, we load it with require() here.
// When the real HTML page loads history.js via a <script> tag, require isn't needed.
var { recordAnswer, loadHistory, weakSpots, clearHistory } = require("./history.js");

// Reset stored data before each test so tests don't bleed into each other
beforeEach(function() {
  clearHistory();
});

// --- recordAnswer ---

test("stores a single answer", function() {
  recordAnswer("AKs", "UTG", "RFI", 25, "raise", "raise", true);
  expect(loadHistory().length).toBe(1);
});

test("appends without overwriting previous answers", function() {
  recordAnswer("AKs", "UTG", "RFI", 25, "raise", "raise", true);
  recordAnswer("QQ",  "BTN", "RFI", 25, "fold",  "raise", false);
  expect(loadHistory().length).toBe(2);
});

test("saves all expected fields", function() {
  recordAnswer("KJs", "BTN", "RFI", 80, "fold", "raise", false);
  var entry = loadHistory()[0];
  expect(entry.hand).toBe("KJs");
  expect(entry.position).toBe("BTN");
  expect(entry.situation).toBe("RFI");
  expect(entry.stack_depth).toBe(80);
  expect(entry.user_action).toBe("fold");
  expect(entry.correct_action).toBe("raise");
  expect(entry.is_correct).toBe(false);
  expect(entry.timestamp).toBeDefined();
});

// --- weakSpots ---

test("returns empty object when there is no history", function() {
  expect(weakSpots()).toEqual({});
});

test("excludes spots with fewer than 3 hands", function() {
  recordAnswer("AKs", "UTG", "RFI", 25, "raise", "raise", true);
  recordAnswer("QQ",  "UTG", "RFI", 25, "raise", "raise", true);
  expect(weakSpots()).toEqual({});
});

test("includes a spot once 3 hands are played", function() {
  recordAnswer("AKs", "UTG", "RFI", 25, "raise", "raise", true);
  recordAnswer("QQ",  "UTG", "RFI", 25, "raise", "raise", true);
  recordAnswer("22",  "UTG", "RFI", 25, "raise", "fold",  false);
  var spots = weakSpots();
  expect(spots["UTG|RFI|25"]).toBeDefined();
});

test("computes accuracy correctly", function() {
  recordAnswer("AKs", "UTG", "RFI", 25, "raise", "raise", true);
  recordAnswer("QQ",  "UTG", "RFI", 25, "raise", "raise", true);
  recordAnswer("22",  "UTG", "RFI", 25, "raise", "fold",  false);
  var spot = weakSpots()["UTG|RFI|25"];
  expect(spot.hands_played).toBe(3);
  expect(spot.correct).toBe(2);
  expect(spot.accuracy).toBeCloseTo(2 / 3);
});

test("tracks two different spots independently", function() {
  for (var i = 0; i < 3; i++) recordAnswer("AKs", "BTN", "RFI",     80, "raise", "raise", true);
  for (var i = 0; i < 3; i++) recordAnswer("AKs", "UTG", "VS_SHOVE", 25, "call",  "call",  true);
  var spots = weakSpots();
  expect(spots["BTN|RFI|80"]).toBeDefined();
  expect(spots["UTG|VS_SHOVE|25"]).toBeDefined();
  expect(Object.keys(spots).length).toBe(2);
});

test("minHands threshold can be changed by the caller", function() {
  for (var i = 0; i < 5; i++) recordAnswer("AKs", "UTG", "RFI", 25, "raise", "raise", true);
  expect(weakSpots(5)["UTG|RFI|25"]).toBeDefined(); // exactly 5 — should pass
  expect(weakSpots(6)).toEqual({});                 // only 5 hands — should be excluded
});

// --- clearHistory ---

test("wipes all stored entries", function() {
  recordAnswer("AKs", "UTG", "RFI", 25, "raise", "raise", true);
  clearHistory();
  expect(loadHistory().length).toBe(0);
});
