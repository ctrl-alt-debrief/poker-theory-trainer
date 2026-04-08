// history.js — tracks player answers and surfaces weak spots
//
// All data is stored in the browser's localStorage under one key.
// localStorage is a built-in browser key/value store that persists
// across page refreshes. Values must be strings, so we use JSON.stringify
// to save and JSON.parse to read back.

var HISTORY_KEY = "poker_trainer_history";


// --- Saving answers ---

// Call this once after the player submits each hand.
// It loads whatever history already exists, adds the new result, and saves it back.
function recordAnswer(hand, position, situation, stackDepth, userAction, correctAction, isCorrect) {
  var history = loadHistory();

  history.push({
    timestamp:      new Date().toISOString(), // e.g. "2026-04-08T14:00:00.000Z"
    hand:           hand,
    position:       position,
    situation:      situation,
    stack_depth:    stackDepth,
    user_action:    userAction,
    correct_action: correctAction,
    is_correct:     isCorrect
  });

  // JSON.stringify turns the array into a string so localStorage can store it
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}


// --- Reading history ---

// Returns the full history array.
// JSON.parse turns the stored string back into a real JavaScript array.
// If nothing is saved yet, getItem returns null — we default to an empty array.
function loadHistory() {
  var stored = localStorage.getItem(HISTORY_KEY);
  if (stored === null) {
    return [];
  }
  return JSON.parse(stored);
}


// --- Weak spot analysis ---

// Reads all history and returns accuracy stats for spots where the
// player has answered at least minHands hands.
//
// A "spot" is the combination of position + situation + stack depth.
// We use those three fields as a key, e.g. "UTG|RFI|25".
//
// Returns an object like:
// {
//   "UTG|RFI|25": { position, situation, stack_depth, hands_played, correct, accuracy },
//   "BTN|RFI|80": { ... }
// }
function weakSpots(minHands) {
  // Default to 3 if the caller doesn't pass a value
  if (minHands === undefined) {
    minHands = 3;
  }

  var history = loadHistory();
  var spots = {};

  // Loop through every recorded answer and group by spot
  for (var i = 0; i < history.length; i++) {
    var entry = history[i];
    var key = entry.position + "|" + entry.situation + "|" + entry.stack_depth;

    // If we haven't seen this spot yet, create a fresh stats object for it
    if (spots[key] === undefined) {
      spots[key] = {
        position:    entry.position,
        situation:   entry.situation,
        stack_depth: entry.stack_depth,
        hands_played: 0,
        correct:      0,
        accuracy:     0
      };
    }

    spots[key].hands_played += 1;
    if (entry.is_correct) {
      spots[key].correct += 1;
    }
  }

  // Second pass: compute accuracy and drop spots below the threshold.
  // We build a new object (result) with only the spots that qualify.
  var result = {};
  for (var key in spots) {
    var stats = spots[key];
    if (stats.hands_played >= minHands) {
      stats.accuracy = stats.correct / stats.hands_played; // e.g. 0.67 means 67%
      result[key] = stats;
    }
  }

  return result;
}


// --- Utility ---

// Wipes all stored history. Hook this up to a "Reset Progress" button.
function clearHistory() {
  localStorage.removeItem(HISTORY_KEY);
}
