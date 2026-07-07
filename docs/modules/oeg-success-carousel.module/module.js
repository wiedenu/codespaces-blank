function sectionCarousel() {
  $("body").find(".section--columns").each(function () {
    var $section = $(this);
    var $cards   = $section.find(".section--columns--card");
    var $dots    = $section.find(".section--columns--dot");
    var $counter = $section.find(".section--columns--counter");
    var total    = $cards.length;
    var current  = 0;

    if (total <= 1) {
      $section.find(".carousel-nav, .section--columns--dots, .section--columns--counter").hide();
      return;
    }

    function goTo(index) {
      $cards.eq(current).removeClass("is-active").attr("aria-hidden", "true");
      $dots.eq(current).removeClass("is-active");

      current = (index + total) % total;

      $cards.eq(current).addClass("is-active").removeAttr("aria-hidden");
      $dots.eq(current).addClass("is-active");
      $counter.text((current + 1) + " of " + total);
    }

    $section.find(".carousel-nav--prev").on("click", function () { goTo(current - 1); });
    $section.find(".carousel-nav--next").on("click", function () { goTo(current + 1); });

    $dots.on("click keypress", function (e) {
      if (e.type === "click" || e.which === 13) {
        goTo(parseInt($(this).data("index"), 10));
      }
    });

    // Keyboard arrow support when focus is inside the section
    $section.on("keydown", function (e) {
      if (e.key === "ArrowLeft")  { goTo(current - 1); }
      if (e.key === "ArrowRight") { goTo(current + 1); }
    });
  });
}

$(document).ready(function () {
  sectionCarousel();
});
