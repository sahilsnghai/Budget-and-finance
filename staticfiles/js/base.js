document.addEventListener('click', function (event) {
    var dropdownMenu = document.getElementById("dropdownMenu");
    var userArea = document.querySelector(".user-info");

    if (!userArea.contains(event.target)) {
        dropdownMenu.style.display = "none";
    }
});

function toggleDropdown() {
    var dropdownMenu = document.getElementById("dropdownMenu");
    dropdownMenu.style.display = (dropdownMenu.style.display === "block") ? "none" : "block";
}
