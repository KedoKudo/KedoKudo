const fs = require('fs');
const path = require('path');
const https = require('https');

const username = process.env.GITHUB_USERNAME || 'KedoKudo';
const token = process.env.GITHUB_TOKEN;
const apiBase = 'https://api.github.com';
const orgNames = (process.env.ORG_NAMES || '')
  .split(',')
  .map((name) => name.trim())
  .filter(Boolean);
const orgRepoFilter = (process.env.ORG_REPO_FILTER || 'contributed').toLowerCase();
const orgRepoLimit = Number.parseInt(process.env.ORG_REPO_LIMIT || '', 10);

const headers = {
  'User-Agent': 'kedokudo-profile-automation',
  Accept: 'application/vnd.github+json',
};

if (token) {
  headers.Authorization = `Bearer ${token}`;
}

function requestJson(url) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, { headers }, (res) => {
      const chunks = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => {
        const body = Buffer.concat(chunks).toString('utf-8');
        if (res.statusCode && res.statusCode >= 400) {
          return reject(
            new Error(
              `Request failed (${res.statusCode}) for ${url}: ${body}`,
            ),
          );
        }
        try {
          resolve(JSON.parse(body));
        } catch (err) {
          reject(
            new Error(`Failed to parse JSON response from ${url}: ${err}`),
          );
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function fetchUser() {
  return requestJson(`${apiBase}/users/${username}`);
}

async function fetchAllRepos(page = 1, acc = []) {
  const repos = await requestJson(
    `${apiBase}/users/${username}/repos?per_page=100&page=${page}`,
  );
  if (!Array.isArray(repos) || repos.length === 0) {
    return acc;
  }
  const next = acc.concat(repos);
  if (repos.length < 100) {
    return next;
  }
  return fetchAllRepos(page + 1, next);
}

async function fetchOrgRepos(org, page = 1, acc = []) {
  const repos = await requestJson(
    `${apiBase}/orgs/${org}/repos?type=public&per_page=100&page=${page}`,
  );
  if (!Array.isArray(repos) || repos.length === 0) {
    return acc;
  }
  const next = acc.concat(repos);
  if (repos.length < 100) {
    return next;
  }
  return fetchOrgRepos(org, page + 1, next);
}

async function isContributor(owner, repo) {
  const targetLogin = username.toLowerCase();
  let page = 1;
  while (page < 25) {
    const contributors = await requestJson(
      `${apiBase}/repos/${owner}/${repo}/contributors?per_page=100&page=${page}`,
    );
    if (!Array.isArray(contributors) || contributors.length === 0) {
      return false;
    }
    const match = contributors.find(
      (contributor) => contributor.login && contributor.login.toLowerCase() === targetLogin,
    );
    if (match) {
      return true;
    }
    if (contributors.length < 100) {
      return false;
    }
    page += 1;
  }
  return false;
}

async function filterOrgReposByContribution(repos) {
  const filtered = [];
  for (const repo of repos) {
    const [owner, name] = (repo.full_name || '').split('/');
    if (!owner || !name) {
      continue;
    }
    try {
      const contributed = await isContributor(owner, name);
      if (contributed) {
        filtered.push(repo);
      }
    } catch (err) {
      console.warn(`Skipping ${repo.full_name} due to contributor check failure.`, err);
    }
    if (orgRepoLimit > 0 && filtered.length >= orgRepoLimit) {
      break;
    }
  }
  return filtered;
}

function mergeRepos(primary, additional) {
  const byFullName = new Map();
  primary.forEach((repo) => {
    if (repo && repo.full_name) {
      byFullName.set(repo.full_name, repo);
    }
  });
  additional.forEach((repo) => {
    if (repo && repo.full_name && !byFullName.has(repo.full_name)) {
      byFullName.set(repo.full_name, repo);
    }
  });
  return Array.from(byFullName.values());
}

function summarizeLanguages(repos) {
  const counts = {};
  let totalCount = 0;
  repos.forEach((repo) => {
    if (repo.language) {
      const lang = repo.language;
      counts[lang] = (counts[lang] || 0) + 1;
      totalCount += 1;
    }
  });

  const entries = Object.entries(counts)
    .map(([language, count]) => ({
      language,
      count,
      percent: totalCount === 0 ? 0 : Number(((count / totalCount) * 100).toFixed(1)),
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 4);

  const topLanguagesText =
    entries.length === 0
      ? 'Not enough public repositories to determine top languages.'
      : entries.map((entry) => `${entry.language} (${entry.percent}%)`).join(', ');

  return {
    topLanguages: entries,
    topLanguagesText,
  };
}

function formatNumber(value) {
  return new Intl.NumberFormat('en-US').format(value);
}

function buildSvg(stats) {
  const width = 600;
  const height = 320;
  const padding = 24;
  const maxBarWidth = width - padding * 2 - 140;
  const titleY = padding + 20;
  const lines = [
    `Followers: ${formatNumber(stats.followers)}`,
    `Following: ${formatNumber(stats.following)}`,
    `Repos tracked: ${formatNumber(stats.trackedRepos ?? stats.publicRepos)}`,
    `Stars earned: ${formatNumber(stats.totalStars)}`,
  ];

  const baseY = titleY + 30;
  const lineSpacing = 24;

  const statLines = lines
    .map(
      (line, index) =>
        `<text x="${padding}" y="${baseY + index * lineSpacing}" class="stat-line">${line}</text>`,
    )
    .join('\n');

  const barStartY = baseY + lines.length * lineSpacing + 48;

  const bars = stats.topLanguages
    .map((lang, idx) => {
      const barWidth = (lang.percent / 100) * maxBarWidth;
      const y = barStartY + idx * 28;
      return `
      <text x="${padding}" y="${y}" class="lang-name">${lang.language}</text>
      <rect x="${padding + 110}" y="${y - 14}" width="${barWidth}" height="16" rx="4" class="bar"></rect>
      <text x="${padding + 110 + barWidth + 8}" y="${y}" class="lang-percent">${lang.percent}%</text>
    `;
    })
    .join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .card { fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 16; }
    .title { font: 700 20px 'Segoe UI', Ubuntu, Sans-Serif; fill: #f0f6fc; }
    .stat-line { font: 400 16px 'Segoe UI', Ubuntu, Sans-Serif; fill: #c9d1d9; }
    .lang-name { font: 600 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: #58a6ff; }
    .lang-percent { font: 400 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8b949e; }
    .bar { fill: #2ea043; }
  </style>
  <rect class="card" x="0.5" y="0.5" width="${width - 1}" height="${height - 1}" rx="16" />
  <text x="${padding}" y="${titleY}" class="title">GitHub Snapshot · ${new Date(stats.generatedAt).toLocaleDateString(
    'en-US',
  )}</text>
  ${statLines}
  <text x="${padding}" y="${barStartY - 24}" class="stat-line">Top languages</text>
  ${bars || `<text x="${padding}" y="${barStartY + 4}" class="lang-name">No data yet</text>`}
</svg>`;
}

function ensureLanguageFields(stats) {
  if (stats.topLanguages && stats.topLanguagesText) {
    return stats;
  }

  const languages = Array.isArray(stats.topLanguages) ? stats.topLanguages : [];
  const hasValidEntry = languages.length > 0 && typeof languages[0].language === 'string';
  if (hasValidEntry && stats.topLanguagesText) {
    return stats;
  }

  const fallbackText =
    languages.length === 0
      ? 'Not enough public repositories to determine top languages.'
      : languages.map((entry) => `${entry.language} (${entry.percent ?? '?'}%)`).join(', ');
  return {
    ...stats,
    topLanguages: languages,
    topLanguagesText: fallbackText,
  };
}

async function run() {
  try {
    let stats;
    if (process.env.STATS_SOURCE_FILE) {
      const offlinePath = path.resolve(process.env.STATS_SOURCE_FILE);
      stats = JSON.parse(fs.readFileSync(offlinePath, 'utf-8'));
      if (!stats.generatedAt) {
        stats.generatedAt = new Date().toISOString();
      }
      stats = ensureLanguageFields(stats);
    } else {
      const user = await fetchUser();
      const userRepos = await fetchAllRepos();
      let orgRepos = [];
      if (orgNames.length > 0) {
        for (const org of orgNames) {
          const repos = await fetchOrgRepos(org);
          orgRepos = orgRepos.concat(repos);
        }
        if (orgRepoFilter !== 'all') {
          orgRepos = await filterOrgReposByContribution(orgRepos);
        }
        if (orgRepoLimit > 0) {
          orgRepos = orgRepos.slice(0, orgRepoLimit);
        }
      }
      const trackedRepos = mergeRepos(userRepos, orgRepos);
      const { topLanguages, topLanguagesText } = summarizeLanguages(trackedRepos);
      stats = {
        username,
        generatedAt: new Date().toISOString(),
        followers: user.followers,
        following: user.following,
        publicRepos: user.public_repos,
        trackedRepos: trackedRepos.length,
        totalStars: trackedRepos.reduce((sum, repo) => sum + (repo.stargazers_count || 0), 0),
        topLanguages,
        topLanguagesText,
        orgsIncluded: orgNames,
        orgRepoFilter,
      };
    }

    if (!stats.username) {
      stats.username = username;
    }

    fs.mkdirSync(path.join(__dirname, 'data'), { recursive: true });
    fs.mkdirSync(path.join(__dirname, 'assets'), { recursive: true });

    fs.writeFileSync(
      path.join(__dirname, 'data', 'stats.json'),
      `${JSON.stringify(stats, null, 2)}\n`,
    );
    fs.writeFileSync(path.join(__dirname, 'assets', 'stats.svg'), buildSvg(stats));
    console.log('GitHub stats updated successfully.');
  } catch (err) {
    console.error('Failed to update GitHub stats.', err);
    process.exit(1);
  }
}

run();
