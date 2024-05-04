import fs from 'fs';
import yaml from 'js-yaml';
import {index_template} from "index_template.mjs";
import {add_links} from "utils.mjs";

function main() {

  if (process.argv.length !== 4) {
    console.error('Usage: node generate_html.mjs <input_file> <output_file>');
    process.exit(1);
  }

  let input_file = process.argv[2];
  let output_file = process.argv[3];

  try {
    const doc = yaml.load(fs.readFileSync(input_file, 'utf8'));
    let htmlOutput = index_template(doc);
    htmlOutput = add_links(htmlOutput);
    fs.writeFileSync(output_file, htmlOutput);
    console.log('HTML file has been generated successfully!');
  } catch (e) {
    console.error('Failed to generate HTML:', e);
  }
}

main();
