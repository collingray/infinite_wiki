import {contents_template} from "./contents_template.mjs";
import {body_template} from "./body_template.mjs";
import {infocard_template} from "./infocard_template.mjs";

export function index_template(data) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=0.75">
    <title>${data.title}</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="/static/script.js" defer></script>
    <link rel="icon" href="/static/assets/favicon.png" type="image/png">
</head>
<body>
<div class="container">
    <div>
        <a href="/">
          <img src="/static/assets/logo.png" alt="logo" width="80px">
          <div class="logo-text">
              <img src="/static/assets/logo_title.png" alt="infinipedia" width="135px">
              <img src="/static/assets/logo_subtitle.png" alt="the endless encyclopedia" width="135px">
          </div>
        </a>
    </div>
    <div>
        <div id="search" class="search-container">
            <div class="search-bar">
                <svg class="search-magnifying-glass">
                    <path d="M12.2 13.6a7 7 0 111.4-1.4l5.4 5.4-1.4 1.4zM3 8a5 5 0 1010 0A5 5 0 003 8"></path>
                </svg>
                <input class="search-box" type="text" placeholder="Search Infinipedia">
            </div>
            <ul class="search-suggestions"></ul>
        </div>
    </div>
    <div>
        <nav class="table-of-contents">
            <h4>Contents</h4>
            <ul>
                <li><a href="#" class="active">(Top)</a></li>
                ${contents_template(data.content)}
            </ul>
        </nav>
    </div>
    <div class="main-content">
        <h1>${data.title}</h1>
        ${infocard_template(data.card)}
        <div class="main-text">
            ${body_template(data.content)}
        </div>
    </div>
</div>
</body>
</html>`;
}