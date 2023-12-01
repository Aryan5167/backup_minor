// JavaScript (static/index.js)
document.getElementById("diveInBtn").addEventListener("click", function() {
    fetch('/run-main-script', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        console.log('main.py executed:', data);
        // Handle the response as needed
    })
    .catch(error => console.error('Error executing main.py:', error));
});

// Get the button element by ID
var diveInBtn = document.getElementById("diveInBtn");

// Add a mousedown event listener
diveInBtn.addEventListener("mousedown", function() {
    diveInBtn.classList.add("pressed");
});

// Add a mouseup event listener
diveInBtn.addEventListener("mouseup", function() {
    diveInBtn.classList.remove("pressed");
});

// Add a tap event listener (assuming you have a tap event handler)
diveInBtn.addEventListener("tap", function() {
    diveInBtn.classList.remove("pressed");
});

// Add a mouseout event listener
diveInBtn.addEventListener("mouseout", function() {
    diveInBtn.classList.remove("pressed");
});
