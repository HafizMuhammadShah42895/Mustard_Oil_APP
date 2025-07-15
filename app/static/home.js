AOS.init({ duration: 1000 });
    $("a[href^='#']").on("click", function (e) {
      e.preventDefault();
      const target = $($(this).attr("href"));
      if (target.length) {
        $('html, body').animate({ scrollTop: target.offset().top }, 600);
      }
    });




function scrollCarousel(direction) {
    const container = document.getElementById('carouselContainer');
    const card = container.querySelector('.carousel-card');
    const scrollAmount = card.offsetWidth + 24;
    container.scrollBy({ left: scrollAmount * direction, behavior: 'smooth' });
  }