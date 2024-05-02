import {name_to_id} from "./utils.mjs";

export function contents_template(content) {
  const keys = Object.keys(content);

  let out = ""

  for (let i = 0; i < keys.length; i++) {
    let key = keys[i];

    // Skip the summary, it doesn't have a header
    if (key !== "summary") {
      let id = name_to_id(key);

      // If the content is an object, it's contains subsections and should be a dropdown
      if (content[key].constructor === Object) {
        out += `<li class="dropdown">
    <button class="dropdown-button">
        <span class="dropdown-button-src"></span>
    </button>
    <a href="#${id}">${key}</a>
    <ul>
        ${contents_template(content[key])}
    </ul>
</li>
`
      } else {
        out += `<li><a href="#${id}">${key}</a></li>`
      }
    }
  }

  return out;
}