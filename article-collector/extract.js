#!/usr/bin/env node

/**
 * 文章提取工具
 * 支持提取微信公众号文章和普通网页内容
 */

const cheerio = require('cheerio');
const dayjs = require('dayjs');
const rp = require('request-promise');
const qs = require('qs');
const unescape = require('lodash.unescape');

/**
 * 从URL或HTML提取文章内容
 * @param {string} input - URL或HTML内容
 * @param {object} options - 配置选项
 * @returns {Promise<object>} 提取结果
 */
async function extract(input, options = {}) {
  const {
    shouldReturnContent = true,
    shouldReturnRawMeta = false,
    shouldFollowTransferLink = true,
    shouldExtractMpLinks = false,
    shouldExtractTags = false,
    shouldExtractRepostMeta = false,
    url: sourceUrl = null
  } = options;

  try {
    let html, url;

    // 判断输入是URL还是HTML
    if (input.startsWith('http://') || input.startsWith('https://')) {
      url = input;
      html = await fetchHTML(url);
    } else {
      html = input;
      url = sourceUrl || extractUrlFromHtml(html);
    }

    // 使用cheerio解析HTML
    const $ = cheerio.load(html);
    
    // 检测文章类型
    const articleType = detectArticleType($, url);
    
    // 根据类型提取内容
    let result;
    if (articleType === 'wechat') {
      result = await extractWechatArticle($, html, url, {
        shouldReturnContent,
        shouldReturnRawMeta,
        shouldFollowTransferLink,
        shouldExtractMpLinks,
        shouldExtractTags,
        shouldExtractRepostMeta
      });
    } else {
      result = await extractGenericArticle($, html, url, {
        shouldReturnContent
      });
    }

    return result;
  } catch (error) {
    return {
      done: false,
      code: 1000,
      msg: `文章获取失败: ${error.message}`
    };
  }
}

/**
 * 获取HTML内容
 */
async function fetchHTML(url) {
  try {
    const html = await rp({
      uri: url,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      },
      timeout: 30000
    });
    return html;
  } catch (error) {
    throw new Error(`请求失败: ${error.message}`);
  }
}

/**
 * 检测文章类型
 */
function detectArticleType($, url) {
  if (url && url.includes('mp.weixin.qq.com')) {
    return 'wechat';
  }
  return 'generic';
}

/**
 * 从HTML中提取URL
 */
function extractUrlFromHtml(html) {
  const match = html.match(/var msg_link = "([^"]+)"/);
  return match ? match[1] : null;
}

/**
 * 提取微信公众号文章
 */
async function extractWechatArticle($, html, url, options) {
  try {
    // 提取脚本中的数据
    const scriptData = extractScriptData(html);
    
    // 基础信息
    const data = {
      // 账号信息
      account_name: scriptData.nickname || $('#js_name').text().trim(),
      account_alias: scriptData.alias || $('#js_alias').text().trim(),
      account_avatar: scriptData.round_head_img || $('#js_avatar').attr('src'),
      account_description: $('#js_desc').text().trim(),
      account_id: scriptData.user_name || '',
      account_biz: scriptData.__biz || extractBiz(url),
      
      // 文章信息
      msg_title: scriptData.title || $('.rich_media_title').text().trim(),
      msg_desc: scriptData.desc || $('.rich_media_meta_desc').text().trim(),
      msg_cover: scriptData.cover || $('#js_cover').attr('src'),
      msg_author: scriptData.author || $('#js_name').text().trim(),
      msg_type: detectMsgType($),
      msg_has_copyright: scriptData.copyright_stat === 1,
      
      // 链接信息
      msg_link: url,
      msg_source_url: scriptData.source_url || '',
    };

    // 提取发布时间
    if (scriptData.create_time) {
      data.msg_publish_time = new Date(scriptData.create_time * 1000);
      data.msg_publish_time_str = dayjs(data.msg_publish_time).format('YYYY/MM/DD HH:mm:ss');
    }

    // 提取正文内容
    if (options.shouldReturnContent) {
      const contentEl = $('.rich_media_content');
      if (contentEl.length > 0) {
        data.msg_content = contentEl.html();
        data.msg_content_text = contentEl.text().trim();
        
        // 提取正文中的所有图片URL
        data.msg_images = [];
        contentEl.find('img').each((i, el) => {
          const img = $(el);
          const src = img.attr('data-src') || img.attr('src');
          if (src && src.startsWith('http')) {
            data.msg_images.push({
              url: src.replace(/&amp;/g, '&'),
              alt: img.attr('alt') || '',
              width: img.attr('data-w') || img.attr('width') || '',
              height: img.attr('data-h') || img.attr('height') || ''
            });
          }
        });
      }
    }

    // 提取嵌入的微信文章链接
    if (options.shouldExtractMpLinks) {
      data.mp_links = [];
      $('a[href*="mp.weixin.qq.com"]').each((i, el) => {
        data.mp_links.push($(el).attr('href'));
      });
    }

    // 提取标签
    if (options.shouldExtractTags) {
      data.tags = [];
      $('.rich_media_tag_link').each((i, el) => {
        data.tags.push($(el).text().trim());
      });
    }

    return {
      done: true,
      code: 0,
      data
    };
  } catch (error) {
    return {
      done: false,
      code: 1005,
      msg: `脚本解析失败: ${error.message}`
    };
  }
}

