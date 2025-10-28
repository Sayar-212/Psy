let lastScroll = 0;
const nav = document.querySelector('nav');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > lastScroll && currentScroll > 100) {
        nav.classList.add('scroll-down');
    } else {
        nav.classList.remove('scroll-down');
    }
    
    lastScroll = currentScroll;
});

window.addEventListener('load', () => {
    setTimeout(() => {
        document.querySelector('.split-word').classList.add('animate');
    }, 1500);
});
