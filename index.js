// index.js
const Mustache = require('mustache');
const fs = require('fs');
const path = require('path');

const MUSTACHE_MAIN_DIR = './main.mustache';
const PROFILE_TIME_ZONE = 'America/Chicago';
/**
  * DATA is the object that contains all
  * the data to be provided to Mustache
  * Notice the "name" and "date" property.
*/
let DATA = {
  name: 'Chen (KedoKudo)',
  date: formatProfileTimestamp(new Date()),
  stats: loadStats(),
};

function loadStats() {
  const fallback = {
    followers: 'N/A',
    following: 'N/A',
    publicRepos: 'N/A',
    trackedRepos: 'N/A',
    totalStars: 'N/A',
    topLanguagesText: 'N/A',
    generatedAt: 'Not yet generated',
  };
  const statsPath = path.join(__dirname, 'data', 'stats.json');
  if (!fs.existsSync(statsPath)) {
    console.warn('stats.json not found, using fallback values.');
    return fallback;
  }

  try {
    const stats = JSON.parse(fs.readFileSync(statsPath, 'utf-8'));
    return {
      followers: formatNumber(stats.followers, fallback.followers),
      following: formatNumber(stats.following, fallback.following),
      publicRepos: formatNumber(stats.publicRepos, fallback.publicRepos),
      trackedRepos: formatNumber(stats.trackedRepos, fallback.trackedRepos),
      totalStars: formatNumber(stats.totalStars, fallback.totalStars),
      topLanguagesText: stats.topLanguagesText ?? fallback.topLanguagesText,
      generatedAt: formatProfileTimestamp(stats.generatedAt) ?? fallback.generatedAt,
    };
  } catch (err) {
    console.warn('Failed to parse stats.json, using fallback values.', err);
    return fallback;
  }
}

function formatProfileTimestamp(value) {
  try {
    const date = value instanceof Date ? value : new Date(value);
    if (Number.isNaN(date.getTime())) {
      throw new Error('Invalid date');
    }
    return date.toLocaleString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      timeZoneName: 'short',
      timeZone: PROFILE_TIME_ZONE,
    });
  } catch (err) {
    return null;
  }
}

function formatNumber(value, fallback = 'N/A') {
  if (typeof value === 'number') {
    return new Intl.NumberFormat('en-US').format(value);
  }
  if (typeof value === 'string' && value.trim().length > 0) {
    return value;
  }
  if (typeof fallback === 'number') {
    return new Intl.NumberFormat('en-US').format(fallback);
  }
  return fallback;
}
/**
  * A - We open 'main.mustache'
  * B - We ask Mustache to render our file with the data
  * C - We create a README.md file with the generated output
  */
function generateReadMe() {
  fs.readFile(MUSTACHE_MAIN_DIR, (err, data) =>  {
    if (err) throw err;
    const output = Mustache.render(data.toString(), DATA);
    fs.writeFileSync('README.md', output);
  });
}
generateReadMe();
