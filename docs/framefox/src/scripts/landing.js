document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (this, e) {
        e.preventDefault();

        const href = this.getAttribute("href");
        if (href) {
        const targetElement = document.querySelector(href);
        if (targetElement) {
            targetElement.scrollIntoView({
            behavior: "smooth",
            });
        }
        }
    });
});


// Gestion du menu mobile
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const nav = document.querySelector('nav');
    
    if (mobileMenuToggle && nav) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenuToggle.classList.toggle('active');
            nav.classList.toggle('active');
        });
        
        // Fermer le menu quand on clique sur un lien
        const navLinks = nav.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenuToggle.classList.remove('active');
                nav.classList.remove('active');
            });
        });
    }
});