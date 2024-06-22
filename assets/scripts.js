// assets/scripts.js
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.Select').forEach(function (dropdown) {
        dropdown.addEventListener('click', function () {
            dropdown.querySelectorAll('.Select-multi-value').forEach(function (item) {
                item.style.display = 'inline-block';
            });
            const extra = dropdown.querySelector('.Select-multi-value:first-of-type::after');
            if (extra) extra.style.display = 'none';
        });
    });
});
