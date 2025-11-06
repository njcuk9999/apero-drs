//
// bizstyle.js
// ~~~~~~~~~~~
//
// Sphinx javascript -- for bizstyle theme.
//
// This theme was created by referring to 'sphinxdoc'
//
// :copyright: Copyright 2007-2023 by Sphinx team, see AUTHORS.
// :license: BSD, see LICENSE for details.
//
const initialiseBizStyle = () => {
    if (navigator.userAgent.includes("iPhone") || navigator.userAgent.includes("Android")) {
        document.querySelector("li.nav-item-0 a").innerText = "Top";
    }

    const truncator = item => {
        if (item.textContent.length > 20) {
            item.title = item.innerText;
            item.innerText = item.innerText.substring(0, 17) + "...";
        }
    };

    // Convert NodeList → Array and skip index 0:
    [...document.querySelectorAll("div.related:first-of-type ul li:not(.right) a")]
        .slice(1).forEach(truncator);

    [...document.querySelectorAll("div.related:last-of-type ul li:not(.right) a")]
        .slice(1).forEach(truncator);
};

window.addEventListener("resize",
  () => (document.querySelector("li.nav-item-0 a").innerText = (window.innerWidth <= 776) ? "Top" : "APERO Reduction Interface 0.7.289 documentation")
)

if (document.readyState !== "loading") initialiseBizStyle()
else document.addEventListener("DOMContentLoaded", initialiseBizStyle)