// Order the table
    $(document).ready(function() {
        $('.dataTable').DataTable({
            responsive: true
        });
    });

    let deferredPrompt2;
    const showInstallPrompt = () => {
        if (deferredPrompt2) {
            Swal.fire({
                title: 'Install our app!',
                text: 'To get the best experience, install our app on your device.',
                icon: 'info',
                showCancelButton: true,
                confirmButtonText: 'Install',
                cancelButtonText: 'Maybe later',
                reverseButtons: true
            }).then((result) => {
                if (result.isConfirmed) {
                    deferredPrompt2.prompt();
                    deferredPrompt2.userChoice.then((choiceResult) => {
                        if (choiceResult.outcome === 'accepted') {
                            Swal.fire('Installed', 'The app has been installed.', 'success');
                        } else {
                            Swal.fire('Not Installed', 'The app was not installed.', 'info');
                            // Set timeout for showing prompt again in 1 minute
                            localStorage.setItem('nextPromptTime', Date.now() + 1 * 60 * 1000);
                        }
                        deferredPrompt2 = null;
                    });
                }
            });
        }
    };
    
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt2 = e;
    
        const lastPromptTime = localStorage.getItem('lastPromptTime');
        const nextPromptTime = localStorage.getItem('nextPromptTime');
        const now = Date.now();
        //const oneHour = 3600000; // 1 hour in milliseconds
        const teenMinutes = 180000; // 10 minutes in milliseconds
    
        if (!lastPromptTime || (now - lastPromptTime) > teenMinutes) {
            if (!nextPromptTime || now > nextPromptTime) {
                showInstallPrompt();
                localStorage.setItem('lastPromptTime', now);
            }
        }
    });
    
