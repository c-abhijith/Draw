function validateUsername() {
    const username = document.getElementById("username").value;
    const usernameError = document.getElementById("usernameError");

    if (username.length < 4) {
        usernameError.textContent = "Username must be at least 4 characters long.";
    } else {
        usernameError.textContent = "";
    }
}

function validateEmail() {
    const email = document.getElementById("email").value;
    const emailError = document.getElementById("emailError");
    const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/; // Basic email validation

    if (!email.match(emailPattern)) {
        emailError.textContent = "Please enter a valid email address.";
    } else {
        emailError.textContent = "";
    }
}

function validatePassword() {
    const password = document.getElementById("password").value;
    const passwordError = document.getElementById("passwordError");

    if (password.length < 8) {
        passwordError.textContent = "Password must be at least 8 characters long.";
    } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        passwordError.textContent = "Password must include at least one special character.";
    } else {
        passwordError.textContent = "";
    }
}

function validateLoginUsername() {
    const username = document.getElementById("username").value;
    const loginUsernameError = document.getElementById("loginUsernameError");

    if (username.length < 4) {
        loginUsernameError.textContent = "Username must be at least 4 characters long.";
    } else {
        loginUsernameError.textContent = "";
    }
}

function validateLoginPassword() {
    const password = document.getElementById("password").value;
    const loginPasswordError = document.getElementById("loginPasswordError");

    if (password.length < 8) {
        loginPasswordError.textContent = "Password must be at least 8 characters long.";
    } else {
        loginPasswordError.textContent = "";
    }
}


function toggleLove(element) {
    element.classList.toggle("active");
}