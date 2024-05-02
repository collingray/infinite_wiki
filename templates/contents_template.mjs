export function contents_template(content) {
  const keys = Object.keys(content);

  let out = ""

  for (let i = 0; i < keys.length; i++) {
    let key = keys[i];

    // Skip the summary, it doesn't have a header
    if (key !== "summary") {
      // The title is the key with underscores replaced with spaces
      let title = key.replace(/_/g, " ");

      // If the content is an object, it's contains subsections and should be a dropdown
      if (content[key].constructor === Object) {
        out += `<li class="dropdown">
    <button class="dropdown-button">
        <span class="dropdown-button-src"></span>
    </button>
    <a href="#${key}">${title}</a>
    <ul>
        ${contents_template(content[key])}
    </ul>
</li>
`
      } else {
        out += `<li><a href="#${key}">${title}</a></li>`
      }
    }
  }

  return out;
}