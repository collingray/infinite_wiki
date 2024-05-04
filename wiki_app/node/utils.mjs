import { JSDOM } from 'jsdom';

export function name_to_id(name) {
  return encodeURI(name.replace(/\s+/g, '_'));
}

export function add_links(html) {
  const dom = new JSDOM(html);
  const links = dom.window.document.querySelectorAll('a:not([href])');
  links.forEach(link => {
    link.setAttribute('href', `/wiki/${name_to_id(link.textContent)}`);
  });

  return dom.serialize();
}