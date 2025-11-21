document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss flash messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    });

    // Add hover effect to cards
    const cards = document.querySelectorAll('.glass-panel');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });
});

// Modal Functions
function openUploadModal() {
    const modal = document.getElementById('uploadModal');
    modal.style.display = 'flex';
    // Add simple animation
    modal.style.opacity = '0';
    setTimeout(() => modal.style.opacity = '1', 10);
}

function closeUploadModal() {
    const modal = document.getElementById('uploadModal');
    modal.style.opacity = '0';
    setTimeout(() => modal.style.display = 'none', 300);
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('uploadModal');
    if (event.target == modal) {
        closeUploadModal();
    }
}
