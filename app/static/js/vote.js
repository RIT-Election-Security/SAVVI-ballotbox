function fillClosestContestContainer(id) {
    selected_radio = document.getElementById(id);
    container = selected_radio.closest(".contest-container")
    container.style.borderColor = "lightgreen";
    container.style.backgroundColor = "honeydew";
}