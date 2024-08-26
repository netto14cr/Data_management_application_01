let deferredPrompt;
const installBtn = document.getElementById('installBtn');

// Muestra el botón de instalación solo si hay un prompt pendiente
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    installBtn.style.display = 'block'; // Muestra el botón de instalación
});

// Maneja el clic en el botón de instalación
installBtn.addEventListener('click', () => {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                Swal.fire('Installed', 'The app has been installed.', 'success');
            } else {
                Swal.fire('Not Installed', 'The app was not installed.', 'info');
                // Establece un temporizador para volver a mostrar el botón después de 3 minutos
                localStorage.setItem('nextPromptTime', Date.now() + 3 * 60 * 1000);
            }
            deferredPrompt = null;
            installBtn.style.display = 'none'; // Oculta el botón después de la acción
        });
    }
});

// Oculta el botón si la app ya está instalada
window.addEventListener('appinstalled', () => {
    installBtn.style.display = 'none';
});

// Mostrar el botón de instalación según la configuración de localStorage
const lastPromptTime = localStorage.getItem('lastPromptTime');
const nextPromptTime = localStorage.getItem('nextPromptTime');
const now = Date.now();
const oneHour = 3600000; // 1 hora en milisegundos

if (!lastPromptTime || (now - lastPromptTime) > oneHour) {
    if (!nextPromptTime || now > nextPromptTime) {
        installBtn.style.display = 'block'; // Muestra el botón si corresponde
    }
} else {
    installBtn.style.display = 'none'; // Oculta el botón si el tiempo no ha llegado
}

// Registro del Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/pwa/service/service-worker.js')
        .then(function(registration) {
            console.log('ServiceWorker registrado con éxito:', registration.scope);
        }, function(error) {
            console.log('Fallo al registrar el ServiceWorker:', error);
        });
    });
}