/**
 * 提取普通网页文章
 */
async function extractGenericArticle($, html, url, options) {
  try {
    // 尝试提取常见meta标签
    const data = {
      msg_title: $('meta[property="og:title"]').attr('content') ||
                  $('meta[name="title"]').attr('content') ||
                  $('title').text().trim(),
      
      msg_desc: $('meta[property="og:description"]').attr('content') ||
                $('meta[name="description"]').attr('content') ||
                $('meta[name="Description"]').attr('content'),
      
      msg_cover: $('meta[property="og:image"]').attr('content') ||
                 $('meta[name="image"]').attr('content'),
      
      msg_author: $('meta[name="author"]').attr('content') ||
                  $('meta[property="article:author"]').attr('content'),
      
      msg_link: url,
      msg_type: 'article',
    };

    // 提取发布时间
    const publishTime = $('meta[property="article:published_time"]').attr('content') ||
                       $('meta[name="publishdate"]').attr('content') ||
                       $('meta[name="date"]').attr('content');
    
    if (publishTime) {
      data.msg_publish_time = new Date(publishTime);
      data.msg_publish_time_str = dayjs(data.msg_publish_time).format('YYYY/MM/DD HH:mm:ss');
    }

    // 提取正文内容
    if (options.shouldReturnContent) {
      // 尝试常见的文章容器
      const contentSelectors = [
        'article',
        '.post-content',
        '.article-content',
        '.entry-content',
        '.content',
        '#content',
        'main'
      ];
      
      for (const selector of contentSelectors) {
        const contentEl = $(selector);
        if (contentEl.length > 0) {
          data.msg_content = contentEl.html();
          data.msg_content_text = contentEl.text().trim();
          break;
        }
      }
      
      // 如果没找到，尝试提取body
      if (!data.msg_content) {
        data.msg_content = $('body').html();
        data.msg_content_text = $('body').text().trim();
      }
    }

    return {
      done: true,
      code: 0,
      data
    };
  } catch (error) {
    return {
      done: false,
      code: 1005,
      msg: `内容提取失败: ${error.message}`
    };
  }
}

/**
 * 从脚本中提取数据
 */
function extractScriptData(html) {
  const data = {};
  
  // 提取 window.msg_title
  const titleMatch = html.match(/var msg_title = "([^"]+)"/);
  if (titleMatch) data.title = unescape(titleMatch[1]);
  
  // 提取其他变量
  const patterns = {
    desc: /var msg_desc = "([^"]+)"/,
    link: /var msg_link = "([^"]+)"/,
    cover: /var msg_cover = "([^"]+)"/,
    nickname: /var nickname = "([^"]+)"/,
    alias: /var alias = "([^"]+)"/,
    user_name: /var user_name = "([^"]+)"/,
    author: /var author = "([^"]+)"/,
    create_time: /var create_time = "(\d+)"/,
    source_url: /var source_url = "([^"]+)"/,
    __biz: /var __biz = "([^"]+)"/,
    copyright_stat: /var copyright_stat = "(\d+)"/,
  };
  
  for (const [key, pattern] of Object.entries(patterns)) {
    const match = html.match(pattern);
    if (match) {
      data[key] = key === 'create_time' || key === 'copyright_stat' 
        ? parseInt(match[1]) 
        : unescape(match[1]);
    }
  }
  
  return data;
}

/**
 * 从URL中提取biz参数
 */
function extractBiz(url) {
  const match = url.match(/__biz=([^&]+)/);
  return match ? match[1] : '';
}

/**
 * 检测文章类型
 */
function detectMsgType($) {
  if ($('.rich_media_video').length > 0) return 'video';
  if ($('.rich_media_images').length > 0) return 'image';
  if ($('.rich_media_voice').length > 0) return 'voice';
  if ($('.rich_media_repost').length > 0) return 'repost';
  return 'post';
}

// 命令行接口
if (require.main === module) {
  const url = process.argv[2];
  if (!url) {
    console.error('Usage: node extract.js <url>');
    process.exit(1);
  }
  
  extract(url, {
    shouldReturnContent: true
  }).then(result => {
    console.log(JSON.stringify(result, null, 2));
  }).catch(error => {
    console.error('Error:', error.message);
    process.exit(1);
  });
}

module.exports = { extract };
