// Example: Add scroll animations
document.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('.fade-in');
    sections.forEach(section => {
        const sectionTop = section.getBoundingClientRect().top;
        if (sectionTop < window.innerHeight * 0.75) {
            section.style.opacity = 1;
            section.style.transform = 'translateY(0)';
        }
    });
});