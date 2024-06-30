// navbar.js

function toggleMobileMenu() {
    var x = document.getElementById("myNavbar");
    if (x.className === "navbar") {
        x.className += " responsive";
    } else {
        x.className = "navbar";
        // При закрытии меню на мобильном устройстве скрываем dropdown-content
        document.querySelector(".dropdown-content").style.display = "none";
    }
}


function toggleProfileMenu() {
    var menu = document.getElementById("profileMenu");
    if (menu.style.display === "block") {
        menu.style.display = "none";
    } else {
        menu.style.display = "block";
    }
}
