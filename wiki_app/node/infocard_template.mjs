export function infocard_template(card) {

  if (card === undefined) {
    return ""
  }

  let rows = ""

  for (let key in card) {
    if (key !== "title" && key !== "image" && key !== "caption") {
      let name = key.replace(/_/g, " ")
      let value = card[key]

      if (value.constructor === Array) {
        value = value.join("<br>")
      }

      rows +=
        `<tr>
          <th>${name}</th>
          <td>${value}</td>
        </tr>`
    }
  }

  return `<table class="info-card">
    <tbody>
    <tr>
      <td class="info-card-title" colspan="2">${card.title}</td>
    </tr>
    <tr>
      <td class="info-card-image" colspan="2">
        <div class="loading-background">
          <img src="${card.image}" alt="${card.caption.replace('"', '&quot;')}" width="220px" height="294px"/>
        </div>
        <label>${card.caption}</label>
      </td>
    </tr>
    ${rows}
    </tbody>
  </table>`
}