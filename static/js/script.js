document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const button = form.querySelector('button');

    form.addEventListener('submit', () => {
        button.disabled = true;
        button.textContent = 'Processing...';
        button.style.backgroundColor = '#5e1e99';
    });
});
