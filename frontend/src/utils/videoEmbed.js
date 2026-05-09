const PLATFORMS = {
  bilibili: {
    name: 'Bilibili',
    patterns: [
      [/{% *bilibili +(\S+) *%}/i, 1],
      [/bilibili\.com\/video\/(BV\w+)/i, 1],
      [/b23\.tv\/(\w+)/i, 1],
    ],
    render(id) {
      const bvid = id.startsWith('BV') ? id : id;
      return `<iframe src="https://player.bilibili.com/player.html?bvid=${bvid}&page=1&isOutside=true&autoplay=0&danmaku=0" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>`;
    },
  },
  youtube: {
    name: 'YouTube',
    patterns: [
      [/{% *youtube +(\S+) *%}/i, 1],
      [/youtube\.com\/watch\?v=([\w-]+)/i, 1],
      [/youtu\.be\/([\w-]+)/i, 1],
    ],
    render(id) {
      return `<iframe src="https://www.youtube.com/embed/${id}" sandbox="allow-scripts allow-same-origin allow-popups" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
    },
  },
};

function wrapEmbed(html) {
  return `<div class="video-embed">${html}</div>`;
}

export function parseVideoEmbeds(text) {
  let result = text;

  for (const [, platform] of Object.entries(PLATFORMS)) {
    for (const [pattern, groupIdx] of platform.patterns) {
      result = result.replace(pattern, (match, id) => {
        return wrapEmbed(platform.render(id));
      });
    }
  }

  return result;
}

export function extractVideoId(input) {
  const trimmed = input.trim();
  for (const [key, platform] of Object.entries(PLATFORMS)) {
    for (const [pattern, groupIdx] of platform.patterns) {
      const m = trimmed.match(pattern);
      if (m) {
        return { platform: key, id: m[groupIdx] };
      }
    }
  }
  return null;
}

export function getPlatformNames() {
  return Object.entries(PLATFORMS).map(([key, p]) => ({ key, name: p.name }));
}
