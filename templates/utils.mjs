export function name_to_id(name) {
  return encodeURI(name.replace(/\s+/g, '_'));
}