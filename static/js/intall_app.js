let deferredPrompt;
const installBox = document.getElementById('installBox');

// Show the install button only if there is a pending prompt
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault(); // Prevent the default prompt
    deferredPrompt = e; // Save the event to show the prompt later
    installBox.style.display = 'block'; // Display the install box
});

// Function to handle the installation prompt
function handleInstallPrompt() {
    if (deferredPrompt) {
        deferredPrompt.prompt(); // Show the install prompt
        deferredPrompt.userChoice.then((choiceResult) => {
            const now = Date.now();
            localStorage.setItem('lastPromptTime', now); // Update the last prompt time

            if (choiceResult.outcome === 'accepted') {
                Swal.fire('Installed', 'The app has been installed.', 'success');
            } else {
                Swal.fire('Not Installed', 'The app was not installed.', 'info');
                // Set a timer to show the button again after 3 minutes
                localStorage.setItem('nextPromptTime', now + 3 * 60 * 1000);
            }
            deferredPrompt = null;
            installBox.style.display = 'none'; // Hide the box after the action
        });
    }
}


// Handle the click event on the install box (clicking anywhere in the box will trigger the prompt)
installBox.addEventListener('click', handleInstallPrompt);

// Hide the button if the app is already installed
window.addEventListener('appinstalled', () => {
    installBox.style.display = 'none'; // Hide the install box
});

// Show or hide the install button based on localStorage configuration
function checkInstallButtonVisibility() {
    const lastPromptTime = localStorage.getItem('lastPromptTime');
    const nextPromptTime = localStorage.getItem('nextPromptTime');
    const now = Date.now();
    const oneHour = 3600000; // 1 hour in milliseconds

    if (!lastPromptTime || (now - lastPromptTime) > oneHour) {
        if (!nextPromptTime || now > nextPromptTime) {
            installBox.style.display = 'block'; // Show the install box if appropriate
        } else {
            installBox.style.display = 'none'; // Hide the install box if the time hasn't arrived
        }
    } else {
        installBox.style.display = 'none'; // Hide the install box if the time hasn't arrived
    }
}

// Check the visibility when the page loads
checkInstallButtonVisibility();
