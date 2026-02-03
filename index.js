// index.js
const Mustache = require('mustache');
const fs = require('fs');
const path = require('path');

const MUSTACHE_MAIN_DIR = './main.mustache';
/**
  * DATA is the object that contains all
  * the data to be provided to Mustache
  * Notice the "name" and "date" property.
*/
let DATA = {
  name: 'Chen (KedoKudo)',
  date: new Date().toLocaleDateString('en-GB', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    timeZoneName: 'short',
    timeZone: 'America/Chicago',
  }),
  stats: loadStats(),
};

function loadStats() {
  const fallback = {
    followers: 'N/A',
    following: 'N/A',
    publicRepos: 'N/A',
    totalStars: 'N/A',
    topLanguagesText: 'N/A',
  };
  const statsPath = path.join(__dirname, 'data', 'stats.json');
  if (!fs.existsSync(statsPath)) {
    console.warn('stats.json not found, using fallback values.');
    return fallback;
  }

  try {
    const stats = JSON.parse(fs.readFileSync(statsPath, 'utf-8'));
    return {
      followers: stats.followers ?? fallback.followers,
      following: stats.following ?? fallback.following,
      publicRepos: stats.publicRepos ?? fallback.publicRepos,
      totalStars: stats.totalStars ?? fallback.totalStars,
      topLanguagesText: stats.topLanguagesText ?? fallback.topLanguagesText,
    };
  } catch (err) {
    console.warn('Failed to parse stats.json, using fallback values.', err);
    return fallback;
  }
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
