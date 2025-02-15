// static/js/main.js

// Function to check if an element is in the viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Function to handle scroll-triggered animations
function handleScrollAnimations() {
    const animatedElements = document.querySelectorAll('.scroll-animate');

    animatedElements.forEach((element) => {
        if (isInViewport(element)) {
            element.classList.add('animate');
        }
    });
}

// Add event listener for scroll
window.addEventListener('scroll', handleScrollAnimations);

// Trigger animations on page load
document.addEventListener('DOMContentLoaded', handleScrollAnimations);
