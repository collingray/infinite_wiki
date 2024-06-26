document.addEventListener('DOMContentLoaded', function () {
  var dropdownButtons = document.getElementsByClassName('dropdown-button');
  var i;

  for (i = 0; i < dropdownButtons.length; i++) {
    dropdownButtons[i].addEventListener("click", function () {
      this.parentElement.classList.toggle("collapsed");
    });
  }

  let data = [];

  fetch('/api/fetch_titles').then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  }).then(json => {
    data = json;
  })

  let search = document.getElementById('search');
  let search_box = search
    .getElementsByClassName('search-bar')[0]
    .getElementsByClassName('search-box')[0];
  let search_suggestions = search
    .getElementsByClassName('search-suggestions')[0];

  search_box.addEventListener('input', function () {
    let input = this.value;
    search_suggestions.innerHTML = '';

    if (input.length > 0) {
      const filteredData = data.filter(item => item.toLowerCase().startsWith(input.toLowerCase()));
      filteredData.forEach(item => {
        let li = document.createElement('li');
        li.textContent = item;
        li.onclick = function () {
          // on click, redirect to the page
          window.location.href = `/wiki/${item.replace(/\s+/g, '_')}`;
        };
        li.style.cursor = 'pointer';
        search_suggestions.appendChild(li);
      });

      if (filteredData.length === 0) {
        li = document.createElement('li');
        li.textContent = `No results found for "${input}"`;
        search_suggestions.appendChild(li);
      }

      search_suggestions.classList.add("suggesting");
    } else {
      search_suggestions.classList.remove("suggesting");
    }
  });

  search_box.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      let input = this.value;
      if (input.length > 0) {
        window.location.href = `/wiki/${input.replace(/\s+/g, '_')}`;
      }
    }
  });

  function throttle(func, limit) {
    let lastFunc;
    let lastRan;
    return function() {
      const context = this;
      const args = arguments;
      if (!lastRan) {
        func.apply(context, args);
        lastRan = Date.now();
      } else {
        clearTimeout(lastFunc);
        lastFunc = setTimeout(function() {
          if ((Date.now() - lastRan) >= limit) {
            func.apply(context, args);
            lastRan = Date.now();
          }
        }, limit - (Date.now() - lastRan));
      }
    }
  }

  const sections = document.querySelectorAll('h2, h3');
  const navLinks = document.querySelectorAll('nav ul li a');

  window.addEventListener('scroll', throttle(() => {
    let current = '';

    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      if (pageYOffset >= (sectionTop - sectionHeight / 3)) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === "#"+current) {
        link.classList.add('active');
      }
    });
  }, 200));
});