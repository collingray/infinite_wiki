export function body_template(content, heading_level = 2) {

  let out = ""

  const keys = Object.keys(content);

  for (let i = 0; i < keys.length; i++) {
    let key = keys[i];

    // The summary doesn't have a title
    if (key !== "summary") {
      // The title is the key with underscores replaced with spaces
      let title = key.replace(/_/g, " ");

      out += `<h${heading_level} id="${key}">${title}</h${heading_level}>`
    }

    if (content[key].constructor === Object) {
      out += body_template(content[key], heading_level + 1)
    } else if (content[key].constructor === Array) {
      out += `<ul>`

      for (let j = 0; j < content[key].length; j++) {
        out += `<li>${content[key][j]}</li>`
      }

      out += `</ul>`
    } else {
      let paragraphs = content[key].split("\n")

      for (let j = 0; j < paragraphs.length; j++) {
        out += `<p>${paragraphs[j]}</p>`
      }
    }
  }

  return out;
}